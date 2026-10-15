from __future__ import annotations

import json
import shutil
from pathlib import Path

from firm_bench.paths import DEFAULT_AREA, area_root, fixtures_dir, tasks_dir
from firm_bench.validate import iter_task_paths, load_task, validate_area


EXPORT_FORBIDDEN_NAMES = frozenset({"gold"})


def build_export_tree(
    dest: Path,
    practice_area: str = DEFAULT_AREA,
    *,
    check: bool = True,
) -> Path:
    if check:
        errors = validate_area(practice_area)
        if errors:
            raise ValueError("validate failed:\n" + "\n".join(errors))

    pack = dest / practice_area
    if pack.exists():
        shutil.rmtree(pack)
    pack.mkdir(parents=True)

    tasks_out = pack / "tasks"
    tasks_out.mkdir()
    for path in iter_task_paths(practice_area):
        task = load_task(path)
        (tasks_out / path.name).write_text(
            task.model_dump_json(indent=2) + "\n",
            encoding="utf-8",
        )

    src_fixtures = fixtures_dir(practice_area)
    if src_fixtures.is_dir():
        shutil.copytree(src_fixtures, pack / "fixtures")

    run_instructions = {
        "practice_area": practice_area,
        "harness_contract": (
            "Load each tasks/*.json prompt and inputs. Write a run artifact JSON "
            "with task_id, system_id, harness_id, prompt_hash, and artifacts.text. "
            "Score offline against private gold keys that are never in this pack."
        ),
        "never_include": ["gold/"],
        "contamination_warning": (
            "Do not train on or publish model outputs from these prompts as "
            "training data if you also keep gold keys. Holdout cases live under "
            "holdout/ and are reserved."
        ),
    }
    (pack / "RUN.md").write_text(
        "# Pack run instructions\n\n"
        + json.dumps(run_instructions, indent=2)
        + "\n",
        encoding="utf-8",
    )
    (pack / "manifest.json").write_text(
        json.dumps(
            {
                "practice_area": practice_area,
                "task_ids": [p.stem for p in iter_task_paths(practice_area)],
                "contains_gold": False,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    _assert_no_gold(pack, area_root(practice_area))
    return pack


def _assert_no_gold(pack: Path, source_area: Path) -> None:
    for path in pack.rglob("*"):
        if path.is_dir() and path.name in EXPORT_FORBIDDEN_NAMES:
            raise RuntimeError(f"export emitted forbidden path: {path}")
        if path.is_file() and "gold" in path.parts:
            raise RuntimeError(f"export emitted gold path: {path}")
    source_gold = source_area / "gold"
    if not source_gold.is_dir():
        return
    for gpath in source_gold.glob("*.json"):
        leaked = pack / "gold" / gpath.name
        if leaked.exists():
            raise RuntimeError(f"export leaked gold file: {leaked}")
        gold_body = gpath.read_text(encoding="utf-8")
        for out in pack.rglob("*.json"):
            if out.read_text(encoding="utf-8") == gold_body:
                raise RuntimeError(f"export duplicated gold body into {out}")
