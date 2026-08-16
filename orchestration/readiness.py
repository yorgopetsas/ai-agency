"""
Readiness System - Human-in-the-Loop
Tracks agent performance and determines approval requirements.

Phase 5: Orchestration
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class AgentMetrics:
    """Metrics for a specific agent"""
    total_tasks: int = 0
    approved_without_revision: int = 0
    total_revisions: int = 0
    avg_confidence: float = 0.0
    thumbs_up: int = 0
    thumbs_down: int = 0
    errors: int = 0
    
    @property
    def success_rate(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return self.approved_without_revision / self.total_tasks
    
    @property
    def avg_revisions(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return self.total_revisions / self.total_tasks
    
    @property
    def feedback_ratio(self) -> float:
        total = self.thumbs_up + self.thumbs_down
        if total == 0:
            return 0.0
        return self.thumbs_up / total
    
    @property
    def error_rate(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return self.errors / self.total_tasks

class ReadinessSystem:
    """
    Tracks agent performance and determines approval level.
    
    Independence Levels:
    1 - Full Control (always require approval)
    2 - Guided (simple tasks auto-route)
    3 - Supervised (routine tasks auto-approve)
    4 - Trusted (verified workflows auto-complete)
    5 - Autonomous (full independence)
    """
    
    # Thresholds for promotion
    PROMOTION_THRESHOLDS = {
        'success_rate': 0.90,  # 90% approved without revision
        'avg_revisions': 1.5,  # Less than 1.5 avg revisions
        'avg_confidence': 0.8, # 80% confidence
        'feedback_ratio': 0.8, # 4:1 positive feedback
        'error_rate': 0.05     # Less than 5% errors
    }
    
    # Tasks needed for promotion
    TASKS_FOR_PROMOTION = 20
    
    def __init__(self):
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.agent_levels: Dict[str, int] = {}  # Agent ID -> Level
    
    def record_task_result(
        self,
        agent_id: str,
        approved: bool,
        revisions: int,
        confidence: float,
        feedback: Optional[str] = None,
        error: bool = False
    ):
        """Record the result of a task for an agent"""
        if agent_id not in self.agent_metrics:
            self.agent_metrics[agent_id] = AgentMetrics()
        
        metrics = self.agent_metrics[agent_id]
        metrics.total_tasks += 1
        
        if approved:
            metrics.approved_without_revision += 1
        
        metrics.total_revisions += revisions
        
        # Update average confidence
        metrics.avg_confidence = (
            (metrics.avg_confidence * (metrics.total_tasks - 1) + confidence) 
            / metrics.total_tasks
        )
        
        if feedback == 'up':
            metrics.thumbs_up += 1
        elif feedback == 'down':
            metrics.thumbs_down += 1
        
        if error:
            metrics.errors += 1
        
        # Check for promotion
        self._check_promotion(agent_id)
    
    def _check_promotion(self, agent_id: str):
        """Check if agent should be promoted to next level"""
        if agent_id not in self.agent_metrics:
            return
        
        metrics = self.agent_metrics[agent_id]
        current_level = self.agent_levels.get(agent_id, 1)
        
        # Can't promote past level 5
        if current_level >= 5:
            return
        
        # Need minimum tasks before promotion
        if metrics.total_tasks < self.TASKS_FOR_PROMOTION:
            return
        
        # Check all thresholds
        can_promote = True
        if metrics.success_rate < self.PROMOTION_THRESHOLDS['success_rate']:
            can_promote = False
        if metrics.avg_revisions > self.PROMOTION_THRESHOLDS['avg_revisions']:
            can_promote = False
        if metrics.avg_confidence < self.PROMOTION_THRESHOLDS['avg_confidence']:
            can_promote = False
        if metrics.feedback_ratio < self.PROMOTION_THRESHOLDS['feedback_ratio']:
            can_promote = False
        if metrics.error_rate > self.PROMOTION_THRESHOLDS['error_rate']:
            can_promote = False
        
        if can_promote:
            self.agent_levels[agent_id] = current_level + 1
    
    def get_approval_required(self, agent_id: str, task_type: str = 'normal') -> bool:
        """
        Determine if approval is required for a task.
        
        Returns True if human approval is needed.
        """
        level = self.agent_levels.get(agent_id, 1)
        
        # Level 1: Always require approval
        if level == 1:
            return True
        
        # Level 2: Simple tasks auto-route
        if level == 2:
            return task_type != 'simple'
        
        # Level 3: Routine tasks auto-approve
        if level == 3:
            return task_type not in ['simple', 'routine']
        
        # Level 4+: Only major tasks need approval
        if level >= 4:
            return task_type == 'major'
        
        return True
    
    def get_agent_level(self, agent_id: str) -> int:
        """Get current independence level of an agent"""
        return self.agent_levels.get(agent_id, 1)
    
    def get_metrics(self, agent_id: str) -> Optional[AgentMetrics]:
        """Get metrics for an agent"""
        return self.agent_metrics.get(agent_id)
    
    def get_all_levels(self) -> Dict[str, int]:
        """Get all agent levels"""
        return self.agent_levels.copy()


# Default readiness system instance
default_readiness = ReadinessSystem()
