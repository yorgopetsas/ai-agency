#!/usr/bin/env python3
"""
Skill Runner Module - Phase 3
=================================
Executes skills from a-i--skills and Anthropic Skills libraries.

Three initial skill sets configured:
- Technical (Web Researcher)
- Content Writer  
- Code Developer
"""
import os
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, List

# Base paths
SKILLS_BASE = Path(__file__).parent / "skills"
A_I_SKILLS = SKILLS_BASE / "a-i--skills" / "organized"
ANTHROPIC_SKILLS = SKILLS_BASE / "anthropic" / "anthropic" / "skills"
AGENCY_SKILLS = SKILLS_BASE / "agency"

class SkillRunner:
    """Execute skills from the skill libraries"""
    
    def __init__(self):
        self.available_skills = self._discover_skills()
    
    def _discover_skills(self) -> Dict[str, List[str]]:
        """Discover all available skills"""
        skills = {
            "a-i--skills": {},
            "anthropic": {},
            "agency": {}
        }
        
        # Discover a-i--skills
        if A_I_SKILLS.exists():
            for category in A_I_SKILLS.iterdir():
                if category.is_dir():
                    skill_list = [s.stem for s in category.glob("*.skill")]
                    if skill_list:
                        skills["a-i--skills"][category.name] = skill_list
        
        # Discover Anthropic skills
        if ANTHROPIC_SKILLS.exists():
            for skill_dir in ANTHROPIC_SKILLS.iterdir():
                if skill_dir.is_dir():
                    skills["anthropic"][skill_dir.name] = [skill_dir.stem]
        
        # Discover agency skills
        if AGENCY_SKILLS.exists():
            for skill_dir in AGENCY_SKILLS.iterdir():
                if skill_dir.is_dir():
                    skill_md = skill_dir / "SKILL.md"
                    if skill_md.exists():
                        skills["agency"][skill_dir.name] = [skill_dir.name]
        
        return skills
    
    def list_skills(self, library: str = "a-i--skills") -> Dict[str, List[str]]:
        """List skills by library"""
        return self.available_skills.get(library, {})
    
    def get_skill_path(self, library: str, category: str, skill: str) -> Path:
        """Get path to a skill"""
        if library == "a-i--skills":
            return A_I_SKILLS / category / f"{skill}.skill"
        elif library == "anthropic":
            return ANTHROPIC_SKILLS / skill
        return None
    
    def read_skill(self, library: str, category: str, skill: str) -> Optional[str]:
        """Read skill instructions"""
        if library == "agency":
            skill_path = AGENCY_SKILLS / skill
            skill_file = skill_path / "SKILL.md"
            if skill_file.exists():
                return skill_file.read_text()
            return None
        
        path = self.get_skill_path(library, category, skill)
        if path and path.exists():
            # Look for SKILL.md file
            skill_file = path / "SKILL.md"
            if skill_file.exists():
                return skill_file.read_text()
            
            # Or read .skill file
            for f in path.glob("*.skill"):
                return f.read_text()
        return None
    
    def run_skill_script(self, library: str, skill: str, script_args: list) -> Optional[str]:
        """Run a skill's script with given arguments"""
        if library == "agency":
            script_path = AGENCY_SKILLS / skill / "scripts"
            scripts = list(script_path.glob("*.py")) if script_path.exists() else []
            if scripts:
                result = subprocess.run(
                    ["python3", str(scripts[0])] + script_args,
                    capture_output=True, text=True, timeout=30
                )
                return result.stdout if result.returncode == 0 else result.stderr
        return None

# Initial configured skills
CONFIGURED_SKILLS = {
    "web_researcher": {
        "library": "a-i--skills",
        "category": "data", 
        "skill": "data-storytelling-analyst",
        "note": "Web research handled by Phase 1 capabilities (DuckDuckGo)"
    },
    "content_writer": {
        "library": "a-i--skills", 
        "category": "creative",
        "skill": "creative-writing-craft"
    },
    "code_developer": {
        "library": "a-i--skills",
        "category": "development",
        "skill": "python-packaging-patterns"
    },
    "ui_ux_designer": {
        "library": "agency",
        "category": "ui-ux-design",
        "skill": "ui-ux-design",
        "note": "Design system intelligence: styles, palettes, fonts, UX guidelines"
    },
    "website_scaffolder": {
        "library": "agency",
        "category": "scaffold-react-app",
        "skill": "scaffold-react-app",
        "note": "Creates production-ready React + Vite + Tailwind projects"
    },
    "component_creator": {
        "library": "agency",
        "category": "create-component",
        "skill": "create-component",
        "note": "Generates individual React components: hero, pricing, features, testimonials, CTA, forms, nav, footer"
    },
    "docker_containerizer": {
        "library": "agency",
        "category": "containerize-docker",
        "skill": "containerize-docker",
        "note": "Generates Dockerfiles, docker-compose.yml, and .dockerignore for React, Flask, or fullstack"
    }
}

def get_runner() -> SkillRunner:
    """Get skill runner instance"""
    return SkillRunner()

def list_initial_skills():
    """List the 3 initial configured skills"""
    print("=" * 50)
    print("Configured Initial Skills")
    print("=" * 50)
    
    for name, config in CONFIGURED_SKILLS.items():
        print(f"\n{name}:")
        print(f"  Library: {config['library']}")
        print(f"  Category: {config['category']}")
        print(f"  Skill: {config['skill']}")

if __name__ == "__main__":
    runner = get_runner()
    
    print("=" * 50)
    print("Phase 3: Skills Framework")
    print("=" * 50)
    
    print(f"\nAvailable Skills:")
    a_i_skills = runner.list_skills("a-i--skills")
    for category, skill_list in a_i_skills.items():
        print(f"  {category}: {len(skill_list)} skills")
    
    print(f"\nAnthropic Skills:")
    anthropic_skills = runner.list_skills("anthropic")
    for category, skill_list in anthropic_skills.items():
        print(f"  {category}: {len(skill_list)} skills")
    
    print(f"\nAgency Skills:")
    agency_skills = runner.list_skills("agency")
    for category, skill_list in agency_skills.items():
        print(f"  {category}: {', '.join(skill_list)}")
    
    list_initial_skills()