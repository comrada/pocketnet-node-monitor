import logging
import os

from apscheduler.schedulers.blocking import BlockingScheduler

from pocketnet_node_monitor.balance_checker import BalanceChecker
from pocketnet_node_monitor.github_client import GithubClient
from pocketnet_node_monitor.log_watcher import LogWatcher
from pocketnet_node_monitor.new_version_checker import NewVersionChecker
from pocketnet_node_monitor.rpc_client import RpcClient
from pocketnet_node_monitor.telegram_client import TelegramClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

RPC_HOST = os.environ.get("RPC_HOST")
RPC_PORT = int(os.getenv("RPC_PORT", 8899))
RPC_SCHEME = os.environ.get("RPC_SCHEME", "http")
RPC_USER = os.environ.get("RPC_USER")
RPC_PASSWORD = os.environ.get("RPC_PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", 0))
INTERVAL_STACKING_SEC = int(os.getenv("INTERVAL_STACKING_SEC", 120))
INTERVAL_BALANCE_SEC = int(os.getenv("INTERVAL_BALANCE_SEC", 300))
DOCKER_BASE_URL = os.getenv("DOCKER_BASE_URL", "unix://var/run/docker.sock")

telegram_client = TelegramClient(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
new_version_checker = NewVersionChecker(telegram_client, GithubClient())
rpc_client = RpcClient(RPC_SCHEME, RPC_HOST, RPC_PORT, RPC_USER, RPC_PASSWORD)
balance_checker = BalanceChecker(rpc_client, telegram_client)
log_watcher = LogWatcher(DOCKER_BASE_URL, telegram_client)


def check_github_release():
    new_version_checker.check()


def get_balance():
    balance_checker.check()


def check_staking():
    log_watcher.check_staking()


def start():
    scheduler = BlockingScheduler()
    scheduler.add_job(get_balance, 'interval', seconds=INTERVAL_STACKING_SEC)
    scheduler.add_job(check_staking, 'interval', seconds=INTERVAL_BALANCE_SEC)
    scheduler.add_job(check_github_release, 'cron', hour=0, minute=0)
    scheduler.start()
