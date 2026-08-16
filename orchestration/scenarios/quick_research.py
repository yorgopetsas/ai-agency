"""
Scenario: Quick Research
Simple sequential flow: REQUEST → RESEARCH → Client
"""

def create_workflow():
    return {
        'name': 'quick_research',
        'agents': ['RESEARCH'],
        'flow': 'sequential',
        'output_type': 'summary'
    }

def execute(context):
    """Execute quick research workflow"""
    # Placeholder for execution logic
    return {'status': 'complete'}
