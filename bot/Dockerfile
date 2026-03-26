# bot/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Устанавливаем uv
RUN pip install uv

# Копируем файлы зависимостей из корня проекта
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Копируем код бота
COPY bot/ bot/

# Устанавливаем рабочую директорию для бота
WORKDIR /app/bot

# Команда запуска
CMD ["uv", "run", "bot.py"]
