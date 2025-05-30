import json
import logging
from decimal import Decimal

from pocketnet_node_monitor.rpc_client import RpcClient
from pocketnet_node_monitor.telegram_client import TelegramClient


class StackingChecker:
    def __init__(self, rpc_client: RpcClient, telegram_client: TelegramClient):
        self.rpc_client = rpc_client
        self.telegram_client = telegram_client

    @staticmethod
    def custom_serializer(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f"Type {type(obj)} not serializable")

    def check(self):
        stacking_info = self.rpc_client.get_stacking_info()
        print(stacking_info)
        error_message = None
        if not stacking_info["enabled"]:
            error_message = "Wallet is disabled!"
        if not stacking_info["staking"]:
            error_message = "Stacking is disabled!"
        if error_message:
            logging.error(error_message)
            self.telegram_client.send_message(
                f"{error_message}\n```json\n{json.dumps(stacking_info, indent=2, default=self.custom_serializer)}\n```")
