#!/usr/bin/env python3.11
"""
Optimization Workflow:
Org → Research → Org → Coding → Feedback
"""
import json
import os
import asyncio
import time
from datetime import datetime, timedelta
from telegram import Bot
from telegram.error import TelegramError

# Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "your_token_here")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "149263552")
LOG_FILE = "agent_logs.json"
TASKS_FILE = "agent_tasks.json"
IMPROVEMENTS_FILE = "improvements.json"

AGENTS = {
    "org": {
        "role": "Organizational Manager",
        "goal": "Coordinate team efforts and optimize workflows",
        "backstory": "Experienced project manager focused on continuous improvement"
    },
    "coding": {
        "role": "Developer",
        "goal": "Implement improvements and write code",
        "backstory": "Senior developer who implements optimizations efficiently"
    },
    "research": {
        "role": "Research Analyst",
        "goal": "Find best practices and optimization opportunities",
        "backstory": "Thorough researcher who finds actionable improvements"
    }
}

SYSTEM_PROMPT = """You are {role}. {goal} {backstory}"""

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
    logs.append({
        "id": len(logs) + 1,
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "task": task,
        "status": status,
        "result": result[:500] if result else ""
    })
    save_json(LOG_FILE, logs)
    return logs

def save_improvement(category: str, improvement: str, priority: str, status: str = "pending"):
    improvements = load_json(IMPROVEMENTS_FILE)
    improvements.append({
        "id": len(improvements) + 1,
        "timestamp": datetime.now().isoformat(),
        "category": category,  # "found", "approved", "implemented"
        "improvement": improvement,
        "priority": priority,  # "high", "medium", "low"
        "status": status
    })
    save_json(IMPROVEMENTS_FILE, improvements)
    return improvements

def call_ollama(system_prompt: str, user_prompt: str) -> str:
    import ollama
    
    try:
        response = ollama.chat(
            model="llama3",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"

async def send_telegram_message(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"📱 (Telegram not configured - message saved): {message[:100]}...")
        return
    
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode="HTML"
        )
        print(f"✅ Telegram message sent")
    except TelegramError as e:
        print(f"❌ Telegram error: {e}")

async def notify_new_feature(message: str):
    """Send feedback when new feature is live"""
    await send_telegram_message(f"🆕 <b>NEW FEATURE LIVE!</b>\n\n{message}")

