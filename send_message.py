import asyncio
from telegram import Bot
import os

async def send_message(chat_id: str, text: str):
    bot = Bot(token=os.environ.get("TELEGRAM_BOT_TOKEN", ""))
    try:
        await bot.send_message(chat_id=chat_id, text=text)
        print(f"✅ Sent to {chat_id}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    # Hardcoded for now
    bot_token = "your_token_here"
    
    # Try different chat IDs
    chat_ids = [
        "149263552",
        "8662248146",
    ]
    
    for cid in chat_ids:
        try:
            asyncio.run(send_message(cid, "🧪 Test message from AI Agency Bot"))
        except:
            pass