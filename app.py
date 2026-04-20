import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="AI Agents Agency - Tutorials",
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

# ============================================
# HELPER FUNCTIONS
# ============================================

def read_tutorial(filename):
    path = f"tutorials/{filename}.md"
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    return None

# ============================================
# HOME PAGE
# ============================================

def show_home():
    st.title("🤖 AI Agents Agency")
    st.markdown("## Complete Multi-Agent AI System Tutorial")
    
    st.markdown("---")
    st.markdown("### 📚 Choose Your Tutorial Path:")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        ### 🦙 Ollama (FREE)
        Run AI locally on your Mac
        Complete guide - 400+ lines
        """)
        if st.button("🦙 Start Ollama Tutorial"):
            st.session_state['page'] = 'ollama'
            st.rerun()
    
    with col2:
        st.markdown("""
        ### 🔥 OpenAI (Paid)
        Use GPT models via API
        Coming soon
        """)
        if st.button("🔥 OpenAI (Coming)"):
            st.session_state['page'] = 'openai'
            st.rerun()
    
    with col3:
        st.markdown("""
        ### 🔵 Anthropic (Paid)
        Use Claude AI
        Coming soon
        """)
        if st.button("🔵 Anthropic (Coming)"):
            st.session_state['page'] = 'anthropic'
            st.rerun()
    
    with col4:
        st.markdown("""
        ### ⚡ Hybrid (Best)
        Mix local + cloud
        Coming soon
        """)
        if st.button("⚡ Hybrid (Coming)"):
            st.session_state['page'] = 'hybrid'
            st.rerun()
    
    st.markdown("---")
    
    if st.button("📊 Go to Dashboard"):
        st.session_state['page'] = 'dashboard'
        st.rerun()

# ============================================
# OLLAMA TUTORIAL - COMPREHENSIVE
# ============================================

def show_ollama():
    # Check for full tutorial file
    content = read_tutorial("OLLAMA_COMPLETE_GUIDE")
    
    if content:
        st.title("🦙 Ollama Complete Guide 2026")
        st.markdown("[← Back to Home](#)")
        if st.button("← Back to Home"):
            st.session_state['page'] = 'home'
            st.rerun()
        
        st.markdown("---")
        
        # Show content in sections
        sections = content.split("## ")
        
        # Create sidebar for navigation
        st.sidebar.title("📑 Sections")
        
        for i, section in enumerate(sections[1:], 1):
            title = section.split('\n')[0][:50]
            if st.sidebar.button(f"{i}. {title}"):
                st.session_state['ollama_section'] = i
                st.rerun()
        
        # Get current section
        current = st.session_state.get('ollama_section', 1)
        
        if current <= len(sections) - 1 and current > 0:
            st.markdown(f"## {sections[current]}")
        else:
            # Show full content
            st.markdown(content)
    else:
        # Fallback to inline content
        st.title("🦙 Ollama Tutorial")
        if st.button("← Back to Home"):
            st.session_state['page'] = 'home'
            st.rerun()
        
        # Section 1: What is Ollama
        st.markdown("""
        # 🦙 Complete Ollama Tutorial
        
        ## 1. What is Ollama?
        
        Ollama is a free, open-source tool that lets you run Large Language Models (LLMs) 
        directly on your Mac - no internet required after installation!
        
        **Why Ollama?**
        - 🆓 Free - No API costs
        - 🔒 Private - Your data stays on your Mac
        - ⚡ Fast - Runs locally
        - 📱 Simple - One command to run AI
        
        ## 2. System Requirements
        
        | Component | Minimum | Recommended |
        |-----------|---------|-------------|
        | macOS | 11 Big Sur | 14 Sonoma+ |
        | Chip | Apple Silicon (M1+) | M2/M3/M4 |
        | RAM | 8 GB | 16 GB+ |
        | Storage | 10 GB free | 50 GB free |
        
        ## 3. Installation (Homebrew)
        
        ```bash
        # Install Homebrew
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Install Ollama
        brew install ollama
        
        # Verify
        ollama --version
        ```
        
        ## 4. First Run
        
        ```bash
        # Download model
        ollama pull llama3.2
        
        # Run!
        ollama run llama3.2
        ```
        
        ## 5. Commands Quick Reference
        
        | Command | What it does |
        |---------|--------------|
        | `ollama pull <model>` | Download model |
        | `ollama run <model>` | Start chat |
        | `ollama list` | See installed models |
        | `ollama serve` | Start API server |
        | `ollama remove <model>` | Delete model |
        
        ## 6. Troubleshooting
        
        **Problem: "ollama: command not found"**
        
        ```bash
        export PATH="/usr/local/bin:$PATH"
        source ~/.zshrc
        ```
        
        **Problem: Model runs slow**
        - Close other apps
        - Use smaller model (llama3.2:3b)
        
        **Problem: Out of memory**
        - Use smaller model
        - Free up RAM
        
        ---
        
        ## Next Steps
        
        1. ✅ Install Ollama
        2. ⬇️ Download llama3.2
        3. 💬 Have your first chat
        4. 🔧 Try the API
        5. 🚀 Build an app!
        """)

# ============================================
# DASHBOARD
# ============================================

def show_dashboard():
    st.title("📊 Dashboard")
    if st.button("← Back to Home"):
        st.session_state['page'] = 'home'
        st.rerun()
    
    logs = load_logs()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tasks", len(logs))
    with col2:
        completed = len([l for l in logs if l.get("status") == "completed"])
        st.metric("Completed", completed)
    with col3:
        running = len([l for l in logs if l.get("status") == "running"])
        st.metric("In Progress", running)
    with col4:
        failed = len([l for l in logs if l.get("status") == "failed"])
        st.metric("Failed", failed)
    
    st.markdown("---")
    st.markdown("### Recent Activity")
    
    if logs:
        for log in reversed(logs[-10:]):
            emoji = "✅" if log.get("status") == "completed" else "🔄" if log.get("status") == "running" else "❌"
            st.markdown(f"{emoji} **{log.get('agent', 'Agent')}**: {log.get('task', 'Task')[:50]}")
    else:
        st.info("No activity yet. Run some tasks!")
    
    st.markdown("---")
    if st.button("🗑️ Clear All Logs"):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)
        st.success("Logs cleared!")
        st.rerun()

# ============================================
# MAIN APP
# ============================================

if 'page' not in st.session_state:
    st.session_state['page'] = 'home'
    st.session_state['ollama_section'] = 1

st.sidebar.title("🤖 AI Agency")
st.sidebar.markdown("---")

main_page = st.session_state.get('page', 'home')

if main_page == 'home':
    show_home()
elif main_page == 'ollama':
    show_ollama()
elif main_page == 'openai':
    show_home()
    st.warning("Coming soon!")
elif main_page == 'anthropic':
    show_home()
    st.warning("Coming soon!")
elif main_page == 'hybrid':
    show_home()
    st.warning("Coming soon!")
elif main_page == 'dashboard':
    show_dashboard()
else:
    show_home()