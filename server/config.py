class Config:
    PASSWORD_HASH = "SHA256" # SHA256 or BYCRPT or ARGON2
    
    # enable defense mechanisms
    ENABLE_PEPPER = False
    ENABLE_RATE_LIMIT = False
    ENABLE_LOCKOUT = False
    ENABLE_TOTP = False
    ENABLE_CAPTCHA = False
    
    # mechanism specific congifs
    # rate limit
    MS_DELAY = 0 # delay in ms
    # lockout
    MAX_ATTEMPTS = 0
    LOCKOUT_DURATION = 0
    
    