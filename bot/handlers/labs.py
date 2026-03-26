"""Handler for /labs command."""
import asyncio
from services.lms_client import LMSClient


async def handle_labs() -> str:
    """Return list of available labs."""
    client = LMSClient()
    items = await client.get_items()
    if not items:
        is_healthy, error = await client.check_health()
        if not is_healthy:
            return f"❌ Ошибка бэкенда: {error}"
        return "Не удалось получить список лабораторных."
    labs = [item for item in items if item.get("type") == "lab"]
    if not labs:
        return "Лабораторные не найдены."
    lines = ["📚 Доступные лабораторные:"]
    for lab in labs:
        lines.append(f"- {lab['title']}")
    return "\n".join(lines)
