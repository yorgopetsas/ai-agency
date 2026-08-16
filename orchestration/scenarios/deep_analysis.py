"""
Scenario: Deep Analysis
Parallel + Sequential: RESEARCH + ANALYST → WRITER → ORG
"""

def create_workflow():
    return {
        'name': 'deep_analysis',
        'agents': ['RESEARCH', 'ANALYST'],
        'flow': 'parallel',
        'output_type': 'report'
    }