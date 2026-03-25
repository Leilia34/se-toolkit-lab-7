#!/usr/bin/env python3
import sys
import os
import argparse
import asyncio
import json
import re

# Add bot directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from services.lms_client import LMSClient
from services.llm_client import LLMClient
from handlers.start import handle_start
from handlers.help import handle_help
from handlers.health import handle_health
from handlers.labs import handle_labs
from handlers.scores import handle_scores

if not Config.BOT_TOKEN:
    print("ERROR: BOT_TOKEN not set")
    sys.exit(1)

async def handle_natural_language(query: str) -> str:
    """Send query to LLM, handle tool calls, return final answer."""        
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
    "/start": lambda: handle_start(),
    "/help": lambda: handle_help(),
    "/health": handle_health,
    "/labs": handle_labs,
    "/scores": handle_scores,
}

async def run_bot():
    """Run the Telegram bot."""
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
                if base_cmd in ("/start", "/help"):
                    result = handler()
                elif base_cmd in ("/health", "/labs"):
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
