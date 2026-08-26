
from typing import List
import re


# Dictionary of common abbreviations and aliases for hostels
ABBR_DICT = {
    "BH": "Boys Hostel",
    "GH": "Girls Hostel",
    "Hostel": ["Hostel", "H"],
    "Boys Hostel": ["BH", "Boys Hostel"],
    "Girls Hostel": ["GH", "Girls Hostel"],
    "BH5": ["Boys Hostel-05", "Boys Hostel 5", "Hostel 5", "BH-05"],
    "BH05": ["Boys Hostel-05", "Boys Hostel 5", "Hostel 5", "BH5"],
    "BH-05": ["Boys Hostel-05", "Boys Hostel 5", "Hostel 5", "BH5"],
    "Boys Hostel-05": ["BH5", "BH-05", "BH05", "Boys Hostel 5", "Hostel 5"],
    "Boys Hostel 5": ["BH5", "BH-05", "BH05", "Boys Hostel-05", "Hostel 5"],
}


def expand_abbreviations(query: str) -> List[str]:
    """Expand common abbreviations in the query to create multiple variations."""
    queries = [query]
    
    # Process each abbreviation
    for abbr, expansions in ABBR_DICT.items():
        if abbr.lower() in query.lower():
            # For each expansion, create a new query variation
            for exp in expansions:
                # Replace abbreviation with expansion in a case-insensitive way
                pattern = re.compile(re.escape(abbr), re.IGNORECASE)
                new_query = pattern.sub(exp, query)
                if new_query not in queries:
                    queries.append(new_query)
    
    return queries


def rewrite_query(query: str) -> List[str]:
    """
    Rewrite user query to generate multiple variations for multi-query retrieval.
    
    Returns:
        List of rewritten query variations
    """
    variations = []
    
    # 1. Original query
    variations.append(query)
    
    # 2. Expand abbreviations
    abbr_variations = expand_abbreviations(query)
    variations.extend(abbr_variations)
    
    # 3. Simplify query (remove extra words)
    simplified = re.sub(r'[^\w\s]', '', query)  # Remove punctuation
    if simplified not in variations:
        variations.append(simplified)
    
    return list(set(variations))  # Remove duplicates


def generate_multi_queries(original_query: str, num_queries: int = 4) -> List[str]:
    """
    Generate multiple semantically similar queries for multi-query retrieval.
    Uses the query rewriter to create variations focused on abbreviations and synonyms.
    """
    rewritten = rewrite_query(original_query)
    # Limit to num_queries, ensuring original is first
    if original_query not in rewritten:
        rewritten.insert(0, original_query)
    return rewritten[:num_queries]

