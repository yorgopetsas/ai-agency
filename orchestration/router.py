"""
Router - The Receptionist
Routes incoming requests to the appropriate agent based on intent classification.

Phase 5: Orchestration
"""

import yaml
from typing import Dict, Optional, Tuple

class Router:
    """
    Routes client requests to the appropriate agent.
    Uses rule-based classification with keyword matching.
    """
    
    def __init__(self, config_path: str = None):
        self.rules = []
        self.industry_keywords = {}
        self.auto_route_threshold = 0.80
        self.ask_user_threshold = 0.50
        
        if config_path:
            self.load_config(config_path)
        else:
            self._default_config()
    
    def _default_config(self):
        """Default routing rules"""
        self.rules = [
            {
                'name': 'research',
                'primary': ['research', 'find', 'gather', 'investigate', 'explore', 'discover'],
                'secondary': ['info', 'data', 'sources', 'facts'],
                'agent': 'RESEARCH'
            },
            {
                'name': 'writer',
                'primary': ['write', 'create', 'draft', 'compose', 'blog', 'article'],
                'secondary': ['content', 'post', 'story', 'copy'],
                'agent': 'WRITER'
            },
            {
                'name': 'developer',
                'primary': ['code', 'build', 'develop', 'implement', 'function', 'program', 'script'],
                'secondary': ['app', 'website', 'software', 'feature'],
                'agent': 'DEVELOPER'
            },
            {
                'name': 'designer',
                'primary': ['design', 'mockup', 'ui', 'interface', 'visual', 'layout', 'prototype'],
                'secondary': ['wireframe', 'mock'],
                'agent': 'DESIGNER'
            },
            {
                'name': 'analyst',
                'primary': ['analyze', 'analysis', 'market', 'trend', 'report', 'metrics'],
                'secondary': ['statistics', 'insights', 'forecast'],
                'agent': 'ANALYST'
            },
            {
                'name': 'reviewer',
                'primary': ['review', 'check', 'audit', 'quality', 'test', 'verify'],
                'secondary': ['examine', 'assess', 'critique'],
                'agent': 'REVIEWER'
            },
            {
                'name': 'supervisor',
                'primary': ['complex', 'project', 'build website', 'everything', 'end-to-end'],
                'secondary': ['full', 'complete', 'entire'],
                'agent': 'ORG'
            }
        ]
        
        self.industry_keywords = {
            'healthcare': 'RESEARCH',
            'legal': 'RESEARCH',
            'academic': 'RESEARCH',
            'fintech': 'ANALYST',
            'marketing': 'WRITER',
            'seo': 'WRITER',
            'frontend': 'DEVELOPER',
            'backend': 'DEVELOPER',
            'ux': 'DESIGNER',
            'security': 'REVIEWER',
            'compliance': 'REVIEWER'
        }
    
    def load_config(self, config_path: str):
        """Load routing configuration from YAML file"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        if 'router' in config:
            router_config = config['router']
            self.rules = router_config.get('rules', [])
            self.industry_keywords = {}
            for rule in self.rules:
                for kw in rule.get('industry_keywords', []):
                    self.industry_keywords[kw] = rule['agent']
            
            self.auto_route_threshold = router_config.get('confidence', {}).get('auto_route_threshold', 0.80)
            self.ask_user_threshold = router_config.get('confidence', {}).get('ask_user_threshold', 0.50)
    
    def route(self, request: str) -> Tuple[str, float]:
        """
        Route a request to the appropriate agent.
        
        Returns:
            Tuple of (agent_name, confidence_score)
        """
        request_lower = request.lower()
        
        # Score each rule
        scores = []
        for rule in self.rules:
            score = self._calculate_score(request_lower, rule)
            if score > 0:
                scores.append((rule['agent'], score))
        
        if not scores:
            return ('ORG', 1.0)  # Default to supervisor
        
        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)
        
        agent, confidence = scores[0]
        
        # Check for industry keywords that might override
        for industry, forced_agent in self.industry_keywords.items():
            if industry in request_lower:
                return (forced_agent, confidence * 0.9)  # Slightly reduce confidence
        
        return (agent, confidence)
    
    def _calculate_score(self, request: str, rule: Dict) -> float:
        """Calculate matching score for a rule"""
        score = 0.0
        
        # Primary keywords (higher weight)
        for kw in rule.get('primary', []):
            if kw in request:
                score += 2.0
        
        # Secondary keywords (lower weight)
        for kw in rule.get('secondary', []):
            if kw in request:
                score += 1.0
        
        return score
    
    def should_ask_user(self, confidence: float) -> bool:
        """Determine if we should ask the user to confirm routing"""
        return confidence < self.auto_route_threshold


# Default router instance
default_router = Router()
