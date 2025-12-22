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
    
    # hash configs. use aither SHA256 or BCRYPT or ARGON2
    PASSWORD_HASH_MODE = "SHA256"
    # sha256
    SHA256_SALT_SIZE = 16
    # bcrypt
    BCRYPT_COST = 12
    # argon2
    ARGON2_TIME_COST = 1
    ARGON2_MEMORY_COST = 64 * 1024 # in Kib
    ARGON2_PARALLELISM = 1
    ARGON2_LENGTH = 32 # common choice, also same as sha256 - good for comparison
    
    
    # protections enabled - usage: <protection1> | <protection2> | <protection3>
    PROTECTION_FLAGS = Protection.PEPPER | Protection.RATE_LIMIT
    # rate limit
    MS_DELAY = 0 # delay in ms
    # lockout
    MAX_ATTEMPTS = 0
    LOCKOUT_DURATION = 0
    