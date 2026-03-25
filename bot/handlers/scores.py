"""Handler for /scores command."""
import asyncio
import re
from services.lms_client import LMSClient


async def handle_scores(lab_name: str = None) -> str:
    """Return per-task pass rates for a lab."""
    if not lab_name:
        return "❓ Укажите название лабораторной: /scores <lab>\nПример: /scores lab-04"
    
    client = LMSClient()
    lab = await client.find_lab_by_id(lab_name)
    
    if not lab:
        items = await client.get_items()
        for item in items:
            if item.get("type") == "lab" and item.get("title", "").lower() == lab_name.lower():
                lab = item
                break
    
    if not lab:
        return f"❌ Лабораторная '{lab_name}' не найдена. Используйте /labs для списка доступных."
    
    lab_id = lab_name.lower().strip()
    if not lab_id.startswith("lab-"):
        title = lab.get("title", "")
        match = re.search(r'Lab\s*(\d+)', title, re.IGNORECASE)
        if match:
            lab_id = f"lab-{match.group(1).zfill(2)}"
        else:
            lab_id = f"lab-{lab.get('id', '00')}"
    
    success, pass_rates, error = await client.get_pass_rates(lab_id)
    
    if not success:
        return f"❌ Ошибка бэкенда: {error}"
    
    if not pass_rates:
        lab_number = lab_id.replace("lab-", "").lstrip("0") or "0"
        lab_number_padded = lab_id.replace("lab-", "").zfill(2)
        
        for alt_id in [f"lab-{lab_number_padded}", f"lab-{lab_number}", lab_id]:
            success, pass_rates, error = await client.get_pass_rates(alt_id)
            if pass_rates:
                break
    
    if not pass_rates:
        return f"Нет данных о проходимость для {lab['title']}."
    
    lab_display = lab['title']
    lines = [f"📊 Pass rates for {lab_display}:"]
    for task in pass_rates:
        task_name = task.get("task", "unknown")
        avg_score = task.get("avg_score", 0)
        attempts = task.get("attempts", 0)
        lines.append(f"- {task_name}: {avg_score:.1f}% ({attempts} attempts)")
    return "\n".join(lines)
