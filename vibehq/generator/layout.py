"""Procedural Isometric Office Layout & Grid Generator.
Dynamically scales grid dimensions, carves departmental wings, and allocates
spacious, collision-free workstations based on the recruited staff size.
"""
from __future__ import annotations

from typing import Any

from vibehq.recruiter import HiredAgent


class ProceduralLayoutGenerator:
    """Generates procedural floorplan dimensions and rooms matching staff size."""

    def generate_layout(self, squad: list[HiredAgent]) -> dict[str, Any]:
        count = len(squad)

        # 1. Dynamically select campus archetype
        if count <= 3:
            grid_w, grid_h = 16, 14
            mode = "compact_loft"
        elif count <= 7:
            grid_w, grid_h = 24, 20
            mode = "studio_campus"
        else:
            grid_w, grid_h = 32, 26
            mode = "enterprise_campus"

        rooms: dict[str, dict[str, Any]] = {}
        desks: list[dict[str, Any]] = []

        # 2. Partition floorplan by archetype
        if mode == "compact_loft":
            # 16x14 Boutique Startup Loft
            rooms["lounge"] = {"name": "Espresso Café Lounge", "x1": 1, "y1": 1, "x2": 5, "y2": 5, "floor": "bistro_check"}
            rooms["executive"] = {"name": "Executive & Plan Desk", "x1": 6, "y1": 1, "x2": 15, "y2": 5, "floor": "mahogany"}
            rooms["bullpen"] = {"name": "Open-Plan Studio Bullpen", "x1": 1, "y1": 6, "x2": 15, "y2": 13, "floor": "oak_parquet"}

            # Desk slots
            available_slots = [
                {"x": 10.0, "y": 3.0, "zone": "executive"},
                {"x": 4.5, "y": 9.0, "zone": "bullpen"},
                {"x": 11.5, "y": 9.0, "zone": "bullpen"},
            ]

        elif mode == "studio_campus":
            # 24x20 Mid-Size Tech Studio (Current flagship)
            rooms["lounge"] = {"name": "Café Lounge & Breakroom", "x1": 1, "y1": 1, "x2": 6, "y2": 6, "floor": "bistro_check"}
            rooms["executive"] = {"name": "Executive Suite (Lead)", "x1": 7, "y1": 1, "x2": 14, "y2": 6, "floor": "mahogany"}
            rooms["serverVault"] = {"name": "Data Vault (Server Room)", "x1": 15, "y1": 1, "x2": 23, "y2": 6, "floor": "raised_grate"}
            rooms["uiStudio"] = {"name": "UI/UX Design Studio", "x1": 1, "y1": 7, "x2": 6, "y2": 13, "floor": "terrazzo"}
            rooms["bullpen"] = {"name": "Engineering Bullpen", "x1": 7, "y1": 7, "x2": 15, "y2": 13, "floor": "oak_parquet"}
            rooms["qaLab"] = {"name": "QA & Telecom Lab", "x1": 16, "y1": 7, "x2": 23, "y2": 13, "floor": "antistatic_cyan"}
            rooms["socLab"] = {"name": "Cyber SOC Enclave", "x1": 1, "y1": 14, "x2": 8, "y2": 19, "floor": "matrix_grid"}
            rooms["warRoom"] = {"name": "Executive War Room Amphitheater", "x1": 9, "y1": 14, "x2": 23, "y2": 19, "floor": "acoustic_navy"}

            available_slots = [
                {"x": 10.5, "y": 3.5, "zone": "executive"},
                {"x": 3.5, "y": 10.0, "zone": "uiStudio"},
                {"x": 9.5, "y": 9.5, "zone": "bullpen"},
                {"x": 13.0, "y": 11.0, "zone": "bullpen"},
                {"x": 4.5, "y": 16.5, "zone": "socLab"},
                {"x": 18.0, "y": 11.5, "zone": "qaLab"},
                {"x": 18.0, "y": 8.5, "zone": "qaLab"},
                {"x": 19.5, "y": 3.5, "zone": "serverVault"},
            ]

        else:
            # 32x26 Enterprise Tech Campus
            rooms["lounge"] = {"name": "Grand Atrium & Café", "x1": 1, "y1": 1, "x2": 8, "y2": 7, "floor": "bistro_check"}
            rooms["executive"] = {"name": "Executive Boardroom & Lead Suite", "x1": 9, "y1": 1, "x2": 20, "y2": 7, "floor": "mahogany"}
            rooms["serverVault"] = {"name": "Data Center & Cloud Vault", "x1": 21, "y1": 1, "x2": 31, "y2": 7, "floor": "raised_grate"}
            rooms["uiStudio"] = {"name": "Creative & UI/UX Lab", "x1": 1, "y1": 8, "x2": 9, "y2": 16, "floor": "terrazzo"}
            rooms["bullpen"] = {"name": "Core Engineering Bullpen", "x1": 10, "y1": 8, "x2": 21, "y2": 16, "floor": "oak_parquet"}
            rooms["qaLab"] = {"name": "QA & Test Verification Lab", "x1": 22, "y1": 8, "x2": 31, "y2": 16, "floor": "antistatic_cyan"}
            rooms["socLab"] = {"name": "Cyber SOC Defense Enclave", "x1": 1, "y1": 17, "x2": 11, "y2": 25, "floor": "matrix_grid"}
            rooms["warRoom"] = {"name": "Global War Room Amphitheater", "x1": 12, "y1": 17, "x2": 31, "y2": 25, "floor": "acoustic_navy"}

            available_slots = [
                {"x": 14.5, "y": 4.0, "zone": "executive"},
                {"x": 5.0, "y": 11.5, "zone": "uiStudio"},
                {"x": 13.0, "y": 11.0, "zone": "bullpen"},
                {"x": 17.0, "y": 12.5, "zone": "bullpen"},
                {"x": 5.5, "y": 20.5, "zone": "socLab"},
                {"x": 25.0, "y": 11.5, "zone": "qaLab"},
                {"x": 25.0, "y": 13.5, "zone": "qaLab"},
                {"x": 26.0, "y": 4.0, "zone": "serverVault"},
                {"x": 5.0, "y": 13.5, "zone": "uiStudio"},
                {"x": 13.0, "y": 13.5, "zone": "bullpen"},
            ]

        # 3. Assign hired specialists to appropriate room slots
        assigned_slots: set[int] = set()

        for agent in squad:
            # Find best matching slot in agent's designated department
            match_idx = None
            for idx, slot in enumerate(available_slots):
                if idx in assigned_slots:
                    continue
                if slot["zone"] == agent.department:
                    match_idx = idx
                    break

            # Fallback to any unassigned slot
            if match_idx is None:
                for idx, slot in enumerate(available_slots):
                    if idx not in assigned_slots:
                        match_idx = idx
                        break

            if match_idx is not None:
                assigned_slots.add(match_idx)
                s = available_slots[match_idx]
                desks.append({
                    "x": s["x"],
                    "y": s["y"],
                    "name": f"{agent.name}'s Station ({agent.title})",
                    "zone": s["zone"],
                    "agentName": agent.name,
                    "deskFinish": agent.deskFinish,
                    "prop": agent.prop,
                    "screenType": agent.screenType,
                })

        return {
            "mode": mode,
            "staffCount": count,
            "grid": {
                "width": grid_w,
                "height": grid_h,
                "tileW": 64,
                "tileH": 32,
            },
            "rooms": rooms,
            "desks": desks,
            "camera": {
                "focusGx": grid_w / 2,
                "focusGy": grid_h / 2,
                "defaultZoom": 1.0 if count >= 6 else 1.25,
            },
        }

