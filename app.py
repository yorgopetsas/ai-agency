import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="AI Agents Agency Tutorial",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

LOG_FILE = "agent_logs.json"

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

st.title("🤖 AI Agents Agency - Complete Tutorial")
st.markdown("## Build Your Own Multi-Agent AI System from Scratch")

st.sidebar.title("📚 Tutorial Navigation")
st.sidebar.markdown("---")

menu = st.sidebar.selectbox(
    "Choose a Section:",
    [
        "Introduction",
        "Prerequisites",
        "Architecture Overview",
        "Setting Up the Foundation",
        "Creating Agents",
        "Agent Communication",
        "Task Assignment",
        "Tracking & Monitoring",
        "Remote Control (Telegram)",
        "Building Your Own System",
        "Best Practices",
        "Dashboard"
    ]
)

if menu == "Introduction":
    st.header("🤖 Welcome to AI Agents Agency")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        This comprehensive tutorial will teach you how to build a **multi-agent AI system** that can:
        
        - 🤝 **Coordinate** multiple AI agents for different tasks
        - 💻 **Code** and solve technical problems
        - 📣 **Market** your products and services
        - 🔍 **Research** and gather information
        
        ### What You'll Build
        """)
        
        st.info("📍 A 4-agent system: Org Manager, Coding Specialist, Marketing Strategist, Research Analyst")
    
    with col2:
        st.image("https://img.icons8.com/color/144/robot.png", width=120)
    
    st.markdown("---")
    st.markdown("### 📋 System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Agents", "4")
    with col2:
        st.metric("Framework", "Ollama")
    with col3:
        st.metric("Cost", "Free")
    with col4:
        st.metric("Setup Time", "~30 min")
    
    st.markdown("---")
    st.markdown("### 🎯 Learning Outcomes")
    st.markdown("""
    By the end of this tutorial, you will understand:
    1. How multi-agent systems work
    2. How to create specialized AI agents
    3. How to delegate tasks between agents
    4. How to track agent activity
    5. How to control agents remotely
    """)

elif menu == "Prerequisites":
    st.header("📋 Prerequisites")
    
    st.markdown("""
    Before starting, make sure you have:
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Required Software")
        st.code("""# Python 3.11+
brew install python@3.11

# Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Ollama
curl -fsSL https://ollama.com | sh""", language="bash")
    
    with col2:
        st.markdown("### Required Accounts")
        st.code("""# Telegram Bot (free)
1. Open @BotFather on Telegram
2. Send /newbot
3. Get your bot token

# OpenAI (optional, for cloud models)
https://platform.openai.com/api-keys""", language="bash")
    
    st.markdown("---")
    st.markdown("### 🛠️ Installation Commands")
    
    st.code("""# Install Python dependencies
pip3.11 install streamlit
pip3.11 install python-telegram-bot
pip3.11 install crewai

# Pull Ollama model
ollama pull llama3

# Verify installation
ollama list""", language="bash")
    
    st.success("✅ All prerequisites ready!")
    st.warning("⚠️ Make sure Ollama is running: ollama serve")

elif menu == "Architecture Overview":
    st.header("🏗️ System Architecture")
    
    st.markdown("### How the Multi-Agent System Works")
    
    st.image("https://mermaid.ink/img/ graph TD; A[User] --> B[Org Manager]; B --> C[Coding Agent]; B --> D[Marketing Agent]; B --> E[Research Agent]; C --> B; D --> B; E --> B; B --> A; ", width=600)
    
    st.markdown("""
    ```
    ┌─────────────┐
    │   User    │
    └─────┬─────┘
          │
          ▼
    ┌─────────────────┐
    │  Org Manager  │◄─── Coordinates & Delegates
    └──────┬────────┘
           │
    ┌──────┼──────┬──────┐
    ▼     ▼     ▼     ▼
    ┌────┐┌────┐┌────┐
    │Code││Mktg││Rsrch│
    └──┬─┘└────┘└────┘
       └──────────┘
    ```
    """)
    
    st.markdown("### Component Breakdown")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 👤 User Interface")
        st.markdown("- CLI commands\n- Telegram Bot\n- Web Dashboard\n- API endpoint")
    with col2:
        st.markdown("#### 🤖 Org Manager")
        st.markdown("- Task delegation\n- Quality control\n- Progress tracking")
    with col3:
        st.markdown("#### ⚡ Specialist Agents")
        st.markdown("- Coding Agent\n- Marketing Agent\n- Research Agent")

