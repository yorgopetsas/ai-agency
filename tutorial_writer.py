#!/usr/bin/env python3.11
"""
Tutorial Writer Agent - Specialized for creating engaging tutorials
"""
import os
import json
from datetime import datetime

AGENT = {
    "name": "Tutorial Writer",
    "role": "Technical Content Creator",
    "goal": "Create engaging, easy-to-follow tutorials",
    "backstory": """You are an expert technical writer who creates tutorials that are:
- Engaging and fun to read
- Easy to follow step-by-step
- Visually appealing with code blocks
- Include troubleshooting tips
- Have copy-paste ready code
- Progress from beginner to advanced

You write for different skill levels and make complex topics simple."""
}

SYSTEM_PROMPT = """You are {role}.

{backstory}

When writing tutorials:
1. Start with WHY someone should care
2. Use numbered steps
3. Include code they can copy-paste
4. Add troubleshooting for common issues
5. End with next steps
6. Make it visually scannable with emojis and headers"""

def call_ollama(system: str, user: str) -> str:
    import ollama
    try:
        response = ollama.chat(
            model="llama3",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ]
        )
        return response['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

def run_tutorial_writer(topic: str, audience: str = "beginner", style: str = "engaging"):
    """Generate a tutorial for a given topic"""
    
    system_prompt = SYSTEM_PROMPT.format(**AGENT)
    
    user_prompt = f"""Write a complete tutorial about: {topic}

Audience level: {audience}
Style: {style}

Include:
1. Catchy title with emoji
2. Quick summary (what they'll learn)
3. Prerequisites
4. Step-by-step instructions with code
5. Copy-paste code blocks
6. Troubleshooting section
7. Next steps
8. Estimated time

Make it beginner-friendly and fun to read!"""
    
    print(f"✍️ Writing tutorial about: {topic}")
    tutorial = call_ollama(system_prompt, user_prompt)
    
    return tutorial

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "how to use Ollama for AI agents"
    
    tutorial = run_tutorial_writer(topic)
    print("\n" + "="*50)
    print("✍️ GENERATED TUTORIAL")
    print("="*50)
    print(tutorial)