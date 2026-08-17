#!/usr/bin/env python3
"""
Memory Module - Phase 2: Mem0 Integration
=====================================
Per-agent memory using Mem0 with Ollama configuration.

Each client+agent combination gets its own isolated memory space.
Storage keyed by: agent_{client_id}_{agent_name}
"""
import os
import json
from datetime import datetime
from typing import Optional, Dict

# Module-level cache of client→memories mappings
_memories_cache: Dict[str, Dict[str, 'AgentMemory']] = {}


class AgentMemory:
    """
    Memory management for individual AI agents, scoped per client.
    Each client+agent has separate memory for personalization.
    """

    def __init__(self, agent_id: str, client_id: str = "internal"):
        self.agent_id = agent_id
        self.client_id = client_id
        self.user_id = f"{client_id}_{agent_id}"
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load Mem0 configuration"""
        return {
            "llm": {
                "provider": "ollama",
                "config": {
                    "model": "llama3",
                    "temperature": 0.3
                }
            },
            "embedding": {
                "provider": "ollama",
                "config": {
                    "model": "mxbai-embed-large"
                }
            },
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": f"agent_{self.client_id}_{self.agent_id}"
                }
            }
        }

    def add(self, memory_text: str, metadata: dict = None) -> dict:
        """Add a memory for this agent"""
        pass

    def search(self, query: str, limit: int = 5) -> list:
        """Search memories"""
        pass

    def get_all(self) -> list:
        """Get all memories for this agent"""
        pass

    def delete(self, memory_id: str) -> bool:
        """Delete a memory"""
        pass


def get_agent_memory(agent_id: str, client_id: str = "internal") -> AgentMemory:
    """Get or create memory for an agent, scoped to client"""
    cache_key = f"{client_id}_{agent_id}"
    if client_id not in _memories_cache:
        _memories_cache[client_id] = {}
    if agent_id not in _memories_cache[client_id]:
        _memories_cache[client_id][agent_id] = AgentMemory(
            agent_id=agent_id, client_id=client_id
        )
    return _memories_cache[client_id][agent_id]


def initialize_all_agent_memories(client_id: str = "internal") -> Dict[str, AgentMemory]:
    """Initialize memory for all agents, scoped to client"""
    agents = ["org", "research", "writer", "developer", "designer", "analyst", "reviewer"]
    memories = {}

    for agent in agents:
        memories[agent] = get_agent_memory(agent, client_id=client_id)

    return memories


if __name__ == "__main__":
    print("=" * 50)
    print("Agent Memory Module - Phase 6 (Client-Scoped)")
    print("=" * 50)

    # Test initialization for two different clients
    for cid in ["internal", "client_001"]:
        memories = initialize_all_agent_memories(client_id=cid)
        print(f"\n{cid}: Initialized {len(memories)} agent memories:")
        for agent_id, mem in memories.items():
            print(f"  - {agent_id}: {mem.user_id}")

    print("\nNote: Full Mem0 integration requires running Ollama")
    print("Command: ollama pull mxbai-embed-large")
    print("Command: ollama pull llama3")