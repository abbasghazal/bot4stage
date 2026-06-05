# config.py
from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio
import os
from typing import Tuple, Optional
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

def _get_int_env(name, default=0):
    value = os.environ.get(name, str(default)).strip()
    return int(value) if value else default

# Load credentials and settings from environment variables only.
API_ID = _get_int_env('API_ID')
API_HASH = os.environ.get('API_HASH', '').strip()
BOT_TOKEN = os.environ.get('BOT_TOKEN', '').strip()

# Developer/admin settings
DEVELOPER_ID = _get_int_env('DEVELOPER_ID', 6848908141)
ADMINS = [int(x) for x in os.environ.get('ADMINS', str(DEVELOPER_ID)).split(',') if x.strip()] if os.environ.get('ADMINS') else ([DEVELOPER_ID] if DEVELOPER_ID else [])

# Optional user session (for search features)
SESSION1 = os.environ.get('SESSION1', '').strip()

# OpenAI (optional)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
WEBAPP_URL = os.environ.get('WEBAPP_URL', os.environ.get('RENDER_EXTERNAL_URL', '')).strip().rstrip('/')

def is_valid_webapp_url(url):
    parsed = urlparse(url or '')
    return parsed.scheme == 'https' and bool(parsed.netloc)

WEBAPP_URL_VALID = is_valid_webapp_url(WEBAPP_URL)

# تحديد مسار حفظ البيانات (لـ Render)
ON_RENDER = os.environ.get('RENDER', '').lower() in ('1', 'true', 'yes')
if ON_RENDER:
    DATA_PATH = '/opt/render/data'  # مسار الـ Persistent Disk
    # التأكد من وجود المجلد
    os.makedirs(DATA_PATH, exist_ok=True)
else:
    DATA_PATH = '.'  # المجلد المحلي

UPLOADS_PATH = os.environ.get('UPLOADS_PATH', '').strip() or os.path.join(DATA_PATH, 'uploads')
os.makedirs(UPLOADS_PATH, exist_ok=True)

# Database file paths (file-based JSON storage)
DB_FILES = {
    'users': os.path.join(DATA_PATH, 'users.json'),
    'users_stages': os.path.join(DATA_PATH, 'users_stages.json'),
    'subjects': os.path.join(DATA_PATH, 'subjects.json'),
    'admins': os.path.join(DATA_PATH, 'admins.json'),
    'required_channels': os.path.join(DATA_PATH, 'required_channels.json'),
    'comments': os.path.join(DATA_PATH, 'comments.json'),
    'comments_meta': os.path.join(DATA_PATH, 'comments_meta.json'),
    'search_channels': os.path.join(DATA_PATH, 'search_channels.json'),
    'support_tickets': os.path.join(DATA_PATH, 'support_tickets.json'),
    'ai_usage': os.path.join(DATA_PATH, 'ai_usage.json'),
    'settings': os.path.join(DATA_PATH, 'settings.json'),
    'stage_content': os.path.join(DATA_PATH, 'stage_content.json'),
    'physics_channel': os.path.join(DATA_PATH, 'physics_channel.json'),
    'physics_requests': os.path.join(DATA_PATH, 'physics_requests.json')
}

def _get_event_loop() -> asyncio.AbstractEventLoop:
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

def create_clients() -> Tuple[TelegramClient, Optional[TelegramClient], asyncio.AbstractEventLoop]:
    """Create and start Telethon clients (bot and optional user client).

    Returns (bot_client, user_client_or_None, loop)
    """
    loop = _get_event_loop()

    if not API_ID or not API_HASH:
        raise RuntimeError('API_ID and API_HASH must be set in environment')

    bot_client = TelegramClient('bot_session', API_ID, API_HASH, loop=loop)
    # We don't call start() synchronously here; the caller should await .start() in async context

    user_client = None
    if SESSION1:
        try:
            user_client = TelegramClient(StringSession(SESSION1), API_ID, API_HASH, loop=loop)
        except Exception:
            user_client = None

    return bot_client, user_client, loop

# Create clients (do not auto-start here to avoid blocking imports)
bot_client, user_client, loop = create_clients()

# Convenience alias used across the project
BOT_CLIENT = bot_client
USER_CLIENT = user_client
# Backwards-compatible names expected by the codebase
client = bot_client
