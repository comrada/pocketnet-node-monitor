from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

import pytest

from pocketnet_node_monitor.log_watcher import LogWatcher


@pytest.fixture
def mock_telegram_client():
    return MagicMock()


@patch("pocketnet_node_monitor.log_watcher.docker.DockerClient")
def test_staking_without_error(mock_docker_client_class, mock_telegram_client):
    log_lines = [
        "2025-05-25T12:00:00Z === Staking : new PoS block found hash: 3301312 - 4910828adc7a4ab8f09082a204855de9e5ce53630d2eb9e9be76be12f9388d4c",
        "2025-05-25T12:00:01Z All good"
    ]
    mock_container = MagicMock()
    mock_container.logs.return_value = "\n".join(log_lines).encode()

    mock_docker_client = MagicMock()
    mock_docker_client.containers.get.return_value = mock_container
    mock_docker_client_class.return_value = mock_docker_client

    watcher = LogWatcher(base_url="unix://var/run/docker.sock", telegram_client=mock_telegram_client)
    watcher.last_timestamp = datetime.now(timezone.utc) - timedelta(seconds=60)

    watcher.check_staking()

    mock_telegram_client.send_message.assert_called_once()


@patch("pocketnet_node_monitor.log_watcher.docker.DockerClient")
def test_staking_with_error_1(mock_docker_client_class, mock_telegram_client):
    log_lines = [
        "2025-05-24T16:32:14Z === Staking : new PoS block found hash: 3301312 - 4910828adc7a4ab8f09082a204855de9e5ce53630d2eb9e9be76be12f9388d4c",
        "2025-05-24T16:32:14Z ERROR: CheckStake() : generated block is stale"
    ]
    mock_container = MagicMock()
    mock_container.logs.return_value = "\n".join(log_lines).encode()

    mock_docker_client = MagicMock()
    mock_docker_client.containers.get.return_value = mock_container
    mock_docker_client_class.return_value = mock_docker_client

    watcher = LogWatcher(base_url="unix://var/run/docker.sock", telegram_client=mock_telegram_client)
    watcher.last_timestamp = datetime.now(timezone.utc) - timedelta(seconds=60)

    watcher.check_staking()

    mock_telegram_client.send_message.assert_not_called()

@patch("pocketnet_node_monitor.log_watcher.docker.DockerClient")
def test_staking_with_error_2(mock_docker_client_class, mock_telegram_client):
    log_lines = [
        "2025-05-24T16:32:14Z === Staking : new PoS block found hash: 3301312 - 4910828adc7a4ab8f09082a204855de9e5ce53630d2eb9e9be76be12f9388d4c",
        "2025-05-24T16:32:14Z ERROR: CoinStaker: ProcessNewBlock, block not accepted"
    ]
    mock_container = MagicMock()
    mock_container.logs.return_value = "\n".join(log_lines).encode()

    mock_docker_client = MagicMock()
    mock_docker_client.containers.get.return_value = mock_container
    mock_docker_client_class.return_value = mock_docker_client

    watcher = LogWatcher(base_url="unix://var/run/docker.sock", telegram_client=mock_telegram_client)
    watcher.last_timestamp = datetime.now(timezone.utc) - timedelta(seconds=60)

    watcher.check_staking()

    mock_telegram_client.send_message.assert_not_called()
