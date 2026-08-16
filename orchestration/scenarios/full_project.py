"""
Scenario: Full Project
Complete orchestration: RESEARCH → DESIGNER → DEVELOPER → WRITER → REVIEWER → Client
"""

def create_workflow():
    return {
        'name': 'full_project',
        'agents': ['RESEARCH', 'DESIGNER', 'DEVELOPER', 'WRITER', 'REVIEWER'],
        'flow': 'sequential',
        'output_type': 'project'
    }