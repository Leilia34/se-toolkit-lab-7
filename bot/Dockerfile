FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy and install
COPY pyproject.toml ./
RUN uv pip install --system aiogram httpx pydantic-settings

# Copy bot code
COPY . .

# Run the bot
CMD ["python", "bot.py"]
