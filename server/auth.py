import os
import time
import pyotp
import bcrypt
import hashlib
import secrets
import functools
import tracemalloc
from database import Database
from config import Config, Protection
from argon2 import PasswordHasher, Type, exceptions

        
# decorator for metrics
def measure_performance(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start() # start RAM measuring
        # measure start time
        start_time_wall = time.perf_counter()
        start_time_cpu = time.process_time()
        
        try:
            result = func(*args, **kwargs)
        finally:
            _, peak_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            # measure end time
            end_time_wall = time.perf_counter()
            end_time_cpu = time.process_time()

        latency_ms = (end_time_wall - start_time_wall) * 1000
        cpu_ms = (end_time_cpu - start_time_cpu) * 1000
        peak_memory_mb = peak_memory / (1024 * 1024)

        if isinstance(result, dict):
            result['metrics'] = {
                'latency_ms': round(latency_ms, 2),
                'cpu_ms': round(cpu_ms, 2),
                'memory_peak_mb': round(peak_memory_mb, 2)
            }
        return result   
    return wrapper

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
            
    @measure_performance
    def auth_totp(self, db: Database, username: str, totp_token) -> bool:
        user = db.get_user(username)
        if user.totp_secret is None:
            return {"status":"totp_failure"}
            
        totp = pyotp.TOTP(user.totp_secret)
        result = totp.verify(totp_token, valid_window=Config.TOTP_VALID_WINDOW)
        status = "totp_success" if result else "totp_failure"
        return {"status":status}
    
    @measure_performance
    def auth(self, db: Database, username: str, password: str, captcha_token) -> bool:
        user = db.get_user(username)
        if Config.PROTECTION_FLAGS & Protection.LOCKOUT and user.is_locked:
            return {"status": "account_locked"}
        
        if Config.PROTECTION_FLAGS & Protection.RATE_LIMIT:
            now = time.time()
            # check if new window
            if now >= user.rl_window_start + Config.RATE_LIMIT_WINDOW_SIZE:
                user.rl_window_start = int(now / Config.RATE_LIMIT_WINDOW_SIZE) * Config.RATE_LIMIT_WINDOW_SIZE
                db.set_new_window(user)
            # check if reached limit.
            elif user.rl_window_attempts + 1 > Config.RATE_LIMIT_ATTEMPTS_IN_WINDOW:
                window_end = user.rl_window_start + Config.RATE_LIMIT_WINDOW_SIZE
                retry_after = window_end - now
                retry_after = max(1, int(retry_after) + 1) # round up to second
                return {"status": "rate_limit_reached", 
                        "data": {"retry_after": retry_after}}   
            else:
                db.increase_window_attempts(user) # increase attempts by 1
                
        if Config.PROTECTION_FLAGS & Protection.CAPTCHA:
            if user.captcha_attempts + 1 > Config.MAX_CAPTCHA_ATTEMPTS: #captacha required
                # if no token or incorrect
                if captcha_token is None or not secrets.compare_digest(str(captcha_token), str(self.captcha_token)):
                    return {"status": "captcha_required"} 
                else: # token is correct
                    db.reset_captcha_attempts(user)
            else:
                db.increase_captcha_attempts(user)
                    
        if Config.PROTECTION_FLAGS & Protection.PEPPER:
            password += self.PEPPER
            
            
        result = self.is_valid_password(password, user.password, user.salt)
        if result:
            if Config.PROTECTION_FLAGS & Protection.LOCKOUT: # set failed attempts to 0
                user.failed_attempts = 0
                db.update_failed_attempts(user)
            if Config.PROTECTION_FLAGS & Protection.TOTP:
                if user.totp_secret is not None: # than totp login required
                    return {"status": "totp_required"}
            return {"status": "success"} 
                    
        else:
            if Config.PROTECTION_FLAGS & Protection.LOCKOUT:
                if user.failed_attempts + 1 >= Config.MAX_ATTEMPTS: # lock account
                    db.lock_account(user)
                else: # increment failed attempts
                    user.failed_attempts += 1
                    db.update_failed_attempts(user)
                    
        return {"status": "failure"} 
    
    def hash(self, password: str) -> str:
        if Config.PROTECTION_FLAGS & Protection.PEPPER:
            password += self.PEPPER
            
        match Config.PASSWORD_HASH_MODE:
            case "SHA256":
                return self.hash_sha256(password)
            case "ARGON2":
                return self.hash_argon2(password)
            case "BCRYPT":
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
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
        
    def validate_argon2(self, stored_hash, password):
        try:
            self.password_hasher.verify(stored_hash, password)
            return True
        except exceptions.VerifyMismatchError:
            return False
        