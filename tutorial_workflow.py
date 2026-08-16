#!/usr/bin/env python3
"""
UNIFIED TUTORIAL WORKFLOW
=========================
Supports:
- Different models for different tasks
- Web research first
- Version-based improvements
- YAML frontmatter for titles
- Tutorials that grow each iteration

Usage:
    python3 tutorial_workflow.py --topic "Your Topic" --run
    python3 tutorial_workflow.py --improve tutorials/FILE.md --run
"""
import json
import os
import sys
import time
import argparse
from datetime import datetime

# Default models - can be overridden
DEFAULT_MODELS = {
    "research": "llama3",      # Fast for web research
    "writer": "gemma4:e2b",   # Fast for writing
    "dev": "llama3",          # Good for verification
    "review": "llama3"        # Good for quality check
}

ITERATIONS = 5
PROGRESS_FILE = "tutorials/workflow_progress.json"

# ============================================================
# YAML FRONTMATTER HELPERS
# ============================================================

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from content. Returns (metadata, body)"""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            import yaml
            try:
                metadata = yaml.safe_load(parts[1])
                body = parts[2].strip()
                return metadata, body
            except:
                pass
    return {}, content

def add_frontmatter(content: str, title: str, model: str = None, version: float = 1.0) -> str:
    """Add YAML frontmatter to content"""
    model = model or DEFAULT_MODELS["writer"]
    fm = f"""---
title: "{title}"
model: {model}
version: {version}
created: {datetime.now().strftime('%Y-%m-%d')}
---

{content}"""
    return fm

# ============================================================
# MODEL CALLING
# ============================================================

def call_model(system: str, user: str, model: str = "llama3") -> str:
    import ollama
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ]
        )
        return response['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

# ============================================================
# WEB SEARCH
# ============================================================

def web_search(query: str) -> list:
    """Search the web for tutorials"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for result in soup.select('.result')[:10]:
            title = result.select_one('.result__title')
            snippet = result.select_one('.result__snippet')
            if title:
                results.append({
                    'title': title.get_text(strip=True),
                    'snippet': snippet.get_text(strip=True) if snippet else ''
                })
        return results
    except Exception as e:
        return [{"error": str(e)}]

# ============================================================
# AGENT DEFINITIONS
# ============================================================

AGENTS = {
    "org": {
        "name": "Org Manager",
        "system": """You are a Project Manager. Your job is to:
1. Plan what each iteration should achieve
2. Coordinate between agents
3. Ensure quality improves each iteration
4. Always push for MORE content (tutorials should grow, not shrink)"""
    },
    "research": {
        "name": "Research Analyst",
        "system": """You are a Research Analyst. Your job is to:
1. Analyze research data and web search results
2. Extract key commands, facts, and best practices
3. Verify information accuracy
4. Identify what's missing in current content"""
    },
    "writer": {
        "name": "Technical Writer",
        "system": """You are a Technical Writer. Create tutorials that are:
1. Simple language (explain like to a friend)
2. Include WHAT + WHY for each step
3. Provide ALTERNATIVES for each option
4. Include REAL-WORLD examples
5. ALWAYS add MORE content than before (minimum 10% growth)
6. NEVER include prompt reflections or meta-comments"""
    },
    "dev": {
        "name": "Developer",
        "system": """You are a Developer. Your job is to:
1. Verify commands are correct and safe
2. Check for potential errors
3. Suggest code improvements
4. Ensure code blocks are properly formatted"""
    },
    "reviewer": {
        "name": "Content Reviewer",
        "system": """You are a Content Reviewer. Your job is to:
1. Check for completeness
2. Verify technical accuracy
3. Identify gaps
4. Ensure consistent style
5. Rate content quality 1-10"""
    }
}

# ============================================================
# WORKFLOW STEPS
# ============================================================

