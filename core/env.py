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

if SLOWED_MODE:
    logger.info("🐢 SLOWED_MODE is ENABLED. Registration will mimic human delays.")
