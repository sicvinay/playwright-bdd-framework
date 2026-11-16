from dotenv import load_dotenv
from pathlib import Path
import os


# Load local environment variables from config/.env
env_path = Path(__file__).parent / ".env"

load_dotenv(dotenv_path=env_path)


# Application configuration
TARGET_ENV = os.getenv("TARGET_ENV", "qa").lower()
if TARGET_ENV not in {"dev", "qa", "staging"}:
    raise ValueError(f"Unsupported TARGET_ENV: {TARGET_ENV}")

# QA uses SauceDemo; other environments must supply a real deployed URL.
BASE_URL = os.getenv("BASE_URL") or ("https://www.saucedemo.com" if TARGET_ENV == "qa" else None)
if not BASE_URL or not BASE_URL.startswith(("http://", "https://")):
    raise ValueError(f"BASE_URL must be configured for environment {TARGET_ENV}")
APP_USERNAME = os.getenv("USERNAME")
APP_PASSWORD = os.getenv("PASSWORD")


# Playwright timeout configuration
DEFAULT_TIMEOUT_MS = 30000
PAGE_LOAD_TIMEOUT_MS = 60000


# Custom polling configuration
CUSTOM_WAIT_TIMEOUT_SECONDS = 30
POLLING_INTERVAL_SECONDS = 1