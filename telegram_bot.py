import asyncio
import subprocess
import json
import os
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, Context_defaults, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LOG_FILE = "agent_logs.json"

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

async def start_command(update: Update, context):
    await update.message.reply_text(
        "🤖 AI Agency Bot\n\n"
        "Available commands:\n"
        "/start - Show this message\n"
        "/help - Show help\n"
        "/status - Show agent status\n"
        "/logs - Show recent activity\n"
        "/agents - List agents\n"
        "\nTo run a task, just type your task!\n"
        "Example: write hello world in python"
    )

async def help_command(update: Update, context):
    await update.message.reply_text(
        "📖 How to use:\n\n"
        "1. Type a task and I'll assign it to the right agent\n"
        "2. Use /agents to see all agents\n"
        "3. Use /status to check what's running\n"
        "4. Use /logs to see history\n\n"
        "Example tasks:\n"
        "- write a hello world program\n"
        "- create a marketing plan\n"
        "- research AI trends 2026"
    )

async def status_command(update: Update, context):
    logs = load_logs()
    if not logs:
        await update.message.reply_text("✅ All agents idle - no recent activity")
        return
    
    recent = logs[-5:]
    msg = "📊 Recent Activity:\n\n"
    for log in reversed(recent):
        status_emoji = "✅" if log["status"] == "completed" else "🔄"
        msg += f"{status_emoji} {log['agent']}: {log['task'][:40]}...\n"
    
    await update.message.reply_text(msg)

async def logs_command(update: Update, context):
    logs = load_logs()
    if not logs:
        await update.message.reply_text("No activity logs yet")
        return
    
    msg = "📜 Activity Logs:\n\n"
    for log in logs[-10:]:
        msg += f"🕐 {log['timestamp'][:19]}\n"
        msg += f"🤖 {log['agent']}\n"
        msg += f"📝 {log['task']}\n"
        msg += f"status: {log['status']}\n\n"
    
    await update.message.reply_text(msg)

async def agents_command(update: Update, context):
    msg = "👥 Available Agents:\n\n"
    for key, name in AGENTS.items():
        msg += f"/{key} - {name}\n"
    
    msg += "\n💡 Use /agent_name to assign to specific agent\n"
    await update.message.reply_text(msg)

def run_agent_task(task: str, agent_key: str = None) -> str:
    import ollama
    
    if not agent_key:
        task_lower = task.lower()
        if any(w in task_lower for w in ["code", "program", "write", "python", "debug"]):
            agent_key = "coding"
        elif any(w in task_lower for w in ["marketing", "campaign", "content", "seo"]):
            agent_key = "marketing"
        elif any(w in task_lower for w in ["research", "find", "learn", "information"]):
            agent_key = "research"
        else:
            agent_key = "org"
    
    agent_name = AGENTS.get(agent_key, "Agent")
    
    system_prompts = {
        "org": "You are an Organizational Manager. Coordinate team efforts and ensure projects stay on track.",
        "coding": "You are a Coding Specialist. Write clean, efficient code and solve technical problems.",
        "marketing": "You are a Marketing Strategist. Create effective marketing strategies and campaigns.",
        "research": "You are a Research Analyst. Gather accurate information and provide insights."
    }
    
    try:
        response = ollama.chat(
            model="llama3",
            messages=[
                {"role": "system", "content": system_prompts[agent_key]},
                {"role": "user", "content": f"Handle this task: {task}"}
            ]
        )
        result = response['message']['content']
        save_log(agent_name, task, result)
        return f"🤖 {agent_name}:\n\n{result}"
    except Exception as e:
        return f"Error: {str(e)}"

async def handle_message(update: Update, context):
    task = update.message.text
    chat = update.message.chat_id
    
    await update.message.reply_text("🔄 Processing your task...")
    
    try:
        result = run_agent_task(task)
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def run_bot():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    
    if not token:
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: print("⚠️  TELEGRAM_BOT_TOKEN not set!")
        )
        print("\nTo setup Telegram bot:")
        print("1. Open @BotFather on Telegram")
        print("2. Send /newbot to create a new bot")
        print("3. Follow instructions to get token")
        print("4. Set token: export TELEGRAM_BOT_TOKEN='your_token'")
        print("5. Run again")
        return
    
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("logs", logs_command))
    app.add_handler(CommandHandler("agents", agents_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Telegram bot starting... (Press Ctrl+C to stop)")
    print("Make sure Ollama is running: ollama serve")
    
    await app.run_polling(allowed_updates=[])

if __name__ == "__main__":
    asyncio.run(run_bot())