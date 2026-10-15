from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PRACTICE_AREAS = REPO_ROOT / "practice_areas"
HOLDOUT = REPO_ROOT / "holdout"
RESULTS = REPO_ROOT / "results"
DEFAULT_AREA = "nsw_estate_planning"


def area_root(practice_area: str = DEFAULT_AREA) -> Path:
    return PRACTICE_AREAS / practice_area


def tasks_dir(practice_area: str = DEFAULT_AREA) -> Path:
    return area_root(practice_area) / "tasks"


def gold_dir(practice_area: str = DEFAULT_AREA) -> Path:
    return area_root(practice_area) / "gold"


def fixtures_dir(practice_area: str = DEFAULT_AREA) -> Path:
    return area_root(practice_area) / "fixtures"
