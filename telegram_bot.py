import asyncio
import json
import os
import logging
from datetime import datetime

import ollama

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LOG_FILE = "agent_logs.json"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "149263552")

AGENTS = {
    "org": "Organizational Manager",
    "coding": "Coding Specialist", 
    "marketing": "Marketing Strategist",
    "research": "Research Analyst"
}

def load_logs():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_log(agent: str, task: str, result: str, status: str = "completed"):
    logs = load_logs()
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "task": task,
        "status": status,
        "result": result[:500] if result else ""
    })
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)
    return logs

async def send_message(text: str):
    if not TELEGRAM_BOT_TOKEN:
        print(f"📱 Telegram not configured: {text[:100]}")
        return
    
    from telegram import Bot
    from telegram.error import TelegramError
    
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        # Try to send to configured chat ID or try fallback methods
        if TELEGRAM_CHAT_ID:
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
            print(f"✅ Sent to Telegram")
    except TelegramError as e:
        print(f"❌ Telegram error: {e}")

async def send_message_to(text: str, chat_id: str):
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        return
    
    from telegram import Bot
    from telegram.error import TelegramError
    
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=chat_id, text=text)
        print(f"✅ Sent to {chat_id}")
    except TelegramError as e:
        print(f"❌ Telegram error: {e}")

async def handle_update(update: dict):
    message = update.get("message", {})
    text = message.get("text", "")
    chat = message.get("chat", {})
    chat_id = str(chat.get("id", ""))
    
    # Check if it's from a user (not a bot)
    from_user = message.get("from", {})
    if from_user.get("is_bot"):
        print("⚠️ Ignoring message from bot")
        return
    
    # Log the chat ID so we can use it
    if chat_id and chat_id != TELEGRAM_CHAT_ID:
        print(f"📱 New chat ID received: {chat_id} (user: {from_user.get('first_name')})")
    
    if not text:
        return
    
    response_text = ""
    
    if text == "/start":
        response_text = ("🤖 AI Agency Bot\n\n"
            "Available commands:\n"
            "/help - Show help\n"
            "/status - Agent status\n"
            "/logs - Activity logs\n"
            "/agents - List agents\n\n"
            "Just type a task!")
    elif text == "/help":
        response_text = ("📖 How to use:\n\n"
            "1. Type a task and I'll assign to the right agent\n"
            "2. /agents - See all agents\n"
            "3. /status - Check what's running\n"
            "4. /logs - See history")
    elif text == "/status":
        logs = load_logs()
        if not logs:
            response_text = "✅ All agents idle"
        else:
            recent = logs[-5:]
            response_text = "📊 Recent Activity:\n\n"
            for log in reversed(recent):
                emoji = "✅" if log["status"] == "completed" else "🔄"
                response_text += f"{emoji} {log['agent']}: {log['task'][:30]}...\n"
    elif text == "/logs":
        logs = load_logs()
        if not logs:
            response_text = "No activity logs yet"
        else:
            response_text = "📜 Logs (last 5):\n\n"
            for log in logs[-5:]:
                response_text += f"🤖 {log['agent']}\n📝 {log['task'][:50]}\n\n"
    elif text == "/agents":
        response_text = "👥 Available Agents:\n\n"
        for key, name in AGENTS.items():
            response_text += f"• {name}\n"
    else:
        # Process task
        await send_message("🔄 Processing...")
        
        task_lower = text.lower()
        if any(w in task_lower for w in ["code", "program", "write", "python"]):
            agent_key = "coding"
        elif any(w in task_lower for w in ["marketing", "campaign", "content"]):
            agent_key = "marketing"
        elif any(w in task_lower for w in ["research", "find", "learn"]):
            agent_key = "research"
        else:
            agent_key = "org"
        
        agent_name = AGENTS[agent_key]
        
        system_prompts = {
            "org": "You are an Organizational Manager. Coordinate team efforts.",
            "coding": "You are a Coding Specialist. Write clean, efficient code.",
            "marketing": "You are a Marketing Strategist. Create effective content.",
            "research": "You are a Research Analyst. Gather accurate information."
        }
        
        try:
            response = ollama.chat(
                model="llama3",
                messages=[
                    {"role": "system", "content": system_prompts[agent_key]},
                    {"role": "user", "content": f"Handle this task: {text}"}
                ]
            )
            result = response['message']['content']
            save_log(agent_name, text, result)
            response_text = f"🤖 {agent_name}:\n\n{result}"
        except Exception as e:
            response_text = f"Error: {str(e)}"
    
    # Reply to the user who messaged us
    if chat_id:
        await send_message_to(response_text, chat_id)

async def run_bot():
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ TELEGRAM_BOT_TOKEN not set!")
        print("\nTo setup:")
        print("1. @BotFather -> /newbot")
        print("2. export TELEGRAM_BOT_TOKEN='your_token'")
        print("3. Run again")
        return
    
    print("🤖 AI Agency Bot starting...")
    print(f"📱 Chat ID: {TELEGRAM_CHAT_ID}")
    print("Waiting for messages...")
    
    from telegram import Bot
    
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # Skip auto-message - wait for user to message first
    print("🤖 Bot ready! Message me on Telegram to start.")
    
    # Simple polling with updates
    offset = 0
    while True:
        try:
            updates = await bot.get_updates(offset=offset, timeout=30)
            for update in updates:
                if update.message:
                    await handle_update(update.to_dict())
                offset = update.update_id + 1
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\nBot stopped.")