import asyncio

if __name__ == "__main__":
    from pocketnet_node_monitor import monitor

    asyncio.run(monitor.start())
