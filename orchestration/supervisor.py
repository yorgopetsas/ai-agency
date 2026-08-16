"""
Supervisor - The Manager
ORG agent coordinates complex multi-agent tasks.

Phase 5: Orchestration
"""

import uuid
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass

@dataclass
class TaskSpec:
    """Specification for a subtask"""
    id: str
    agent: str  # RESEARCH, WRITER, etc.
    description: str
    depends_on: List[str] = None  # Task IDs this depends on
    parallel_ok: bool = True  # Can run in parallel with siblings

class Supervisor:
    """
    ORG agent acts as supervisor to coordinate complex tasks.
    Decomposes tasks and delegates to specialist agents.
    """
    
    def __init__(self):
        self.scenarios = {}
        self._register_scenarios()
    
    def _register_scenarios(self):
        """Register pre-built workflow scenarios"""
        self.scenarios = {
            'quick_research': {
                'agents': ['RESEARCH'],
                'flow': 'sequential',
                'output_type': 'summary'
            },
            'write_article': {
                'agents': ['RESEARCH', 'WRITER', 'DESIGNER', 'REVIEWER'],
                'flow': 'sequential',
                'output_type': 'article'
            },
            'build_feature': {
                'agents': ['DEVELOPER', 'REVIEWER'],
                'flow': 'parallel',
                'output_type': 'code'
            },
            'deep_analysis': {
                'agents': ['RESEARCH', 'ANALYST'],
                'flow': 'parallel',
                'output_type': 'report'
            },
            'full_project': {
                'agents': ['RESEARCH', 'DESIGNER', 'DEVELOPER', 'WRITER', 'REVIEWER'],
                'flow': 'sequential',
                'output_type': 'project'
            }
        }
    
    def decompose(self, request: str) -> List[TaskSpec]:
        """
        Break a complex request into subtasks.
        Returns list of TaskSpec objects.
        """
        # Detect scenario or use general decomposition
        scenario = self._detect_scenario(request)
        
        if scenario:
            return self._scenario_to_tasks(scenario)
        
        # General decomposition - ask LLM or use rules
        return self._general_decompose(request)
    
    def _detect_scenario(self, request: str) -> Optional[str]:
        """Detect which pre-built scenario applies"""
        request_lower = request.lower()
        
        # Simple keyword matching
        if 'article' in request_lower or 'blog' in request_lower:
            return 'write_article'
        if 'build' in request_lower and 'website' in request_lower:
            return 'full_project'
        if 'analyze' in request_lower:
            return 'deep_analysis'
        if 'code' in request_lower or 'function' in request_lower:
            return 'build_feature'
        if 'find' in request_lower or 'research' in request_lower:
            return 'quick_research'
        
        return None
    
    def _scenario_to_tasks(self, scenario_name: str) -> List[TaskSpec]:
        """Convert scenario to task specifications"""
        scenario = self.scenarios.get(scenario_name, {})
        agents = scenario.get('agents', ['ORG'])
        
        tasks = []
        for i, agent in enumerate(agents):
            task_id = str(uuid.uuid4())[:8]
            depends_on = [tasks[-1].id] if tasks else None
            
            tasks.append(TaskSpec(
                id=task_id,
                agent=agent,
                description=f"Task for {agent}",
                depends_on=depends_on,
                parallel_ok=(scenario.get('flow') == 'parallel')
            ))
        
        return tasks
    
    def _general_decompose(self, request: str) -> List[TaskSpec]:
        """
        General task decomposition for unknown requests.
        Returns basic task to ORG for handling.
        """
        return [TaskSpec(
            id=str(uuid.uuid4())[:8],
            agent='ORG',
            description=request,
            depends_on=None
        )]
    
    def should_run_parallel(self, tasks: List[TaskSpec]) -> bool:
        """Check if tasks can run in parallel"""
        if len(tasks) < 2:
            return False
        
        # Check if all tasks have no dependencies
        return all(t.depends_on is None or len(t.depends_on) == 0 for t in tasks)


# Default supervisor instance
default_supervisor = Supervisor()