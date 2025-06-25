# Pocketcoin Node Monitor

A simple monitoring service.
Monitor functions:

1. Read the logs in the Docker container of a node and search them for a string regarding the staking reward
2. Daily checking for the release of a new version of the node
3. Getting the balance of the node's wallet using JSON-RPC
4. Getting node staking status using JSON-RPC

In case of new information, the monitor sends a message to Telegram.

## Setup

The monitor runs inside a Docker container. You can run it in the same Docker-compose stack where the node is running,
but **it is not recommended**, because in case of any changes/updates of the monitor, it may lead to unnecessary restart
of the node. Instead, it is recommended to run it in a separate stack and connect to the node using its network.

Example, let's say the node is running in a docker-compose stack that has a network named `bastyon_default` and
container named `pocketnet.core`, then docker-compose for the monitor will look like this:

```yaml
networks:
  bastyon_default:
    name: bastyon_default
    external: true

services:
  node-monitor:
    image: comrada/pocketnet-node-monitor
    container_name: node-monitor
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
    environment:
      - TELEGRAM_BOT_TOKEN=<paste-your-token>
      - TELEGRAM_CHAT_ID=<paste-your-chat-id>
      - RPC_HOST=pocketnet.core
      - RPC_PORT=8899
      - RPC_USER=<user>
      - RPC_PASSWORD=<pass>
      - RPC_TIMEOUT=60
      - INTERVAL_STACKING_REWARDS_SEC=120
      - INTERVAL_STACKING_MIN=60
      - INTERVAL_BALANCE_SEC=300
    networks:
      - bastyon_default
```

You need to substitute the values of the required environment variables.
Environment variables used in the monitor:

- `DOCKER_BASE_URL` - URL through which the client can connect to the Docker API, default is empty (no `/restart`
  Telegram command in this case)
- `RPC_HOST` - node hostname
- `RPC_PORT` - node JSON-RPC port (defined by the `rpcport` parameter)
- `RPC_SCHEME` - JSON-RPC scheme: `http` or `https` (default is `http`)
- `RPC_USER` - JSON-RPC user name
- `RPC_PASSWORD` - JSON-RPC password
- `RPC_TIMEOUT` - JSON-RPC call timeout
- `TELEGRAM_BOT_TOKEN` - token to access the Telegram bot
- `TELEGRAM_CHAT_ID` - the ID of the channel where the bot will send you messages, see the Telegram API documentation to
  learn how to find this ID
- `INTERVAL_STACKING_REWARDS_SEC` - interval in seconds after which the node log will be checked for information about
  the award (default is 120 sec.)
- `INTERVAL_STACKING_MIN` - interval in minutes after which the status of staking will be checked (default is 60 min.)
- `INTERVAL_BALANCE_SEC` - interval in seconds after which the node's wallet balance will be checked (default is 300
  sec.)

In order for the monitor to connect to the node, JSON-RPC calls must be activated in the node, for this purpose set the
following parameters in the `pocketcoin.conf` file:

```properties
rpcbind=0.0.0.0
rpcallowip=172.0.0.0/8
rpcauth=user:8a993920f2fdd0aadf2cf146b5975b7d$f0d8d8cdb095132943e98ffff60f3b308b469b6403ff59d3566bd2c12f328bc2
rpcport=8899
```

To generate a password, execute the command: `poetry run gen-pass user pass` where `user` is your username and `pass` is
its password.

You should not open port 8899 to the outside of the node container docker, it is dangerous. In this case, the access
will only be inside the Docker network.
The `rpcallowip=172.0.0.0/8` parameter allows connection to the node from any docker container.

## Local dev

To test JSON-RPC calls, you can use the built-in mock server, which can be started with the `poetry run rpc-mock`
command. It will start on and listen on port `8899`, username and password `user:pass`.

## Testing

Use the `poetry run pytest` command to run the tests.
