import uuid
import logging
import structlog
from user import User
from config import Config
from database import Database
from flask import Flask, request, jsonify
from auth import AuthManager

flask_loggger = logging.getLogger('werkzeug')
flask_loggger.setLevel(logging.ERROR)

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
    user = User(username, hashed_password, category, totp_secret, salt)
    db.register_user(user)
    return jsonify({}), 200


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    captcha_token = data.get('captcha_token')

    result = auth_manager.auth(db, username, password, captcha_token)
    
    logger.info("", 
                username=username,
                result=result["status"], 
                latency_ms = result["metrics"]["latency_ms"],
                cpu_ms = result["metrics"]["cpu_ms"],
                peak_memory = result["metrics"]["memory_peak_mb"])
    
    response_data = {"status": result["status"]}
    if "data" in result:
        response_data["retry_after"] = result["data"]["retry_after"]
    status_code = 200 if result["status"] == "success" else 401
    return jsonify(response_data), status_code
  
@app.route('/login_totp', methods=['POST'])
def login_totp():
    data = request.json
    username = data.get('username')
    totp_token = data.get('totp_token')
    totp_result = auth_manager.auth_totp(db, username, totp_token)
    
    response_data = {"status": totp_result["status"]}
    status_code = 200 if totp_result["status"] == "totp_success" else 401
    return jsonify(response_data), status_code

@app.route('/admin/get_captcha_token', methods=['GET'])
def get_captcha_token():
    provided_seed = request.args.get('group_seed')
    if str(provided_seed) != str(Config.GROUP_SEED):
        return jsonify({"status":"captcha_bad_group_seed"}), 401
    auth_manager.captcha_token = uuid.uuid4()
    return jsonify({"status":"success", "captcha_token": auth_manager.captcha_token}), 200


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