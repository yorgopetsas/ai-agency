from crewai import Crew, Process
from tasks import coordination_task, coding_task, marketing_task, research_task
from agents import org_agent, coding_agent, marketing_agent, research_agent

agency_crew = Crew(
    agents=[coding_agent, marketing_agent, research_agent],
    tasks=[coordination_task, coding_task, marketing_task, research_task],
    process=Process.hierarchical,
    manager_agent=org_agent,
)

if __name__ == "__main__":
    result = agency_crew.kickoff()
    print(result)