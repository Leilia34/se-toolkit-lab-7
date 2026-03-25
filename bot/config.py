# bot/config.py
import os
from pathlib import Path

def load_env():
    env_file = Path(__file__).parent.parent / ".env.bot.secret"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, val = line.split('=', 1)
                    os.environ.setdefault(key, val)

load_env()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    LMS_API_BASE_URL = os.getenv("LMS_API_BASE_URL")
    LMS_API_KEY = os.getenv("LMS_API_KEY")
    LLM_API_MODEL = os.getenv("LLM_API_MODEL")
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_API_BASE_URL = os.getenv("LLM_API_BASE_URL")
