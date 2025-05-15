import logging

import requests


class TelegramClient:
    def __init__(self, token: str, chat_id: int):
        self.token = token
        self.chat_id = chat_id
        if not self.token or not self.token:
            logging.error("Telegram credentials not set")

    def send_message(self, message: str):
        if not self.token or not self.token:
            logging.warning("Telegram credentials not set. Skipping notification.")
            return

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        response = requests.post(url, json=payload)
        if response.status_code != 200:
            logging.error(f"Telegram error: {response.status_code} - {response.text}")
