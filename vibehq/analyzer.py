"""Codebase Profiler & Requirement Analyzer.
Inspects an arbitrary repository to detect programming languages, frameworks,
databases, security requirements, documentation needs, and testing setup.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ProjectProfile:
    root_path: Path
    name: str
    languages: set[str] = field(default_factory=set)
    frameworks: set[str] = field(default_factory=set)
    databases: set[str] = field(default_factory=set)
    has_frontend: bool = False
    has_backend: bool = False
    has_security_needs: bool = False
    has_tests: bool = False
    has_docs: bool = False
    has_cloud_infra: bool = False
    has_mobile: bool = False
    detected_files: list[str] = field(default_factory=list)

    def summary(self) -> dict[str, any]:
        return {
            "name": self.name,
            "languages": sorted(self.languages),
            "frameworks": sorted(self.frameworks),
            "databases": sorted(self.databases),
            "has_frontend": self.has_frontend,
            "has_backend": self.has_backend,
            "has_security_needs": self.has_security_needs,
            "has_tests": self.has_tests,
            "has_docs": self.has_docs,
            "has_cloud_infra": self.has_cloud_infra,
            "has_mobile": self.has_mobile,
        }


class CodebaseAnalyzer:
    def __init__(self, root: str | Path = "."):
        self.root = Path(root).resolve()

    def analyze(self) -> ProjectProfile:
        profile = ProjectProfile(
            root_path=self.root,
            name=self.root.name,
        )

        # 1. Inspect package manifests & project files
        self._inspect_manifests(profile)

        # 2. Inspect directory layout
        self._inspect_directories(profile)

        # 3. Detect security requirements
        self._inspect_security(profile)

        return profile

    def _inspect_manifests(self, profile: ProjectProfile) -> None:
        # Node / JavaScript / TypeScript (root or frontend/client/ui directories)
        candidate_pkg_jsons = [
            self.root / "package.json",
            self.root / "frontend" / "package.json",
            self.root / "client" / "package.json",
            self.root / "ui" / "package.json",
            self.root / "web" / "package.json",
        ]
        for pkg_json in candidate_pkg_jsons:
            if pkg_json.exists():
                profile.languages.add("JavaScript")
                profile.has_frontend = True
                profile.detected_files.append(str(pkg_json.relative_to(self.root)))
                try:
                    with open(pkg_json, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                        if "typescript" in deps:
                            profile.languages.add("TypeScript")
                        if "react" in deps or "next" in deps:
                            profile.frameworks.add("React" if "react" in deps else "Next.js")
                            profile.has_frontend = True
                        if "vue" in deps or "nuxt" in deps:
                            profile.frameworks.add("Vue")
                            profile.has_frontend = True
                        if "tailwindcss" in deps:
                            profile.frameworks.add("TailwindCSS")
                        if "react-native" in deps or "expo" in deps:
                            profile.has_mobile = True
                            profile.frameworks.add("React Native")
                        if "express" in deps or "fastify" in deps or "nestjs" in deps:
                            profile.has_backend = True
                            profile.frameworks.add("Node.js Backend")
                        if any(t in deps for t in ("jest", "vitest", "mocha", "playwright", "cypress")):
                            profile.has_tests = True
                        if any(db in deps for t in ("prisma", "mongoose", "pg", "sqlite3", "mysql2") for db in deps if t in db):
                            profile.databases.add("Relational/NoSQL")
                except Exception:
                    pass

        # Python
        pyproject = self.root / "pyproject.toml"
        reqs = self.root / "requirements.txt"
        if pyproject.exists() or reqs.exists() or list(self.root.glob("*.py")):
            profile.languages.add("Python")
            if reqs.exists():
                profile.detected_files.append("requirements.txt")
                try:
                    content = reqs.read_text(encoding="utf-8", errors="ignore").lower()
                    if "fastapi" in content or "uvicorn" in content:
                        profile.frameworks.add("FastAPI")
                        profile.has_backend = True
                    if "django" in content:
                        profile.frameworks.add("Django")
                        profile.has_backend = True
                    if "flask" in content:
                        profile.frameworks.add("Flask")
                        profile.has_backend = True
                    if "sqlalchemy" in content or "tortoise" in content:
                        profile.databases.add("SQLAlchemy ORM")
                    if "pytest" in content:
                        profile.has_tests = True
                except Exception:
                    pass

        # Rust
        if (self.root / "Cargo.toml").exists():
            profile.languages.add("Rust")
            profile.has_backend = True
            profile.detected_files.append("Cargo.toml")

        # Go
        if (self.root / "go.mod").exists():
            profile.languages.add("Go")
            profile.has_backend = True
            profile.detected_files.append("go.mod")

    def _inspect_directories(self, profile: ProjectProfile) -> None:
        for entry in self.root.iterdir():
            if not entry.is_dir() or entry.name.startswith("."):
                continue

            name = entry.name.lower()
            if name in ("frontend", "ui", "web", "client", "src/components"):
                profile.has_frontend = True
            elif name in ("backend", "server", "api", "services", "telephony"):
                profile.has_backend = True
            elif name in ("tests", "test", "__tests__", "spec"):
                profile.has_tests = True
            elif name in ("docs", "documentation", "wiki"):
                profile.has_docs = True

        # Check for changelog or documentation files
        if (self.root / "CHANGELOG.md").exists() or (self.root / "README.md").exists():
            profile.has_docs = True

        # Check for cloud / infra
        if (self.root / "Dockerfile").exists() or (self.root / "docker-compose.yml").exists() or (self.root / ".github/workflows").exists():
            profile.has_cloud_infra = True

    def _inspect_security(self, profile: ProjectProfile) -> None:
        # Check if auth, security tests, or sensitive tokens exist
        if (self.root / ".env").exists() or (self.root / ".env.example").exists():
            profile.has_security_needs = True
        if list(self.root.glob("**/auth*.py")) or list(self.root.glob("**/test*security*.py")):
            profile.has_security_needs = True
        if profile.has_backend:
            # All web backends handling state benefit from an AppSec auditor
            profile.has_security_needs = True
