# ai_handler.py
"""Simple optional OpenAI integration using aiohttp and usage tracking.

Features:
- check daily usage per user
- record usage
- call OpenAI Chat Completions (gpt-3.5-turbo by default)
- graceful fallback when OPENAI_API_KEY is missing
"""
import os
import aiohttp
import asyncio
from datetime import datetime, date
from typing import Optional, Dict, Any
from config import OPENAI_API_KEY
from database import db

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
DAILY_TOKEN_LIMIT = int(os.environ.get('OPENAI_DAILY_LIMIT', '4000'))


async def _call_openai(prompt: str, system: Optional[str] = None, max_tokens: int = 512) -> Dict[str, Any]:
    if not OPENAI_API_KEY:
        raise RuntimeError('OpenAI API key is not configured')

    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        'model': MODEL,
        'messages': messages,
        'max_tokens': max_tokens,
        'temperature': 0.2
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(OPENAI_API_URL, json=payload, headers=headers, timeout=60) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise RuntimeError(f'OpenAI API error {resp.status}: {text}')
            return await resp.json()


def _today_iso() -> str:
    return date.today().isoformat()


def get_user_daily_usage(user_id: int) -> int:
    """Return total tokens used today by user."""
    usage = db._read_data('ai_usage') or {}
    if not isinstance(usage, dict):
        usage = {}
    today = _today_iso()
    user_key = str(user_id)
    user_record = usage.get(user_key, {})
    return int(user_record.get('daily_tokens', {}).get(today, 0))


def record_user_usage(user_id: int, prompt_tokens: int, completion_tokens: int):
    """Record tokens used by user for today."""
    usage = db._read_data('ai_usage') or {}
    if not isinstance(usage, dict):
        usage = {}
    today = _today_iso()
    user_key = str(user_id)
    user_record = usage.get(user_key, {'daily_tokens': {}})
    daily = user_record.get('daily_tokens', {})
    daily[today] = daily.get(today, 0) + int(prompt_tokens) + int(completion_tokens)
    user_record['daily_tokens'] = daily
    user_record['last_used'] = datetime.now().isoformat()
    usage[user_key] = user_record
    db._write_data('ai_usage', usage)


async def summarize_text(user_id: int, text: str) -> str:
    """Summarize text using OpenAI while checking daily quota."""
    if not OPENAI_API_KEY:
        return "⚠️ ميزة الذكاء الاصطناعي غير مفعّلة. يرجى ضبط `OPENAI_API_KEY`."

    current = get_user_daily_usage(user_id)
    if current >= DAILY_TOKEN_LIMIT:
        return "⚠️ تم تجاوز الحدّ اليومي لاستهلاك الذكاء الاصطناعي. حاول لاحقًا."

    system = "أنت مساعد تعليمي متخصص بتلخيص المحتوى الدراسي باختصار وبأسلوب بسيط للطلاب."
    try:
        resp = await _call_openai(prompt=text, system=system, max_tokens=400)
        # محاولة استخراج النص
        choices = resp.get('choices') or []
        if not choices:
            raise RuntimeError('No choices from OpenAI')
        message = choices[0].get('message', {}).get('content', '')

        # تسجيل استهلاك إن كان متاحًا (بعض API لا يعيد الحسابات بشكل كامل)
        usage_info = resp.get('usage', {})
        prompt_tokens = usage_info.get('prompt_tokens', 0)
        completion_tokens = usage_info.get('completion_tokens', 0)
        record_user_usage(user_id, prompt_tokens, completion_tokens)

        return message.strip()
    except Exception as e:
        return f"❌ خطأ في طلب الذكاء الاصطناعي: {e}"


async def explain_question(user_id: int, question: str) -> str:
    if not OPENAI_API_KEY:
        return "⚠️ ميزة الذكاء الاصطناعي غير مفعّلة."
    prompt = f"اشرح السؤال التالي للطالب بطريقة مبسطة ومختصرة:\n{question}"
    return await summarize_text(user_id, prompt)
