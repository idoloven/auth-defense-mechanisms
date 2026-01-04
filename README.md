# Authentication Defense Mechanisms Research

**Course:** Introduction to Cyber Security (20940)
**Group Seed:** `214265977`

---

## Ethical Disclaimer
**This software is developed for educational and research purposes only.**
The attacks implemented in this project are performed solely on a local, isolated environment owned by the student. No external networks or real user accounts were targeted. The author bear no responsibility for any misuse of this code.

---

## Overview
This project performs a comparative analysis of password-based authentication mechanisms. It simulates a vulnerable server and an automated attacker to measure the trade-offs between security and performance using various Hashing Algorithms (SHA-256, bcrypt, Argon2) and Defense Strategies (Rate Limiting, CAPTCHA, TOTP, LOCKOUT & PEPPER).

---

## Project Structure

```text
├── assets/
│   ├── rockyou_top_50k.txt   # Short Dictionary for attacks
│   └── users.json            # User definitions (Weak/Medium/Strong)
├── client/
|   ├── register_users.py     # Script for registering users to the server
│   └── attacker.py           # The attack script (Brute Force / Password Spraying)
├── server/
│   ├── server.py             # Flask server implementation
│   ├── auth.py               # Authentication logic (Hashing, Defenses)
│   ├── database.py           # SQLite management
|   ├── user.py               # User model
│   └── config.py             # Server configuration (Toggles, Constants)
├── scripts/
|   ├── shorten_dict.py       # Creates a shortened dictionary from a large one.
|   ├── create_users.py       # Creates users.json file from dictionary
│   └── time_series.py        # Graph generation
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## Installation 
1. Clone the repository or extract the project files.
2. Install Dependencies: Ensure you have Python 3.10+ installed.
pip install -r requirements.txt

---

## Configuration
1. Choose hash mode
2. Toggle Defenses - use bitwise flags to enable specific protections

--

## How To Run An Experiment
1. Configure the server and start it. The server listens on 127.0.0.1:5000
2. Initialize DB - run python client/register_users.py
You must run this script every time you change the PASSWORD_HASH_MODE in config.py to re-hash the user passwords correctly.
3. Run the attack
4. Analyze Results

---

## Users Selection Strategy
For each experiment, three user types are targeted:

Weak User: Password exists early in the dictionary. -> Goal: Measure Time-to-Crack.
Medium User: Password exists deep in the dictionary. -> Goal: Measure Sustained Throughput.
Strong User: Password NOT in dictionary. -> Goal: Run until threshold (50k attempts) and perform Extrapolation

---

## Author - Ido Loven
Introduction to Cyber Security, Open University of Israel.
