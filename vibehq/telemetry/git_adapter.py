"""Universal Git Telemetry Adapter.
Watches git commits, branches, and staged diffs as a universal zero-config telemetry source.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


class GitTelemetryAdapter:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def get_git_info(self) -> dict[str, Any]:
        info: dict[str, Any] = {
            "branch": "main",
            "recentCommits": [],
            "uncommittedCount": 0,
        }
        if not (self.repo_path / ".git").exists():
            return info

        try:
            # Branch
            res = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )
            if res.returncode == 0 and res.stdout.strip():
                info["branch"] = res.stdout.strip()

            # Recent Commits
            log_res = subprocess.run(
                ["git", "log", "-n", "5", "--format=%h|%s|%cr"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )
            if log_res.returncode == 0:
                for line in log_res.stdout.strip().splitlines():
                    parts = line.split("|", 2)
                    if len(parts) == 3:
                        info["recentCommits"].append({
                            "hash": parts[0],
                            "message": parts[1],
                            "age": parts[2],
                        })

            # Uncommitted count
            diff_res = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )
            if diff_res.returncode == 0:
                lines = [l for l in diff_res.stdout.strip().splitlines() if l.strip()]
                info["uncommittedCount"] = len(lines)

        except Exception:
            pass

        return info

