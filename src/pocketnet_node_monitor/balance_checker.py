import logging
from decimal import Decimal

from pocketnet_node_monitor.rpc_client import RpcClient
from pocketnet_node_monitor.telegram_client import TelegramClient


class BalanceChecker:
    def __init__(self, rpc_client: RpcClient, telegram_client: TelegramClient):
        self.rpc_client = rpc_client
        self.telegram_client = telegram_client
        self.wallet_balance = self.get_balance()
        logging.info(f"Current balance: `{self.wallet_balance}`")

    def check(self):
        new_balance = self.get_balance()
        if new_balance != self.wallet_balance:
            difference = new_balance - self.wallet_balance
            wallet_balance = new_balance
            message = f"Balance has been updated, new value: `{wallet_balance}`, change: `{difference}`"
            logging.info(message)
            self.telegram_client.send_message(message)

    def get_balance(self) -> Decimal:
        result = self.rpc_client.get_wallet_info()
        if result:
            return Decimal(result["balance"])
        else:
            return Decimal(0)