elif menu == "Setting Up the Foundation":
    st.header("🛠️ Setting Up the Foundation")
    
    st.markdown("### Step 1: Create Project Directory")
    
    st.code("""# Create project folder
mkdir ai_agency
cd ai_agency

# Verify
ls -la""", language="bash")
    
    st.markdown("### Step 2: Install Dependencies")
    
    st.code("""# Create requirements.txt
cat > requirements.txt << 'EOF'
crewai
crewai[tools]
python-dotenv
streamlit
python-telegram-bot
EOF

# Install with Python 3.11
/opt/homebrew/opt/python@3.11/bin/pip3.11 install -r requirements.txt""", language="bash")
    
    st.markdown("### Step 3: Configure Ollama")
    
    st.code("""# Download Llama 3 model
ollama pull llama3

# Verify
ollama list

# Test
ollama run llama3 "Hello" """, language="bash")
    
    st.markdown("### Step 4: Environment Variables")
    
    st.code("""# Create .env file
cat > .env << 'EOF'
# Telegram Bot (get from @BotFather)
TELEGRAM_BOT_TOKEN=your_token_here

# Ollama (default)
OLLAMA_HOST=http://localhost:11434
EOF

# Load variables
source .env""", language="bash")
    
    st.success("✅ Foundation ready!")

elif menu == "Creating Agents":
    st.header("🎭 Creating Your Agents")
    
    st.markdown("""
    Each agent has three key components:
    - **Role**: What they are called
    - **Goal**: What they're trying to achieve  
    - **Backstory**: Their background/personality
    """)
    
    st.markdown("### Agent Definitions")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Org Manager", "Coding", "Marketing", "Research"])
    
    with tab1:
        st.code("""org_agent = {
    "role": "Organizational Manager",
    "goal": "Coordinate team efforts and ensure projects stay on track",
    "backstory": "Experienced project manager who excels at coordinating teams and resources"
}""", language="python")
        st.info("👔 Responsible for delegating tasks to other agents")
    
    with tab2:
        st.code("""coding_agent = {
    "role": "Coding Specialist",
    "goal": "Write clean, efficient code and solve technical problems",
    "backstory": "Senior software engineer with expertise in multiple languages"
}""", language="python")
        st.info("💻 Handles all programming tasks")
    
    with tab3:
        st.code("""marketing_agent = {
    "role": "Marketing Strategist",
    "goal": "Create effective marketing strategies and campaigns",
    "backstory": "Creative marketing professional with deep knowledge of digital marketing"
}""", language="python")
        st.info("📣 Creates marketing content and campaigns")
    
    with tab4:
        st.code("""research_agent = {
    "role": "Research Analyst",
    "goal": "Gather accurate information and provide insights",
    "backstory": "Thorough researcher skilled at finding and synthesizing information"
}""", language="python")
        st.info("🔍 Gathers and analyzes information")

elif menu == "Agent Communication":
    st.header("💬 Agent Communication")
    
    st.markdown("### How Agents Talk to Each Other")
    
    st.markdown("""
    1. **Task Assignment**: Org Manager receives user task
    2. **Analysis**: Org Manager determines which specialist needed
    3. **Delegation**: Task sent to appropriate agent
    4. **Execution**: Agent processes the task
    5. **Reporting**: Result passed back to user
    """)
    
    st.markdown("### System Prompt Template")
    
    st.code("""SYSTEM_PROMPT = '''You are an AI agent in a multi-agent agency crew.

Your Role: {role}
Your Goal: {goal}
Your Backstory: {backstory}

Always stay in character and work to achieve your goal.'''""", language="python")
    
    st.markdown("### The Communication Flow")
    
    st.code("""import ollama

def call_agent(system_prompt: str, user_prompt: str) -> str:
    response = ollama.chat(
        model='llama3',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
    )
    return response['message']['content']""", language="python")

