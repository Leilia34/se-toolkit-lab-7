# LMS Telegram Bot Development Plan

## Overview

This document describes the development plan for the LMS Telegram Bot that integrates with the Learning Management System backend. The bot provides students with quick access to their lab progress, scores, and analytics through a conversational interface.

## Architecture

The bot follows a layered architecture with clear separation of concerns:

1. **Entry Point (`bot.py`)**: Handles CLI test mode and Telegram bot initialization
2. **Handlers (`handlers/`)**: Command logic as pure functions (no Telegram dependency)
3. **Services (`services/`)**: External API clients (LMS, LLM)
4. **Configuration (`config.py`)**: Environment variable management

## Task 1: Project Scaffold

- Create directory structure: `bot/`, `handlers/`, `services/`
- Implement `--test` mode for offline verification
- Set up `pyproject.toml` with dependencies (aiogram, httpx, pydantic-settings)
- Create `.env.bot.example` template and `.env.bot.secret` for production

## Task 2: Backend Integration

Implement 5 slash commands connected to the LMS backend:

- `/start` — Welcome message with bot name
- `/help` — List all available commands with descriptions
- `/health` — Check backend connectivity via `GET /items/`
- `/labs` — List available labs from backend
- `/scores <lab>` — Show per-task pass rates with percentages

Error handling must show actual error details (e.g., "connection refused") without raw tracebacks.

## Task 3: Intent Routing (LLM-powered)

Implement natural language understanding:

- Define intents: `list_labs`, `get_scores`, `check_health`, `unknown`
- Use LLM to classify user messages into intents
- Extract entities (lab names, parameters) from user input
- Route to appropriate handlers based on detected intent
- Handle ambiguous queries with clarifying questions

Example: "покажи лабораторные" → `list_labs` intent → call `handle_labs()`

## Task 4: Deployment & Monitoring

- Docker containerization for consistent deployment
- Health check endpoint for monitoring
- Logging configuration for debugging
- Graceful restart on configuration changes
- Integration with existing docker-compose setup

## Testing Strategy

- Unit tests for handlers (pure functions, easy to test)
- Integration tests for service layer (mock HTTP responses)
- End-to-end tests via `--test` mode
- Manual testing in Telegram for user experience verification

## File Structure
bot/
├── bot.py # Entry point with --test mode
├── config.py # Configuration management
├── pyproject.toml # Dependencies
├── handlers/
│ ├── init.py
│ ├── start.py # /start handler
│ ├── help.py # /help handler
│ ├── health.py # /health handler
│ ├── labs.py # /labs handler
│ └── scores.py # /scores handler
└── services/
├── init.py
├── lms_client.py # LMS API client
└── llm_client.py # LLM API client

