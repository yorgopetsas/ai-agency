"""
Scenario: Build Feature
Parallel flow: ORG → DEVELOPER + REVIEWER (parallel) → ORG
"""

def create_workflow():
    return {
        'name': 'build_feature',
        'agents': ['DEVELOPER', 'REVIEWER'],
        'flow': 'parallel',
        'output_type': 'code'
    }