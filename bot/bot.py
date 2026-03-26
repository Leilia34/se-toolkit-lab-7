#!/usr/bin/env python3
import sys
import argparse
import asyncio
import json
import re
from config import Config
from services.lms_client import LMSClient
from services.llm_client import LLMClient
from services.llm_tools import TOOLS, call_tool

if not Config.BOT_TOKEN:
    print("ERROR: BOT_TOKEN not set")
    sys.exit(1)

def handle_start() -> str:
    return "👋 Привет! Я LMS бот. Используйте /help для списка команд."

def handle_help() -> str:
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

async def handle_health() -> str:
    client = LMSClient()
    is_healthy, message = await client.check_health()
    return message

async def handle_labs() -> str:
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

async def handle_scores(lab_name: str = None) -> str:
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

async def handle_natural_language(query: str) -> str:
    llm = LLMClient()
    lms = LMSClient()
    messages = [
        {"role": "system", "content": "You are a helpful assistant that can retrieve information about labs and scores. Use the provided tools to answer user questions. If the user asks for labs, call get_labs. If they ask for scores for a specific lab, call get_scores. Always use the exact lab title as shown in the list."},
        {"role": "user", "content": query}
    ]
    response = await llm.chat(messages)

    if "tool_calls" in response and response["tool_calls"]:
        tool_call = response["tool_calls"][0]
        tool_name = tool_call["function"]["name"]
        tool_args = json.loads(tool_call["function"]["arguments"])

        if tool_name == "get_labs":
            tool_result = await handle_labs()
        elif tool_name == "get_scores":
            tool_result = await handle_scores(tool_args.get("lab_title"))    
        else:
            tool_result = "Unknown tool"

        messages.append(response)
        messages.append({"role": "tool", "content": tool_result, "tool_call_id": tool_call["id"]})
        final_response = await llm.chat(messages)
        return final_response.get("content", "Не удалось получить ответ.")  
    else:
        return response.get("content", "Извините, я не понял запрос.")      

COMMANDS = {
    "/start": handle_start,
    "/help": handle_help,
    "/health": handle_health,
    "/labs": handle_labs,
    "/scores": handle_scores,
}

async def run_bot():
    from aiogram import Bot, Dispatcher, types
    from aiogram.filters import CommandStart, Command

    bot = Bot(token=Config.BOT_TOKEN)
    dp = Dispatcher()
    
    @dp.message(CommandStart())
    async def cmd_start(message: types.Message):
        await message.answer(handle_start())

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        await message.answer(handle_help())

    @dp.message(Command("health"))
    async def cmd_health(message: types.Message):
        result = await handle_health()
        await message.answer(result)

    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message):
        result = await handle_labs()
        await message.answer(result)
    
    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message, command: types.Command):   
        lab_name = command.args.strip() if command.args else None
        result = await handle_scores(lab_name)
        await message.answer(result)
    
    @dp.message()
    async def handle_message(message: types.Message):
        result = await handle_natural_language(message.text)
        await message.answer(result)

    await dp.start_polling(bot)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", help="Тестовый режим: передать команду или текст")
    args = parser.parse_args()

    if args.test:
        cmd = args.test.strip()
        if cmd.startswith("/"):
            parts = cmd.split(maxsplit=1)
            base_cmd = parts[0]
            arg = parts[1] if len(parts) > 1 else None
            if base_cmd in COMMANDS:
                handler = COMMANDS[base_cmd]
                if base_cmd in ("/health", "/labs"):
                    result = asyncio.run(handler())
                elif base_cmd == "/scores":
                    result = asyncio.run(handler(arg))
                else:
                    result = handler()
                print(result)
            else:
                print(f"Неизвестная команда: {cmd}\nИспользуйте /help для списка команд.")
        else:
            result = asyncio.run(handle_natural_language(cmd))
            print(result)
    else:
        print("Запуск бота...")
        asyncio.run(run_bot())

if __name__ == "__main__":
    main()
