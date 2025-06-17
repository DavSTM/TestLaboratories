import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    r = requests.post(url, json=payload)
    return r.status_code

def extract_user_id(person):
    user_field = person.get("fields", {}).get("User")

    if isinstance(user_field, list) and user_field:
        return user_field[0].get("id")
    elif isinstance(user_field, dict):
        return user_field.get("id")
    return None
