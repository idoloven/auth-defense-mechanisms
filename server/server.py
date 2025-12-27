import io
import uuid
import structlog
from user import User
from config import Config
from database import Database
from flask import Flask, request, jsonify
from auth import AuthManager

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
    hashed_password, salt = auth_manager.hash(password)
    user = User(username, hashed_password, salt, category, totp_secret)
    db.register_user(user)


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    #todo validate func signature
    result, message, totp_secret = auth_manager.verify_login(username, password)

    # todo validate signature
    logger.info("", username=username, result="")
    
    # validate 
    response_data = {
        "message": "Login successful",
        "totp_required": (totp_secret is not None) 
    }
    # add fail logic, status codes, 429
    return jsonify(response_data), 200
  
@app.route('/login_totp', methods=['POST'])
def login_totp():
    data = request.json
    username = data.get('username')
    totp_token = data.get('totp_token')
    totp_result = auth_manager.auth_totp(db, username, totp_token)
    return # todo what to return

@app.route('/admin/get_captcha_token', methods=['GET'])
def get_captcha_token(provided_seed):
    if provided_seed != Config.GROUP_SEED:
            return #todo what to return
    auth_manager.captcha_token = uuid.uuid4()
    return # what to return auth_manager.captach_token


def configure_logger(log_file):
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.WriteLoggerFactory(file=log_file),
        cache_logger_on_first_use=True,
    )

    
if __name__ == "__main__":
    # logger config
    log_file = open(Config.LOG_FILE_NAME, "a", encoding="utf-8", buffering=Config.LOG_BUFFER_SIZE)
    configure_logger(log_file)
    logger = structlog.get_logger().bind(
    group_seed=Config.GROUP_SEED,
    hash_mode=Config.PASSWORD_HASH_MODE,
    protection_flags=Config.PROTECTION_FLAGS
    )

    try:
        app.run()
        
    except KeyboardInterrupt:
        print("\nStopping server")
        
    finally:
        print("Flushing buffer to disk")
        log_file.flush()
        log_file.close()
        print("logs saved to disk. exiting")