elif menu == "Task Assignment":
    st.header("📋 Task Assignment")
    
    st.markdown("### Automatic Task Routing")
    
    st.code("""def route_task(task: str) -> str:
    task_lower = task.lower()
    
    # Determine which agent handles the task
    if any(w in task_lower for w in ['code', 'program', 'write', 'python']):
        return 'coding'
    elif any(w in task_lower for w in ['marketing', 'campaign', 'content']):
        return 'marketing'
    elif any(w in task_lower for w in ['research', 'find', 'learn']):
        return 'research'
    else:
        return 'org'  # Default to org manager""", language="python")
    
    st.markdown("### Manual Agent Selection")
    
    st.code("""# Via command
/coding write hello world in python
/marketing create a marketing plan
/research artificial intelligence trends
/org coordinate the team""", language="bash")
    
    st.markdown("### Task Queue System")
    
    st.code("""tasks = [
    {'id': 1, 'task': 'fix login bug', 'agent': 'coding', 'status': 'pending'},
    {'id': 2, 'task': 'create ad campaign', 'agent': 'marketing', 'status': 'pending'},
    {'id': 3, 'task': 'research competitors', 'agent': 'research', 'status': 'pending'},
]""", language="python")

elif menu == "Tracking & Monitoring":
    st.header("📊 Tracking & Monitoring")
    
    st.markdown("### Activity Logging")
    
    st.code("""import json
from datetime import datetime

LOG_FILE = 'agent_logs.json'

def save_log(agent: str, task: str, result: str, status: str):
    logs = load_logs()
    logs.append({
        'timestamp': datetime.now().isoformat(),
        'agent': agent,
        'task': task,
        'status': status,
        'result': result[:500]
    })
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)""", language="python")
    
    st.markdown("### Log Structure")
    
    st.code("""[
  {
    'timestamp': '2026-04-20T10:30:00',
    'agent': 'Coding Specialist',
    'task': 'write hello world in python',
    'status': 'completed',
    'result': 'print(\"Hello, World!\")'
  }
]""", language="json")
    
    st.markdown("### Metrics Tracked")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tasks Completed", "24")
    with col2:
        st.metric("Active Agents", "4")
    with col3:
        st.metric("Success Rate", "96%")
    with col4:
        st.metric("Avg Time", "45s")

elif menu == "Remote Control (Telegram)":
    st.header("📱 Telegram Remote Control")
    
    st.markdown("### Setup Telegram Bot")
    
    tab1, tab2, tab3 = st.tabs(["Setup", "Commands", "Code"])
    
    with tab1:
        st.markdown("""
        1. Open Telegram and search @BotFather
        2. Send /newbot
        3. Follow instructions:
           - Bot name: AI Agency
           - Username: ai_agency_bot
        4. Copy the bot token
        5. Start the bot
        """)
    
    with tab2:
        st.markdown("""
        /start - Start the bot
        /help - Show help
        /status - Show agent status
        /logs - Show activity logs
        /agents - List agents
        
        Just type a task to assign it!
        """)
    
    with tab3:
        st.code("""from telegram import Update
from telegram.ext import Application, CommandHandler

async def start_command(update: Update, context):
    await update.message.reply_text(
        "🤖 AI Agency Bot\n\n"
        "Commands:\n"
        "/start - Start\n"
        "/status - Show status\n"
        "/logs - Show logs\n"
        "\nType a task to get started!"
    )
    
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start_command))
await app.run_polling()""", language="python")

