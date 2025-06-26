# syntax=docker/dockerfile:1
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем переменные окружения, чтобы poetry не создавала venv
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Устанавливаем poetry
RUN pip install poetry

# Копируем файлы с зависимостями
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости
RUN poetry install --no-dev --no-root

# Копируем исходный код приложения
COPY . .

# Открываем порт для FastAPI
EXPOSE 8000 