import os
import sys
import json
import requests

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
ASSETS_DIR = os.path.join(PROJECT_ROOT, 'assets')
USERS_FILE_PATH = os.path.join(ASSETS_DIR, 'users.json')

SERVER_URL = "http://127.0.0.1:5000"

def register_users():
    print(f"Reading users from {USERS_FILE_PATH}")
    try:
        with open(USERS_FILE_PATH, 'r', encoding='utf-8') as f:
            users_data = json.load(f)
    except FileNotFoundError:
        print(f"file {USERS_FILE_PATH} not found")
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