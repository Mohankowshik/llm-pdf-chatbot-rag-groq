
import requests
import json
import os

BASE_URL = "http://localhost:8000"

def test_root():
    print("\nTesting root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}, Response: {response.text}")
    return response.status_code == 200

def test_register():
    print("\nTesting register endpoint...")
    user_data = {
        "username": "testuser001",
        "email": "testuser001@example.com",
        "password": "Testpass123!"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Status: {response.status_code}, Response: {response.text}")
    return response.status_code in [200, 400]  # 400 if already exists, that's okay

def test_login():
    print("\nTesting login endpoint...")
    login_data = {
        "username": "testuser001",
        "password": "Testpass123!"
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    print(f"Status: {response.status_code}, Response: {response.text}")
    if response.status_code == 200:
        token = response.json()["access_token"]
        return token
    return None

def test_upload(token):
    print("\nTesting upload endpoint...")
    # Use existing PDF in backend/uploads/
    pdf_path = os.path.join(os.path.dirname(__file__), "backend", "uploads", "AI_Chatbot_Test_Document.pdf")
    if not os.path.exists(pdf_path):
        print("Test PDF not found, skipping upload test.")
        return False
    
    with open(pdf_path, "rb") as f:
        files = {"files": ("AI_Chatbot_Test_Document.pdf", f, "application/pdf")}
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/api/upload", files=files, headers=headers)
        print(f"Status: {response.status_code}, Response: {response.text}")
        return response.status_code == 200

def test_chat(token):
    print("\nTesting chat endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    chat_data = {"question": "What is this document about?"}
    response = requests.post(f"{BASE_URL}/api/chat", json=chat_data, headers=headers)
    print(f"Status: {response.status_code}, Response: {response.text}")
    return response.status_code == 200

def test_history(token):
    print("\nTesting chat history endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/history", headers=headers)
    print(f"Status: {response.status_code}, Response: {response.text}")
    return response.status_code == 200

if __name__ == "__main__":
    print("=" * 50)
    print("Testing LLM PDF Chatbot Endpoints")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test root
    if not test_root():
        all_tests_passed = False
        
    # Test register
    test_register()  # Okay if already exists
        
    # Test login
    token = test_login()
    if not token:
        print("Login failed, skipping authenticated endpoints.")
        all_tests_passed = False
    else:
        print(f"Successfully obtained token: {token[:20]}...")
        
        # Test upload
        test_upload(token)
        
        # Test chat (twice to test conversation memory)
        print("\n--- First chat test ---")
        test_chat(token)
        print("\n--- Second chat test (follow-up) ---")
        test_chat(token)
        
        # Test history
        test_history(token)
    
    print("\n" + "=" * 50)
    print("Testing complete!")
    print("=" * 50)
