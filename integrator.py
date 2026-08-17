#!/usr/bin/env python3
"""
AI Agency Integration Layer - Phase 7: UNIFY
=========================================
Central hub that connects all modules into unified system.

This module glues together:
- Multi-Client (client isolation)
- Agent Framework (7 agents)
- Memory System (Mem0)
- Skills Framework (a-i--skills)
- RAG Pipeline (knowledge)
- Orchestration (workflows)

Usage:
    from integrator import AgencyIntegrator

    # Create integrator for a client
    agency = AgencyIntegrator(client_id="client_123")

    # Execute a task through all layers
    result = agency.execute("Research AI trends for 2026")
"""

import os
import sys
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
from enum import Enum

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all modules
try:
    from agent_framework import BaseAgent, AgentRole, AgentFactory, TaskRouter
    from memory import AgentMemory, get_agent_memory
    from skill_runner import SkillRunner
    from rag_pipeline import RAGPipeline, KnowledgeBaseManager, AgentsKBClient, get_client_rag
    from multi_client import IsolatedQuery, ClientManager, UsageTracker
    from knowledge_manager import KnowledgeManager, get_client_knowledge
    from orchestration.router import TaskRouter as OrchestrationRouter
    from orchestration.supervisor import Supervisor
except ImportError as e:
    print(f"Warning: Some modules not available: {e}")


class IntegrationError(Exception):
    """Raised when integration fails"""
    pass


class AgencyIntegrator:
    """
    Central integration hub connecting all AI Agency modules.

    This class provides a unified interface to:
    - Route tasks to appropriate agents
    - Load context from memory and RAG
    - Execute with skills
    - Store results back to memory
    - Track usage per client
    """

    def __init__(self, client_id: str = "internal", config: Optional[Dict] = None):
        """
        Initialize the integration layer.

        Args:
            client_id: Client identifier for isolation
            config: Optional configuration overrides
        """
        self.client_id = client_id
        self.config = config or self._load_default_config()
        self._initialize_components()

    def _load_default_config(self) -> Dict:
        """Load default configuration"""
        return {
            "model": "llama3",
            "temperature": 0.3,
            "max_tokens": 2048,
            "memory_enabled": True,
            "rag_enabled": True,
            "skills_enabled": True,
            "orchestration_mode": "supervisor",  # supervisor, router, sequential
            "human_oversight": "medium",  # none, low, medium, high, full
        }

    def _initialize_components(self):
        """Initialize all component modules"""
        # Multi-Client layer
        self.client_manager = ClientManager()
        self.usage_tracker = UsageTracker()

        # Agent Framework
        self.agents = AgentFactory.create_team(self.client_id)

        # RAG Pipeline — client-scoped
        self.rag = get_client_rag(self.client_id)
        self.knowledge = get_client_knowledge(self.client_id)
        self.agentskb = AgentsKBClient()

        # Orchestration
        self.router = OrchestrationRouter()
        self.supervisor = Supervisor()

        # Memory per agent — client-scoped
        self.memories: Dict[str, AgentMemory] = {}

        # Skills
        self.skill_runner = SkillRunner()

        # Task history
        self.task_history: List[Dict] = []

    def _get_agent_memory(self, agent_name: str) -> AgentMemory:
        """Get or create memory for an agent, scoped to this client"""
        if agent_name not in self.memories:
            self.memories[agent_name] = get_agent_memory(
                agent_id=agent_name,
                client_id=self.client_id
            )
        return self.memories[agent_name]

    def execute(self, task: str, context: Optional[Dict] = None, agent_role: Optional[str] = None) -> Dict:
        """
        Execute a task through the integrated system.

        Args:
            task: Task description
            context: Additional context
            agent_role: Specific agent role to use (optional)

        Returns:
            Dict with execution results
        """
        start_time = datetime.now()
        result = {
            "task": task,
            "client_id": self.client_id,
            "started_at": start_time.isoformat(),
            "status": "running",
        }

        try:
            # Step 1: Route task to appropriate agents
            if agent_role:
                routed_agents = [AgentRole(agent_role)]
            else:
                routed_agents = self.router.route(task)

            result["agents"] = [a.value for a in routed_agents]

            # Step 2: Load context from memory
            memory_context = {}
            if self.config.get("memory_enabled"):
                for agent_role in routed_agents:
                    agent_name = agent_role.value
                    memory = self._get_agent_memory(agent_name)
                    memories = memory.search(task, limit=5)
                    memory_context[agent_name] = memories

            result["memory_context"] = memory_context

            # Step 3: Enhance with RAG knowledge
            rag_context = {}
            if self.config.get("rag_enabled"):
                for agent in routed_agents:
                    agent_name = agent.value
                    try:
                        docs = self.rag.get_pipeline(agent_name).search(task, n_results=3)
                        rag_context[agent_name] = docs
                    except Exception:
                        rag_context[agent_name] = []

            result["rag_context"] = rag_context

            # Step 4: Execute with agents
            execution_result = self._execute_with_agents(task, routed_agents, context, memory_context, rag_context)
            result["execution"] = execution_result

            # Step 5: Store in memory
            if self.config.get("memory_enabled"):
                for agent_role in routed_agents:
                    agent_name = agent_role.value
                    memory = self._get_agent_memory(agent_name)
                    memory.add(
                        f"Task: {task}\nResult: {execution_result.get('result', '')}",
                        metadata={"client_id": self.client_id}
                    )

            # Step 6: Track usage
            self.usage_tracker.record(self.client_id, "tasks", 1)

            result["status"] = "completed"
            result["completed_at"] = datetime.now().isoformat()

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        self.task_history.append(result)
        return result

    def _execute_with_agents(
        self,
        task: str,
        agents: List[AgentRole],
        context: Optional[Dict],
        memory_context: Dict,
        rag_context: Dict
    ) -> Dict:
        """
        Execute task with multiple agents.

        Args:
            task: Task description
            agents: List of agent roles to involve
            context: Additional context
            memory_context: From memory layer
            rag_context: From RAG layer

        Returns:
            Execution results
        """
        combined_context = {**(context or {}), **memory_context, **rag_context}

        if self.config.get("orchestration_mode") == "supervisor":
            # Supervisor mode: ORG coordinates
            return self.supervisor.coordinate(agents, task, combined_context)
        else:
            # Simple mode: Execute sequentially
            results = []
            for agent in agents:
                results.append({
                    "agent": agent.value,
                    "task": task,
                    "context": combined_context
                })
            return {"results": results}

    def search_knowledge(self, query: str, domain: Optional[str] = None) -> List[Dict]:
        """
        Search all knowledge sources for this client.

        Args:
            query: Search query
            domain: Optional domain filter

        Returns:
            Combined search results from all sources
        """
        results = {
            "internal_rag": self.rag.search_all(query),
            "agentskb": self.agentskb.search(query, domain)
        }
        return results

    def get_agent_status(self) -> List[Dict]:
        """Get status of all agents"""
        return [agent.to_dict() for agent in self.agents]

    def get_usage_stats(self) -> Dict:
        """Get usage statistics for this client"""
        try:
            usage = self.usage_tracker.get_usage(self.client_id)
            return {
                "total_tasks": sum(u.get("value", 0) for u in usage),
                "period": usage[0].get("period", "unknown") if usage else None,
                "records": usage
            }
        except Exception:
            return {"total_tasks": 0, "period": None, "records": []}


