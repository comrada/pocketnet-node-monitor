import logging
import os
import signal
from asyncio import (
    Event,
    get_running_loop,
    create_task
)

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from pocketnet_node_monitor.balance_checker import BalanceChecker
from pocketnet_node_monitor.base_telegram_bot import BaseTelegramBot
from pocketnet_node_monitor.github_client import GithubClient
from pocketnet_node_monitor.new_version_checker import NewVersionChecker
from pocketnet_node_monitor.python_telegram_bot import PythonTelegramBot
from pocketnet_node_monitor.rpc_client import RpcClient
from pocketnet_node_monitor.stacking_checker import StackingChecker
from pocketnet_node_monitor.telegram_client import TelegramClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

RPC_HOST = os.getenv("RPC_HOST", "localhost")
RPC_PORT = int(os.getenv("RPC_PORT", 8899))
RPC_SCHEME = os.getenv("RPC_SCHEME", "http")
RPC_USER = os.getenv("RPC_USER", "user")
RPC_PASSWORD = os.getenv("RPC_PASSWORD", "pass")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", 0))
TELEGRAM_BOT_IMPL = os.getenv("TELEGRAM_BOT_IMPL", "python-telegram-bot")
INTERVAL_STACKING_REWARDS_SEC = int(os.getenv("INTERVAL_STACKING_REWARDS_SEC", 120))
INTERVAL_STACKING_MIN = int(os.getenv("INTERVAL_STACKING_MIN", 60))
INTERVAL_BALANCE_SEC = int(os.getenv("INTERVAL_BALANCE_SEC", 300))

telegram_client = TelegramClient(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
new_version_checker = NewVersionChecker(telegram_client, GithubClient())
rpc_client = RpcClient(RPC_SCHEME, RPC_HOST, RPC_PORT, RPC_USER, RPC_PASSWORD)
balance_checker = BalanceChecker(rpc_client, telegram_client)
stacking_checker = StackingChecker(rpc_client, telegram_client)


async def check_github_release():
    new_version_checker.check()


async def get_balance():
    balance_checker.check()


async def check_staking_rewards():
    stacking_checker.check_new_rewards()


async def check_stacking():
    stacking_checker.check_status()


async def start():
    scheduler = AsyncIOScheduler()

    scheduler.add_job(get_balance, 'interval', seconds=INTERVAL_BALANCE_SEC)
    scheduler.add_job(check_staking_rewards, 'interval', seconds=INTERVAL_STACKING_REWARDS_SEC)
    scheduler.add_job(check_stacking, 'interval', minutes=INTERVAL_STACKING_MIN)
    scheduler.add_job(check_github_release, 'cron', hour=0, minute=0)
    scheduler.start()
    telegram_bot = create_telegram_bot()
    await telegram_bot.run()
    await reg_shutdown_signal(telegram_bot, scheduler)


def create_telegram_bot() -> BaseTelegramBot:
    if TELEGRAM_BOT_IMPL == "python-telegram-bot":
        return PythonTelegramBot(TELEGRAM_TOKEN, rpc_client)
    raise NotImplementedError(f"Unknown Implementation: '{TELEGRAM_BOT_IMPL}'")


async def reg_shutdown_signal(bot: BaseTelegramBot, scheduler: AsyncIOScheduler):
    loop = get_running_loop()
    stop_event = Event()
    for sig_name in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(
            getattr(signal, sig_name),
            lambda: create_task(shutdown(stop_event, bot, scheduler))
        )
    await stop_event.wait()


async def shutdown(stop_event: Event, bot: BaseTelegramBot, scheduler: AsyncIOScheduler):
    logging.info("Shutting down...")
    await bot.stop()
    scheduler.shutdown()
    stop_event.set()
