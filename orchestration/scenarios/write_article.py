"""
Scenario: Write Article
Sequential flow: RESEARCH → WRITER → DESIGNER → REVIEWER → Client
"""

def create_workflow():
    return {
        'name': 'write_article',
        'agents': ['RESEARCH', 'WRITER', 'DESIGNER', 'REVIEWER'],
        'flow': 'sequential',
        'output_type': 'article'
    }