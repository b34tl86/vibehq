"""Comprehensive unit and integration test suite for VibeHQ."""
from pathlib import Path

from fastapi.testclient import TestClient

from vibehq.analyzer import CodebaseAnalyzer, ProjectProfile
from vibehq.generator.layout import ProceduralLayoutGenerator
from vibehq.recruiter import SquadRecruiter
from vibehq.telemetry.server import create_app


def test_analyzer_on_keevah():
    """Verify analyzer correctly extracts stack details from Keevah."""
    keevah_dir = Path("/Users/techadmin/Documents/Project/Keevah")
    analyzer = CodebaseAnalyzer(keevah_dir)
    profile = analyzer.analyze()

    assert profile.name == "Keevah"
    assert "Python" in profile.languages
    assert "TypeScript" in profile.languages or "JavaScript" in profile.languages
    assert profile.has_frontend is True
    assert profile.has_backend is True
    assert profile.has_security_needs is True
    assert profile.has_docs is True
    assert profile.has_tests is True


def test_recruiter_auto_hires_core_squad():
    """Verify recruiter drafts the expected specialists for full-stack app."""
    profile = ProjectProfile(
        root_path=Path("/tmp/dummy"),
        name="TestApp",
        has_frontend=True,
        has_backend=True,
        has_security_needs=True,
        has_tests=True,
        has_docs=True,
    )
    recruiter = SquadRecruiter()
    squad = recruiter.hire_squad(profile)
    names = [a.name for a in squad]

    # Should include Orchestrator, Frontend, Backend, Security, QA, Docs
    assert "Claude" in names
    assert "Ava" in names
    assert "Felix" in names
    assert "Hunter" in names
    assert "Victor" in names
    assert "Archie" in names
    assert len(squad) == 6


def test_procedural_layout_scaling():
    """Verify procedural layout scales dimensions based on staff size."""
    layout_gen = ProceduralLayoutGenerator()
    recruiter = SquadRecruiter()

    # 1. Small team (2 people) -> compact loft
    p_small = ProjectProfile(root_path=Path("/tmp"), name="Small", has_backend=True)
    squad_small = recruiter.hire_squad(p_small)
    layout_small = layout_gen.generate_layout(squad_small)
    assert layout_small["mode"] == "compact_loft"
    assert layout_small["grid"]["width"] == 16
    assert layout_small["grid"]["height"] == 14
    assert len(layout_small["desks"]) == len(squad_small)

    # 2. Medium team (6 people) -> studio campus
    p_med = ProjectProfile(
        root_path=Path("/tmp"),
        name="Med",
        has_frontend=True,
        has_backend=True,
        has_security_needs=True,
        has_tests=True,
        has_docs=True,
    )
    squad_med = recruiter.hire_squad(p_med)
    layout_med = layout_gen.generate_layout(squad_med)
    assert layout_med["mode"] == "studio_campus"
    assert layout_med["grid"]["width"] == 24
    assert layout_med["grid"]["height"] == 20
    assert len(layout_med["desks"]) == len(squad_med)

    # 3. Enterprise team (8+ people) -> enterprise campus
    p_large = ProjectProfile(
        root_path=Path("/tmp"),
        name="Large",
        has_frontend=True,
        has_backend=True,
        has_security_needs=True,
        has_tests=True,
        has_docs=True,
        has_cloud_infra=True,
        has_mobile=True,
    )
    squad_large = recruiter.hire_squad(p_large)
    layout_large = layout_gen.generate_layout(squad_large)
    assert layout_large["mode"] == "enterprise_campus"
    assert layout_large["grid"]["width"] == 32
    assert layout_large["grid"]["height"] == 26
    assert len(layout_large["desks"]) == len(squad_large)


def test_server_api_endpoints():
    """Verify server exposes /api/squad and /api/agent-office/live correctly."""
    app = create_app(Path("/Users/techadmin/Documents/Project/Keevah"))
    client = TestClient(app)

    # Test /api/squad
    res_squad = client.get("/api/squad")
    assert res_squad.status_code == 200
    data_squad = res_squad.json()
    assert "squad" in data_squad
    assert "layout" in data_squad
    assert len(data_squad["squad"]) >= 5

    # Test /api/agent-office/live
    res_live = client.get("/api/agent-office/live")
    assert res_live.status_code == 200
    data_live = res_live.json()
    assert "git" in data_live
    assert "metrics" in data_live
    assert "subagents" in data_live

    # Test / (visualizer HTML)
    res_html = client.get("/")
    assert res_html.status_code == 200
    assert "<canvas" in res_html.text or "viewport" in res_html.text

