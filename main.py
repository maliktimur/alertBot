from flask import Flask, request
import requests
import os
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)
app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

@app.route("/", methods=["POST"])
def alert():
    data = request.json

    # Формируем текст для Telegram
    policy = data.get("incident", {}).get("policy_name", "Unknown policy")
    state = data.get("incident", {}).get("state", "UNKNOWN")
    url = data.get("incident", {}).get("url", "")
    
    message = f"🚨 Cloud Monitoring Alert\nPolicy: {policy}\nState: {state}\nURL: {url}"

    # Отправляем в Telegram
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": message}
    )
    return "ok"

# --- Health check ---
@app.route("/", methods=["GET"])
def health():
    return "Bot is running"