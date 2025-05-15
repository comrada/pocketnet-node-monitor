import logging

import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

GITHUB_API_URL = "https://api.github.com/repos/pocketnetteam/pocketnet.core/releases/latest"


class GithubClient:

    @staticmethod
    def fetch_latest_github_release():
        try:
            response = requests.get(GITHUB_API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("tag_name")
        except Exception as e:
            logging.error(f"Error fetching GitHub release: {e}")
            return None
