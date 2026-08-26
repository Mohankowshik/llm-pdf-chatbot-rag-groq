
import fitz  # PyMuPDF
from typing import List, Dict, Any, Tuple
import re


def extract_tables_and_text_from_page(page, page_num: int) -> List[Dict[str, Any]]:
    """Extract both text and tables from a single page, preserving structure."""
    elements = []
    
    # Extract tables first
    tables = page.find_tables()
    for table in tables:
        table_data = table.extract()
        if table_data and len(table_data) > 0:
            # Format table as Markdown for better preservation
            table_md = []
            for row in table_data:
                # Handle None values
                cleaned_row = [cell if cell is not None else "" for cell in row]
                table_md.append(f"| {' | '.join(cleaned_row)} |")
                if len(table_md) == 1:
                    table_md.append(f"| {' | '.join(['---' for _ in cleaned_row])} |")
            
            elements.append({
                "type": "table",
                "content": "\n".join(table_md),
                "page": page_num
            })
    
    # Extract text with structure (preserve paragraphs, lists, headings)
    text_blocks = page.get_text("blocks")
    for block in text_blocks:
        x0, y0, x1, y1, text, block_no, block_type = block
        if block_type == 0:  # Text block
            cleaned_text = text.strip()
            if cleaned_text:
                # Detect headings (larger font, bold, etc.)
                fonts = []
                for line in page.get_text("dict")["blocks"]:
                    if line.get("lines"):
                        for span in line["lines"]:
                            if span.get("spans"):
                                for s in span["spans"]:
                                    fonts.append(s.get("size", 12))
                
                avg_font = sum(fonts) / len(fonts) if fonts else 12
                
                # Check if this block is likely a heading
                is_heading = False
                for line in page.get_text("dict")["blocks"]:
                    if line.get("lines"):
                        for span in line["lines"]:
                            if span.get("spans"):
                                for s in span["spans"]:
                                    if s.get("text") in cleaned_text and s.get("size", 0) > avg_font:
                                        is_heading = True
                                        break
                
                elements.append({
                    "type": "heading" if is_heading else "text",
                    "content": cleaned_text,
                    "page": page_num
                })
    
    return elements


def load_pdf(file_path: str) -> Dict[str, Any]:
    """
    Load PDF and extract structured content including text, tables, and page metadata.
    
    Returns:
        Dict with:
        - filename: name of the PDF file
        - total_pages: number of pages
        - pages: list of page elements (text, tables, headings) with page numbers
    """
    import os
    filename = os.path.basename(file_path)
    
    doc = fitz.open(file_path)
    all_elements = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        elements = extract_tables_and_text_from_page(page, page_num + 1)
        all_elements.extend(elements)
    
    return {
        "filename": filename,
        "total_pages": len(doc),
        "pages": all_elements
    }