def step_org_plan(iteration: int, topic: str, previous: str) -> str:
    """Org agent creates a plan for this iteration"""
    model = DEFAULT_MODELS["research"]
    system = AGENTS["org"]["system"]
    user = f"""Iteration {iteration}/5

Topic: {topic}

Previous content:
{previous[:500] if previous else 'None'}

Create a brief plan for what this iteration should achieve. Focus on adding MORE content and improving quality."""
    
    result = call_model(system, user, model)
    print(f"   📋 Plan: {result[:100]}...")
    return result

def step_web_research(topic: str) -> str:
    """Do web research on the topic"""
    print("   🌐 Searching the web...")
    
    searches = [
        f"{topic} tutorial 2024 2025",
        f"{topic} installation guide Mac",
        f"{topic} troubleshooting common errors"
    ]
    
    all_results = []
    for search_query in searches:
        print(f"      🔍 {search_query}")
        results = web_search(search_query)
        all_results.extend(results)
        time.sleep(0.5)
    
    # Synthesize
    model = DEFAULT_MODELS["research"]
    system = AGENTS["research"]["system"]
    user = f"""Analyze these search results for: {topic}

Search Results:
{json.dumps(all_results[:15], indent=2)}

Extract:
- Key commands to include
- Step-by-step instructions
- Common errors and fixes
- Best practices"""
    
    result = call_model(system, user, model)
    print(f"   🔍 Research: {result[:150]}...")
    return result

def step_writer(topic: str, research: str, previous: str, iteration: int) -> str:
    """Writer agent creates content"""
    model = DEFAULT_MODELS["writer"]
    system = AGENTS["writer"]["system"]
    
    # Calculate growth target
    prev_len = len(previous) if previous else 0
    target_len = int(prev_len * 1.15) if prev_len > 0 else 3000
    
    user = f"""Create a comprehensive tutorial about: {topic}

RESEARCH FINDINGS:
{research[:1500]}

PREVIOUS VERSION (improve and expand):
{previous[:800] if previous else 'None'}

REQUIREMENTS:
1. Simple, friendly language (explain like to a friend)
2. WHAT + WHY for each section
3. Alternatives for each option
4. Real-world examples
5. Include actual commands with code blocks

TARGET: Write at least {target_len} characters (15% more than before)

Sections to include:
- Introduction (what and why)
- Installation/Setup
- Basic Usage
- Advanced Features
- Troubleshooting
- Real-world Examples

IMPORTANT: 
- Start directly with the content, no meta-comments
- Do NOT include phrases like "This is a fantastic request"
- Write the actual tutorial content only"""
    
    result = call_model(system, user, model)
    print(f"   ✍️ Writer: {len(result)} chars")
    return result

def step_dev_verify(content: str) -> str:
    """Developer verifies commands"""
    model = DEFAULT_MODELS["dev"]
    system = AGENTS["dev"]["system"]
    user = f"""Review this tutorial and verify:

{content[:1200]}

Check for:
1. Commands syntactically correct?
2. Any missing dependencies?
3. Potentially dangerous commands?
4. Missing important steps?

Respond with issues found (if any)."""
    
    result = call_model(system, user, model)
    print(f"   💻 Review: {result[:100]}...")
    return result

def step_review(content: str, previous_len: int) -> str:
    """Reviewer rates quality"""
    model = DEFAULT_MODELS["review"]
    system = AGENTS["reviewer"]["system"]
    user = f"""Rate this tutorial:

{content[:1000]}

Previous length: {previous_len} chars
Current length: {len(content)} chars

Rate 1-10 for:
1. Completeness
2. Clarity
3. Technical accuracy
4. Practical examples

Also verify:
- Does NOT contain prompt reflections?
- Has proper YAML frontmatter (title, model, version)?
- Is longer than previous version?"""
    
    result = call_model(system, user, model)
    print(f"   👀 Review: {result[:100]}...")
    return result

# ============================================================
# MAIN WORKFLOW
# ============================================================

