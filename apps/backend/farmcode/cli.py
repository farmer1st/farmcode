"""CLI interface for Farm Code (for testing)."""

from __future__ import annotations

import argparse
import asyncio

from farmcode.orchestrator import Orchestrator


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Farm Code - AI Agent Orchestration")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Create feature command
    create_parser = subparsers.add_parser("create", help="Create a new feature")
    create_parser.add_argument("title", help="Feature title")
    create_parser.add_argument("description", help="Feature description")

    # List features command
    subparsers.add_parser("list", help="List all features")

    # Show feature command
    show_parser = subparsers.add_parser("show", help="Show feature details")
    show_parser.add_argument("issue_number", type=int, help="GitHub issue number")

    # Approve gate command
    approve_parser = subparsers.add_parser("approve", help="Approve a gate phase")
    approve_parser.add_argument("issue_number", type=int, help="GitHub issue number")

    # Run orchestrator command
    run_parser = subparsers.add_parser("run", help="Run orchestrator polling loop")
    run_parser.add_argument(
        "--interval",
        type=int,
        default=10,
        help="Polling interval in seconds (default: 10)",
    )

    args = parser.parse_args()

    # Create orchestrator
    orchestrator = Orchestrator()

    if args.command == "create":
        print(f"Creating feature: {args.title}")
        state = orchestrator.create_feature(args.title, args.description)
        print(f"✅ Feature created: #{state.issue_number}")
        print(f"   Branch: {state.branch_name}")
        print(f"   Worktree: {state.worktree_path}")
        print(f"   Phase: {state.current_phase.value}")

    elif args.command == "list":
        features = orchestrator.list_all_features()
        if not features:
            print("No active features")
        else:
            print(f"Active features: {len(features)}")
            for state in features:
                print(f"  #{state.issue_number}: {state.title}")
                print(f"    Phase: {state.current_phase.value}")
                print(f"    Branch: {state.branch_name}")

    elif args.command == "show":
        state = orchestrator.get_feature_state(args.issue_number)
        if state is None:
            print(f"Feature #{args.issue_number} not found")
        else:
            print(f"Feature #{state.issue_number}: {state.title}")
            print(f"  Description: {state.description}")
            print(f"  Branch: {state.branch_name}")
            print(f"  Worktree: {state.worktree_path}")
            print(f"  Current Phase: {state.current_phase.value}")
            print(f"  Phase History:")
            for phase_state in state.phase_history:
                status = "✅" if phase_state.completed_at else "🔄"
                print(f"    {status} {phase_state.phase.value}")

    elif args.command == "approve":
        if orchestrator.approve_gate(args.issue_number):
            print(f"✅ Gate approved for #{args.issue_number}")
            state = orchestrator.get_feature_state(args.issue_number)
            if state:
                print(f"   Advanced to: {state.current_phase.value}")
        else:
            print(f"❌ Could not approve gate for #{args.issue_number}")

    elif args.command == "run":
        print(f"🚀 Starting orchestrator (polling every {args.interval}s)")
        print("Press Ctrl+C to stop")
        orchestrator.poll_interval = args.interval
        try:
            asyncio.run(orchestrator.run_polling_loop())
        except KeyboardInterrupt:
            print("\n✅ Orchestrator stopped")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