class AgencyCLI:
    """Command-line interface for Agency Integrator"""

    def __init__(self):
        self.integrator: Optional[AgencyIntegrator] = None

    def start(self, client_id: str = "internal"):
        """Start the agency for a client"""
        self.integrator = AgencyIntegrator(client_id=client_id)
        print(f"Agency started for client: {client_id}")
        return self.integrator

    def run_interactive(self):
        """Run interactive CLI loop"""
        print("\n" + "=" * 50)
        print("AI Agency CLI - Type 'exit' to quit")
        print("=" * 50)

        while True:
            try:
                task = input("\n> ")
                if task.lower() in ("exit", "quit"):
                    break

                if not self.integrator:
                    print("Agency not started. Use: agency.start('client_id')")
                    continue

                result = self.integrator.execute(task)
                print(f"\nStatus: {result['status']}")
                if result.get("agents"):
                    print(f"Agents: {', '.join(result['agents'])}")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

        print("\nGoodbye!")


def create_agency(client_id: str = "internal") -> AgencyIntegrator:
    """
    Factory function to create an agency integrator.

    Args:
        client_id: Client identifier

    Returns:
        Configured AgencyIntegrator instance
    """
    return AgencyIntegrator(client_id=client_id)


def quick_research(query: str, client_id: str = "internal") -> Dict:
    """
    Quick research task through the agency.

    Args:
        query: Research question
        client_id: Client identifier

    Returns:
        Research results
    """
    agency = AgencyIntegrator(client_id=client_id)
    return agency.execute(query, agent_role="research")


def quick_write(topic: str, client_id: str = "internal") -> Dict:
    """
    Quick writing task through the agency.

    Args:
        topic: Writing topic
        client_id: Client identifier

    Returns:
        Writing results
    """
    agency = AgencyIntegrator(client_id=client_id)
    return agency.execute(topic, agent_role="writer")


def quick_develop(spec: str, client_id: str = "internal") -> Dict:
    """
    Quick development task through the agency.

    Args:
        spec: Development specification
        client_id: Client identifier

    Returns:
        Development results
    """
    agency = AgencyIntegrator(client_id=client_id)
    return agency.execute(spec, agent_role="developer")


# ============================================================
# Main - For Testing
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("AI Agency - Integration Layer Test")
    print("=" * 50)

    # Create agency for internal client
    agency = AgencyIntegrator(client_id="internal")

    print(f"\nInitialized for client: {agency.client_id}")
    print(f"Agents: {len(agency.agents)}")

    # Test routing
    test_tasks = [
        ("Research AI trends for 2026", "research"),
        ("Write a blog post about automation", "writer"),
        ("Build a REST API endpoint", "developer"),
        ("Create a logo design", "designer"),
    ]

    print("\nTask Routing Tests:")
    for task, expected_agent in test_tasks:
        result = agency.execute(task)
        print(f"  '{task[:30]}...'")
        print(f"    -> {result.get('agents', ['unknown'])}")

    # Test knowledge search
    print("\nKnowledge Search:")
    results = agency.search_knowledge("python web development")
    print(f"  Found {len(results.get('internal_rag', {}))} internal sources")
    print(f"  Found {len(results.get('agentskb', []))} AgentsKB sources")

    # Usage stats
    stats = agency.get_usage_stats()
    print(f"\nUsage: {stats.get('total_tasks', 0)} tasks executed")

    print("\n✅ Integration Layer Ready!")