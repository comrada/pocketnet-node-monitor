FROM python:3.13-slim-bookworm

ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* ./
COPY src/pocketnet_node_monitor ./pocketnet_node_monitor

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --only main

CMD ["poetry", "run", "python", "-m", "pocketnet_node_monitor"]
