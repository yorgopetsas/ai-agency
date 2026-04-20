from crewai import Task
from agents import org_agent, coding_agent, marketing_agent, research_agent

coordination_task = Task(
    description="Coordinate the team to complete the given project or request",
    agent=org_agent,
    expected_output="Project plan with assigned tasks and timeline",
)

coding_task = Task(
    description="Write code, debug issues, or provide technical solutions",
    agent=coding_agent,
    expected_output="Working code with explanation",
)

marketing_task = Task(
    description="Create marketing content, strategies, or campaigns",
    agent=marketing_agent,
    expected_output="Marketing plan or content deliverables",
)

research_task = Task(
    description="Research topics, gather data, or find information",
    agent=research_agent,
    expected_output="Comprehensive research findings",
)