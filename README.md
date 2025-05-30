# Pocketcoin Node Monitor

It's a simple application that runs inside a Docker container, connects to the container with Pocketcoin Core node and
reads its log, as soon as it finds staking reward information there, it immediately sends a message to Telegram.

## Local dev

To test JSON-RPC calls, you can use the built-in mock server, which can be started with the `poetry run rpc-mock`
command. It will start on and listen on port `8899`, username and password `user:pass`.

## Test

Use the `poetry run pytest` command to run the tests.
