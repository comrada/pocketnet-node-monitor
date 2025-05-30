from unittest.mock import patch, MagicMock

import pytest

from pocketnet_node_monitor.stacking_checker import StackingChecker


@pytest.fixture
def mock_telegram_client():
    return MagicMock()


@patch("pocketnet_node_monitor.stacking_checker.RpcClient")
def test_check_staking_enabled(mock_rpc_client_class, mock_telegram_client):
    mock_rpc = MagicMock()
    mock_rpc.get_stacking_info.return_value = {
        "enabled": True,
        "staking": True,
        "errors": "",
        "expectedtime": 12345
    }
    mock_rpc_client_class.return_value = mock_rpc

    checker = StackingChecker(mock_rpc, mock_telegram_client)
    checker.check()

    mock_telegram_client.send_message.assert_not_called()


@patch("pocketnet_node_monitor.stacking_checker.RpcClient")
def test_check_staking_disabled(mock_rpc_client_class, mock_telegram_client):
    mock_rpc = MagicMock()
    mock_rpc.get_stacking_info.return_value = {
        "enabled": True,
        "staking": False,
        "errors": "",
        "expectedtime": 12345
    }
    mock_rpc_client_class.return_value = mock_rpc

    checker = StackingChecker(mock_rpc, mock_telegram_client)
    checker.check()

    mock_telegram_client.send_message.assert_called_once()
    message = mock_telegram_client.send_message.call_args[0][0]
    assert "Stacking is disabled!" in message
