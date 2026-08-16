---
title: "My AI Agency Tutorial"
model: llama3
version: 4.0
created: 2026-04-22
phase: 8
---

# My AI Agency Tutorial

A step-by-step guide to building your own AI Agency system from scratch. Learn every element needed to offer AI agency services to clients.

---

## Introduction: What is an AI Agency?

An AI Agency is a system that leverages AI agents to deliver services to clients. Think of it like a digital agency where instead of human employees, you have AI agents that can:

- **Research** information from the web
- **Write** content (blogs, docs, marketing)
- **Develop** code and applications
- **Design** visuals and interfaces
- **Analyze** data and generate insights
- **Review** quality of work

### Why Build Your Own?

1. **Learning**: Understand how AI agent systems actually work
2. **Service Delivery**: Offer AI services to clients
3. **Automation**: Automate your own workflows
4. **Business**: Build a profitable AI agency

---

## Phase 1: Foundation - Building the Base

Think of Phase 1 as building the headquarters for our agency. Before hiring employees or taking clients, we need offices, desks, communication systems, and basic infrastructure. This phase creates the foundation everything else runs on.

### 1. Project Structure

```
ai_agency/
├── accounts/             # Account data
│   └── internal/       # Our first account
│       ├── config/     # Account settings
│       ├── memory/    # Agent memory (Phase 2)
│       ├── tasks/     # Task queue
│       └── output/   # Generated content
├── data/              # SQLite databases
│   ├── agents.db     # Agent config, history
│   ├── projects.db  # Client projects
│   ├── clients.db  # Client info
│   ├── knowledge.db # RAG content
│   └── meetings.db # Meeting records
├── agent_framework.py  # The agent system
└── tutorials/        # Output tutorials
```

### 2. Agent Roles (7 Total)

We hire 7 specialists, each with a specific job - like a company with manager, researchers, writers, developers, designers, analysts, and quality reviewers.

| Role | What They Do | Can Edit Tasks |
|------|-------------|-------------|
| **ORG** | Manager, coordinator | ✅ Yes |
| **RESEARCH** | Web research, data gathering | ❌ No |
| **WRITER** | Content creation | ❌ No |
| **DEVELOPER** | Code development | ❌ No |
| **DESIGNER** | Mockups, UI designs | ❌ No |
| **ANALYST** | Market research, trends | ❌ No |
| **REVIEWER** | Quality control | ❌ No |

### 3. Per-Agent Settings

Each agent is configured differently - researchers need accuracy, writers need creativity, developers need precision. This is like setting up each employee's work style.

| Setting | Description | Recommended Range |
|---------|-------------|----------------|
| **model** | AI model to use | llama3, gemma4:e2b |
| **temperature** | Randomness level | 0.1 - 1.0 |
| **max_tokens** | Max response size | 1024 - 8192 |
| **system_prompt** | Custom instructions | Custom |

**Temperature Guide:**

- **ORG**: 0.1-0.3 (manager - clear decisions)
- **RESEARCH**: 0.1-0.3 (accurate, factual)
- **WRITER**: 0.5-0.8 (creative, varied)
- **DEVELOPER**: 0.1-0.3 (precise, correct)
- **DESIGNER**: 0.6-0.9 (creative)
- **ANALYST**: 0.2-0.4 (analytical)
- **REVIEWER**: 0.3-0.5 (critical)

### 4. Capabilities (Phase 1)

These are the tools each agent can use - like giving employees web access, file editors, calculators, and database tools.

| Capability | What It Does | Setup Required |
|-----------|-------------|---------------|
| **Web Search** | Search the internet | DuckDuckGo API |
| **File Read/Write** | Access files | MCP server |
| **API Calls** | Call external services | API keys |
| **Command Run** | Execute commands | Security config |
| **Browser/Visit** | Navigate websites | MCP browser |
| **Database Query** | Query SQL databases | Connection |

**Note**: Memory capability will be added in Phase 2 (Mem0).

### 5. Agent Communication

We set up rules for how agents talk to each other - like an org chart showing who reports to whom and how information flows.

```
Communication Flow:
├── Agent A sends message to Agent B
├── Proposals go to ORG (manager)
├── ORG reviews and decides
├── Only ORG can edit current task
└── Meeting logs record everything
```

### 6. Task System (Priority + Dependencies)

We create a priority system for tasks, like a to-do list where urgent items are highlighted and some tasks must wait for others to complete first.

**Priority Levels:**
- **urgent (0)**: Immediate - drop everything
- **high (1)**: Today - end of day
- **normal (2)**: This week - regular work
- **low (3)**: Backlog - when time permits

**Dependencies:**
```
Task A (Priority: Urgent)
  ↓ completes
Task B (Priority: Normal, depends on A)
  ↓ completes  
Task C (Priority: Low)
```

### 7. Meetings Overview

We keep records of important conversations and decisions - like meeting notes that everyone can reference later.

| Field | Description |
|-------|-------------|
| **Timestamp** | When it happened |
| **Participants** | Who was involved |
| **Topic** | What was discussed |
| **Decisions** | What was decided |
| **Action items** | What needs to happen |
| **Duration** | How long it took |
| **Agent confidence** | How sure the agent is (0-1) |
| **Key findings** | Important insights |
| **Blocking issues** | Any problems |

---

## Services We're Preparing For

### 1. Chatbot from Files

Uses: **RAG + MCP + Mem0**

Creates a chatbot that answers from your documents. Can be integrated into:
- WhatsApp
- Telegram
- Website

### 2. React Website Creation

Tools required:
- **Node.js** - Runtime
- **React** - UI framework
- **Tailwind CSS** - Styling
- **Vite** - Build tool
- **Docker** - Containerization
- **ESLint** + **Prettier** - Code quality
- **Playwright** - Testing

Agent skills needed:
- Scaffold React app
- Configure Tailwind
- Create components
- Add routing
- Containerize with Docker

