import json
import logging
import socket
import sys
from decimal import Decimal
from functools import lru_cache
from typing import Any
from typing import Dict
from typing import List
from typing import Union

import riprova
from bitcoin.rpc import JSONRPCError, InWarmupError, Proxy

TIMEOUT = 30
RETRY_EXCEPTIONS = (InWarmupError, ConnectionError, socket.timeout)
RpcResult = Union[Dict[str, Any], List[Any], str, int, float, bool, None]


class RpcClient:

    def __init__(self, scheme: str, hostname: str, port: int, user: str, password: str):
        self.scheme = scheme
        self.hostname = hostname
        self.port = port
        self.user = user
        self.password = password

    @staticmethod
    def on_retry(err: Exception, next_try: float) -> None:
        err_type = type(err)
        exception_name = err_type.__module__ + "." + err_type.__name__
        logging.error("Retry after exception %s: %s", exception_name, err)

    @staticmethod
    def error_evaluator(e: Exception) -> bool:
        return isinstance(e, RETRY_EXCEPTIONS)

    @lru_cache(maxsize=1)
    def rpc_client_factory(self):
        host = self.hostname
        host = "{}:{}@{}".format(self.user, self.password, host)
        if self.port:
            host = "{}:{}".format(host, self.port)
        service_url = "{}://{}".format(self.scheme, host)
        return lambda: Proxy(service_url=service_url, timeout=TIMEOUT)

    def rpc_client(self):
        return self.rpc_client_factory()()

    @riprova.retry(
        timeout=TIMEOUT,
        backoff=riprova.ExponentialBackOff(),
        on_retry=on_retry,
        error_evaluator=error_evaluator,
    )
    def call(self, *args) -> RpcResult:
        try:
            result = self.rpc_client().call(*args)
            logging.debug("Result:   %s", result)
            return result
        except riprova.exceptions.RetryError as e:
            logging.error("Refresh failed during retry. Cause: " + str(e))
            return None
        except JSONRPCError as e:
            logging.debug("Pocketcoin RPC error refresh", exc_info=True)
            return None
        except json.decoder.JSONDecodeError as e:
            logging.error("RPC call did not return JSON. Bad credentials? " + str(e))
            sys.exit(1)

    def get_wallet_balance(self) -> Decimal:
        result = self.call("getwalletinfo")
        if result:
            return Decimal(result["balance"])
        else:
            return Decimal(0)
