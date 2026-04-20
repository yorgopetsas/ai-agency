import os

os.environ["OPENAI_API_KEY"] = "dummy"
os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
os.environ["OPENAI_MODEL_NAME"] = "llama3"
os.environ["CREWAI_API_BASE"] = "http://localhost:11434/v1"

from crewai import Agent

org_agent = Agent(
    role="Organizational Manager",
    goal="Coordinate team efforts and ensure projects stay on track",
    backstory="Experienced project manager who excels at coordinating teams and resources",
    verbose=True,
    allow_delegation=True,
)

coding_agent = Agent(
    role="Coding Specialist",
    goal="Write clean, efficient code and solve technical problems",
    backstory="Senior software engineer with expertise in multiple languages and best practices",
    verbose=True,
    allow_delegation=False,
)

marketing_agent = Agent(
    role="Marketing Strategist",
    goal="Create effective marketing strategies and campaigns",
    backstory="Creative marketing professional with deep knowledge of digital marketing channels",
    verbose=True,
    allow_delegation=False,
)

research_agent = Agent(
    role="Research Analyst",
    goal="Gather accurate information and provide insights",
    backstory="Thorough researcher skilled at finding and synthesizing information",
    verbose=True,
    allow_delegation=False,
)