### 3. Lead Generation

- Web scraping for business data
- Competitor analysis
- Market research
- Data for cold calls/marketing

---

## Stage 2: What's Coming (After All Phases)

```
Advanced Features:
├── Authentication (per account)
├── Temporal scheduler (advanced)
├── Agent sync meetings
├── Designer: Logo creation
├── Image generation tools
└── Advanced integrations
```

---

## Summary: Phase 1 Enhanced

What we learned in Phase 1:

- [x] 7-agent framework with specific roles
- [x] Per-agent settings (model, temperature)
- [x] 6+ capabilities (web search, files, APIs, etc.)
- [x] Agent communication rules
- [x] Task priority system
- [x] Task dependencies
- [x] SQLite databases (5 separate)
- [x] Celery for scheduling
- [x] Meeting logs with details
- [x] Services we can offer

### File Structure After Phase 1
```
ai_agency/
├── accounts/
│   └── internal/
│       └── config/account.yaml
├── data/
│   └── meetings.json
├── agent_framework.py
└── tutorials/
    └── My_AI_Agency_Tutorial.md
```

### How to Reproduce This (Phase 1)
```bash
# Create project structure
mkdir -p ai_agency/accounts/internal/{config,memory,tasks,output}
mkdir -p ai_agency/data

# Create account config
cat > ai_agency/accounts/internal/config/account.yaml << 'EOF'
account_id: internal
name: AI Agency Internal
type: internal
agents:
  - name: org
  - name: research
  - name: writer
  - name: developer
  - name: designer
  - name: analyst
  - name: reviewer
EOF
```

---

## Phase 2: Memory System (Mem0)

Imagine hiring a new employee who has no memory - every conversation starts from zero, they forget your preferences, and repeat the same mistakes. That's what Phase 1 agents are like. Phase 2 gives each agent their own memory - they remember past conversations, client preferences, and what worked before.

### What is Mem0?

Mem0 is an intelligent memory layer for AI agents. It provides:

- **Persistent memory** between conversations
- **Per-agent memory** - each agent remembers separately
- **Semantic search** - find memories by meaning, not just keywords

### Installation

```bash
pip install mem0ai
```

### Embedding Models

These are the "brains" that help agents understand meaning - like giving each employee a brain that can connect concepts and find related information.

When using local AI (Ollama), you need embedding models to convert text into searchable vectors. Options include:

- `nomic-embed-text` (balanced, 137M params)
- `mxbai-embed-large` (higher accuracy, 334M params) - recommended
- `all-minilm` (faster, 23M params)

```bash
ollama pull mxbai-embed-large
```

### Per-Agent Memory

Each agent gets their own separate notebook - just like each employee has their own files and records that others shouldn't access.

| Agent | Memory ID | Purpose |
|-------|----------|---------|
| ORG | org | Manager decisions, task history |
| RESEARCH | research | Research findings |
| WRITER | writer | Content style, preferences |
| DEVELOPER | developer | Code patterns, solutions |
| DESIGNER | designer | Design preferences |
| ANALYST | analyst | Analysis patterns |
| REVIEWER | reviewer | Quality standards |

### Using Memory

```python
from memory import AgentMemory

# Get memory for an agent
memory = AgentMemory(agent_id="research")

# Add a memory
memory.add("User prefers short summaries")

# Search memories
results = memory.search("user preferences")
```

---

## Summary: Phase 2 Complete

- [x] Installed mem0ai
- [x] Configured Ollama for memory
- [x] Each agent has separate memory
- [x] Downloaded mxbai-embed-large for embeddings
- [x] Created memory.py module

### File Structure After Phase 2
```
ai_agency/
├── accounts/
│   └── internal/
│       └── config/account.yaml
├── data/
│   └── meetings.json
├── agent_framework.py
├── memory.py                  # NEW: Mem0 integration
└── tutorials/
    └── My_AI_Agency_Tutorial.md
```

### How to Reproduce This (Phase 2)
```bash
# Install Mem0
pip install mem0ai

# Download embedding model
ollama pull mxbai-embed-large

# Create memory module
cat > ai_agency/memory.py << 'EOF'
# (Copy from memory.py in system)
EOF
```

---

## Phase 3: Skills Framework

Now that our agents have memory, it's time to train them with specific skills. Just like a company trains employees on different tasks - some do accounting, others do sales - our agents learn specialized capabilities. We download pre-made skill packages (like training courses) and teach agents how to use them.

### Skills Options - Comparison

### Skills Options - Comparison

| Source | # Skills | Cost | Setup | Best For |
|--------|----------|------|-------|---------|
| **a-i--skills** | 101 | Free | Medium | Full library, many categories |
| **Anthropic Skills** | 24 | Free | Easy | Built-in, backup |
| **SupaSkills** | 1,144 | Paid API | Easy | Highest quality (requires API key) |

### What Are Skills?

Skills are like training manuals or standard operating procedures - detailed instructions on how to do specific tasks properly.

- `SKILL.md` - Instructions (required)
- `metadata` - Name, description
- `resources/` - Templates, examples
- `scripts/` - Helper scripts

### Organization

```
skills/
├── a-i--skills/
│   ├── creative/       (art, writing, design)
│   ├── data/          (research, analysis)
│   ├── development/   (coding, APIs)
│   ├── documentation/  (docs, manuals)
│   └── ... (12 categories)
├── anthropic/
│   └── document/       (PDF, Word, Excel)
└── skill_runner.py     (execution engine)
```

### Initial Skills Configured

| Agent | Primary Skill | Secondary Skill | Why |
|-------|-------------|---------------|-----|
| **RESEARCH** | market-gap-analysis | data-storytelling-analyst | Identifies trends + converts to narratives |
| **WRITER** | creative-writing-craft | grant-proposal-writer | Storytelling + structured writing |
| **DEVELOPER** | python-packaging-patterns | api-design-patterns | Packaging + API best practices |
| **DESIGNER** | UI_UX_MAX_PRO | - | Industry-specific design (see Phase 8) |