elif menu == "Building Your Own System":
    st.header("🛠️ Building Your Own System")
    
    st.markdown("### Complete Code Example")
    
    st.code("""import ollama
import json
import os
from datetime import datetime

# Agent definitions
AGENTS = {
    'org': {
        'role': 'Organizational Manager',
        'goal': 'Coordinate team efforts',
        'backstory': 'Experienced project manager'
    },
    'coding': {
        'role': 'Coding Specialist',
        'goal': 'Write clean code',
        'backstory': 'Senior software engineer'
    },
    'marketing': {
        'role': 'Marketing Strategist',
        'goal': 'Create marketing campaigns',
        'backstory': 'Creative marketing professional'
    },
    'research': {
        'role': 'Research Analyst',
        'goal': 'Gather information',
        'backstory': 'Thorough researcher'
    }
}

SYSTEM_PROMPT = '''You are an AI agent.

Role: {role}
Goal: {goal}
Backstory: {backstory}'''

def call_agent(agent_key, task):
    prompt = SYSTEM_PROMPT.format(**AGENTS[agent_key])
    response = ollama.chat(
        model='llama3',
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': task}
        ]
    )
    return response['message']['content']

def route_task(task):
    task_lower = task.lower()
    if 'code' in task_lower or 'program' in task_lower:
        return 'coding'
    if 'marketing' in task_lower or 'campaign' in task_lower:
        return 'marketing'
    if 'research' in task_lower or 'find' in task_lower:
        return 'research'
    return 'org'

def run_task(task):
    agent_key = route_task(task)
    result = call_agent(agent_key, task)
    return AGENTS[agent_key]['role'], result

if __name__ == '__main__':
    task = input('Enter task: ')
    agent, result = run_task(task)
    print(f'{agent}: {result}')""", language="python")
    
    st.markdown("### Copy & Paste This")
    
    st.download_button(
        "📥 Download agency.py",
        data=open("/Users/yorgopetsasedel/dev/opencode/ai_agency/agency.py").read(),
        file_name="agency.py",
        mime="text/x-python"
    )

elif menu == "Best Practices":
    st.header("⭐ Best Practices")
    
    st.markdown("### Keeping Agents Productive")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 1. Clear Task Definitions")
        st.code("""# Bad
'Do something'

# Good
'Write a Python function 
that calculates 
fibonacci numbers'""")
    
    with col2:
        st.markdown("#### 2. Proper Context")
        st.code("""# Bad
'Fix it'

# Good
'Fix the login error:
File: auth.py
Line 42: undefined variable'""")
    
    st.markdown("### Avoiding Lazy Agents")
    
    st.markdown("""
    1. **Timeout Settings** - Don't let agents run forever
    2. **Progress Checks** - Request periodic updates
    3. **Quality Gates** - Require approval before completion
    4. **Metrics** - Track task completion time
    5. **Escalation** - Route to another agent if stuck
    """)
    
    st.markdown("### Agent Health Checks")
    
    st.code("""def check_agent_health(agent_id):
    logs = load_logs()
    agent_logs = [l for l in logs if l['agent'] == agent_id]
    
    # Check for stuck tasks
    stuck = [l for l in agent_logs if l['status'] == 'running']
    if stuck and time.time() - stuck[0]['start_time'] > 300:
        return 'stuck'
    
    return 'healthy'""", language="python")

elif menu == "Dashboard":
    st.header("📊 Central Dashboard")
    
    logs = load_logs()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tasks", len(logs))
    with col2:
        completed = len([l for l in logs if l['status'] == 'completed'])
        st.metric("Completed", completed)
    with col3:
        running = len([l for l in logs if l['status'] == 'running'])
        st.metric("In Progress", running)
    with col4:
        failed = len([l for l in logs if l['status'] == 'failed'])
        st.metric("Failed", failed)
    
    st.markdown("---")
    st.markdown("### Activity Timeline")
    
    if logs:
        for log in reversed(logs[-10:]):
            status_emoji = "✅" if log["status"] == "completed" else "🔄" if log["status"] == "running" else "❌"
            st.markdown(f"{status_emoji} **{log['agent']}** - {log['task']}")
            st.caption(f"🕐 {log['timestamp']}")
    else:
        st.info("No activity yet. Run some tasks to see them here!")
    
    st.markdown("---")
    st.markdown("### Quick Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 View All Logs"):
            st.json(logs)
    with col2:
        if st.button("🗑️ Clear Logs"):
            with open(LOG_FILE, "w") as f:
                json.dump([], f)
            st.success("Logs cleared!")
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 Quick Start")
st.sidebar.code("""# Terminal 1
ollama serve

# Terminal 2  
cd ai_agency
python3.11 agency.py "hello world"

# Terminal 3 (optional)
streamlit run app.py""", language="bash")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📞 Support")
st.sidebar.markdown("- Check README.md\n- Open issue on GitHub\n- Ask in Telegram group")

if __name__ == "__main__":
    pass