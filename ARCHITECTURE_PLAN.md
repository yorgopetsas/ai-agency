# AI Agency System - Comprehensive Architecture Plan

## Main Goal
Build an AI agency system to learn how such systems are built (elements, architecture) to offer as a service to clients.

---

## All Elements to Learn & Build

```
┌─────────────────────────────────────────────────────────────┐
│                    AI AGENCY SYSTEM                        │
├─────────────────────────────────────────────────────────────┤
│  CORE ELEMENTS                                             │
│  ├── Account Management (isolation, auth)                  │
│  ├── Agent Framework (base class, types)                   │
│  ├── Memory System (Mem0 → upgrade later)                  │
│  ├── Skills Framework (a-i--skills, configure, orchestrate)│
│  ├── Task Routing (which skill/agent for what)             │
│  └── MCP Integration (tools, data sources)                 │
├─────────────────────────────────────────────────────────────┤
│  ADDITIONAL ELEMENTS                                        │
│  ├── RAG Pipeline (knowledge base, retrieval)             │
│  ├── Orchestration (workflows, agent communication)         │
│  ├── Client Interface (dashboard, API)                    │
│  └── Remote Control (Telegram)                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Decisions

| Component | Decision | Why |
|-----------|----------|-----|
| **Memory** | Mem0 | Simplest to learn, then upgrade later |
| **Skills** | Download a-i--skills (101 skills) | Start with existing, learn to configure |
| **Initial Skills** | Web Researcher, Content Writer, Code Developer | As requested |
| **MCP Servers** | File system, Web search, GitHub, Database | All mentioned |
| **RAG Content** | External Documentation | As requested |
| **Account** | Single account (AI Agency internal) first | Learn before multi-client |
| **Scheduler Phase 1** | Celery | Simple, lower learning curve |
| **Scheduler Stage 2** | Temporal | Better for AI, built-in state persistence |

---

## Implementation Phases - Phase 1: Foundation (Enhanced)

### Phase 1: Foundation
- [x] Project structure (agency folder, accounts folder)
- [x] Single account (internal AI Agency)
- [x] Basic agent framework (base class, types)
- [x] Task routing logic
- [x] Enhanced with 7 roles, capabilities, communication, Celery, SQLite

**Phase 1 Complete Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: FOUNDATION (Enhanced)                            │
├─────────────────────────────────────────────────────────────┤
│  1. Project Structure                                    │
│     ├── ai_agency/                                       │
│     ├── accounts/{account_id}/                           │
│     │   ├── config/                                     │
│     │   ├── memory/                                      │
│     │   ├── tasks/                                       │
│     │   └── output/                                     │
│     └── data/ (SQLite databases)                         │
├─────────────────────────────────────────────────────────────┤
│  2. Account System                                      │
│     ├── Config (YAML)                                    │
│     ├── Usage tracking: tasks, time, tokens               │
│     └── Per-agent settings: model, temp, max_tokens       │
├─────────────────────────────────────────────────────────────┤
│  3. Agent Framework (7 Roles)                            │
│     ├── ORG (manager) - can edit tasks                 │
│     ├── RESEARCH (researcher)                           │
│     ├── WRITER (content creator)                        │
│     ├── DEVELOPER (code writer)                        │
│     ├── DESIGNER (mockups, Stage 2 logos)              │
│     ├── ANALYST (trends, market research)              │
│     └── REVIEWER (quality control)                     │
├─────────────────────────────────────────────────────────────┤
│  4. Capabilities                                       │
│     ├── Web Search (DuckDuckGo)                          │
│     ├── File System (MCP)                               │
│     ├── API Calls                                      │
│     ├── Command Run                                    │
│     ├── Browser/Visit Websites                         │
│     └── Database Query                                │
├─────────────────────────────────────────────────────────────┤
│  5. Communication                                      │
│     ├── Agent → Agent messages                         │
│     ├── Proposals flow to ORG                        │
│     ├── Only ORG edits tasks                         │
│     └── Meetings log (timestamp, confidence)        │
├─────────────────────────────────────────────────────────────┤
│  6. Task System                                        │
│     ├── Priority: urgent, high, normal, low          │
│     ├── Dependencies: depends_on, blocks              │
│     ├── Status: queued, running, completed, failed   │
│     └── Progress persistence                         │
├─────────────────────────────────────────────────────────────┤
│  7. Database (SQLite)                                 │
│     ├── agents.db (config, history, state)            │
│     ├── projects.db (client projects)               │
│     ├── clients.db (client info)                   │
│     ├── knowledge.db (RAG content)                  │
│     └── meetings.json (meeting records)        │
├─────────────────────────────────────────────────────────────┤
│  8. Scheduler (Celery)                                │
│     ├── Daily task execution                         │
│     ├── Task queues per agent                        │
│     └── (Temporal in Stage 2)                     │
└─────────────────────────────────────────────────────────────┘
```