### Recommended Skills by Agent

#### RESEARCH Agent
```
┌─────────────────────────────────────────────────────────────┐
│  Primary: market-gap-analysis                          │
│  - Identifies market opportunities                  │
│  - Analyzes competitor gaps                        │
│  - Finds trends and patterns                      │
│                                                      │
│  Secondary: data-storytelling-analyst              │
│  - Converts data to compelling narratives          │
│  - Creates charts and visualizations              │
└─────────────────────────────────────────────────────────────┘
```

#### WRITER Agent
```
┌─────────────────────────────────────────────────────────────┐
│  Primary: creative-writing-craft                     │
│  - Headlines and hooks                             │
│  - Storytelling techniques                     │
│  - Engagement optimization                      │
│                                                      │
│  Secondary: grant-proposal-writer               │
│  - Structured writing                         │
│  - Clear communication                       │
│  - Persuasive arguments                         │
└─────────────────────────────────────────────────────────────┘
```

#### DEVELOPER Agent
```
┌─────────────────────────────────────────────────────────────┐
│  Primary: python-packaging-patterns                │
│  - Package structure                            │
│  - Distribution best practices              │
│  - pip / conda packaging                   │
│                                                      │
│  Secondary: api-design-patterns              │
│  - REST API design                        │
│  - Endpoint structure                     │
│  - Authentication patterns               │
└─────────────────────────────────────────────────────────────┘
```

#### DESIGNER Agent (Phase 8)
```
┌─────────────────────────────────────────────────────────────┐
│  Primary: UI_UX_MAX_PRO                              │
│  - 67 UI Styles (Glassmorphism, Brutalism, etc.)   │
│  - 161 Industry-specific color palettes           │
│  - Design System Generator (v2.0)               │
│  - Works with Claude, Cursor, Windsurf              │
│                                                      │
│  Stats: 68,804 GitHub stars, 28,000+ weekly installs │
└─────────────────────────────────────────────────────────────┘
```

### Using Skills

```python
from skill_runner import get_runner, CONFIGURED_SKILLS

# Get runner
runner = get_runner()

# List all available
skills = runner.list_skills("a-i--skills")
for category, skill_list in skills.items():
    print(f"{category}: {len(skill_list)} skills")

# Read a specific skill
skill_content = runner.read_skill("a-i--skills", "data", "market-gap-analysis")
```

### Backup Plan

If a-i--skills don't perform well, we can fall back to Anthropic Skills (24 built-in skills).

---

## Summary: Phase 3 Complete

- [x] Downloaded a-i--skills (101 skills)
- [x] Downloaded Anthropic Skills (24 skills)
- [x] Organized by category
- [x] Configured 3 initial skills
- [x] Created skill_runner.py
- [ ] SupaSkills - Requires paid API (optional, not downloaded)

### File Structure After Phase 3
```
ai_agency/
├── accounts/
│   └── internal/
│       └── config/account.yaml
├── data/
│   └── meetings.json
├── agent_framework.py
├── memory.py
├── skill_runner.py           # NEW: Skills execution
└── tutorials/
    └── My_AI_Agency_Tutorial.md
```

### How to Reproduce This (Phase 3)
```bash
# Create skills directory
mkdir -p ai_agency/skills

# Clone a-i--skills (101 skills)
cd ai_agency/skills
git clone https://github.com/organvm-iv-taxis/a-i--skills.git a-i--skills

# Clone Anthropic Skills (24 skills)
git clone https://github.com/anthropics/skills.git anthropic

# Create skill runner
cat > ai_agency/skill_runner.py << 'EOF'
# (Copy from skill_runner.py in system)
EOF
```

---

## Phase 4: RAG + MCP Integration

Now our agents have skills, but they need access to information and tools. Think of this as giving our team:
- A reference library (knowledge base) they can search
- External tools like calculators, web browsers, and database access

### What is RAG?

### What is RAG?

RAG (Retrieval-Augmented Generation) gives agents access to external knowledge:
- **Knowledge bases** - Documents, docs, guides per agent
- **Vector stores** - Fast semantic search
- **Retrieval** - Find relevant information quickly

### Per-Agent RAG Pipelines ✅

Each agent gets their own reference library - like giving researchers a library, writers a style guide, and developers an API documentation set.

```
knowledge/
├── researcher/     → Chroma vector store
├── writer/        → Chroma vector store
├── developer/     → Chroma vector store
├── designer/      → Chroma vector store
└── analyst/      → Chroma vector store
```

### Knowledge Base Sources by Agent

| Agent | Main Source | Backup | Cost |
|-------|-------------|--------|------|
| **DEVELOPER** | AgentsKB (39,827 Q&As) | One Knowledge (on request) | FREE |
| **RESEARCH** | Web Search (DuckDuckGo) | Consensus (on request) | FREE |
| **WRITER** | Web Search + Custom KB | - | FREE |
| **DESIGNER** | Web Search | - | FREE |
| **ANALYST** | Web Search | - | FREE |

### AgentsKB Details (DEVELOPER Agent)
- **API**: `https://agentskb-api.agentskb.com/api/free`
- **Authentication**: None required (free)
- **Coverage**: 244 technical domains, 39,827 Q&As
- **Documentation**: https://agentskb.com/docs/

### Technology Stack

| Component | Choice | Why |
|-----------|--------|-----|
| **Vector Store** | Chroma (Phase 4) → Qdrant (Stage 2) | Free, local, simple |
| **Embeddings** | mxbai-embed-large | High accuracy |
| **Chunking** | Fixed 512 chars (Phase 4) → Semantic (Stage 2) | Simple start |

### RAG Chunking Explained

#### What is Chunking?

