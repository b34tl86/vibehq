"""VibeHQ Telemetry & Visualizer Server.
Serves the procedural isometric canvas visualizer and streams real-time agent telemetry.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from vibehq.analyzer import CodebaseAnalyzer
from vibehq.generator.layout import ProceduralLayoutGenerator
from vibehq.recruiter import HiredAgent, SquadRecruiter
from vibehq.telemetry.claude_adapter import ClaudeCodeAdapter
from vibehq.telemetry.git_adapter import GitTelemetryAdapter


def create_app(repo_root: Path | None = None) -> FastAPI:
    if repo_root is None:
        repo_root = Path.cwd()
    repo_root = repo_root.resolve()

    app = FastAPI(title="VibeHQ", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    recruiter = SquadRecruiter()
    layout_gen = ProceduralLayoutGenerator()
    claude_adapter = ClaudeCodeAdapter(repo_root)
    git_adapter = GitTelemetryAdapter(repo_root)

    def load_or_create_squad() -> list[HiredAgent]:
        squad_file = repo_root / ".vibehq" / "squad.json"
        if squad_file.exists():
            try:
                with open(squad_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [HiredAgent(**d) for d in data]
            except Exception:
                pass

        # Auto-hire based on codebase analysis
        analyzer = CodebaseAnalyzer(repo_root)
        profile = analyzer.analyze()
        squad = recruiter.hire_squad(profile)
        recruiter.save_squad(squad, repo_root)
        recruiter.generate_workspace_directives(squad, profile, repo_root)
        return squad

    @app.get("/api/squad")
    def get_squad(response: Response) -> dict[str, Any]:
        response.headers["Access-Control-Allow-Origin"] = "*"
        squad = load_or_create_squad()
        layout = layout_gen.generate_layout(squad)
        return {
            "squad": [asdict(a) for a in squad],
            "layout": layout,
        }

    @app.get("/api/agent-office/live")
    def get_live_telemetry(response: Response) -> dict[str, Any]:
        response.headers["Access-Control-Allow-Origin"] = "*"
        live = claude_adapter.get_live_state()
        live["git"] = git_adapter.get_git_info()
        return live

    @app.get("/", response_class=HTMLResponse)
    def get_visualizer() -> str:
        html_path = Path(__file__).parent.parent / "generator" / "visualizer.html"
        if html_path.exists():
            return html_path.read_text(encoding="utf-8")
        return "<h1>VibeHQ Visualizer Template Not Found</h1>"

    return app

