class User():
    def __init__(self,
                 username,
                 password,
                 category,
                 totp_secret=None,
                 salt=None,
                 failed_attempts=0,
                 is_locked=False,
                 rl_window_start=0,
                 rl_window_attempts=0,
                 captcha_attempts=0) -> None:
        self.username = username
        self.password = password
        self.category = category
        self.totp_secret = totp_secret
        self.salt = salt
        self.failed_attempts = failed_attempts
        self.is_locked = is_locked
        self.rl_window_start = rl_window_start
        self.rl_window_attempts = rl_window_attempts
        self.captcha_attempts = captcha_attempts
