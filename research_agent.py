#!/usr/bin/env python3.11
"""
Research Agent with Web Access
Researches online tutorials and creates detailed content
"""
import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

AGENT = {
    "name": "Research Analyst",
    "role": "Online Content Researcher",
    "goal": "Find and synthesize the best tutorials from the web",
    "backstory": """You search the web for the best tutorials, guides, and documentation.
You find practical, working solutions with real commands.
You verify information from multiple sources and provide accurate code."""
}

def search_web(query: str, num_results: int = 10) -> list:
    """Search the web for tutorials"""
    try:
        # Use DuckDuckGo (no API key needed)
        url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for result in soup.select('.result')[:num_results]:
            title = result.select_one('.result__title')
            snippet = result.select_one('.result__snippet')
            link = result.select_one('.result__url')
            
            if title:
                results.append({
                    'title': title.get_text(strip=True),
                    'snippet': snippet.get_text(strip=True) if snippet else '',
                    'link': link.get_text(strip=True) if link else ''
                })
        
        return results
    except Exception as e:
        return [{"error": str(e)}]

def research_topic(topic: str) -> dict:
    """Research a topic and return findings"""
    
    searches = [
        f"{topic} tutorial",
        f"{topic} best practices 2024", 
        f"{topic} command line guide"
    ]
    
    all_results = []
    
    for query in searches:
        results = search_web(query, 5)
        all_results.extend(results)
    
    # Compile findings
    findings = {
        "topic": topic,
        "searched": searches,
        "results": all_results[:15],
        "timestamp": datetime.now().isoformat()
    }
    
    return findings

def create_tutorial(topic: str, research: dict) -> str:
    """Create a tutorial from research"""
    
    import ollama
    
    system = f"""You are a technical writer. Create an engaging, detailed tutorial.

Topic: {topic}

Create a tutorial that:
1. Starts with WHY this is useful
2. Has clear numbered steps  
3. Includes copy-paste code blocks
4. Adds troubleshooting section
5. Ends with next steps"""
    
    user = f"""Based on this research:
{research['results']}

Create a complete tutorial in markdown format. Include real commands and code."""
    
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

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "install Ollama Mac Python"
    
    print(f"🔍 Researching: {topic}")
    research = research_topic(topic)
    
    print(f"Found {len(research['results'])} results")
    
    # Save research
    with open("research.json", "w") as f:
        json.dump(research, f, indent=2)
    
    print("✅ Research saved to research.json")
    print("\n" + "="*50)
    print("Research Results:")
    print("="*50)
    
    for r in research['results'][:5]:
        if 'error' not in r:
            print(f"\n📌 {r.get('title', 'No title')}")
            print(f"   {r.get('snippet', '')[:100]}...")