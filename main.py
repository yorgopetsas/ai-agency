#!/usr/bin/env python3
"""
AI Agency - Main Entry Point
==========================
Unified CLI for the AI Agency system.

Usage:
    python3 main.py --client <client_id>
    python3 main.py --task "Research AI trends"
    python3 main.py --interactive
    python3 main.py --status
"""

import os
import sys
import argparse
from datetime import datetime

# Add agency directory to path
AGENCY_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AGENCY_DIR)

# Import integration layer
from integrator import AgencyIntegrator, AgencyCLI, quick_research, quick_write, quick_develop


def print_header():
    """Print header"""
    print("\n" + "=" * 60)
    print(" AI AGENCY SYSTEM - Phase 7: UNIFY")
    print("=" * 60)


def cmd_status(agency: AgencyIntegrator):
    """Show system status"""
    print_header()

    print(f"\nClient: {agency.client_id}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Agents
    print("\n[AGENTS]")
    for agent in agency.get_agent_status():
        print(f"  {agent['name']}: {agent['role']} ({agent['status']})")

    # Usage
    stats = agency.get_usage_stats()
    print(f"\n[USAGE]")
    print(f"  Total Tasks: {stats.get('total_tasks', 0)}")
    print(f"  Period: {stats.get('period', 'N/A')}")


def cmd_task(agency: AgencyIntegrator, task: str):
    """Execute a task"""
    print_header()
    print(f"\nExecuting: {task}")

    result = agency.execute(task)

    print(f"\n[RESULT]")
    print(f"  Status: {result['status']}")
    if result.get('agents'):
        print(f"  Agents: {', '.join(result['agents'])}")
    if result.get('execution'):
        print(f"  Execution: {result['execution']}")


def cmd_research(agency: AgencyIntegrator, query: str):
    """Quick research"""
    result = quick_research(query, agency.client_id)
    print(f"\nResearch completed: {result['status']}")
    if result.get('rag_context'):
        for agent, docs in result['rag_context'].items():
            if docs:
                print(f"  {agent}: {len(docs)} documents found")


def cmd_write(agency: AgencyIntegrator, topic: str):
    """Quick write"""
    result = quick_write(topic, agency.client_id)
    print(f"\nWriting completed: {result['status']}")


def cmd_develop(agency: AgencyIntegrator, spec: str):
    """Quick develop"""
    result = quick_develop(spec, agency.client_id)
    print(f"\nDevelopment completed: {result['status']}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI Agency System - Phase 7")

    parser.add_argument("--client", default="internal", help="Client ID")
    parser.add_argument("--task", help="Task to execute")
    parser.add_argument("--research", help="Quick research query")
    parser.add_argument("--write", help="Quick write topic")
    parser.add_argument("--develop", help="Quick development spec")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--version", action="version", version="1.0.0 (Phase 7: UNIFY)")

    args = parser.parse_args()

    # Initialize agency
    print_header()
    print(f"\nStarting AI Agency for client: {args.client}")

    agency = AgencyIntegrator(client_id=args.client)

    # Execute commands
    if args.status:
        cmd_status(agency)
    elif args.task:
        cmd_task(agency, args.task)
    elif args.research:
        cmd_research(agency, args.research)
    elif args.write:
        cmd_write(agency, args.write)
    elif args.develop:
        cmd_develop(agency, args.develop)
    elif args.interactive:
        cli = AgencyCLI()
        cli.integrator = agency
        cli.run_interactive()
    else:
        print("\nNo command specified. Use --help for options.")
        cmd_status(agency)


if __name__ == "__main__":
    main()