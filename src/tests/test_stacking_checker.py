from unittest.mock import call
from unittest.mock import patch, MagicMock

import pytest

from pocketnet_node_monitor.stacking_checker import StackingChecker


@pytest.fixture
def mock_telegram_client():
    return MagicMock()


@patch("pocketnet_node_monitor.stacking_checker.RpcClient")
def test_check_staking_enabled(mock_rpc_client_class, mock_telegram_client):
    mock_rpc_client_class.get_stacking_info.return_value = {
        "enabled": True,
        "staking": True,
        "errors": "",
        "expectedtime": 12345
    }

    checker = StackingChecker(mock_rpc_client_class, mock_telegram_client)
    checker.check_status()

    mock_telegram_client.send_message.assert_not_called()


@patch("pocketnet_node_monitor.stacking_checker.RpcClient")
def test_check_staking_disabled(mock_rpc_client_class, mock_telegram_client):
    mock_rpc_client_class.get_stacking_info.return_value = {
        "enabled": True,
        "staking": False,
        "errors": "",
        "expectedtime": 12345
    }

    checker = StackingChecker(mock_rpc_client_class, mock_telegram_client)
    checker.check_status()

    mock_telegram_client.send_message.assert_called_once()
    message = mock_telegram_client.send_message.call_args[0][0]
    assert "Stacking is disabled!" in message


@patch("pocketnet_node_monitor.stacking_checker.RpcClient")
def test_check_staking_rewards(mock_rpc_client_class, mock_telegram_client):
    mock_rpc_client_class.get_stake_report.return_value = {
        "2025-06-05T00:00:00Z": "0.00",
        "2025-06-04T00:00:00Z": "0.00",
        "2025-06-03T00:00:00Z": "0.00",
        "2025-06-02T00:00:00Z": "0.00",
        "2025-06-01T00:00:00Z": "0.00",
        "2025-05-31T00:00:00Z": "0.00",
        "Last 24H": "0.00",
        "Last 7 Days": "0.00",
        "Last 30 Days": "0.00",
        "Last 365 Days": "7.31250107",
        "Latest Stake": "2.43750003",
        "Latest Time": "2025-04-21T09:51:12Z",
        "Stake counted": 3,
        "time took (ms)": 2533
    }

    checker = StackingChecker(mock_rpc_client_class, mock_telegram_client)
    checker.check_new_rewards()

    mock_telegram_client.send_message.assert_not_called()

    mock_rpc_client_class.get_stake_report.return_value = {
        "2025-06-06T00:00:00Z": "2.43750003",
        "2025-06-05T00:00:00Z": "0.00",
        "2025-06-04T00:00:00Z": "0.00",
        "2025-06-03T00:00:00Z": "0.00",
        "2025-06-02T00:00:00Z": "0.00",
        "2025-06-01T00:00:00Z": "0.00",
        "Last 24H": "0.00",
        "Last 7 Days": "0.00",
        "Last 30 Days": "0.00",
        "Last 365 Days": "7.31250107",
        "Latest Stake": "2.43750003",
        "Latest Time": "2025-04-21T09:51:12Z",
        "Stake counted": 3,
        "time took (ms)": 2533
    }
    checker.check_new_rewards()

    mock_rpc_client_class.get_stake_report.return_value = {
        "2025-06-07T00:00:00Z": "2.43750003",
        "2025-06-06T00:00:00Z": "2.43750003",
        "2025-06-05T00:00:00Z": "0.00",
        "2025-06-04T00:00:00Z": "0.00",
        "2025-06-03T00:00:00Z": "0.00",
        "2025-06-02T00:00:00Z": "0.00",
        "Last 24H": "0.00",
        "Last 7 Days": "0.00",
        "Last 30 Days": "0.00",
        "Last 365 Days": "7.31250107",
        "Latest Stake": "2.43750003",
        "Latest Time": "2025-04-21T09:51:12Z",
        "Stake counted": 3,
        "time took (ms)": 2533
    }
    checker.check_new_rewards()

    mock_rpc_client_class.get_stake_report.return_value = {
        "2025-06-10T00:00:00Z": "2.43750003",
        "2025-06-09T00:00:00Z": "2.43750003",
        "2025-06-08T00:00:00Z": "0.00",
        "2025-06-07T00:00:00Z": "2.43750003",
        "2025-06-06T00:00:00Z": "2.43750003",
        "2025-06-05T00:00:00Z": "0.00",
        "2025-06-04T00:00:00Z": "0.00",
        "Last 24H": "0.00",
        "Last 7 Days": "0.00",
        "Last 30 Days": "0.00",
        "Last 365 Days": "7.31250107",
        "Latest Stake": "2.43750003",
        "Latest Time": "2025-04-21T09:51:12Z",
        "Stake counted": 3,
        "time took (ms)": 2533
    }
    checker.check_new_rewards()

    mock_telegram_client.send_message.assert_has_calls([
        call('🎉 You got a reward for stacking!:\n```text\n2025-06-06T00:00:00Z: 2.43750003\n```'),
        call('🎉 You got a reward for stacking!:\n```text\n2025-06-07T00:00:00Z: 2.43750003\n```'),
        call('🎉 You got a reward for stacking!:\n```text\n2025-06-09T00:00:00Z: 2.43750003\n2025-06-10T00:00:00Z: 2.43750003\n```'),
    ])
