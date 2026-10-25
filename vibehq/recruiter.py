"""Auto-Recruiter Engine.
Hires the optimal team of specialist agents based on the project requirements,
persists the squad roster, and generates AI workspace directives (CLAUDE.md, GEMINI.md).
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from vibehq.analyzer import ProjectProfile


@dataclass
class HiredAgent:
    id: str
    name: str
    title: str
    department: str
    avatar: str
    color: str
    shirtColor: str
    pantsColor: str
    hairColor: str
    tag: str
    description: str
    skills: list[str]
    screenType: str
    deskFinish: str
    prop: str
    roomName: str
    roomFloor: str


class SquadRecruiter:
    def __init__(self, roles_path: Path | None = None):
        if roles_path is None:
            roles_path = Path(__file__).parent / "templates" / "roles.json"
        with open(roles_path, "r", encoding="utf-8") as f:
            self.role_catalog: dict[str, Any] = json.load(f)["roles"]

    def hire_squad(self, profile: ProjectProfile) -> list[HiredAgent]:
        """Automatically draft core specialists based on detected project profile."""
        hired_keys: list[str] = ["lead"]

        if profile.has_frontend:
            hired_keys.append("frontend")
        if profile.has_backend:
            hired_keys.append("backend")
        if profile.has_security_needs:
            hired_keys.append("security")
        if profile.has_tests:
            hired_keys.append("qa")
        if profile.has_docs:
            hired_keys.append("docs")
        if profile.has_cloud_infra:
            hired_keys.append("devops")
        if profile.has_mobile:
            hired_keys.append("mobile")

        squad: list[HiredAgent] = []
        for key in hired_keys:
            if key in self.role_catalog:
                r = self.role_catalog[key]
                squad.append(
                    HiredAgent(
                        id=r["id"],
                        name=r["defaultName"],
                        title=r["title"],
                        department=r["department"],
                        avatar=r["avatar"],
                        color=r["color"],
                        shirtColor=r["shirtColor"],
                        pantsColor=r["pantsColor"],
                        hairColor=r["hairColor"],
                        tag=r["tag"],
                        description=r["description"],
                        skills=r["skills"],
                        screenType=r["screenType"],
                        deskFinish=r["deskFinish"],
                        prop=r["prop"],
                        roomName=r["roomName"],
                        roomFloor=r["roomFloor"],
                    )
                )

        return squad

    def save_squad(self, squad: list[HiredAgent], target_dir: Path) -> Path:
        """Persist the hired squad configuration in .vibehq/squad.json."""
        vibe_dir = target_dir / ".vibehq"
        vibe_dir.mkdir(parents=True, exist_ok=True)
        out_file = vibe_dir / "squad.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump([asdict(a) for a in squad], f, indent=2)
        return out_file

    def generate_workspace_directives(self, squad: list[HiredAgent], profile: ProjectProfile, target_dir: Path) -> dict[str, Path]:
        """Generate synchronized CLAUDE.md, GEMINI.md, and AGENTS.md for the target project."""
        lines: list[str] = [
            f"# {profile.name} — VibeHQ Agent Squad Directives",
            "",
            f"> Auto-configured by **VibeHQ** for {profile.name}.",
            f"> Tech Stack: {', '.join(sorted(profile.languages | profile.frameworks)) or 'Universal'}",
            "",
            "## 👥 Active Engineering Squad & Role Allocations",
            "",
        ]

        for a in squad:
            lines.append(f"### {a.avatar} {a.name} — {a.title}")
            lines.append(f"- **Department:** `{a.department}` | **Badge:** `{a.tag}`")
            lines.append(f"- **Responsibilities:** {a.description}")
            if a.skills:
                lines.append(f"- **Equipped Skills:** {', '.join(f'`{s}`' for s in a.skills)}")
            lines.append("")

        lines.append("## 🏛️ Squad Collaboration Protocol")
        lines.append("- **Lead Orchestrator:** Breaks down high-level requests into crisp plans and coordinates specialist handoffs.")
        lines.append("- **Specialist Ownership:** Tasks are routed strictly to the designated specialist.")
        lines.append("- **Verification Before Completion:** Every code change is verified with automated tests and documentation updates.")
        lines.append("")

        directive_content = "\n".join(lines)

        written: dict[str, Path] = {}
        for fname in ("CLAUDE.md", "GEMINI.md", "AGENTS.md"):
            dest = target_dir / fname
            dest.write_text(directive_content, encoding="utf-8")
            written[fname] = dest

        return written
