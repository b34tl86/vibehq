"""Claude Code Telemetry Adapter.
Parses active Claude Code subagent JSONLs and session event streams.
"""
from __future__ import annotations

import glob
import json
import os
from pathlib import Path
from typing import Any


class ClaudeCodeAdapter:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path.resolve()
        self.claude_home = Path.home() / ".claude"
        self.projects_dir = self.claude_home / "projects"

    def find_project_dir(self) -> Path | None:
        if not self.projects_dir.exists():
            return None
        repo_sanitized = str(self.repo_path).replace("/", "-")
        target = self.projects_dir / repo_sanitized
        if target.exists():
            return target
        for p in self.projects_dir.iterdir():
            if p.is_dir() and repo_sanitized in p.name:
                return p
        return None

    def get_live_state(self) -> dict[str, Any]:
        state: dict[str, Any] = {
            "connected": False,
            "session": None,
            "subagents": [],
            "recentEvents": [],
            "metrics": {"totalToolCalls": 0, "activeSubagents": 0},
        }

        project_dir = self.find_project_dir()
        if not project_dir:
            return state

        # 1. Discover session info
        session_status = "idle"
        session_pid = None
        session_files = sorted(glob.glob(str(self.claude_home / "sessions" / "*.json")), key=os.path.getmtime, reverse=True)
        if session_files:
            try:
                with open(session_files[0], "r", encoding="utf-8") as f:
                    s_data = json.load(f)
                    session_status = s_data.get("status", "idle")
                    session_pid = s_data.get("pid")
            except Exception:
                pass

        # 2. Main session JSONL
        jsonl_files = sorted(glob.glob(str(project_dir / "*.jsonl")), key=os.path.getmtime, reverse=True)
        if not jsonl_files:
            return state

        main_jsonl = jsonl_files[0]
        session_id = Path(main_jsonl).stem
        state["connected"] = True
        state["session"] = {
            "id": session_id,
            "pid": session_pid,
            "status": session_status,
            "is_working": session_status == "busy",
            "model": "Claude Opus 5.5",
        }

        # 3. Read events from main log tail
        events: list[dict[str, Any]] = []
        tool_count = 0
        try:
            with open(main_jsonl, "rb") as f:
                f.seek(0, os.SEEK_END)
                size = f.tell()
                seek_pos = max(0, size - 131072)
                f.seek(seek_pos)
                lines = f.readlines()
                if seek_pos > 0 and lines:
                    lines = lines[1:]

                for line in lines:
                    try:
                        d = json.loads(line.decode("utf-8", errors="ignore"))
                        tp = d.get("type")
                        ts = d.get("timestamp", "")
                        if tp == "assistant":
                            msg = d.get("message", {})
                            for item in msg.get("content", []):
                                if item.get("type") == "tool_use":
                                    tool_count += 1
                                    name = item.get("name")
                                    inp = item.get("input", {})
                                    detail = ""
                                    if name == "Bash":
                                        detail = inp.get("description") or inp.get("command", "")[:80]
                                    elif name in ("Read", "Edit", "Write"):
                                        p = inp.get("file_path", "")
                                        detail = f"{name} {Path(p).name}" if p else name
                                    elif name == "Agent":
                                        detail = inp.get("description") or "Dispatched subagent"
                                    else:
                                        detail = name

                                    events.append({
                                        "source": "Claude Orchestrator",
                                        "tool": name,
                                        "detail": detail,
                                        "timestamp": ts,
                                    })
                    except Exception:
                        continue
        except Exception:
            pass

        state["recentEvents"] = events[-15:]
        state["metrics"]["totalToolCalls"] = tool_count

        # 4. Read active subagents
        subagents_dir = project_dir / session_id / "subagents"
        if subagents_dir.exists():
            import time
            now = time.time()
            sub_files = sorted(glob.glob(str(subagents_dir / "agent-*.jsonl")), key=os.path.getmtime, reverse=True)
            active_count = 0
            for sf in sub_files[:10]:
                sub_id = Path(sf).stem.replace("agent-", "")
                age_seconds = now - os.path.getmtime(sf)
                sub_state: dict[str, Any] = {
                    "id": sub_id,
                    "name": f"Engineer {sub_id[:4].upper()}",
                    "role": "Assigned Subtask",
                    "task": "Working on assigned subtask...",
                    "status": "active",
                    "lastTool": "init",
                    "toolCount": 0,
                    "files": [],
                }
                try:
                    with open(sf, "rb") as f:
                        for line in f:
                            try:
                                d = json.loads(line.decode("utf-8", errors="ignore"))
                                if d.get("type") == "user" and sub_state["task"] == "Working on assigned subtask...":
                                    content = d.get("message", {}).get("content", "")
                                    if isinstance(content, str):
                                        sub_state["task"] = content.strip().split("\n")[0][:70]
                                elif d.get("type") == "assistant":
                                    for item in d.get("message", {}).get("content", []):
                                        if item.get("type") == "tool_use":
                                            sub_state["toolCount"] += 1
                                            sub_state["lastTool"] = item.get("name")
                                            if item.get("name") == "SubagentHandback":
                                                sub_state["status"] = "completed"
                            except Exception:
                                continue
                except Exception:
                    pass

                sub_state["is_working"] = sub_state["status"] == "active"
                if sub_state["status"] == "active":
                    active_count += 1
                    state["subagents"].append(sub_state)
                elif age_seconds < 60:
                    state["subagents"].append(sub_state)

            state["metrics"]["activeSubagents"] = active_count

        return state