When you add documents to the knowledge base, you can't add entire books at once. You need to split them into smaller pieces called "chunks" that the AI can search and understand.

#### Chunking Methods

**Method 1: Fixed Size (512 characters) - Phase 4**
```
Original Text:
"The quick brown fox jumps over the lazy dog. This classic pangram contains
every letter of the alphabet. It's commonly used for font testing and
displaying examples."

Chunks (512 chars):
Chunk 1: "The quick brown fox jumps over the lazy dog. This classic pangram contains..."
Chunk 2: "...every letter of the alphabet. It's commonly used for font..."
```

**Method 2: Semantic (Stage 2)**
```
Original Text:
"## Introduction
Welcome to our AI Agency. This system helps businesses automate tasks.

## Features
Our platform offers:
1. Research automation
2. Content generation
3. Code development"

Semantic Chunks:
Chunk 1: "## Introduction\nWelcome to our AI Agency..."
Chunk 2: "## Features\nOur platform offers: 1. Research..."
```

#### RAG Search Example

```
YOU: "How do I create a new agent?"

1. Your query is converted to a vector
2. Chroma searches for similar chunks
3. Returns: "To create a new agent, use AgentFactory..."
4. AI combines with its knowledge
5. Response: "Use the AgentFactory.create_agent() method..."
```

#### Adding Documents to RAG

```python
from rag_pipeline import RAGPipeline

# Create pipeline for developer
rag = RAGPipeline("developer")

# Add a document
rag.add_document(
    document_id="doc_api_001",
    content="REST API Best Practices: Use nouns, not verbs in endpoints...",
    metadata={"source": "api-guide", "topic": "api-design"}
)

# Search for relevant info
results = rag.search("How to design REST APIs?", n_results=3)

# Results include matching chunks with scores
for doc in results:
    print(f"Content: {doc['content']}")
    print(f"Relevance: {1 - doc['distance']:.0%}")
```

### MCP Servers (4 Total)

| # | MCP Server | Purpose | Cost |
|---|------------|---------|------|
| 1 | **File System** | Read/write files, run commands | FREE |
| 2 | **Web Search** | DuckDuckGo search | FREE |
| 3 | **GitHub** | Repository management | Later |
| 4 | **Database** | Query SQLite | FREE |

### MCP - What It Is & Why It Matters

#### The Core Problem MCP Solves

**Before MCP**: Every AI tool had its own way to connect to external tools. Claude had its own integration, Cursor had another, OpenAI had another. If you wanted the same file-reading capability across tools, you had to build it 3 different times.

**After MCP**: Like USB-C for devices. One standard that works everywhere.

#### MCP Explained Simply

```
┌─────────────────────────────────────────────────────────────┐
│  MCP = Model Context Protocol                              │
│  A STANDARD way for AI to connect to external tools         │
├─────────────────────────────────────────────────────────────┤
│  Like USB-C:                                            │
│  • One cable works for all devices                       │
│  • Camera, phone, computer all use same port            │
│  • No need 10 different adapters                     │
│                                                        │
│  MCP does the same for AI:                               │
│  • One server works for all AI tools                    │
│  • Claude, Cursor, Windsurf all use same tools          │
│  • Build once, use everywhere                         │
└─────────────────────────────────────────────────────────────┘
```

#### What MCP Servers Do (Real Examples)

| Server | What It Does | Real Example |
|--------|------------|------------|
| **File System** | Read/write files on your computer | "Read my config.yaml" → server reads it |
| **Web Search** | Search the internet | "Find recent AI news" → server searches |
| **GitHub** | Manage repos, issues, PRs | "Create issue for bug fix" → server creates |
| **Database** | Query SQL databases | "Show my sales data" → server queries |
| **Slack** | Send messages, list channels | "Post to #dev-team" → server posts |

#### How It Works (Conversation Flow)

```
┌─────────────────────────────────────────────────────────────┐
│  YOU: "What's in my project config file?"               │
│                                                        │
│  1. Your message goes to Claude                        │
│  2. Claude sees it needs to READ a file                │
│  3. Claude calls MCP file_system server with "read_file" │
│  4. Server reads /project/config.yaml                │
│  5. Server returns content to Claude                 │
│  6. Claude summarizes: "It's a Node.js project..." │
└─────────────────────────────────────────────────────────────┘
```

#### MCP Practice Examples

**Example 1: File System Server**
```
YOU: "Show me my package.json dependencies"
RESULT: Claude uses file_system MCP → reads package.json
        Returns: {"name": "ai-agency", "dependencies": {"react": "^18.0.0"}}

YOU: "Create a backup of config.yaml"
RESULT: Claude uses file_system MCP → copies file
        Returns: "Backup created: config.yaml.backup"
```

**Example 2: Web Search Server**
```
YOU: "Find AI agent news from the last 24 hours"
RESULT: Claude uses web_search MCP → searches news
        Returns: [Article(title, url, summary), ...]

YOU: "What's the latest on Claude MCP updates?"
RESULT: Claude uses web_search MCP → searches
        Returns: Recent MCP changelog and news
```

**Example 3: Database Server**
```
YOU: "Show my usage for today"
RESULT: Claude uses database MCP → queries SQLite
        Returns: {"tasks_completed": 5, "time_spent": "2h 30m"}

YOU: "Count all active clients"
RESULT: Claude uses database MCP → queries
        Returns: {"total_clients": 12}
```

**Example 4: GitHub Server (Stage 2)**
```
YOU: "Create issue for the login bug"
RESULT: Claude uses github MCP → creates issue
        Returns: "Issue created: #42 - Login not working"

YOU: "List recent pull requests"
RESULT: Claude uses github MCP → lists PRs
        Returns: [PR(title, status, author), ...]
```

