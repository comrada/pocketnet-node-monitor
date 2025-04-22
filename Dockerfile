FROM python:3.13-slim-bookworm

RUN pip install "poetry==2.1.2"

WORKDIR /app

COPY pyproject.toml poetry.lock* ./
COPY src/pocketnet_node_monitor ./pocketnet_node_monitor

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

CMD ["poetry", "run", "python", "-m", "pocketnet_node_monitor.log_watcher"]
