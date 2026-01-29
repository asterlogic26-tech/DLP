import requests
import json
import os
import sys

API_URL = "https://cyberguard-backend-l2yo.onrender.com"

def generate_token():
    print("="*50)
    print("CYBERGUARD TOKEN GENERATOR")
    print("="*50)
    print(f"Connecting to: {API_URL}")
    print("-" * 50)

    # 1. Ask for email
    email = input("Enter your email address to register/login: ").strip()
    if not email:
        print("Error: Email cannot be empty.")
        return

    # 2. Send request
    print(f"\nRequesting token for {email}...")
    try:
        response = requests.post(f"{API_URL}/auth/simple", json={"email": email})
        
        # 3. Handle Response
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            
            if token:
                # 4. Save Token
                with open("token.txt", "w") as f:
                    f.write(token)
                
                print("\n[SUCCESS] Token generated successfully!")
                print(f"Token saved to: {os.path.abspath('token.txt')}")
                print("\nInstructions:")
                print("1. Copy this 'token.txt' file.")
                print("2. Paste it into the same folder as your 'CyberGuard_DLP_Agent.exe'.")
                print("3. Run the Agent again.")
            else:
                print("\n[ERROR] Server returned 200 but no token found in response.")
                print(f"Response: {data}")
        
        elif response.status_code == 404:
            print("\n[ERROR] Endpoint not found (404).")
            print("Likely cause: The backend server has not finished deploying the latest code yet.")
            print("Please wait 1-2 minutes and try again.")
            
        else:
            print(f"\n[ERROR] Server returned status code: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"\n[EXCEPTION] Failed to connect: {e}")

if __name__ == "__main__":
    generate_token()
    input("\nPress Enter to exit...")
