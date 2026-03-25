FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install -r pyproject.toml

# Copy bot code
COPY . .

# Run the bot
CMD ["python", "bot.py"]
