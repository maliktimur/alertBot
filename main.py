from flask import Flask, request
from google.cloud import tasks_v2
import requests
import os
import json
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# --- ENV ---
PROJECT = os.environ.get("GCP_PROJECT")
QUEUE = "telegram-alert-queue"
LOCATION = "europe-central2"
TASK_HANDLER_URL = os.environ.get("TASK_HANDLER_URL")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


# =========================
# WEBHOOK (быстрый)
# =========================
@app.route("/", methods=["POST"])
def alert():
    data = request.get_json(silent=True) or {}

    client = tasks_v2.CloudTasksClient()
    parent = client.queue_path(PROJECT, LOCATION, QUEUE)

    payload = json.dumps(data).encode()

    task = {
        "http_request": {
            "http_method": tasks_v2.HttpMethod.POST,
            "url": TASK_HANDLER_URL,
            "headers": {"Content-Type": "application/json"},
            "body": payload,
        }
    }

    client.create_task(parent=parent, task=task)

    return "ok", 200


# =========================
# WORKER (обработка)
# =========================
@app.route("/task", methods=["POST"])
def handle_task():
    data = request.get_json(silent=True) or {}

    policy = data.get("incident", {}).get("policy_name", "Unknown policy")
    state = data.get("incident", {}).get("state", "UNKNOWN")
    url = data.get("incident", {}).get("url", "")

    message = f"🚨 Cloud Monitoring Alert\n\nPolicy: {policy}\nState: {state}\nURL: {url}"

    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": message},
            timeout=5
        )
    except Exception as e:
        logging.error(f"Telegram error: {e}")
        raise e  # важно для retry

    return "ok", 200


# =========================
# HEALTH CHECK
# =========================
@app.route("/", methods=["GET"])
def health():
    return "ok", 200