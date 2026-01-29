import requests
import json

API_URL = "https://cyberguard-backend-l2yo.onrender.com"

def test_signup():
    print(f"Testing Signup on {API_URL}...")
    payload = {
        "email": "debug_user_01@example.com",
        "password": "password123",
        "full_name": "Debug User"
    }
    
    try:
        r = requests.post(f"{API_URL}/auth/signup", json=payload)
        print(f"Status Code: {r.status_code}")
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_signup()
