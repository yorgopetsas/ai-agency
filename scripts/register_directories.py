#!/usr/bin/env python3
"""
AI Agent Directory Registration Helper
Opens submission pages and provides required information.
"""
import webbrowser
import time
import json

# Registration data for all directories
REGISTRATIONS = {
    "amanita_barcelona": {
        "name": "Amanita AI Agency",
        "short_desc": "AI agency specializing in autonomous agent development, news automation, and website creation.",
        "long_desc": "Amanita AI Agency builds autonomous AI agents that handle research, content creation, and web development. Our agents process 100+ RSS feeds daily, research articles, rate quality, and publish to GitHub Pages. We offer end-to-end automation for businesses looking to leverage AI agents.",
        "url": "https://amanita.barcelona",
        "category": "AI Agency",
        "tags": ["AI agency", "automation", "agents", "web development"],
    },
    "theaiagentsbook": {
        "name": "The AI Agents Book",
        "short_desc": "Comprehensive guide to building AI agents — from architecture to deployment.",
        "long_desc": "The AI Agents Book is a practical guide covering agent frameworks, memory systems, skills, orchestration, and multi-tenant architecture. Learn how to build production-ready AI systems with real code examples and deployment strategies.",
        "url": "https://theaiagentsbook.com",
        "category": "Educational",
        "tags": ["AI agents", "book", "guide", "architecture"],
    },
    "howaiagentswork": {
        "name": "How AI Agents Work",
        "short_desc": "Educational resource explaining how AI agents work — architecture, decision-making, and real-world applications.",
        "long_desc": "How AI Agents Work breaks down complex agent concepts into digestible explanations. Learn about agent loops, tool use, memory, planning, and multi-agent coordination through interactive examples and clear documentation.",
        "url": "https://howaiagentswork.com",
        "category": "Educational",
        "tags": ["AI agents", "education", "tutorial", "learning"],
    },
}

# Directory submission URLs and details
DIRECTORIES = [
    {
        "name": "AI Agents Directory",
        "url": "https://aiagentsdirectory.com/submit-agent",
        "type": "agent_specific",
        "cost": "Free",
        "websites": ["amanita_barcelona", "theaiagentsbook", "howaiagentswork"],
    },
    {
        "name": "AI Agent Store",
        "url": "https://aiagentstore.ai/submit",
        "type": "agent_specific",
        "cost": "Free",
        "websites": ["amanita_barcelona"],
    },
    {
        "name": "AI Agents List",
        "url": "https://aiagentslist.com/submit",
        "type": "agent_specific",
        "cost": "Free",
        "websites": ["amanita_barcelona", "theaiagentsbook", "howaiagentswork"],
    },
    {
        "name": "FindYourAgent.ai",
        "url": "https://findyouragent.ai/submit",
        "type": "agent_specific",
        "cost": "Free",
        "websites": ["amanita_barcelona", "theaiagentsbook", "howaiagentswork"],
    },
    {
        "name": "AgentHunter",
        "url": "https://agenthunter.io/submit",
        "type": "agent_specific",
        "cost": "Free",
        "websites": ["amanita_barcelona"],
    },
    {
        "name": "FutureTools",
        "url": "https://futuretools.io/submit-a-tool",
        "type": "general_ai",
        "cost": "Free",
        "websites": ["theaiagentsbook", "howaiagentswork"],
    },
    {
        "name": "AlternativeTo",
        "url": "https://alternativeto.net/add-application/",
        "type": "general",
        "cost": "Free",
        "websites": ["theaiagentsbook"],
    },
    {
        "name": "SaaSHub",
        "url": "https://saashub.com/submit",
        "type": "general",
        "cost": "Free",
        "websites": ["theaiagentsbook", "howaiagentswork"],
    },
    {
        "name": "Product Hunt",
        "url": "https://producthunt.com/posts/new",
        "type": "launch",
        "cost": "Free",
        "websites": ["amanita_barcelona"],
    },
    {
        "name": "TopAI.tools",
        "url": "https://topai.tools/submit",
        "type": "general_ai",
        "cost": "Free",
        "websites": ["amanita_barcelona", "theaiagentsbook", "howaiagentswork"],
    },
    {
        "name": "AI Tool Hunt",
        "url": "https://aitoolhunt.com/submit",
        "type": "general_ai",
        "cost": "Free",
        "websites": ["theaiagentsbook", "howaiagentswork"],
    },
    {
        "name": "Easy With AI",
        "url": "https://easywithai.com/submit",
        "type": "general_ai",
        "cost": "Free",
        "websites": ["theaiagentsbook", "howaiagentswork"],
    },
    {
        "name": "AI Depot",
        "url": "https://aidepot.co/submit",
        "type": "general_ai",
        "cost": "Free",
        "websites": ["theaiagentsbook", "howaiagentswork"],
    },
    {
        "name": "Ben's Bites",
        "url": "https://bensbites.co/submit",
        "type": "newsletter",
        "cost": "Free",
        "websites": ["amanita_barcelona"],
    },
]

def print_registration_info(directory, website_key):
    """Print registration information for a directory."""
    website = REGISTRATIONS[website_key]
    
    print(f"\n{'='*60}")
    print(f"📁 {directory['name']}")
    print(f"{'='*60}")
    print(f"URL: {directory['url']}")
    print(f"Cost: {directory['cost']}")
    print(f"\n📝 Registration Info:")
    print(f"  Name: {website['name']}")
    print(f"  URL: {website['url']}")
    print(f"  Short Description: {website['short_desc']}")
    print(f"  Category: {website['category']}")
    print(f"  Tags: {', '.join(website['tags'])}")
    print(f"\n📄 Long Description:")
    print(f"  {website['long_desc']}")
    print()

def open_directory(directory):
    """Open directory submission page in browser."""
    print(f"\n🌐 Opening {directory['name']}...")
    webbrowser.open(directory['url'])
    time.sleep(2)

def main():
    print("=" * 60)
    print("🚀 AI Agent Directory Registration Helper")
    print("=" * 60)
    print(f"\nWebsites to register:")
    for key, website in REGISTRATIONS.items():
        print(f"  • {website['name']}: {website['url']}")
    
    print(f"\nDirectories to register on: {len(DIRECTORIES)}")
    print("\n" + "=" * 60)
    
    for directory in DIRECTORIES:
        print(f"\n{'─'*60}")
        print(f"Directory: {directory['name']}")
        print(f"Type: {directory['type']}")
        print(f"Websites: {', '.join(directory['websites'])}")
        
        # Print registration info for first website
        if directory['websites']:
            print_registration_info(directory, directory['websites'][0])
        
        # Ask user if they want to open this directory
        response = input(f"Open {directory['name']}? (y/n/skip): ").lower()
        
        if response == 'y':
            open_directory(directory)
            input("Press Enter when done...")
        elif response == 'skip':
            continue
        else:
            print("Skipping...")

if __name__ == "__main__":
    main()