**Example 5: Combined Workflow**
```
YOU: "Research AI trends, save to file, and post to GitHub"
RESULT: Claude:
  1. Uses web_search → searches AI trends
  2. Uses file_system → saves to trends.md
  3. Uses github → creates PR with trends.md
  Returns: "Saved to trends.md, PR created: #43"
```

#### MCP in Our AI Agency

Our agents use MCP servers to:

| Agent | MCP Server | Task |
|-------|-----------|------|
| **RESEARCH** | web_search | Find news, articles, data |
| **WRITER** | file_system | Read research, save articles |
| **DEVELOPER** | file_system, database | Read specs, query issues |
| **DESIGNER** | file_system | Save mockups, read assets |
| **ORG** | github, database | Track progress, manage |

#### MCP Configuration

```
mcp_servers/
├── config.yaml         # Main configuration
├── filesystem.py     # File read/write server
├── web_search.py     # DuckDuckGo server
├── database.py       # SQLite query server
└── github.py         # GitHub (Stage 2)
```

#### Testing MCP Servers

```bash
# After connecting MCP server in Claude Desktop:
> "Read my project README and tell me what it does"
# Should work automatically if file system MCP is enabled

# Test web search:
> "Find recent articles about AI agents"
# Should return list of articles with summaries
```

---

## Summary: Phase 4 Complete

- [x] Installed ChromaDB
- [x] Installed sentence-transformers
- [x] Planned per-agent RAG pipelines
- [x] Selected knowledge base sources (all free)
- [x] Configured MCP servers (2 of 4)
- [ ] GitHub MCP (Stage 2)

### File Structure After Phase 4
```
ai_agency/
├── accounts/
│   └── internal/
│       └── config/account.yaml
├── data/
│   └── meetings.json
├── agent_framework.py
├── memory.py
├── skill_runner.py
├── knowledge/                 # NEW: Per-agent RAG
│   ├── researcher/
│   ├── writer/
│   ├── developer/
│   ├── designer/
│   └── analyst/
├── mcp_servers/
│   └── config.yaml
└── tutorials/
    └── My_AI_Agency_Tutorial.md
```

### How to Reproduce This (Phase 4)
```bash
# Install ChromaDB and sentence-transformers
pip3 install chromadb sentence-transformers

# Create knowledge base directories
mkdir -p ai_agency/knowledge/{researcher,writer,developer,designer,analyst}

# Create MCP config
mkdir -p ai_agency/mcp_servers
cat > ai_agency/mcp_servers/config.yaml << 'EOF'
mcp_servers:
  file_system:
    enabled: true
  web_search:
    provider: duckduckgo
    enabled: true
  database:
    type: sqlite
    enabled: true
EOF

# Create RAG pipeline
cat > ai_agency/rag_pipeline.py << 'EOF'
# (Copy from rag_pipeline.py in system)
EOF
```

---

## Phase 5: Orchestration

In this phase, we teach our agents how to work together - like a real team where everyone knows their role and how to collaborate. Just like a company has managers, specialists, and teams that coordinate, our AI agents learn to communicate and complete complex tasks together.

### Why Orchestration Matters

Think about when a client asks for something complex, like "Build me a marketing website." This requires many steps: research the market, design the look, write the content, build the code, and check quality. No single person does all of this - a team works together. Orchestration is how our AI agents learn to work as that team.

### What We'll Build

1. **Router** - Like a receptionist who directs visitors to the right person
2. **Supervisor** - Like a manager who coordinates specialists
3. **Pre-built Workflows** - Like standard processes the team follows
4. **Human-in-the-Loop** - Like a supervisor who reviews important decisions
5. **Task Queue Extension** - Like a smarter to-do list that manages priorities

### Orchestration Patterns

Think of these like different ways teams can work:

| Pattern | Real-Life Example | When to Use |
|---------|------------------|-------------|
| **Router** | Receptionist directing visitors | Simple, single-task requests |
| **Supervisor** | Manager coordinating specialists | Complex, multi-step projects |
| **Sequential** | Assembly line | One step after another |
| **Parallel** | Team working simultaneously | Multiple independent tasks |

### 5.1 Router (The Receptionist)

The router is the first point of contact - it listens to what the client wants and directs it to the right agent.

```yaml
# router_config.yaml
router:
  rules:
    - name: research
      primary: [research, find, gather, investigate]
      secondary: [info, data, sources]
      agent: RESEARCH
    - name: writer
      primary: [write, create, draft, blog, article]
      secondary: [content, post, story]
      agent: WRITER
    - name: developer
      primary: [code, build, develop, function, program]
      secondary: [app, website, feature]
      agent: DEVELOPER
    - name: designer
      primary: [design, mockup, ui, interface, visual]
      secondary: [wireframe, mock]
      agent: DESIGNER
    - name: analyst
      primary: [analyze, analysis, market, trend, report]
      secondary: [statistics, insights]
      agent: ANALYST
    - name: reviewer
      primary: [review, check, audit, quality, test]
      secondary: [examine, assess]
      agent: REVIEWER
    - name: supervisor
      primary: [complex, project, build website, everything]
      agent: ORG
```

**Industry Keywords**: We also add industry-specific routing (healthcare→RESEARCH, marketing→WRITER, etc.)

> **Note**: Router rules will be reviewed and tuned in Stage 2 based on real usage.

### 5.2 Supervisor Pattern (The Manager)

The ORG agent becomes the supervisor - it coordinates complex tasks by breaking them into steps and assigning the right agents.

### 5.3 Pre-Built Workflows (Standard Processes)

#### Scenario 1: Quick Research
```
REQUEST → ROUTER → RESEARCH → ORG → Client
```

#### Scenario 2: Write Article with Design
```
REQUEST → RESEARCH → WRITER → DESIGNER → REVIEWER → ORG
```

#### Scenario 3: Build Feature
```
REQUEST → ORG → DEVELOPER + REVIEWER (parallel) → ORG
```

