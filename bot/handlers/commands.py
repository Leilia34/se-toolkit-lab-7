"""Command handlers for the Telegram bot."""

def handle_start() -> str:
    """Handle /start command."""
    return "👋 Привет! Я бот для работы с LMS. Используйте /help для списка команд."

def handle_help() -> str:
    """Handle /help command."""
    return (
        "Доступные команды:\n"
        "/start - приветствие\n"
        "/help - эта справка\n"
        "/health - статус бэкенда\n"
        "/labs - список лабораторных\n"
        "/scores <lab> - проходимость по задачам"
    )

def handle_health() -> str:
    """Handle /health command."""
    return "✅ Бэкенд доступен"

def handle_labs() -> str:
    """Handle /labs command."""
    return "📚 Доступные лабораторные:\n- Lab 01\n- Lab 02"

def handle_scores(lab_name: str = None) -> str:
    """Handle /scores command."""
    if not lab_name:
        return "❓ Укажите название лабораторной: /scores <lab>"
    return f"📊 Проходимость по {lab_name}:"
