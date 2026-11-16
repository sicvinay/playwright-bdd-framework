from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import urlparse
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
if not BASE_URL:
    raise ValueError(f"BASE_URL must be configured for environment {TARGET_ENV}")
parsed_url = urlparse(BASE_URL)
if parsed_url.scheme not in {"http", "https"} or not parsed_url.hostname or parsed_url.username or parsed_url.password:
    raise ValueError(f"BASE_URL must be a valid HTTP(S) URL without embedded credentials for {TARGET_ENV}")
APP_USERNAME = os.getenv("APP_USERNAME") or os.getenv("USERNAME")
APP_PASSWORD = os.getenv("APP_PASSWORD") or os.getenv("PASSWORD")


# Supported Playwright browser engines
BROWSER = os.getenv("BROWSER", "chromium").strip().lower()
if BROWSER not in {"chromium", "firefox", "webkit"}:
    raise ValueError(f"Unsupported BROWSER: {BROWSER}. Use chromium, firefox, or webkit.")


# Playwright timeout configuration
DEFAULT_TIMEOUT_MS = 30000
PAGE_LOAD_TIMEOUT_MS = 60000


# Custom polling configuration
CUSTOM_WAIT_TIMEOUT_SECONDS = 30
POLLING_INTERVAL_SECONDS = 1