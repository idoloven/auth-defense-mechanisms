from user import User
from database import Database
from flask import Flask, request, jsonify
from auth_manager import AuthManager
from logger import write_log

auth_manager = AuthManager()
db = Database()
app = Flask(__name__)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    category = data.get('category')
    totp_secret = data.get('totp_secret')
    user = User(username, password, category, totp_secret)
    db.register_user(user)


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    #todo validate func signature
    result, message, totp_secret = auth_manager.verify_login(username, password)

    # todo validate signature
    write_log("LOGIN_ATTEMPT", username, "SUCCESS", client_ip, "Login successful")
    
    # validate 
    response_data = {
        "message": "Login successful",
        "totp_required": (totp_secret is not None) 
    }
    # add fail logic, status codes, 429
    return jsonify(response_data), 200
  
@app.route('/login_totp', methods=['POST'])
def login_totp():
    pass

@app.route('/admin/get_captcha_token', methods=['POST'])
def get_captcha_token():
    pass