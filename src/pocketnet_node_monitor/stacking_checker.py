import json
import logging
import re
from decimal import Decimal

from pocketnet_node_monitor.rpc_client import RpcClient
from pocketnet_node_monitor.telegram_client import TelegramClient

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class StackingChecker:
    def __init__(self, rpc_client: RpcClient, telegram_client: TelegramClient):
        self.rpc_client = rpc_client
        self.telegram_client = telegram_client
        self._cached_rewards = self._get_current_rewards()

    @staticmethod
    def custom_serializer(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f"Type {type(obj)} not serializable")

    def check_status(self):
        stacking_info = self.rpc_client.get_stacking_info()
        error_message = None
        if not stacking_info["enabled"]:
            error_message = "Wallet is disabled!"
        if not stacking_info["staking"]:
            error_message = "Stacking is disabled!"
        if error_message:
            logging.error(error_message)
            self.telegram_client.send_message(
                f"{error_message}\n```json\n{json.dumps(stacking_info, indent=2, default=self.custom_serializer)}\n```")

    def _get_current_rewards(self) -> dict[str, Decimal]:
        """
        Gets the current awards, filtered by date only.
        Returns the dictionary {date: Decimal sum}, excluding aggregates and meta-fields.
        """
        raw = self.rpc_client.get_stake_report()
        result = {}
        for key, value in raw.items():
            if not DATE_PATTERN.match(key):
                continue
            try:
                amount = Decimal(value)
                if amount > 0:
                    result[key] = amount
            except Exception as e:
                logging.warning(f"⚠️ pair '{key}={value}' skipped: {e}")
        return result

    def check_new_rewards(self) -> list[str]:
        """
        Checks for new dates with non-zero rewards.
        Returns a list of new dates (strings).
        """
        new_rewards = self._get_current_rewards()
        new_dates = [date for date in new_rewards if date not in self._cached_rewards]

        if new_dates:
            report_lines = [
                f"{date}: {new_rewards[date]}" for date in sorted(new_dates)
            ]
            message = "🎉 You got a reward for stacking!:\n```text\n" + "\n".join(report_lines) + "\n```"
            logging.info(f"🎉 Found new rewards {', '.join(report_lines)}")
            self.telegram_client.send_message(message)

        self._cached_rewards = new_rewards
        return sorted(new_dates)
