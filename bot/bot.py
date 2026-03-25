#!/usr/bin/env python3
import sys
import os
import argparse
import asyncio
import json

# Add bot directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from handlers.start import handle_start
from handlers.help import handle_help
from handlers.health import handle_health
from handlers.labs import handle_labs
from handlers.scores import handle_scores
from handlers.natural_language import handle_natural_language
from handlers.keyboard import get_main_keyboard

if not Config.BOT_TOKEN:
    print("ERROR: BOT_TOKEN not set")
    sys.exit(1)

COMMANDS = {
    "/start": lambda: handle_start(),
    "/help": lambda: handle_help(),
    "/health": lambda: asyncio.run(handle_health()),
    "/labs": lambda: asyncio.run(handle_labs()),
    "/scores": lambda arg="": asyncio.run(handle_scores(arg)),
}

async def run_bot():
    """Run the Telegram bot with inline keyboards."""
    from aiogram import Bot, Dispatcher, types
    from aiogram.filters import CommandStart, Command

    bot = Bot(token=Config.BOT_TOKEN)
    dp = Dispatcher()
    
    @dp.message(CommandStart())
    async def cmd_start(message: types.Message):
        result = handle_start()
        await message.answer(result, reply_markup=get_main_keyboard())

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        result = handle_help()
        await message.answer(result)

    @dp.message(Command("health"))
    async def cmd_health(message: types.Message):
        result = await handle_health()
        await message.answer(result)

    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message):
        result = await handle_labs()
        await message.answer(result)
    
    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message):
        args = message.text.split(maxsplit=1)
        lab_name = args[1] if len(args) > 1 else None
        result = await handle_scores(lab_name)
        await message.answer(result)
    
    @dp.callback_query(lambda c: c.data.startswith("cmd_"))
    async def handle_callback(message: types.CallbackQuery):
        data = message.data
        if data == "cmd_labs":
            result = await handle_labs()
        elif data == "cmd_health":
            result = await handle_health()
        elif data.startswith("cmd_scores_"):
            lab_id = data.replace("cmd_scores_", "")
            result = await handle_scores(lab_id)
        elif data.startswith("cmd_top_"):
            lab_id = data.replace("cmd_top_", "")
            result = await handle_scores(lab_id)  # Reuse scores for now
        elif data.startswith("cmd_completion_"):
            lab_id = data.replace("cmd_completion_", "")
            result = await handle_scores(lab_id)
        elif data == "cmd_back":
            result = "Main menu:"
        else:
            result = "Command not recognized"
        
        await message.message.edit_text(result, reply_markup=get_main_keyboard())
        await message.answer()
    
    @dp.message()
    async def handle_message(message: types.Message):
        """Handle natural language queries via LLM routing."""
        result = await handle_natural_language(message.text)
        await message.answer(result)

    await dp.start_polling(bot)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", help="Test mode: send command or text")
    args = parser.parse_args()

    if args.test:
        cmd = args.test.strip()
        if cmd.startswith("/"):
            parts = cmd.split(maxsplit=1)
            base_cmd = parts[0]
            arg = parts[1] if len(parts) > 1 else None
            
            if base_cmd in COMMANDS:
                handler = COMMANDS[base_cmd]
                if base_cmd == "/scores":
                    result = handler(arg)
                else:
                    result = handler()
                print(result)
            else:
                print(f"Unknown command: {cmd}")
        else:
            # Natural language query
            result = asyncio.run(handle_natural_language(cmd))
            print(result)
    else:
        print("Starting bot...")
        asyncio.run(run_bot())


if __name__ == "__main__":
    main()
