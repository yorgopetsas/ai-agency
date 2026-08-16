"""
Tests for Phase 3: Skills Framework
===================================
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from skill_runner import SkillRunner, CONFIGURED_SKILLS


class TestSkills:
    """Test skills functionality"""

    def test_configured_skills_exist(self):
        """Test that 3 initial skills are configured"""
        assert len(CONFIGURED_SKILLS) >= 3
        assert "web_researcher" in CONFIGURED_SKILLS
        assert "content_writer" in CONFIGURED_SKILLS
        assert "code_developer" in CONFIGURED_SKILLS

    def test_skill_runner(self):
        """Test skill runner initialization"""
        runner = SkillRunner()
        assert runner is not None

    def test_researcher_skill(self):
        """Test RESEARCH agent skill config"""
        skill = CONFIGURED_SKILLS["web_researcher"]
        assert skill["library"] == "a-i--skills"
        assert skill["category"] == "data"

    def test_writer_skill(self):
        """Test WRITER agent skill config"""
        skill = CONFIGURED_SKILLS["content_writer"]
        assert skill["library"] == "a-i--skills"
        assert skill["category"] == "creative"

    def test_developer_skill(self):
        """Test DEVELOPER agent skill config"""
        skill = CONFIGURED_SKILLS["code_developer"]
        assert skill["library"] == "a-i--skills"
        assert skill["category"] == "development"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])