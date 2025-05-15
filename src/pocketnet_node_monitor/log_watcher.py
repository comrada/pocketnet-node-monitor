import logging
from datetime import datetime, timedelta, timezone

import docker

from pocketnet_node_monitor.telegram_client import TelegramClient

TARGET_CONTAINER_NAME = "pocketnet.core"
KEYWORD = "=== Staking"


class LogWatcher:
    def __init__(self, base_url: str, telegram_client: TelegramClient):
        self.docker_client = docker.DockerClient(base_url=base_url)
        self.telegram_client = telegram_client
        self.last_timestamp = datetime.now(timezone.utc) - timedelta(seconds=60)

    def check_staking(self):
        try:
            container = self.docker_client.containers.get(TARGET_CONTAINER_NAME)
        except docker.errors.NotFound:
            logging.error(f"Container '{TARGET_CONTAINER_NAME}' not found.")
            return

        try:
            logs = container.logs(since=self.last_timestamp, stream=False).decode(errors="replace")
            lines = logs.splitlines()

            for line in lines:
                if KEYWORD in line:
                    logging.info(f"Found staking log: {line}")
                    self.telegram_client.send_message(f"*Staking alert!*\n```\n{line}\n```")

        except Exception as e:
            logging.error(f"Error while reading logs: {e}")

        self.last_timestamp = datetime.now(timezone.utc)
