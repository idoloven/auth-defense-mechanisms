import json
import requests
import sys

SERVER_URL = "http://localhost:5000"
USERS_FILE = "C:\\Users\\idoloven\\university\\courses\\2026\\intro-to-cyber-security\\auth-defense-mechanisms\\assets\\users.json"

def register_users():
    print(f"Reading users from {USERS_FILE}")
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users_data = json.load(f)
    except FileNotFoundError:
        print(f"file {USERS_FILE} not found")
        sys.exit(1)

    for user in users_data["users"]:   
        payload = {
            "username": user.get("username"),
            "password":user.get("password"),
            "category": user.get("category"),
            "totp_secret": user.get("totp_secret")
        }

        try:
            response = requests.post(f"{SERVER_URL}/register", json=payload)
            if response.status_code != 200:
                print("Erorr creting user")
        except requests.exceptions.ConnectionError:
            print(f"Connection Error")
            sys.exit(1)

    print(f"Successfully registered users")

if __name__ == "__main__":
    register_users()