#### Scenario 4: Deep Analysis
```
REQUEST → RESEARCH + ANALYST (parallel) → WRITER → ORG
```

#### Scenario 5: Full Project
```
ORG orchestrates: RESEARCH → DESIGNER → DEVELOPER → WRITER → REVIEWER → Client
```

### 5.4 Human-in-the-Loop (The Safety Net)

Just like a company has levels of approval:

| Level | Name | What Happens |
|-------|------|-------------|
| 1 | Full Control | Everything requires approval |
| 2 | Guided | Simple tasks auto-route |
| 3 | Supervised | Routine tasks auto-approve |
| 4 | Trusted | Verified workflows auto-complete |
| 5 | Autonomous | Full independence |

### 5.5 Task Queue Extension

```
Celery Task Queue:
├── main (1 at a time)
├── cron (scheduled)
├── urgent (priority)
└── agent_{name} (per-agent)
```

---

## Summary: Phase 5 Complete

- [x] Router (Hybrid - rule-based + keywords + LLM)
- [x] Supervisor Pattern (ORG as coordinator)
- [x] Pre-built Workflows (5 scenarios)
- [x] Human-in-the-Loop (5 levels + metrics)
- [x] Task Queue Extension (lanes + retry)

### File Structure After Phase 5
```
ai_agency/
├── orchestration/               # NEW: Phase 5
│   ├── router.py
│   ├── supervisor.py
│   ├── scenarios/
│   │   ├── quick_research.py
│   │   ├── write_article.py
│   │   ├── build_feature.py
│   │   ├── deep_analysis.py
│   │   └── full_project.py
│   ├── readiness.py
│   └── task_queue.py
```

### How to Reproduce This (Phase 5)
```bash
# Create orchestration module
mkdir -p ai_agency/orchestration/scenarios

# Create router
cat > ai_agency/orchestration/router.py << 'EOF'
# (Copy from orchestration/router.py in system)
EOF

# Create supervisor
cat > ai_agency/orchestration/supervisor.py << 'EOF'
# (Copy from orchestration/supervisor.py in system)
EOF

# Create scenarios
for scenario in quick_research write_article build_feature deep_analysis full_project; do
  cat > ai_agency/orchestration/scenarios/${scenario}.py << 'EOF'
# Scenario for $scenario
EOF
done
```

---

## Phase 6: Multi-Client Expansion

When you're ready to offer your AI agency service to multiple clients, you need to make sure each client can only see their own data. Think of it like an office building - each client has their own floor with locked doors, but everyone shares the building infrastructure (elevators, electricity).

### Why Multi-Client Matters

Running a single agency for yourself is one thing. When clients pay you to use the system, they expect privacy. This phase transforms our single-tenant system into a multi-tenant one where data is strictly isolated per client.

### Critical Rule

Every door must be checked. Every query, every file access, every agent interaction MUST include client_id verification. One mistake = someone walks into the wrong office = catastrophic data leak.

### What We Build

1. **Database Schema** - All tables get client_id column
2. **Row-Level Security** - Every query filters by client_id
3. **ClientManager** - Create and manage client accounts
4. **Isolation Middleware** - Ensure client_id on all operations
5. **Usage Tracking** - Track per-client metrics

### Database Schema

Every table now includes client_id:

```sql
accounts (id, name, type, status, created_at)
tasks (id, client_id, title, status, priority, ...)
meetings (id, client_id, topic, decisions, ...)
memory (id, client_id, agent_id, content, ...)
knowledge (id, client_id, agent_id, content, ...)
```

### Isolation Implementation

```python
# Every query MUST include client_id
with IsolatedQuery(client_id) as q:
    results = q.execute("SELECT * FROM tasks")
```

### Client Creation Flow

1. Create client account → pending status
2. Setup default agents for client
3. Activate account
4. Client starts submitting tasks

### Stage 2 (Later)

- Authentication (passwords)
- Self-service signup
- Client portal UI
- Usage-based billing

---

## Summary: Phase 6 Complete

- [x] Multi-tenant database schema
- [x] Row-level security (client_id filter)
- [x] ClientManager
- [x] IsolatedQuery middleware
- [x] Usage tracking

### File Structure After Phase 6
```
ai_agency/
├── multi_client.py              # NEW: Phase 6
├── orchestration/
├── knowledge/
├── mcp_servers/
├── accounts/
├── data/
└── skills/
```

### How to Reproduce This (Phase 6)
```bash
# Create multi-client module
cat > ai_agency/multi_client.py << 'EOF'
# (Copy from multi_client.py in system)
EOF

# Create accounts manager
cat > ai_agency/accounts_manager.py << 'EOF'
# (Copy from accounts_manager.py in system)
EOF

# Initialize database
python3 ai_agency/multi_client.py
```

---

## Phase 7: Integration Layer (UNIFY)

Now we connect all the pieces together like assembling a car - we have all the parts (engine, wheels, body) but they need to be connected so they work as one unified machine. This phase creates the integration layer that makes everything work together seamlessly.

### Why Integration Matters

Imagine building a house with separate teams: framers, electricians, plumbers, and roofers each do their job, but without coordination, the lights won't connect to the power, the pipes won't fit the fixtures. Integration is the blueprint that ensures every team works in harmony. Without it, our agents and modules are isolated islands that can't collaborate effectively.

### The Problem We Solve

We have all these separate components that work individually but don't communicate:
- Agent Framework (7 agents ready to work)
- Memory System (each agent remembers things)
- Skills (agents know how to do tasks)
- RAG Knowledge (agents can search information)
- Orchestration (agents can work together)
- Multi-Client (clients are isolated)

But how do they all connect? A task comes in - what happens? Who talks to whom? Integration layer answers all of that.

### What We Build

1. **AgencyIntegrator** - The central hub connecting all modules
2. **Unified Configuration** - Single config file for everything
3. **CLI Entry Point** - One command to run the whole system
4. **Task Execution Flow** - How data flows through all layers
5. **Client Isolation** - Security maintained throughout

