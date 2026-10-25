"""VibeHQ Command Line Interface.
Run `vibehq init`, `vibehq start`, or `vibehq status` in any repository.
"""
from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path

from vibehq.analyzer import CodebaseAnalyzer
from vibehq.generator.layout import ProceduralLayoutGenerator
from vibehq.recruiter import SquadRecruiter
from vibehq.telemetry.server import create_app


def cmd_init(args: argparse.Namespace) -> None:
    repo = Path(args.dir).resolve()
    print(f"\n🔍 Analyzing repository at {repo}...")
    analyzer = CodebaseAnalyzer(repo)
    profile = analyzer.analyze()

    print(f"📦 Detected Project: {profile.name}")
    if profile.languages:
        print(f"   • Languages:  {', '.join(sorted(profile.languages))}")
    if profile.frameworks:
        print(f"   • Frameworks: {', '.join(sorted(profile.frameworks))}")
    if profile.databases:
        print(f"   • Databases:  {', '.join(sorted(profile.databases))}")

    print("\n🤝 Recruiting specialized core agents based on requirements...")
    recruiter = SquadRecruiter()
    squad = recruiter.hire_squad(profile)

    for a in squad:
        print(f"   [{a.avatar}] {a.name:<8} — {a.title} ({a.department})")

    squad_file = recruiter.save_squad(squad, repo)
    print(f"\n💾 Saved squad configuration to {squad_file.relative_to(repo)}")

    directives = recruiter.generate_workspace_directives(squad, profile, repo)
    print("📝 Generated workspace AI directives:")
    for fname, path in directives.items():
        print(f"   ✓ {fname}")

    layout_gen = ProceduralLayoutGenerator()
    layout = layout_gen.generate_layout(squad)
    print(f"\n🏢 Procedural Office Layout Generated:")
    print(f"   • Archetype:  {layout['mode']}")
    print(f"   • Grid Size:  {layout['grid']['width']}x{layout['grid']['height']} tiles")
    print(f"   • Total Desks:{len(layout['desks'])} dedicated workstations")
    print("\n🚀 Ready! Run `vibehq start` to open your interactive visual office.\n")


def cmd_status(args: argparse.Namespace) -> None:
    repo = Path(args.dir).resolve()
    analyzer = CodebaseAnalyzer(repo)
    profile = analyzer.analyze()
    recruiter = SquadRecruiter()
    squad = recruiter.hire_squad(profile)
    layout = ProceduralLayoutGenerator().generate_layout(squad)

    print(f"\n🏢 VibeHQ Status for {profile.name}:")
    print(f"   Staff count: {len(squad)} specialists | Office Grid: {layout['grid']['width']}x{layout['grid']['height']} ({layout['mode']})")
    print("\n   Active Squad:")
    for a in squad:
        print(f"   {a.avatar} {a.name:<8} {a.tag:<12} {a.title}")
    print()


def cmd_start(args: argparse.Namespace) -> None:
    import uvicorn

    repo = Path(args.dir).resolve()
    port = args.port
    host = args.host

    print(f"\n🏢 Starting VibeHQ Visualizer on http://{host}:{port} for {repo.name}...")
    app = create_app(repo)

    if not args.no_open:
        try:
            webbrowser.open(f"http://localhost:{port}")
        except Exception:
            pass

    uvicorn.run(app, host=host, port=port, log_level="warning")


def main() -> None:
    parser = argparse.ArgumentParser(prog="vibehq", description="Vibe Coding Agent Headquarters & Procedural Office Visualizer")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # init
    p_init = subparsers.add_parser("init", help="Analyze codebase and auto-hire core squad")
    p_init.add_argument("--dir", default=".", help="Repository root directory")

    # status
    p_status = subparsers.add_parser("status", help="Print active squad and layout status")
    p_status.add_argument("--dir", default=".", help="Repository root directory")

    # start
    p_start = subparsers.add_parser("start", help="Start the live virtual office server")
    p_start.add_argument("--dir", default=".", help="Repository root directory")
    p_start.add_argument("--host", default="127.0.0.1", help="Host interface")
    p_start.add_argument("--port", type=int, default=8484, help="Port to listen on")
    p_start.add_argument("--no-open", action="store_true", help="Do not open browser automatically")

    args = parser.parse_args()
    if args.command == "init":
        cmd_init(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "start":
        cmd_start(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

