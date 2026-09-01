from dotenv import load_dotenv
from pathlib import Path
import os


env_path = Path(__file__).parent / ".env"

load_dotenv(dotenv_path=env_path)


BASE_URL = os.getenv("BASE_URL")
APP_USERNAME = os.getenv("USERNAME")
APP_PASSWORD = os.getenv("PASSWORD")