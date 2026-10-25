# 🏢 VibeHQ

> **Autonomous Multi-Agent Virtual Headquarters & Procedural Isometric Office Visualizer for Vibe Coding.**

Turn invisible terminal logs, background subagents, and AI pair programming into a living, interactive, retro isometric software development campus.

---

## ⚡ What is VibeHQ?

When you're **"vibe coding"** with AI models (Claude Code, Antigravity, Cursor, OpenAI Swarm), your autonomous helpers operate invisibly in terminal logs or background subagents.

**VibeHQ** inspects any codebase, automatically recruits an elite team of specialized AI agents tailored to your exact tech stack, generates your AI workspace directives (`CLAUDE.md`, `GEMINI.md`, `AGENTS.md`), and **procedurally constructs a real-time isometric virtual office** that dynamically resizes to fit your staff!

---

## 🌟 Key Features

* **🔍 Zero-Config Codebase Profiler**: Automatically scans languages (TypeScript, Python, Go, Rust), frameworks (React, Next.js, FastAPI, Django), databases, test suites, and auth systems.
* **🤝 Autonomous Recruiter ("Auto-Hire")**:
  * React/Tailwind/CSS $\rightarrow$ Hires **Ava** (UI/UX Designer)
  * FastAPI/Django/Express $\rightarrow$ Hires **Felix** (Backend Engineer)
  * Sensitive Auth/APIs $\rightarrow$ Hires **Hunter** (Security Pentester)
  * Test Suites $\rightarrow$ Hires **Victor** (QA & Safety Auditor)
  * Changelogs & Docs $\rightarrow$ Hires **Archie** (Lead Code Chronicler)
  * Docker/Cloud $\rightarrow$ Hires **Nova** (DevOps & Infrastructure)
* **🏢 Procedural Campus Generator ("Auto-Resize")**:
  * **1 – 3 Staff**: `16 × 14` Cozy Startup Loft & Espresso Bar
  * **4 – 7 Staff**: `24 × 20` Mid-Size Studio with dedicated wings (Exec, Design Studio, Bullpen, SOC Lab, QA Lab, Data Vault, War Room)
  * **8+ Staff**: `32 × 26` Multi-Wing Enterprise Tech Campus
* **📡 Universal Pluggable Telemetry**: Connects seamlessly with Claude Code subagent logs, Antigravity/Gemini session events, or universal Git commit & file watchers.
* **🎮 Handcrafted 16-Bit Pixel Aesthetic**: Real-time matrix rain displays, oscilloscopes, ambient desk lighting, retro CRT scanline filters, sound effects, and confetti celebrations.

---

## 🚀 Quickstart

### Option 1: Python CLI
```bash
# Clone the repository
git clone https://github.com/your-username/vibehq.git
cd vibehq

# Install in editable mode
pip install -e .

# Navigate to any repository you are vibe coding in
cd ~/my-awesome-app

# 1. Analyze repository & auto-hire your agent squad
vibehq init

# 2. Launch your live virtual office
vibehq start
```

### Option 2: Node / npx
```bash
cd ~/my-awesome-app
npx vibehq init
npx vibehq start
```

---

## 📋 CLI Commands

| Command | Description |
| :--- | :--- |
| `vibehq init` | Analyzes repo stack, auto-hires core squad, writes `CLAUDE.md`, `GEMINI.md`, and persists `.vibehq/squad.json` |
| `vibehq status` | Prints active squad roster, tech profile, and campus grid archetype |
| `vibehq start` | Starts the telemetry daemon and launches the interactive visualizer in your browser (`http://localhost:8484`) |

---

## 🏗️ Architecture

```
vibehq/
├── pyproject.toml              # Modern Python package & CLI entrypoint
├── package.json                # npm wrapper for npx vibehq
├── bin/vibehq.js               # Node executable launcher
├── vibehq/
│   ├── analyzer.py             # Codebase Profiler (detects stack, frameworks, auth, tests)
│   ├── recruiter.py            # Auto-Hiring Engine (maps stack -> agents, emits directives)
│   ├── cli.py                  # Command-line interface (init, status, start)
│   ├── generator/
│   │   ├── layout.py           # Procedural Floorplan & Grid Generator (Auto-resizer)
│   │   └── visualizer.html     # Isometric Canvas Engine with live telemetry sync
│   ├── telemetry/
│   │   ├── server.py           # FastAPI visualizer & REST endpoints
│   │   ├── claude_adapter.py   # Claude Code session & subagent JSONL parser
│   │   └── git_adapter.py      # Universal Git commit & staged diff tracker
│   └── templates/
│       └── roles.json          # Catalog of pre-configured specialist personas
└── tests/
    └── test_vibehq.py          # Automated verification test suite
```

---

## 📜 License
MIT License. Created for the Vibe Coding community.

