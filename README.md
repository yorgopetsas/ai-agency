# AI Agency Crew - Complete System

## Components

| File | Description |
|------|-------------|
| `agency.py` | Main multi-agent system |
| `telegram_bot.py` | Telegram remote control |
| `app.py` | Dashboard & Tutorial website |
| `agent_logs.json` | Activity logs |
| `agent_tasks.json` | Active task tracking |

## Running the System

### Terminal 1 - Ollama (always running)
```bash
ollama serve
```

### Terminal 2 - Run Tasks
```bash
cd ai_agency
python3.11 agency.py "your task here"
```

### Terminal 3 - Dashboard (optional)
```bash
streamlit run app.py
```

### Terminal 4 - Telegram Bot (optional)
```bash
export TELEGRAM_BOT_TOKEN='your_token'
python3.11 telegram_bot.py
```

## Usage Examples

```bash
python3.11 agency.py "write hello world in python"
python3.11 agency.py "create a marketing plan for a coffee shop"
python3.11 agency.py "research AI trends for 2026"
```

## Remote Control via Telegram

1. Get token from @BotFather on Telegram
2. Set token: `export TELEGRAM_BOT_TOKEN='your_token'`
3. Start bot: `python3.11 telegram_bot.py`

### Telegram Commands
- `/start` - Start bot
- `/help` - Show help
- `/status` - Show agent status
- `/logs` - Show activity logs
- `/agents` - List agents

## Dashboard

Open: `streamlit run app.py` then visit `http://localhost:8501`

Shows:
- Tutorial website
- Central dashboard
- Activity logs
- Agent status

## Cost

Free - runs entirely locally using Ollama on your machine.