### Integration Architecture

Think of it like a corporate intranet connecting all departments:

```
┌─────────────────────────────────────────────────────────────┐
│                     MAIN.PY (CLI)                          │
│                  Entry point for everything               │
└─────────────────────────────┬─────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  AgencyIntegrator                           │
│         (The central nervous system of the agency)         │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │   CLIENT     │  │   ORCHESTR   │  │     AGENTS     │  │
│  │   LAYER      │  │    LAYER     │  │    LAYER       │  │
│  │              │  │              │  │                │  │
│  │ multi_client │←→│ router.py   │←→│ agent_fw.py   │  │
│  │ client_mgr   │  │ supervisor  │  │ 7 agents      │  │
│  └──────────────┘  └──────────────┘  └────────────────┘  │
│         ↑                  ↑                  ↑           │
│         └──────────────────┼──────────────────┘           │
│                            ↓                                │
│              ┌─────────────────────────┐                  │
│              │      MEMORY + RAG        │                  │
│              │  (Context & Knowledge)   │                  │
│              └─────────────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

### The Task Execution Flow

Here's what happens when a client submits a task:

```
1. CLIENT LAYER
   ↓
   Task arrives with client_id
   ↓
2. ROUTER
   ↓
   Analyze task → Determine which agents needed
   ↓
3. MEMORY LAYER
   ↓
   For each agent: retrieve past interactions
   "User prefers short summaries"
   ↓
4. RAG LAYER
   ↓
   Search knowledge bases → Get relevant docs
   AgentsKB for developers, web for writers
   ↓
5. AGENT LAYER
   ↓
   Execute task with context from memory + RAG
   Multiple agents work together if needed
   ↓
6. ORCHESTRATION
   ↓
   Supervisor coordinates, ensures quality
   Human-in-the-loop if required
   ↓
7. STORE RESULTS
   ↓
   Save to memory for future reference
   Track usage metrics
   ↓
8. RETURN TO CLIENT
```

### Unified Configuration

Instead of having settings scattered everywhere, we create one central config:

```yaml
# config.yaml - The single source of truth
version: "1.0.0"
name: "AI Agency System"

client:
  default: "internal"
  isolation: true

agents:
  team_size: 7
  roles:
    - name: "org"
      model: "llama3"
      temperature: 0.2
    - name: "research"
      model: "llama3"
      temperature: 0.2

memory:
  enabled: true
  provider: "ollama"

rag:
  enabled: true
  chunk_size: 512

orchestration:
  mode: "supervisor"
  human_oversight: "medium"
```

### Using the Integration Layer

```python
from integrator import AgencyIntegrator

# Create agency for a client
agency = AgencyIntegrator(client_id="client_123")

# Execute any task - everything connects automatically
result = agency.execute("Research AI trends for 2026")

# Results include:
# - Which agents were used
# - Memory context retrieved
# - RAG knowledge found
# - Execution results
# - Usage tracked
```

### Quick Functions

For common tasks, we have shortcuts:

```python
# Quick research
result = quick_research("Python web frameworks", client_id="client_123")

# Quick writing
result = quick_write("Blog post about AI", client_id="client_123")

# Quick development
result = quick_develop("REST API endpoint", client_id="client_123")
```

### CLI Usage

Run the whole system from command line:

```bash
# Check status
python3 main.py --client internal --status

# Execute a task
python3 main.py --client internal --task "Research AI trends"

# Quick research
python3 main.py --client internal --research "Python frameworks"

# Interactive mode
python3 main.py --client internal --interactive
```

### Why This Is Powerful

Before integration, each component was like a separate tool in a toolbox. Now they're all connected into one system that:

- **Remembers everything** - Memory layer stores and retrieves context
- **Knows everything** - RAG layer provides knowledge on demand
- **Works as a team** - Orchestration coordinates multiple agents
- **Stays secure** - Client isolation on every operation
- **Tracks everything** - Usage metrics for billing and optimization

---

## Summary: Phase 7 Complete

- [x] AgencyIntegrator - Central hub connecting all modules
- [x] Unified config.yaml - Single source of truth
- [x] CLI entry point (main.py) - One command to run everything
- [x] Task execution flow - All layers work together
- [x] Client isolation maintained - Security throughout

### File Structure After Phase 7
```
ai_agency/
├── integrator.py              # NEW: Phase 7 - Integration hub
├── config.yaml              # NEW: Phase 7 - Unified config
├── main.py                  # NEW: Phase 7 - CLI entry point
├── agent_framework.py       # Phase 1: 7 agents
├── memory.py               # Phase 2: Mem0
├── skill_runner.py         # Phase 3: Skills
├── rag_pipeline.py         # Phase 4: RAG
├── mcp_integration.py     # Phase 4: MCP
├── knowledge_manager.py   # Phase 4: Knowledge
├── multi_client.py        # Phase 6: Multi-tenant
├── accounts_manager.py    # Phase 6: Accounts
├── orchestration/         # Phase 5: Workflows
│   ├── router.py
│   ├── supervisor.py
│   ├── readiness.py
│   ├── task_queue.py
│   └── scenarios/
├── knowledge/             # Phase 4: Per-agent RAG
├── mcp_servers/          # Phase 4: MCP config
├── accounts/             # Phase 1: Account data
├── data/                 # Phase 1: Databases
└── skills/               # Phase 3: Skill libraries
```

### How to Reproduce This (Phase 7)
```bash
# Create integration layer
cat > ai_agency/integrator.py << 'EOF'
# (Copy from integrator.py in system)
EOF

# Create unified config
cat > ai_agency/config.yaml << 'EOF'
# (Copy from config.yaml in system)
EOF

# Create CLI entry point
cat > ai_agency/main.py << 'EOF'
# (Copy from main.py in system)
EOF

