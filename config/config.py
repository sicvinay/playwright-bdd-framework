from dotenv import load_dotenv
from pathlib import Path
import os


# ==========================================
# Environment Configuration
# ==========================================

env_path = Path(__file__).parent / ".env"

load_dotenv(
    dotenv_path=env_path
)


BASE_URL = os.getenv(
    "BASE_URL"
)

APP_USERNAME = os.getenv(
    "USERNAME"
)

APP_PASSWORD = os.getenv(
    "PASSWORD"
)


# ==========================================
# Framework Timeout Configuration
# ==========================================

DEFAULT_TIMEOUT_MS = 30000

PAGE_LOAD_TIMEOUT_MS = 60000

CUSTOM_WAIT_TIMEOUT_SECONDS = 30

POLLING_INTERVAL_SECONDS = 0.5