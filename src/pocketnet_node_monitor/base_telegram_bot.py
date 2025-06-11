import logging

from abc import ABCMeta, abstractmethod
from .rpc_client import RpcClient, RpcResult


class BaseTelegramBot(metaclass=ABCMeta):
    def __init__(self, token: str, rpc_client: RpcClient):
        self.token = token
        self.rpc_client = rpc_client

    @abstractmethod
    async def run(self):
        """
        Run Telegram bot
        """
        logging.error("Method is not implemented")

    @abstractmethod
    async def stop(self):
        """
        Stops Telegram bot
        """
        logging.error("Method is not implemented")

    async def rpc_call(self, command: str) -> RpcResult:
        return self.rpc_client.call(command)