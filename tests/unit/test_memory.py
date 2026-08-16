"""
Tests for Phase 2: Memory System
==============================
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from memory import AgentMemory, get_agent_memory


class TestMemory:
    """Test memory functionality"""

    def test_create_memory(self):
        """Test memory creation"""
        memory = AgentMemory(agent_id="research")
        assert memory.agent_id == "research"

    def test_get_agent_memory(self):
        """Test factory function"""
        memory = get_agent_memory("writer")
        assert memory.agent_id == "writer"

    def test_memory_config(self):
        """Test memory configuration"""
        memory = AgentMemory(agent_id="developer")
        config = memory._load_config()
        assert "llm" in config
        assert "embedding" in config
        assert config["llm"]["provider"] == "ollama"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])