---

## React Website Creation - Tools Required

```
┌─────────────────────────────────────────────────────────────┐
│  SERVICE: REACT WEBSITE CREATION                              │
├─────────────────────────────────────────────────────────────┤
│  Required Tools:                                            │
│  ├── Node.js - Runtime                                      │
│  ├── npm/yarn - Package manager                            │
│  ├── React - UI framework                                  │
│  ├── Tailwind CSS - Styling                                │
│  ├── Vite - Build tool                                     │
│  ├── Docker - Containerization                             │
│  ├── ESLint - Code linting                                 │
│  ├── Prettier - Code formatting                           │
│  └── Playwright - Testing                                │
├─────────────────────────────────────────────────────────────┤
│  Agent Skills Needed:                                     │
│  ├── scaffold_react_app - Create project structure        │
│  ├── install_dependencies - npm install                   │
│  ├── configure_tailwind - Setup Tailwind                 │
│  ├── create_component - UI components                    │
│  ├── add_routing - React Router setup                   │
│  ├── containerize_docker - Dockerfile                   │
│  └── deploy_container - Docker deployment               │
├─────────────────────────────────────────────────────────────┤
│  Output:                                                 │
│  ├── Ready-to-deploy React app                           │
│  ├── With Tailwind CSS configured                       │
│  ├── Dockerized for production                        │
│  └── Can be deployed to cloud                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Meeting Details - Additional Recommendations

| Field | Description |
|-------|-------------|
| **Timestamp** | When meeting occurred |
| **Agent confidence score** | How confident the agent is (0-1) |
| **Participants** | Who was involved |
| **Topic** | What was discussed |
| **Decisions made** | Clear decisions |
| **Action items** | What needs to happen next |
| **Duration** | How long it took |
| **Key findings** | Data/insights shared |
| **Blocking issues** | Any blockers mentioned |

---

## Services Summary - What's Being Prepared

```
┌─────────────────────────────────────────────────────────────┐
│  SERVICES PREPARED FOR                                    │
├─────────────────────────────────────────────────────────────┤
│  1. Chatbot from Files                                    │
│     → RAG + MCP + Mem0                                    │
│     → WhatsApp, Telegram, Website integration            │
│                                                          │
│  2. React Website Creation                               │
│     → React + Tailwind + Node.js + Docker               │
│     → Designer creates mockups first                    │
│                                                          │
│  3. Lead Generation                                       │
│     → Web scraping (Research agent)                      │
│     → Data for cold calls/marketing                      │
│     → Competitor analysis                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Per-Agent Settings

```
Temperature Guide:
├── ORG: 0.1-0.3 (manager - clear decisions)
├── RESEARCH: 0.1-0.3 (accurate, factual)
├── WRITER: 0.5-0.8 (creative, varied)
├── DEVELOPER: 0.1-0.3 (precise, correct)
├── DESIGNER: 0.6-0.9 (creative)
├── ANALYST: 0.2-0.4 (analytical)
└── REVIEWER: 0.3-0.5 (critical)
```

---

## Phase 7: UNIFY - Integration Layer (Completed)

### Phase 7: Integration Layer
- [x] Unified integrator.py - connects all modules
- [x] Centralized config.yaml - single source of truth
- [x] CLI entry point (main.py) - unified interface
- [x] Client isolation on all paths
- [x] Task execution through all layers

**Integration Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 7: UNIFY - INTEGRATION LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   CLIENT   │  │   ORCHESTR  │  │   AGENT FRAMEWORK  │ │
│  │   LAYER    │←→│   LAYER     │←→│   + SKILLS         │ │
│  │ (multi_    │  │ (Router +  │  │ (7 agents + RAG +  │ │
│  │  client.py)│  │  Supervisor)│  │  Mem0 + Skills)    │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│         ↑               ↑                  ↑               │
│         └───────────────┴──────────────────┘               │
│                         ↓                                  │
│              ┌─────────────────────┐                   │
│              │  AgencyIntegrator  │                      │
│              │   (integrator.py)  │                      │
│              └─────────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

**Integration Flow:**
1. Task arrives → Client layer validates
2. Router determines agents
3. Memory retrieves context
4. RAG enhances with knowledge
5. Agents execute task
6. Results stored in memory
7. Usage tracked

**Key Files:**
- `integrator.py` - Central integration hub
- `config.yaml` - Unified configuration
- `main.py` - CLI entry point

---

## Stage 2: Advanced (After All Phases - Beta Complete)

Stage 1 (Phases 1-6) = Beta Version - Basic stable system

