import logging
import re
from datetime import datetime, timedelta, timezone

import docker

from pocketnet_node_monitor.telegram_client import TelegramClient

TARGET_CONTAINER_NAME = "pocketnet.core"
KEYWORD = "=== Staking"
ERROR_PATTERN_1 = re.compile(r'error.*checkstake\(\)', re.IGNORECASE)
ERROR_PATTERN_2 = re.compile(r'error.*coinstaker', re.IGNORECASE)


class LogWatcher:
    def __init__(self, base_url: str, telegram_client: TelegramClient):
        self.docker_client = docker.DockerClient(base_url=base_url)
        self.telegram_client = telegram_client
        self.last_timestamp = datetime.now(timezone.utc) - timedelta(seconds=60)

    def check_staking_rewards(self):
        try:
            container = self.docker_client.containers.get(TARGET_CONTAINER_NAME)
        except docker.errors.NotFound:
            logging.error(f"Container '{TARGET_CONTAINER_NAME}' not found.")
            return

        try:
            logs = container.logs(since=self.last_timestamp, stream=False).decode(errors="replace")
            lines = logs.splitlines()

            i = 0
            while i < len(lines):
                line = lines[i]
                if KEYWORD in line:
                    next_line = lines[i + 1] if i + 1 < len(lines) else ""
                    if not ERROR_PATTERN_1.search(next_line) and not ERROR_PATTERN_2.search(next_line):
                        logging.info(f"Found valid staking log: {line}")
                        self.telegram_client.send_message("You got an award for stacking!")
                    i += 2
                else:
                    i += 1

        except Exception as e:
            logging.error(f"Error while reading logs: {e}")

        self.last_timestamp = datetime.now(timezone.utc)
