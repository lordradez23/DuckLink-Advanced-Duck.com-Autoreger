import os
from dotenv import load_dotenv
from loguru import logger

if not os.path.exists(".env"):
    logger.warning("No .env file found! Trying to read from system environment variables.")
else:
    load_dotenv()

def get_env_or_warn(var_name, required=True, default=None):
    value = os.environ.get(var_name, default)
    if value is None and required:
        logger.error(f"❌ '{var_name}' not found in .env file!")
        logger.info(f"💡 Please add '{var_name}=your_value_here' to your .env file in the project root.")
        if required:
            raise EnvironmentError(f"Missing required environment variable: {var_name}")
    return value

# Required Keys
OPENROUTER_API_KEY = get_env_or_warn("OPENROUTER_API_KEY")

# Optional / Default Keys
SLOWED_MODE = os.environ.get("SLOWED_MODE", "False").lower() in ("true", "1", "yes")

# Feature 2: Proxy rotation delay env
PROXY_ROTATION_DELAY = int(os.environ.get("PROXY_ROTATION_DELAY", 2))

# Feature 3: Captcha solver configurable wait
CAPTCHA_WAIT_TIME = int(os.environ.get('CAPTCHA_WAIT_TIME', 15))

# Feature 4: Logging Level in Env
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()

# Feature 5: Output file path variable
OUTPUT_CSV_PATH = os.environ.get('OUTPUT_CSV_PATH', 'accounts.csv')

# Feature 6: Load checkpoint file variable
CHECKPOINT_PATH = os.environ.get('CHECKPOINT_PATH', 'data/checkpoint.json')

# Feature 7: Auto-retry limits config
MAX_OTP_ATTEMPTS = int(os.environ.get('MAX_OTP_ATTEMPTS', 20))

# Feature 8: Afk Seconds Range config
AFK_MIN = int(os.environ.get('AFK_MIN', 1))
AFK_MAX = int(os.environ.get('AFK_MAX', 4))

# Feature 9: Pixel tracking toggle
ENABLE_PIXELS = os.environ.get('ENABLE_PIXELS', 'True').lower() in ('true', '1')

if SLOWED_MODE:
    logger.info("🐢 SLOWED_MODE is ENABLED. Registration will mimic human delays.")
