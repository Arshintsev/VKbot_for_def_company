FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Устанавливаем Poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl build-essential \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем файлы Poetry заранее (оптимизация слоёв)
COPY pyproject.toml poetry.lock* ./

# Устанавливаем зависимости
RUN poetry install --no-root --only main

# Копируем исходники
COPY src ./src
COPY images ./images

CMD ["python", "-m", "src.bot.main"]
