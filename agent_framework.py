#!/usr/bin/env python3
"""
Agent Framework - Base Class for AI Agents
Phase 1: Foundation

This module provides the foundational agent classes for the AI Agency system.
Each agent has:
- Name and role
- Available skills
- Task queue
- Memory (for Phase 2)
"""
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

# Agent Roles
class AgentRole(Enum):
    ORG = "org"           # Manager/Coordinator
    RESEARCH = "research" # Research Analyst
    WRITER = "writer"     # Content Writer
    DEVELOPER = "developer" # Developer
    DESIGNER = "designer"  # Designer
    ANALYST = "analyst"    # Market Analyst
    REVIEWER = "reviewer"  # Content Reviewer

# Agent Status
class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Task:
    """Task that an agent can execute"""
    def __init__(self, task_id: str, description: str, agent_role: AgentRole, input_data: Dict = None):
        self.task_id = task_id
        self.description = description
        self.agent_role = agent_role
        self.input_data = input_data or {}
        self.status = AgentStatus.IDLE
        self.result = None
        self.created_at = datetime.now().isoformat()
        self.completed_at = None
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "agent_role": self.agent_role.value,
            "input_data": self.input_data,
            "status": self.status.value,
            "result": self.result,
            "created_at": self.created_at,
            "completed_at": self.completed_at
        }

class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, name: str, role: AgentRole, account_id: str = "internal"):
        self.name = name
        self.role = role
        self.account_id = account_id
        self.status = AgentStatus.IDLE
        self.current_task = None
        self.history = []  # Task history
        self.skills = []
        self.created_at = datetime.now().isoformat()
    
    def add_skill(self, skill_name: str):
        """Add a skill to this agent"""
        if skill_name not in self.skills:
            self.skills.append(skill_name)
    
    def assign_task(self, task: Task):
        """Assign a task to this agent"""
        self.current_task = task
        task.status = AgentStatus.RUNNING
    
    def complete_task(self, result: Any):
        """Complete the current task"""
        if self.current_task:
            self.current_task.result = result
            self.current_task.status = AgentStatus.COMPLETED
            self.current_task.completed_at = datetime.now().isoformat()
            self.history.append(self.current_task.to_dict())
            self.current_task = None
            self.status = AgentStatus.IDLE
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "role": self.role.value,
            "account_id": self.account_id,
            "status": self.status.value,
            "skills": self.skills,
            "history_count": len(self.history),
            "created_at": self.created_at
        }

class AgentFactory:
    """Factory to create agents"""
    
    @staticmethod
    def create_agent(name: str, role: AgentRole, account_id: str = "internal") -> BaseAgent:
        """Create a new agent"""
        return BaseAgent(name, role, account_id)
    
    @staticmethod
    def create_team(account_id: str = "internal") -> List[BaseAgent]:
        """Create a standard team of agents"""
        return [
            BaseAgent("org_manager", AgentRole.ORG, account_id),
            BaseAgent("researcher", AgentRole.RESEARCH, account_id),
            BaseAgent("writer", AgentRole.WRITER, account_id),
            BaseAgent("developer", AgentRole.DEVELOPER, account_id),
            BaseAgent("designer", AgentRole.DESIGNER, account_id),
            BaseAgent("analyst", AgentRole.ANALYST, account_id),
            BaseAgent("reviewer", AgentRole.REVIEWER, account_id),
        ]

class TaskRouter:
    """Routes tasks to appropriate agents"""
    
    def __init__(self):
        self.routes = {
            "research": AgentRole.RESEARCH,
            "write": AgentRole.WRITER,
            "develop": AgentRole.DEVELOPER,
            "design": AgentRole.DESIGNER,
            "style": AgentRole.DESIGNER,
            "color": AgentRole.DESIGNER,
            "layout": AgentRole.DESIGNER,
            "analyze": AgentRole.ANALYST,
            "review": AgentRole.REVIEWER,
            "manage": AgentRole.ORG,
        }
    
    def route(self, task_description: str) -> AgentRole:
        """Determine which agent should handle this task"""
        task_lower = task_description.lower()
        
        for keyword, role in self.routes.items():
            if keyword in task_lower:
                return role
        
        return AgentRole.ORG  # Default to org manager

# ============================================================
# Save and Load Functions
# ============================================================

def save_agent(agent: BaseAgent, path: str):
    """Save agent to file"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(agent.to_dict(), f, indent=2)

def load_agent(path: str) -> BaseAgent:
    """Load agent from file"""
    with open(path, "r") as f:
        data = json.load(f)
    return BaseAgent(data["name"], AgentRole(data["role"]), data["account_id"])

# ============================================================
# Main - For Testing
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("AI Agency - Agent Framework Test")
    print("=" * 50)
    
    # Create a team
    team = AgentFactory.create_team("internal")
    print(f"\nCreated {len(team)} agents:")
    for agent in team:
        print(f"  - {agent.name}: {agent.role.value}")
    
    # Test routing
    router = TaskRouter()
    test_tasks = [
        "Research the latest AI trends",
        "Write a blog post about AI",
        "Develop a Python script",
        "Review the documentation"
    ]
    
    print("\nTask Routing:")
    for task in test_tasks:
        agent_role = router.route(task)
        print(f"  '{task}' -> {agent_role.value}")
    
    print("\n✅ Agent Framework Ready!")