def run_workflow(topic: str, improve_file: str = None):
    print("="*60)
    print("🚀 UNIFIED TUTORIAL WORKFLOW")
    print(f"Topic: {topic}")
    print("="*60)
    
    # Load existing if improving
    current_content = ""
    version = 1.0
    tutorial_title = topic
    
    if improve_file and os.path.exists(improve_file):
        with open(improve_file, "r") as f:
            current_content = f.read()
        
        metadata, body = parse_frontmatter(current_content)
        current_content = body
        version = float(metadata.get("version", 1.0))
        tutorial_title = metadata.get("title", topic)
        print(f"Improving: {tutorial_title} (v{version})")
        print(f"Current: {len(current_content)} chars")
    
    all_iterations = []
    
    for i in range(1, ITERATIONS + 1):
        print(f"\n{'='*50}")
        print(f"🔄 ITERATION {i}/5")
        print(f"{'='*50}")
        
        iteration_data = {"iteration": i, "steps": {}}
        
        # Step 1: Org plans
        print("\n📋 Step 1: Planning...")
        plan = step_org_plan(i, topic, current_content)
        iteration_data["steps"]["plan"] = plan
        
        # Step 2: Research (only on first iteration or if no previous)
        print("\n🔍 Step 2: Research...")
        if i == 1:
            research = step_web_research(topic)
        else:
            research = "Using previous research data"
        iteration_data["steps"]["research"] = research
        
        # Step 3: Writer creates
        print("\n✍️ Step 3: Writing...")
        prev_len = len(current_content)
        content = step_writer(topic, research, current_content, i)
        iteration_data["steps"]["content"] = content
        iteration_data["content_length"] = len(content)
        iteration_data["growth"] = len(content) - prev_len
        
        # Step 4: Dev verifies
        print("\n💻 Step 4: Verification...")
        dev_review = step_dev_verify(content)
        iteration_data["steps"]["dev_review"] = dev_review
        
        # Step 5: Review
        print("\n👀 Step 5: Review...")
        review = step_review(content, prev_len)
        iteration_data["steps"]["review"] = review
        
        all_iterations.append(iteration_data)
        current_content = content
        
        # Save progress
        progress = {
            "topic": topic,
            "title": tutorial_title,
            "version": version,
            "iterations": all_iterations,
            "current_content": current_content,
            "updated": datetime.now().isoformat()
        }
        with open(PROGRESS_FILE, "w") as f:
            json.dump(progress, f, indent=2, default=str)
        
        print(f"\n✅ Iteration {i} complete! ({len(content)} chars, +{len(content)-prev_len})")
    
    # Save final tutorial
    new_version = version + 0.1
    final_content = add_frontmatter(current_content, tutorial_title, DEFAULT_MODELS["writer"], new_version)
    
    # Determine filename
    safe_name = "".join(c for c in tutorial_title.lower() if c.isalnum() or c == " ")
    filename = f"tutorials/{safe_name.replace(' ', '_')}.md"
    
    with open(filename, "w") as f:
        f.write(final_content)
    
    print("\n" + "="*60)
    print("🎉 WORKFLOW COMPLETE!")
    print(f"Saved: {filename}")
    print(f"Version: {new_version}")
    print(f"Final length: {len(current_content)} chars")
    print("="*60)
    
    return all_iterations

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unified Tutorial Workflow")
    parser.add_argument("--topic", type=str, help="Tutorial topic")
    parser.add_argument("--improve", type=str, help="Improve existing tutorial")
    parser.add_argument("--run", action="store_true", help="Run the workflow")
    
    args = parser.parse_args()
    
    if args.run:
        if args.topic:
            run_workflow(args.topic)
        elif args.improve:
            # Extract topic from filename
            topic = args.improve.replace("tutorials/", "").replace(".md", "").replace("_", " ")
            run_workflow(topic, args.improve)
        else:
            print("Usage:")
            print("  python3 tutorial_workflow.py --topic 'Your Topic' --run")
            print("  python3 tutorial_workflow.py --improve tutorials/FILE.md --run")
    else:
        print("Unified Tutorial Workflow")
        print("="*40)
        print("Usage:")
        print("  python3 tutorial_workflow.py --topic 'Your Topic' --run")
        print("  python3 tutorial_workflow.py --improve tutorials/FILE.md --run")
