"""Handler for /help command."""


def handle_help() -> str:
    """Return list of available commands."""
    return (
        "Доступные команды:\n"
        "/start - приветствие\n"
        "/help - эта справка\n"
        "/health - статус бэкенда\n"
        "/labs - список лабораторных\n"
        "/scores <lab> - проходимость по задачам\n"
        "\nИли просто спросите на русском языке, например:\n"
        "  покажи лабораторные\n"
        "  оценки по Lab 01"
    )
