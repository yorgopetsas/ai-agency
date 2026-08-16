"""
Tests for Phase 1: Agent Framework
==============================
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent_framework import BaseAgent, AgentRole, AgentFactory, TaskRouter


class TestAgents:
    """Test agent creation and configuration"""

    def test_create_agent(self):
        """Test basic agent creation"""
        agent = BaseAgent("test_agent", AgentRole.RESEARCH, "internal")
        assert agent.name == "test_agent"
        assert agent.role == AgentRole.RESEARCH
        assert agent.account_id == "internal"

    def test_agent_roles(self):
        """Test all agent roles exist"""
        roles = [AgentRole.ORG, AgentRole.RESEARCH, AgentRole.WRITER,
                 AgentRole.DEVELOPER, AgentRole.DESIGNER,
                 AgentRole.ANALYST, AgentRole.REVIEWER]
        assert len(roles) == 7

    def test_create_team(self):
        """Test team creation"""
        team = AgentFactory.create_team("internal")
        assert len(team) >= 5


class TestTaskRouter:
    """Test task routing logic"""

    def test_route_research(self):
        """Test research task routing"""
        router = TaskRouter()
        role = router.route("Research AI trends")
        assert role == AgentRole.RESEARCH

    def test_route_write(self):
        """Test write task routing"""
        router = TaskRouter()
        role = router.route("Write a blog post")
        assert role == AgentRole.WRITER

    def test_route_develop(self):
        """Test develop task routing"""
        router = TaskRouter()
        role = router.route("Develop a Python script")
        assert role == AgentRole.DEVELOPER

    def test_route_default(self):
        """Test default routing (no keyword match)"""
        router = TaskRouter()
        role = router.route("Something random")
        assert role == AgentRole.ORG  # Default to ORG


if __name__ == "__main__":
    pytest.main([__file__, "-v"])