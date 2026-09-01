from dotenv import load_dotenv
from pathlib import Path
import os


# Load local environment variables from config/.env
env_path = Path(__file__).parent / ".env"

load_dotenv(dotenv_path=env_path)


# Application configuration
BASE_URL = os.getenv("BASE_URL")
APP_USERNAME = os.getenv("USERNAME")
APP_PASSWORD = os.getenv("PASSWORD")


# Playwright timeout configuration
DEFAULT_TIMEOUT_MS = 30000
PAGE_LOAD_TIMEOUT_MS = 60000


# Custom polling configuration
CUSTOM_WAIT_TIMEOUT_SECONDS = 30
POLLING_INTERVAL_SECONDS = 1