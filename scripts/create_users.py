import os
import json
import pyotp
import random
import string

DICTIONARY_PATH = '../assets/rockyou.txt'
OUTPUT_FILE = '../assets/users.json'
GROUP_SEED = 214265977
AMOUNT_OF_TOTP_USERS = 1
# week passwords
WEAK_PASSWORDS_AMOUNT = 10
WEAK_PASSWORDS_START_LINE = 0
WEAK_PASSWORDS_END_LINE = 100
WEAK_PASSWORDS_MIN_LENGTH = 0
WEAK_PASSWORDS_MAX_LENGTH = 6
# medium passwords
MEDIUM_PASSWORDS_AMOUNT = 10
MEDIUM_PASSWORDS_START_LINE = 20000
MEDIUM_PASSWORDS_END_LINE = 50000
MEDIUM_PASSWORDS_MIN_LENGTH = 7
MEDIUM_PASSWORDS_MAX_LENGTH = 9
# strong passwords
STRONG_PASSWORD_AMOUNT = 10
STRONG_PASSWORD_LENGTH = 12


def get_passwords_from_dict(start_line, end_line, min_length, max_length, amount):
    if not os.path.exists(DICTIONARY_PATH):
        print(f"Error: {DICTIONARY_PATH} not found!")
        return None, None

    try:
        with open(DICTIONARY_PATH, 'r', encoding='latin-1') as f:
            # extract only desired lines
            lines = f.readlines()
            if len(lines) <= end_line:
                chunk = lines[start_line:]
            else:
                chunk = lines[start_line:end_line]
            
            candidates = set() # set prevents duplications
            # filter matching lines
            for line in chunk:
                password = line.strip()
                if password.isalnum and max_length >= len(password) >= min_length:
                    candidates.add(password)
            candidates = list(candidates)        
            # select correct amount
            if len(candidates) < amount:
                print(f"Not enough passwords were found (only {len(candidates)}).")
                return candidates
            return random.sample(candidates, amount)
                       
    except Exception as e:
        print(f"Error reading file: {e}")
        return None, None      


def generate_strong_passwords(length, amount):
    chars = string.ascii_letters + string.digits # a-z, A-Z, 0-9
    strong_passwords_list = []
    for _ in range(amount):
        strong_passwords_list.append(''.join(random.choice(chars) for _ in range(length)))
    return strong_passwords_list

def main():
    # create passwords lists
    strong_passwords = generate_strong_passwords(STRONG_PASSWORD_LENGTH, STRONG_PASSWORD_AMOUNT)
    weak_passwords = get_passwords_from_dict(WEAK_PASSWORDS_START_LINE,
                                             WEAK_PASSWORDS_END_LINE,
                                             WEAK_PASSWORDS_MIN_LENGTH,
                                             WEAK_PASSWORDS_MAX_LENGTH,
                                             WEAK_PASSWORDS_AMOUNT)
    meduim_passwords = get_passwords_from_dict(MEDIUM_PASSWORDS_START_LINE,
                                             MEDIUM_PASSWORDS_END_LINE,
                                             MEDIUM_PASSWORDS_MIN_LENGTH,
                                             MEDIUM_PASSWORDS_MAX_LENGTH,
                                             MEDIUM_PASSWORDS_AMOUNT)
    # add group seed as a medium passord
    group_seed_password = str(GROUP_SEED)
    if not group_seed_password in meduim_passwords:
        meduim_passwords[0] = group_seed_password
    random.shuffle(meduim_passwords)
    
    # create user list
    users_list = []
    for j, password_list in enumerate((weak_passwords, meduim_passwords, strong_passwords)):
        strength = ['weak', 'meduim', 'strong'][j]
        for i, password in enumerate(password_list, 1):    
            user = {
                "username": f"user_{strength}_{i}",
                "password": password,
                "category": f"{strength}",
                "totp_secret": pyotp.random_base32() if i in range(1,AMOUNT_OF_TOTP_USERS+1) else None 
            }
            users_list.append(user)

    # write users to file
    users_file_data = {
        "group_seed": GROUP_SEED,
        "users": users_list
    }
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_file_data, f, indent=4)
    
    print(f"Successfully created {OUTPUT_FILE} with {len(users_list)} users.")

if __name__ == "__main__":
    main()