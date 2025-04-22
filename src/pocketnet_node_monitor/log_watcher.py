import time
import docker
import logging
import requests
import os
from datetime import datetime, timedelta, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

TARGET_CONTAINER_NAME = "pocketnet.core"
KEYWORD = "=== Staking"
CHECK_INTERVAL_SECONDS = 60

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logging.warning("Telegram credentials not set. Skipping notification.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    response = requests.post(url, json=payload)
    if response.status_code != 200:
        logging.error(f"Telegram error: {response.status_code} - {response.text}")

def main():
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')

    try:
        container = client.containers.get(TARGET_CONTAINER_NAME)
    except docker.errors.NotFound:
        logging.error(f"Container '{TARGET_CONTAINER_NAME}' not found.")
        return

    last_timestamp = datetime.now(timezone.utc) - timedelta(seconds=60)

    while True:
        try:
            logs = container.logs(since=last_timestamp, stream=False).decode(errors="replace")
            lines = logs.splitlines()

            for line in lines:
                if KEYWORD in line:
                    logging.info(f"Found staking log: {line}")
                    send_telegram_message(f"*Staking alert!*\n```\n{line}\n```")

            last_timestamp = datetime.now(timezone.utc)
        except Exception as e:
            logging.error(f"Error while reading logs: {e}")

        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
