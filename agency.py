import subprocess
import json
import os
from datetime import datetime

LOG_FILE = "agent_logs.json"
AGENT_TASK_FILE = "agent_tasks.json"

def load_json(filename):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def save_log(agent: str, task: str, result: str, status: str = "completed"):
    logs = load_json(LOG_FILE)
    
    # Truncate result if too long
    result_preview = result[:300] if result else ""
    
    logs.append({
        "id": len(logs) + 1,
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "task": task,
        "status": status,
        "result": result_preview
    })
    save_json(LOG_FILE, logs)
    return logs

def get_active_tasks():
    return load_json(AGENT_TASK_FILE)

def save_active_task(agent: str, task: str, task_id: int):
    tasks = load_json(AGENT_TASK_FILE)
    tasks.append({
        "id": task_id,
        "agent": agent,
        "task": task,
        "started_at": datetime.now().isoformat(),
        "status": "running"
    })
    save_json(AGENT_TASK_FILE, tasks)

def complete_active_task(task_id: int, status: str = "completed"):
    tasks = load_json(AGENT_TASK_FILE)
    for t in tasks:
        if t.get("id") == task_id:
            t["status"] = status
            t["completed_at"] = datetime.now().isoformat()
    save_json(AGENT_TASK_FILE, tasks)

def call_ollama(system: str, user: str, model: str = "llama3") -> str:
    prompt = f"""System: {system}

User: {user}

Assistant: """

    result = subprocess.run(
        ["ollama", "generate", model, prompt],
        capture_output=True,
        text=True,
        timeout=120
    )
    return result.stdout if result.stdout else result.stderr

def call_model(messages: list, model: str = "llama3") -> str:
    import ollama
    
    try:
        response = ollama.chat(model=model, messages=messages)
        return response['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

AGENTS = {
    "org": {
        "role": "Organizational Manager",
        "goal": "Coordinate team efforts and ensure projects stay on track",
        "backstory": "Experienced project manager who excels at coordinating teams and resources. You delegate tasks to specialist agents and ensure timely delivery."
    },
    "coding": {
        "role": "Coding Specialist",
        "goal": "Write clean, efficient code and solve technical problems",
        "backstory": "Senior software engineer with expertise in multiple languages including Python, JavaScript, Java, and more. You provide working code solutions."
    },
    "marketing": {
        "role": "Marketing Strategist",
        "goal": "Create effective marketing strategies and campaigns",
        "backstory": "Creative marketing professional with deep knowledge of digital marketing channels, SEO, social media, and content strategy."
    },
    "research": {
        "role": "Research Analyst",
        "goal": "Gather accurate information and provide insights",
        "backstory": "Thorough researcher skilled at finding and synthesizing information from various sources."
    }
}

SYSTEM_PROMPT = """You are an AI agent in a multi-agent agency crew.

Your Role: {role}
Your Goal: {goal}
Your Backstory: {backstory}

Always stay in character and work to achieve your goal. Be helpful, professional, and coordinate with other agents when needed."""

def create_agentPrompt(agent_key):
    agent = AGENTS[agent_key]
    return SYSTEM_PROMPT.format(**agent)

def run_agency(task: str, log_to_file: bool = True):
    task_id = int(datetime.now().timestamp())
    
    print(f"=== Agency Task: {task} ===\n")
    if log_to_file:
        save_active_task("all", task, task_id)
        save_log("Org Manager", task, "Task received", "running")

    messages = [
        {"role": "system", "content": create_agentPrompt("org")},
        {"role": "user", "content": f"""You are the Organizational Manager. Analyze this task and determine which specialist agents should handle it, then delegate.

Task: {task}

Respond with:
1. Which agents to use (coding, marketing, or research)
2. Your plan

Keep it brief."""}
    ]

    print("[Org Agent] Analyzing task...")
    try:
        org_response = call_model(messages)
        print(f"[Org Manager] {org_response}\n")
        if log_to_file:
            save_log("Org Manager", f"Analyze: {task}", org_response[:300], "completed")
    except Exception as e:
        print(f"[Error] {e}")

    task_lower = task.lower()
    agents_to_use = []
    
    if any(w in task_lower for w in ["code", "program", "write", "python", "javascript", "function", "debug"]):
        agents_to_use.append("coding")
    if any(w in task_lower for w in ["marketing", "campaign", "content", "social media", "seo", "advertising"]):
        agents_to_use.append("marketing")
    if any(w in task_lower for w in ["research", "find", "information", "gather", "learn", "explain"]):
        agents_to_use.append("research")

    if not agents_to_use:
        agents_to_use = ["coding"]

    for agent_key in agents_to_use:
        agent_name = AGENTS[agent_key]['role']
        print(f"[{agent_name}] Processing...")
        if log_to_file:
            save_log(agent_name, task, "Task started", "running")
        
        messages = [
            {"role": "system", "content": create_agentPrompt(agent_key)},
            {"role": "user", "content": f"Handle this task: {task}"}
        ]
        try:
            response = call_model(messages)
            print(f"[{agent_name}] {response}\n")
            if log_to_file:
                save_log(agent_name, task, response, "completed")
        except Exception as e:
            print(f"[Error] {e}")
            if log_to_file:
                save_log(agent_name, task, str(e), "failed")

    print("[Org Agent] Finalizing...")
    messages = [
        {"role": "system", "content": create_agentPrompt("org")},
        {"role": "user", "content": f"Summarize what was accomplished for this task: {task}"}
    ]
    try:
        final = call_model(messages)
        print(f"[Summary] {final}\n")
        if log_to_file:
            save_log("Org Manager", f"Complete: {task}", final[:300], "completed")
            complete_active_task(task_id, "completed")
    except Exception as e:
        print(f"[Error] {e}")
        if log_to_file:
            complete_active_task(task_id, "failed")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = input("Enter task for agency: ")
    run_agency(task)