# Test the integration
cd ai_agency
python3 main.py --status
```

---

## System Complete - All 8 Phases

Congratulations! You've built a complete AI Agency system:

| Phase | Component | What It Does |
|-------|-----------|-------------|
| 1 | Foundation | 7 agents with roles, capabilities, task system |
| 2 | Memory | Each agent remembers past interactions |
| 3 | Skills | Agents trained with specialized skills |
| 4 | RAG + MCP | Knowledge bases, MCP servers, chunking |
| 5 | Orchestration | Teams work together on complex tasks |
| 6 | Multi-Client | Multiple clients, data isolation |
| 7 | Integration | Everything connected and working as one |
| 8 | Website Creation | UI_UX_MAX_PRO for professional designs |

### Additional Features

| Feature | What It Does |
|---------|-------------|
| **MCP Servers** | 3 servers (filesystem, web_search, database) |
| **Approval System** | Streamlit page with Approve/Reject buttons |
| **Tests** | pytest framework with 5 test files |
| **Daily News Workflow** | Flask API + Admin panel for AI news |

---

## Stage 2: Daily News Workflow

The Daily News Workflow is an incremental system for creating AI news articles through a step-by-step approval process.

### What It Does

```
┌─────────────────────────────────────────────────────────────┐
│  DAILY NEWS WORKFLOW                                     │
│  RESEARCH → TITLE + SUMMARY → ARTICLE → PUBLISH           │
├─────────────────────────────────────────────────────────────┤
│                                                        │
│  1. YOU paste URL to AI news article                  │
│     Example: https://nvidianews.nvidia.com/news/ai-agents│
│                                                        │
│  2. RESEARCHER fetches URL, generates:                  │
│     • TITLE: "NVIDIA AI Agents SDK"                      │
│     • SUMMARY: One paragraph summary                    │
│                                                        │
│  3. YOU approve/reject summary                        │
│     If reject → Try different URL                       │
│     If approve → Continue                             │
│                                                        │
│  4. WRITER generates full article:                       │
│     • Headline, Overview                              │
│     • 3 Body paragraphs                              │
│                                                        │
│  5. YOU approve/reject article                        │
│     If reject → WRITER revises                        │
│     If approve → Publish                             │
│                                                        │
│  6. PUBLISH to website                                │
│     Article appears on http://localhost:5001         │
│                                                        │
└─────────────────────────────────────────────────────────────┘
```

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  SERVER LAYER (Flask - Port 5001)                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ /admin      │  │ /news       │  │ /api/*          │  │
│  │ (HTML UI)   │  │ (website)   │  │ (JSON API)      │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
│         │                │               │               │
│         └────────────────┼───────────────┘               │
│                        ↓                                  │
│              ┌─────────────────────┐                   │
│              │  SERVICES           │                   │
│              │  • ResearchService │                   │
│              │  • WriterService    │                   │
│              │  • PublisherService │                   │
│              └─────────────────────┘                   │
│                        │                               │
│                        ↓                               │
│              ┌─────────────────────┐                   │
│              │  Ollama (Local AI)  │                   │
│              │  llama3 model      │                   │
│              └─────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

### File Structure

```
ai_agency/
├── server/
│   ├── app.py              # Flask application (port 5001)
│   ├── routes/
│   │   ├── news.py        # GET /api/news
│   │   ├── workflow.py   # POST /api/research, /api/write
│   │   └── admin.py      # POST /api/approve, /api/publish
│   ├── services/
│   │   ├── research.py    # Fetch URL + Title + Summary
│   │   ├── writer.py     # Generate article
│   │   └── publisher.py  # Save + update website
│   └── templates/
│       ├── base.html     # Bootstrap base
│       ├── index.html   # News website
│       ├── admin.html   # Workflow admin panel
│       └── article.html # Single article view
└── data/
    ├── articles.json  # Published articles
    └── pending.json   # Pending approvals
```

### API Endpoints

| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| `/api/news` | GET | Get all articles | - | `[{"headline", "overview", ...}]` |
| `/api/research` | POST | Fetch URL, generate title + summary | `{"url": "..."}` | `{"title", "summary", "id"}` |
| `/api/write` | POST | Write article from summary | `{"summary", "url", "title"}` | `{"headline", "overview", ...}` |
| `/api/workflow/complete` | POST | Publish article | `{"article_id": "..."}` | `{"success": true}` |

### How to Run

```bash
# Terminal 1: Start Flask server
cd ai_agency
python3 -m server.app
# Runs on http://localhost:5001

# Terminal 2: (Optional) Start Streamlit
python3 -m streamlit run app.py --server.port 8502
# Runs on http://localhost:8502
```

### Workflow Steps

1. **Open Admin Panel**: http://localhost:5001/admin
2. **Paste URL**: https://nvidianews.nvidia.com/news/ai-agents
3. **Click "Fetch & Summarize"**: AI generates title + summary
4. **Review**: Check if title/summary is good
5. **Click "Approve & Write Article"**: Writer generates full article
6. **Review Article**: Check headline, overview, paragraphs
7. **Click "Approve & Publish"**: Article appears on website
8. **View**: http://localhost:5001

### Benefits

| Benefit | Explanation |
|---------|-------------|
| **Incremental** | Test each step before moving forward |
| **Human-in-the-Loop** | You approve every step |
| **Title Generation** | Title generated in research, carried through |
| **Reusable** | Can use for any AI news URL |
| **Local AI** | Uses Ollama (no API costs) |

### What's Next - Stage 2

The system is ready for beta testing. Stage 2 adds:
- Authentication (passwords, logins)
- Client portal (self-service)
- Temporal scheduler (better than Celery)
- UI_UX_MAX_PRO for DESIGNER
- Image generation for DESIGNER
- GitHub MCP integration

---

*Tutorial Version 4.0 - Daily News Workflow Added*