Stage 2 = Part 2 / Advanced Features:
```
┌─────────────────────────────────────────────────────────────┐
│  STAGE 2: ADVANCED                                        │
├─────────────────────────────────────────────────────────────┤
│  • Daily News Workflow (RESEARCH → WRITER → publish)       │
│  • Authentication (per account)                          │
│  • Temporal (advanced scheduler)                        │
│  • Agent sync meetings (scheduled)                       │
│  • UI_UX_MAX_PRO for DESIGNER                       │
│  • Image generation tools                             │
│  • GitHub MCP integration                           │
│  • Client portal (self-service)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 8: Website Creation (Completed)

- [x] Website folder created: accounts/internal/website/
- [x] UI_UX_MAX_PRO skill configured for DESIGNER
- [x] First website generation workflow
- [x] Playwright tests

---

## Phase 9: Social Media Content Agent (In Progress)

### Phase 9: Social Media Automation
- [x] Content generator - rewrites articles for each platform
- [x] Moltbook publisher - AI agent social network (free REST API)
- [x] Bluesky publisher - AT Protocol (free app password)
- [x] Mastodon publisher - federated social network (free token)
- [x] Telegram publisher - messaging platform (bot token)
- [x] Reddit publisher - link aggregation (OAuth, needs client ID)
- [x] Social scheduler - queue, rate limits, retries
- [x] Social media manager - orchestrates generation + publishing
- [x] API routes for social media management
- [ ] Admin dashboard social media controls
- [ ] Analytics tracker
- [ ] AI agent directory registration (moltbook.com, claw.direct)

**Social Media Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 9: SOCIAL MEDIA CONTENT AGENT                        │
├─────────────────────────────────────────────────────────────┤
│  Content Generator (LLM rewrites per platform)              │
│  ├── Moltbook (AI agent network, REST API)                  │
│  ├── Bluesky (AT Protocol, app password)                    │
│  ├── Mastodon (federated, token auth)                       │
│  ├── Telegram (bot token, channels)                         │
│  └── Reddit (OAuth, subreddits)                             │
├─────────────────────────────────────────────────────────────┤
│  Scheduler                                                  │
│  ├── Post queue (JSON files)                                │
│  ├── Rate limiting (per platform)                           │
│  ├── Retry logic (exponential backoff)                      │
│  └── Optimal timing (peak hours)                            │
├─────────────────────────────────────────────────────────────┤
│  Manager                                                    │
│  ├── Content plan generation                                │
│  ├── Platform selection                                     │
│  ├── Immediate or scheduled publishing                      │
│  └── History and analytics                                  │
└─────────────────────────────────────────────────────────────┘
```

**Platform Tiers:**
- Tier 1 (Free, no approval): Moltbook, Bluesky, Mastodon, Telegram
- Tier 2 (Free, OAuth): Reddit, LinkedIn
- Tier 3 (Needs approval): Threads, Instagram, Facebook, YouTube

**Key Files:**
- `server/services/social/` - Content generator, platform publishers, scheduler
- `server/routes/social.py` - API routes
- `config.yaml` - Platform configuration
- `agent_framework.py` - SOCIAL role added

---

## Current Status

- [x] Plan finalized and enhanced
- [x] Phase 1: Foundation - COMPLETE
- [x] Phase 2: Memory - COMPLETE
- [x] Phase 3: Skills - COMPLETE
- [x] Phase 4: RAG + MCP - COMPLETE
- [x] Phase 5: Orchestration - COMPLETE
- [x] Phase 6: Multi-Client - COMPLETE
- [x] Phase 7: UNIFY - COMPLETE
- [x] MCP Servers - COMPLETE
- [x] Approval System - COMPLETE
- [x] Tests Framework - COMPLETE
- [x] Phase 8: Website Creation - COMPLETE
- [ ] Phase 9: Social Media Content Agent - IN PROGRESS
- [ ] Stage 2: Advanced - PLANNED

---

## Beta Version Complete

All 8 phases implemented. System ready for testing.

```
ai_agency/
├── integrator.py       # Phase 7: Integration Layer
├── config.yaml       # Phase 7: Unified Configuration
├── main.py          # Phase 7: CLI Entry Point
├── agent_framework.py  # Phase 1: 8 Agents (including SOCIAL)
├── memory.py         # Phase 2: Mem0 Memory
├── skill_runner.py   # Phase 3: Skills Engine
├── rag_pipeline.py  # Phase 4: RAG Knowledge
├── mcp_integration.py  # Phase 4: MCP Servers
├── knowledge_manager.py  # Phase 4: Per-agent Knowledge
├── multi_client.py  # Phase 6: Multi-tenant DB
├── accounts_manager.py  # Phase 6: Account Management
├── orchestration/  # Phase 5: Workflows
│   ├── router.py, supervisor.py
│   ├── readiness.py, task_queue.py
│   └── scenarios/
└── server/
    └── services/
        └── social/  # Phase 9: Social Media
            ├── content_generator.py
            ├── scheduler.py
            ├── manager.py
            └── platforms/
                ├── base.py
                ├── moltbook.py
                ├── bluesky.py
                ├── mastodon.py
                ├── telegram.py
                └── reddit.py
```