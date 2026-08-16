"""
Task Queue Extension - Lane-Based Architecture
Phase 5: Orchestration

Extends Celery with lane-based isolation per agent type.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass
class Task:
    """Represents a task in the queue"""
    id: str
    agent: str
    description: str
    priority: int  # 0=urgent, 1=high, 2=normal, 3=low
    status: str  # queued, running, completed, failed
    depends_on: List[str] = None
    lane: str = "main"
    created_at: datetime = None
    result: Any = None

class LaneConfig:
    """Configuration for a task lane"""
    def __init__(self, name: str, max_concurrent: int = 1):
        self.name = name
        self.max_concurrent = max_concurrent
        self.running_tasks: List[str] = []

class TaskQueue:
    """
    Lane-based task queue system.
    
    Lanes:
    - main: Serial execution (one task at a time)
    - cron: Scheduled tasks
    - urgent: Priority tasks
    - agent_{name}: Per-agent parallel execution
    """
    
    def __init__(self):
        self.lanes: Dict[str, LaneConfig] = {
            'main': LaneConfig('main', max_concurrent=1),
            'cron': LaneConfig('cron', max_concurrent=1),
            'urgent': LaneConfig('urgent', max_concurrent=3),
        }
        self.tasks: Dict[str, Task] = {}
        self._setup_agent_lanes()
    
    def _setup_agent_lanes(self):
        """Setup per-agent lanes for parallel execution"""
        agents = ['RESEARCH', 'WRITER', 'DEVELOPER', 'DESIGNER', 'ANALYST', 'REVIEWER']
        for agent in agents:
            self.lanes[f'agent_{agent.lower()}'] = LaneConfig(
                f'agent_{agent.lower()}',
                max_concurrent=3  # Allow some parallelism
            )
    
    def enqueue(
        self,
        agent: str,
        description: str,
        priority: int = 2,
        depends_on: List[str] = None,
        urgent: bool = False
    ) -> str:
        """Add a task to the queue"""
        task_id = str(uuid.uuid4())[:8]
        
        # Determine lane
        lane = 'urgent' if urgent else f'agent_{agent.lower()}'
        
        task = Task(
            id=task_id,
            agent=agent,
            description=description,
            priority=priority,
            status='queued',
            depends_on=depends_on or [],
            lane=lane,
            created_at=datetime.now()
        )
        
        self.tasks[task_id] = task
        return task_id
    
    def dequeue(self, agent: str, max_tasks: int = 1) -> List[Task]:
        """
        Get next available tasks for an agent.
        Respects lane concurrency limits.
        """
        lane = self.lanes.get(f'agent_{agent.lower()}')
        if not lane:
            lane = self.lanes['main']
        
        if len(lane.running_tasks) >= lane.max_concurrent:
            return []
        
        available = []
        for task_id, task in self.tasks.items():
            if task.status != 'queued':
                continue
            if task.agent != agent:
                continue
            if task_id in lane.running_tasks:
                continue
            
            # Check dependencies
            if task.depends_on:
                deps_complete = all(
                    self.tasks.get(dep_id) and 
                    self.tasks[dep_id].status == 'completed'
                    for dep_id in task.depends_on
                )
                if not deps_complete:
                    continue
            
            available.append(task)
        
        # Sort by priority
        available.sort(key=lambda t: t.priority)
        
        return available[:max_tasks]
    
    def start_task(self, task_id: str) -> bool:
        """Mark a task as running"""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        lane = self.lanes.get(task.lane)
        if lane and len(lane.running_tasks) >= lane.max_concurrent:
            return False
        
        task.status = 'running'
        if lane:
            lane.running_tasks.append(task_id)
        
        return True
    
    def complete_task(self, task_id: str, result: Any = None):
        """Mark a task as completed"""
        task = self.tasks.get(task_id)
        if not task:
            return
        
        task.status = 'completed'
        task.result = result
        
        lane = self.lanes.get(task.lane)
        if lane and task_id in lane.running_tasks:
            lane.running_tasks.remove(task_id)
    
    def fail_task(self, task_id: str, error: str = None):
        """Mark a task as failed"""
        task = self.tasks.get(task_id)
        if not task:
            return
        
        task.status = 'failed'
        if error:
            task.result = {'error': error}
        
        lane = self.lanes.get(task.lane)
        if lane and task_id in lane.running_tasks:
            lane.running_tasks.remove(task_id)
    
    def retry_task(self, task_id: str) -> bool:
        """Retry a failed task"""
        task = self.tasks.get(task_id)
        if not task or task.status != 'failed':
            return False
        
        task.status = 'queued'
        task.result = None
        return True
    
    def get_status(self) -> Dict:
        """Get queue status"""
        return {
            'total': len(self.tasks),
            'queued': len([t for t in self.tasks.values() if t.status == 'queued']),
            'running': len([t for t in self.tasks.values() if t.status == 'running']),
            'completed': len([t for t in self.tasks.values() if t.status == 'completed']),
            'failed': len([t for t in self.tasks.values() if t.status == 'failed']),
        }


# Default instance
task_queue = TaskQueue()