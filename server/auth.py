import os
import bcrypt
import hashlib
import secrets
from database import Database
from config import Config, Protection
from argon2 import PasswordHasher, Type, exceptions


class AuthManager:
    def __init__(self):
        if Config.PASSWORD_HASH_MODE == "ARGON2":
            self.password_hasher = PasswordHasher(
                time_cost=Config.ARGON2_TIME_COST,
                memory_cost=Config.ARGON2_MEMORY_COST,
                parallelism=Config.ARGON2_PARALLELISM,
                hash_len=Config.ARGON2_LENGTH,
                type=Type.ID
        )
        if Config.PROTECTION_FLAGS & Protection.PEPPER:
            self.PEPPER = os.getenv("PEPPER", "")
            
    def auth(self, db: Database, username: str, password: str) -> bool:
        if Config.PROTECTION_FLAGS & Protection.RATE_LIMIT:
            # todo sleep
            pass
        if Config.PROTECTION_FLAGS & Protection.LOCKOUT:
            pass
        
        if Config.PROTECTION_FLAGS & Protection.PEPPER:
            password += self.PEPPER
            
        user = db.get_user(username)
        return self.is_valid_password(user["password"], user["salt"], password)
    
    def hash(self, password: str) -> str:
        if Config.PROTECTION_FLAGS & Protection.PEPPER:
            password += self.PEPPER
            
        match Config.PASSWORD_HASH_MODE:
            case "SHA256":
                return self.hash_sha256(password)
            case "ARGON2":
                return self.hash_argon2(password)
            case "BYCRPT":
                return self.hash_bcrypt(password)
    
    def is_valid_password(self, password: str, stored_hash: str, stored_salt: str) -> bool:
        match Config.PASSWORD_HASH_MODE:
            case "SHA256":
                return self.validate_sha256(stored_hash, password, stored_salt)
            case "BCRYPT":
                return self.validate_bcrypt(stored_hash, password)
            case "ARGON2":
               return self.validate_argon2(stored_hash, password)

    def hash_sha256(self, password):
        salt = secrets.token_hex(Config.SHA256_SALT_SIZE)
        combined = password + salt
        hashed_password = hashlib.sha256(combined.encode('utf-8')).hexdigest()
        return hashed_password, salt
    
    def hash_bcrypt(self, password):
        password_bytes = password.encode('utf-8')
        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=Config.BCRYPT_COST))
        return hashed_password, None

    def hash_argon2(self, password):
        hashed_password = self.password_hasher.hash(password)   
        return hashed_password, None
    

    def validate_sha256(self, stored_hash, password, stored_salt):
        combined = password + stored_salt
        calculated_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
        return secrets.compare_digest(calculated_hash, stored_hash)
    
    def validate_bcrypt(self, stored_hash, password):
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        
    def validate_argon2(self, stored_hash, password):
        try:
            self.password_hasher.verify(stored_hash, password)
            return True
        except exceptions.VerifyMismatchError:
            return False