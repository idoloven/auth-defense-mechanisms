# from crypto import Crypto
class User():
    def __init__(self, username, password, category, totp_secret) -> None:
        self.username = username
        # self.password = Crypto.hash(password)
        self.category = category
        self.totp_secret = totp_secret
        
        # todo add salt if sha256
        
        