async def run_optimization_cycle(topic: str = None):
    """Run the full org → research → org → coding workflow"""
    
    if not topic:
        topic = "general optimization"
    
    print("\n" + "="*50)
    print(f"🔄 Starting Optimization: {topic}")
    print("="*50 + "\n")
    
    # Step 1: Org Agent identifies what to work on
    print("📋 Step 1: Org Agent analyzing task...")
    org_prompt = SYSTEM_PROMPT.format(**AGENTS["org"])
    
    org_task = f"""You are the Organizational Manager. Analyze this task and create an execution plan.

Task: {topic}

Break this down into:
1. What the Research Agent should find
2. What the Developer should implement
3. Timeline (keep it fast!)

Respond with a clear plan."""
    
    org_analysis = call_ollama(org_prompt, org_task)
    print(f"📋 Org Analysis:\n{org_analysis[:500]}...")
    
    await send_telegram_message(f"📋 <b>Optimization Analysis</b>\n\n{org_analysis[:500]}...")
    save_log("Org Manager", "Optimization analysis", org_analysis[:300], "completed")
    
    # Extract improvement areas from org response
    improvement_areas = []
    for line in org_analysis.split("\n"):
        if line.strip() and (line.strip()[0].isdigit() or "-" in line):
            improvement_areas.append(line.strip())
    
    if not improvement_areas:
        improvement_areas = [
            "1. Improve tutorial readability",
            "2. Add more code examples", 
            "3. Better visual elements"
        ]
    
    # Step 2: Research Agent finds best practices
    print("\n🔍 Step 2: Research Agent searching best practices...")
    research_prompt = SYSTEM_PROMPT.format(**AGENTS["research"])
    
    research_results = []
    for area in improvement_areas[:2]:  # Top 2
        research_task = f"""Search for best practices for: {area}

Provide specific, actionable recommendations that can be implemented quickly.
Include code snippets if relevant."""
        
        result = call_ollama(research_prompt, research_task)
        research_results.append({"area": area, "findings": result})
        print(f"🔍 Research for '{area}': {result[:200]}...")
    
    # Compile research findings
    research_summary = "\n\n".join([
        f"📌 {r['area']}\n{r['findings'][:500]}"
        for r in research_results
    ])
    
    await send_telegram_message(f"🔍 <b>Research Findings</b>\n\n{research_summary[:1000]}...")
    save_log("Research Analyst", "Optimization research", research_summary[:300], "completed")
    
    # Save found improvements
    for r in research_results:
        save_improvement("found", r["findings"], "medium", "pending")
    
    # Step 3: Org Agent reviews and approves
    print("\n✅ Step 3: Org Agent approving improvements...")
    approve_task = f"""Review these research findings and select the ONE that can be implemented fastest:

{research_summary}

Respond with:
1. The selected improvement (just the key idea)
2. Why it's the best choice
3. A brief implementation plan"""
    
    org_approval = call_ollama(org_prompt, approve_task)
    print(f"✅ Org Approval:\n{org_approval}")
    
    await send_telegram_message(f"✅ <b>Approved Improvement</b>\n\n{org_approval[:1000]}...")
    save_log("Org Manager", "Approved improvement", org_approval[:300], "completed")
    
    # Save approved
    improvements = load_json(IMPROVEMENTS_FILE)
    for i in improvements:
        if i.get("status") == "pending" and i.get("category") == "found":
            i["status"] = "approved"
            break
    save_json(IMPROVEMENTS_FILE, improvements)
    
    # Step 4: Coding Agent implements
    print("\n💻 Step 4: Coding Agent implementing...")
    coding_prompt = SYSTEM_PROMPT.format(**AGENTS["coding"])
    
    implement_task = f"""Implement this improvement based on the research findings:

{org_approval}

Make the actual code changes to app.py and agency.py.
Focus on one quick win that can be implemented immediately.
Keep it simple and working."""
    
    implementation = call_ollama(coding_prompt, implement_task)
    print(f"💻 Implementation:\n{implementation[:500]}...")
    
    save_log("Developer", "Improvement implementation", implementation[:300], "completed")
    
    # Mark as implemented
    improvements = load_json(IMPROVEMENTS_FILE)
    for i in improvements:
        if i.get("status") == "approved":
            i["status"] = "implemented"
            i["implemented_at"] = datetime.now().isoformat()
            break
    save_json(IMPROVEMENTS_FILE, improvements)
    
    # Step 5: Send feedback
    print("\n📱 Step 5: Sending feedback...")
    feedback = f"""🎉 <b>Optimization Cycle Complete!</b>

<b>Analysis:</b> {org_analysis[:200]}...

<b>Research:</b> {research_summary[:300]}...

<b>Approved:</b> {org_approval[:300]}...

<b>Implemented:</b> {implementation[:300]}...

Next cycle will run tomorrow!"""
    
    await notify_new_feature(feedback)
    
    print("\n" + "="*50)
    print("✅ Optimization Cycle Complete!")
    print("="*50 + "\n")
    
    return "Cycle complete!"

def run_scheduler():
    """Run the optimization cycle on schedule"""
    print("⏰ Scheduler started!")
    print("📅 Running daily at 08:00...")
    
    # Run now for testing
    print("\n🚀 Running initial optimization cycle...")
    asyncio.run(run_optimization_cycle())
    
    # Simple daily scheduler
    while True:
        now = datetime.now()
        next_run = (now + timedelta(days=1)).replace(hour=8, minute=0, second=0)
        seconds_until = (next_run - now).total_seconds()
        
        print(f"⏰ Next run in {int(seconds_until/3600)} hours...")
        time.sleep(seconds_until)
        
        print("\n" + "="*50)
        print("📅 Running scheduled optimization cycle...")
        print("="*50)
        asyncio.run(run_optimization_cycle())

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg == "--now":
            asyncio.run(run_optimization_cycle())
        
        elif arg == "--topic":
            if len(sys.argv) > 2:
                topic = " ".join(sys.argv[2:])
                asyncio.run(run_optimization_cycle(topic))
            else:
                print("Usage: --topic 'your task description'")
        
        elif arg == "--schedule":
            run_scheduler()
        
        else:
            print("Usage:")
            print("  python3.11 optimize_workflow.py --now                    # Run general optimization")
            print("  python3.11 optimize_workflow.py --topic 'task'      # Run specific task")
            print("  python3.11 optimize_workflow.py --schedule      # Run daily")
    else:
        print("Usage:")
        print("  python3.11 optimize_workflow.py --now                    # Run general optimization")
        print("  python3.11 optimize_workflow.py --topic 'task'      # Run specific task")
        print("  python3.11 optimize_workflow.py --schedule      # Run daily")