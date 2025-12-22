from enum import IntFlag

class Protection(IntFlag):
    NONE        = 0
    PEPPER      = 1
    RATE_LIMIT  = 2
    LOCKOUT     = 4
    TOTP        = 8
    CAPTCHA     = 16

class Config:
    GROUP_SEED = 214265977
    EXPERIMENT_NAME = ""
    
    # logging
    LOG_FILE_NAME = EXPERIMENT_NAME + "-logs.json"
    LOG_BUFFER_SIZE = 65536 # for better performances
    
    # SHA256 or BYCRPT or ARGON2
    PASSWORD_HASH_MODE = "SHA256"
    
    # protections enabled - usage: <protection1> | <protection2> | <protection3>
    PROTECTION_FLAGS = Protection.PEPPER | Protection.RATE_LIMIT
    
    # mechanism specific congifs
    # rate limit
    MS_DELAY = 0 # delay in ms
    # lockout
    MAX_ATTEMPTS = 0
    LOCKOUT_DURATION = 0
    
    