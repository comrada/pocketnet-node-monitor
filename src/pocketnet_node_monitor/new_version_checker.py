import logging

from pocketnet_node_monitor.github_client import GithubClient
from pocketnet_node_monitor.telegram_client import TelegramClient


class NewVersionChecker:
    def __init__(self, telegram_client: TelegramClient, github_client: GithubClient):
        self.telegram_client = telegram_client
        self.github_client = github_client
        self.last_release_tag = github_client.fetch_latest_github_release()
        logging.info(f"Latest version: `{self.last_release_tag}`")

    def check(self):
        latest_tag = self.github_client.fetch_latest_github_release()

        if latest_tag and latest_tag != self.last_release_tag:
            logging.info(f"New release detected: {latest_tag}")
            self.telegram_client.send_message(f"🚀 *New Pocketnet Release!*\nLatest version: `{latest_tag}`")
            self.last_release_tag = latest_tag
        else:
            logging.debug("No new release.")
