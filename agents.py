import ollama
import sys

MODEL = "llama3"

AGENTS = {
    "org": {
        "role": "Organizational Manager",
        "goal": "Coordinate team efforts and ensure projects stay on track",
        "backstory": "Experienced project manager who excels at coordinating teams and resources"
    },
    "coding": {
        "role": "Coding Specialist", 
        "goal": "Write clean, efficient code and solve technical problems",
        "backstory": "Senior software engineer with expertise in multiple languages"
    },
    "marketing": {
        "role": "Marketing Strategist",
        "goal": "Create effective marketing strategies and campaigns",
        "backstory": "Creative marketing professional with deep knowledge of digital marketing"
    },
    "research": {
        "role": "Research Analyst",
        "goal": "Gather accurate information and provide insights",
        "backstory": "Thorough researcher skilled at finding and synthesizing information"
    }
}

SYSTEM_PROMPT = """You are an AI agent in a multi-agent agency crew. Your role: {role}

Goal: {goal}
Backstory: {backstory}

Always stay in character and work to achieve your goal. Coordinate with other agents when needed."""

def chat(agent_key, user_message, history=None):
    agent = AGENTS[agent_key]
    prompt = SYSTEM_PROMPT.format(**agent)
    
    messages = [{"role": "system", "content": prompt}]
    
    if history:
        messages.extend(history)
    
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = ollama.chat(model=MODEL, messages=messages)
        return response["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"

def run_agency(task):
    print(f"\n=== Agency Task: {task} ===\n")
    
    print("[Org Agent] Analyzing task and delegating...")
    delegation_prompt = f"""You are the Organizational Manager. Analyze this task and determine which agents should handle it.
Task: {task}

Respond with:
1. Which specialist agent(s) to use (coding, marketing, research)
2. A brief plan for each

Task types:
- coding/programming tasks -> use coding agent
- marketing/content -> use marketing agent  
- research/info gathering -> use research agent
- general coordination -> use org agent

Respond in format:
- Agents to involve: [agent names]
- Plan: [brief description]"""

    plan = chat("org", delegation_prompt)
    print(f"[Org Agent] {plan}\n")
    
    print("[Specialist Agents] Executing tasks...")
    
    if "coding" in plan.lower() or "program" in plan.lower() or "code" in plan.lower():
        result = chat("coding", f"Handle this coding task: {task}")
        print(f"[Coding Agent] {result}\n")
    
    if "marketing" in plan.lower() or "content" in plan.lower() or "campaign" in plan.lower():
        result = chat("marketing", f"Handle this marketing task: {task}")
        print(f"[Marketing Agent] {result}\n")
    
    if "research" in plan.lower() or "info" in plan.lower() or "gather" in plan.lower():
        result = chat("research", f"Handle this research task: {task}")
        print(f"[Research Agent] {result}\n")
    
    print("[Org Agent] Finalizing...")
    final = chat("org", f"Task completed: {task}. Summarize what was done.")
    print(f"[Org Agent] {final}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = input("Enter task for agency: ")
    
    if ollama.list().models:
        run_agency(task)
    else:
        print("Error: Ollama not running. Start with 'ollama serve' in a terminal.")