#!/usr/bin/env python3.11
import asyncio
import os
import sys
sys.path.insert(0, '/Users/yorgopetsasedel/dev/opencode/ai_agency')

from telegram import Bot

async def main():
    bot = Bot(token=os.environ.get("TELEGRAM_BOT_TOKEN", ""))
    
    # Try to find which chat ID works
    for chat_id in ["149263552", "8662248146", "-100123456"]:
        try:
            await bot.send_message(chat_id=chat_id, text="🧪 Test!")
            print(f"Success! Chat ID: {chat_id}")
            break
        except Exception as e:
            print(f"Chat {chat_id}: {e}")

asyncio.run(main())