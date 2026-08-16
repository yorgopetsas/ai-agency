"""
Tests for Phase 7: Integration Layer
====================================
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from integrator import AgencyIntegrator


class TestIntegration:
    """Test integration layer"""

    def test_create_agency(self):
        """Test agency integrator creation"""
        agency = AgencyIntegrator(client_id="internal")
        assert agency.client_id == "internal"

    def test_config_defaults(self):
        """Test default configuration"""
        agency = AgencyIntegrator(client_id="test")
        assert agency.config["memory_enabled"] is True
        assert agency.config["rag_enabled"] is True
        assert agency.config["orchestration_mode"] == "supervisor"

    def test_agents_initialized(self):
        """Test agents are initialized"""
        agency = AgencyIntegrator(client_id="internal")
        assert len(agency.agents) >= 5

    def test_get_agent_status(self):
        """Test agent status retrieval"""
        agency = AgencyIntegrator(client_id="internal")
        status = agency.get_agent_status()
        assert len(status) >= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])