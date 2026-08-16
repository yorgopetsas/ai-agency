import streamlit as st
import json
import os
import re
from datetime import datetime

st.set_page_config(
    page_title="AI Agents Agency",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

LOG_FILE = "agent_logs.json"
MEETINGS_FILE = "data/meetings.json"
ACCOUNTS_FILE = "accounts/internal/config/account.yaml"
APPROVALS_FILE = "data/pending_approvals.json"

def load_logs():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def load_meetings():
    if os.path.exists(MEETINGS_FILE):
        try:
            with open(MEETINGS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def load_approvals():
    if os.path.exists(APPROVALS_FILE):
        try:
            with open(APPROVALS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_approvals(approvals):
    with open(APPROVALS_FILE, "w") as f:
        json.dump(approvals, f, indent=2)

def add_approval(item_type, title, content, agent):
    approvals = load_approvals()
    approval = {
        "id": f"{item_type}_{len(approvals)}",
        "type": item_type,
        "title": title,
        "content": content,
        "agent": agent,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    approvals.append(approval)
    save_approvals(approvals)
    return approval

def approve_item(item_id):
    approvals = load_approvals()
    for a in approvals:
        if a["id"] == item_id:
            a["status"] = "approved"
            a["approved_at"] = datetime.now().isoformat()
    save_approvals(approvals)

def reject_item(item_id, feedback):
    approvals = load_approvals()
    for a in approvals:
        if a["id"] == item_id:
            a["status"] = "rejected"
            a["feedback"] = feedback
            a["rejected_at"] = datetime.now().isoformat()
    save_approvals(approvals)

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from content. Returns (metadata, body)"""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                import yaml
                metadata = yaml.safe_load(parts[1])
                body = parts[2].strip()
                return metadata or {}, body
            except:
                pass
    return {}, content

def load_tutorials():
    tutorials = {}
    tutorial_dir = "tutorials"
    if os.path.exists(tutorial_dir):
        for f in os.listdir(tutorial_dir):
            if f.endswith(".md"):
                filename = f.replace(".md", "")
                path = os.path.join(tutorial_dir, f)
                with open(path, "r") as file:
                    content = file.read()
                    metadata, body = parse_frontmatter(content)
                    name = metadata.get("title", filename.replace("_", " ").title())
                    tutorials[filename] = {
                        "name": name,
                        "content": body if body else content,
                        "sections": extract_sections(body if body else content)
                    }
    return tutorials

def extract_sections(content):
    sections = []
    for line in content.split("\n"):
        if line.startswith("##"):
            title = line.replace("##", "").strip()
            if title:
                sections.append(title)
    return sections

TUTORIALS = load_tutorials()

AGENT_ROLES = {
    "ORG": {"icon": "📋", "color": "🔵", "name": "Manager"},
    "RESEARCH": {"icon": "🔍", "color": "🟢", "name": "Researcher"},
    "WRITER": {"icon": "✍️", "color": "🟣", "name": "Writer"},
    "DEVELOPER": {"icon": "💻", "color": "🟠", "name": "Developer"},
    "DESIGNER": {"icon": "🎨", "color": "🩷", "name": "Designer"},
    "ANALYST": {"icon": "📊", "color": "🩵", "name": "Analyst"},
    "REVIEWER": {"icon": "👀", "color": "🩶", "name": "Reviewer"},
}

def show_search():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Search Tutorials")
    
    query = st.sidebar.text_input("Search...", key="search_input")
    
    if query:
        results = []
        query_lower = query.lower()
        for key, tutorial in TUTORIALS.items():
            if query_lower in tutorial["content"].lower():
                snippets = [line.strip()[:100] for line in tutorial["content"].split("\n") if query_lower in line.lower()]
                results.append({"tutorial": key, "name": tutorial["name"], "matches": snippets[:3]})
        
        if results:
            st.sidebar.markdown(f"**Found {len(results)} results:**")
            for r in results:
                st.sidebar.markdown(f"**{r['name']}**")
                for match in r["matches"]:
                    st.sidebar.markdown(f"  - {match}...")
                if st.sidebar.button(f"Go to {r['name']}", key=f"goto_{r['tutorial']}"):
                    st.session_state['page'] = r['tutorial']
                    st.rerun()
        else:
            st.sidebar.markdown("No results found")

def show_home():
    st.title("🤖 AI Agents Agency")
    st.markdown("## Complete Multi-Agent AI System")
    
    st.markdown("---")
    st.markdown("### 📚 Choose Your Path:")
    
    cols_per_row = 5
    cols = st.columns(cols_per_row)
    
    tutorial_items = list(TUTORIALS.items())
    for i, (key, tutorial) in enumerate(tutorial_items):
        with cols[i % cols_per_row]:
            icon = "📖"
            if "ollama" in key.lower():
                icon = "🦙"
            elif "opencode" in key.lower():
                icon = "⚡"
            elif "agency" in key.lower():
                icon = "🏗️"
            
            st.markdown(f"**{icon} {tutorial['name']}**")
            st.caption(f"{len(tutorial['sections'])} sections")
            
            btn_key = f"btn_{key}"
            if st.button(f"Open", key=btn_key):
                st.session_state['page'] = key
                st.rerun()
    
    st.markdown("---")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("📰 Daily News"):
            st.session_state['page'] = 'news_workflow'
            st.rerun()
    with col2:
        if st.button("📊 Dashboard"):
            st.session_state['page'] = 'dashboard'
            st.rerun()
    with col3:
        if st.button("🤝 Meetings"):
            st.session_state['page'] = 'meetings'
            st.rerun()
    with col4:
        if st.button("👥 Agents"):
            st.session_state['page'] = 'agents'
            st.rerun()
    with col5:
        if st.button("📋 Approvals"):
            st.session_state['page'] = 'approvals'
            st.rerun()

def show_tutorial(tutorial_key):
    if tutorial_key in TUTORIALS:
        tutorial = TUTORIALS[tutorial_key]
        st.title(tutorial['name'])
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("← Back"):
                st.session_state['page'] = 'home'
                st.rerun()
        
        st.markdown("---")
        sections = tutorial['sections']
        
        with st.sidebar:
            st.markdown("### 📑 Phases")
            
            if st.button("📖 Full"):
                st.session_state[f'{tutorial_key}_section'] = 'full'
                st.rerun()
            
            phases_list = [
                ("Phase 1", "Foundation"),
                ("Phase 2", "Memory"),
                ("Phase 3", "Skills"),
                ("Phase 4", "RAG + MCP"),
                ("Phase 5", "Orchestration"),
                ("Phase 6", "Multi-Client"),
            ]
            
            for phase, desc in phases_list:
                if st.button(f"{phase}"):
                    st.session_state[f'{tutorial_key}_section'] = phase
                    st.rerun()
        
        current_section = st.session_state.get(f'{tutorial_key}_section', 'full')
        
        if current_section == 'full':
            st.markdown(tutorial['content'])
        elif isinstance(current_section, str) and current_section.startswith('Phase'):
            # Extract phase number from string like "Phase 1"
            phase_num = int(current_section.split()[1])
            # Find the content for that phase
            content = tutorial['content']
            parts = content.split(f'## {current_section}:')
            if len(parts) > 1:
                # Get the next phase marker
                next_part = parts[1].split('## ')[0] if '## ' in parts[1] else parts[1]
                st.markdown(f'## {current_section}:')
                st.markdown(next_part)
            else:
                st.markdown(tutorial['content'])
        else:
            st.markdown(tutorial['content'])
    else:
        st.error(f"Tutorial not found: {tutorial_key}")
        if st.button("← Back"):
            st.session_state['page'] = 'home'
            st.rerun()

def show_dashboard():
    st.title("📊 Dashboard")
    if st.button("← Back"):
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
    st.markdown("### 🏗️ Phase Status")
    
    phases = [
        ("Phase 1", "Foundation", "✅ Complete"),
        ("Phase 2", "Memory", "✅ Complete"),
        ("Phase 3", "Skills", "✅ Complete"),
        ("Phase 4", "RAG + MCP", "✅ Complete"),
        ("Phase 5", "Orchestration", "✅ Complete"),
        ("Phase 6", "Multi-Client", "✅ Complete"),
        ("Phase 7", "Integration", "✅ Complete"),
    ]
    
    for phase, desc, status in phases:
        st.markdown(f"**{phase}**: {desc} - {status}")
    
    st.markdown("---")
    st.markdown("### 🤖 Our 7 Agents")
    
    for role, info in AGENT_ROLES.items():
        st.markdown(f"{info['icon']} **{role}** - {info['name']}")
    
    st.markdown("---")
    st.markdown("### 📝 Recent Activity")
    
    if logs:
        for log in reversed(logs[-10:]):
            emoji = "✅" if log.get("status") == "completed" else "🔄" if log.get("status") == "running" else "❌"
            st.markdown(f"{emoji} **{log.get('agent', 'Agent')}**: {log.get('task', 'Task')[:50]}")
    else:
        st.info("No activity yet!")
    
    st.markdown("---")
    if st.button("🗑️ Clear Logs"):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)
        st.success("Logs cleared!")
        st.rerun()

def show_meetings():
    st.title("🤝 Meetings Overview")
    if st.button("← Back"):
        st.session_state['page'] = 'home'
        st.rerun()
    
    meetings = load_meetings()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Meetings", len(meetings))
    with col2:
        st.metric("This Week", len([m for m in meetings if True]))  # Simplified
    
    st.markdown("---")
    st.markdown("### Meeting Details")
    
    if meetings:
        for meeting in reversed(meetings[-10:]):
            with st.expander(f"📅 {meeting.get('timestamp', 'N/A')} - {meeting.get('topic', 'No topic')}"):
                st.markdown(f"**Participants**: {meeting.get('participants', 'N/A')}")
                st.markdown(f"**Topic**: {meeting.get('topic', 'N/A')}")
                st.markdown(f"**Decisions**: {meeting.get('decisions', 'N/A')}")
                st.markdown(f"**Action Items**: {meeting.get('action_items', 'N/A')}")
                confidence = meeting.get('confidence', 0)
                st.progress(confidence, text=f"Agent Confidence: {confidence:.0%}")
                st.markdown(f"**Duration**: {meeting.get('duration', 'N/A')}")
    else:
        st.info("No meetings recorded yet!")
    
    st.markdown("---")
    st.caption("💡 Meetings capture agent-to-agent discussions and decisions.")

def show_news_workflow():
    st.title("📰 Daily News Workflow")
    st.markdown("### Add AI News Through Our Multi-Agent System")
    
    if st.button("← Back"):
        st.session_state['page'] = 'home'
        st.rerun()
    
    # Quick links to Flask admin
    st.markdown("---")
    st.markdown("### 🎯 Workflow Panel")
    st.markdown("Use the Flask admin panel for the full workflow:")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("📥 Admin Panel: Add URLs, approve summaries")
        st.markdown("**[Open Admin Panel](http://localhost:5001/admin)**", unsafe_allow_html=True)
    with col2:
        st.info("📰 News Website: View published articles")
        st.markdown("**[Open News Website](http://localhost:5001)**", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### Workflow Steps")
    st.markdown("""
    1. **Open Admin Panel** - Paste a news URL
    2. **Fetch & Summarize** - AI generates title + summary
    3. **Approve Summary** - Review and continue to article
    4. **Approve Article** - Review and publish
    5. **View on Website** - See your article live
    """)
    
    st.markdown("---")
    
    # API Status
    try:
        import requests
        response = requests.get("http://localhost:5001/api/news", timeout=2)
        articles = response.json()
        st.metric("Published Articles", len(articles))
    except:
        st.warning("⚠️ Flask server may not be running on port 5001")
    
    st.markdown("---")
    st.caption("💡 News server runs on port 5001. Start with: `python3 -m server.app`")

def show_approvals():
    st.title("📋 Pending Approvals")
    if st.button("← Back"):
        st.session_state['page'] = 'home'
        st.rerun()

    approvals = load_approvals()
    pending = [a for a in approvals if a.get("status") == "pending"]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total", len(approvals))
    with col2:
        st.metric("Pending", len(pending))

    st.markdown("---")

    if not pending:
        st.info("No items pending approval!")
    else:
        for approval in pending:
            with st.expander(f"📝 {approval.get('title', 'Untitled')} - {approval.get('type', 'unknown')}"):
                st.markdown(f"**Type**: {approval.get('type', 'unknown')}")
                st.markdown(f"**Agent**: {approval.get('agent', 'unknown')}")
                st.markdown(f"**Created**: {approval.get('created_at', 'N/A')}")

                st.markdown("---")
                st.markdown("**Content Preview:**")
                st.markdown(approval.get('content', 'No content')[:500] + "..." if len(approval.get('content', '')) > 500 else approval.get('content', 'No content'))

                st.markdown("---")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button(f"✅ Approve", key=f"approve_{approval['id']}"):
                        approve_item(approval['id'])
                        st.success("Approved!")
                        st.rerun()
                with col_no:
                    feedback = st.text_input("Feedback (if rejected)", key=f"feedback_{approval['id']}")
                    if st.button(f"❌ Reject", key=f"reject_{approval['id']}"):
                        reject_item(approval['id'], feedback)
                        st.success("Rejected with feedback!")
                        st.rerun()

    st.markdown("---")
    st.markdown("### Recently Approved/Rejected")

    processed = [a for a in approvals if a.get("status") in ["approved", "rejected"]]
    if processed:
        for item in reversed(processed[-5:]):
            status_emoji = "✅" if item.get("status") == "approved" else "❌"
            st.markdown(f"{status_emoji} **{item.get('title', 'Untitled')}** - {item.get('status', 'unknown')}")
    else:
        st.info("No processed items yet!")

def show_agents():
    st.title("👥 Our Agents")
    if st.button("← Back"):
        st.session_state['page'] = 'home'
        st.rerun()

    st.markdown("### Agent Team (7 Roles)")
    
    for role, info in AGENT_ROLES.items():
        with st.expander(f"{info['icon']} {role} - {info['name']}"):
            st.markdown(f"**Role ID**: {role}")
            st.markdown(f"**Name**: {info['name']}")
            st.markdown(f"**Icon**: {info['icon']}")
            
            settings = {
                "recommended_temp": "0.1-0.3" if role in ["RESEARCH", "DEVELOPER"] else "0.5-0.8" if role in ["WRITER", "DESIGNER"] else "0.2-0.5",
                "can_edit_tasks": "✅ Yes" if role == "ORG" else "❌ No",
                "communication": "Receives proposals, edits tasks" if role == "ORG" else "Sends proposals to ORG"
            }
            
            for key, value in settings.items():
                st.markdown(f"**{key}**: {value}")
    
    st.markdown("---")
    st.markdown("### Capabilities")
    
    capabilities = [
        ("Web Search", "DuckDuckGo API"),
        ("File Read/Write", "MCP server"),
        ("API Calls", "API keys"),
        ("Command Run", "Security config"),
        ("Browser/Visit", "MCP browser"),
        ("Database Query", "SQL connection"),
        ("Memory", "Mem0 - Phase 2"),
    ]
    
    for cap, setup in capabilities:
        st.markdown(f"- **{cap}**: {setup}")

if 'page' not in st.session_state:
    st.session_state['page'] = 'home'

st.sidebar.title("🤖 AI Agency")
show_search()

main_page = st.session_state.get('page', 'home')

if main_page == 'home':
    show_home()
elif main_page == 'news_workflow':
    show_news_workflow()
elif main_page == 'dashboard':
    show_dashboard()
elif main_page == 'meetings':
    show_meetings()
elif main_page == 'agents':
    show_agents()
elif main_page == 'approvals':
    show_approvals()
elif main_page in TUTORIALS:
    show_tutorial(main_page)
else:
    show_home()