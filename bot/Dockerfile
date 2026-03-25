FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy bot code
COPY . .

# Run the bot
CMD ["uv", "run", "python", "bot.py"]
