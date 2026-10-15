from __future__ import annotations

import json
from pathlib import Path

from firm_bench.paths import DEFAULT_AREA, fixtures_dir, gold_dir, tasks_dir
from firm_bench.schema import Gold, Task


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_task_paths(practice_area: str = DEFAULT_AREA) -> list[Path]:
    root = tasks_dir(practice_area)
    if not root.is_dir():
        raise FileNotFoundError(f"missing tasks directory: {root}")
    return sorted(root.glob("*.json"))


def load_task(path: Path) -> Task:
    return Task.model_validate(load_json(path))


def load_gold(path: Path) -> Gold:
    return Gold.model_validate(load_json(path))


def gold_path_for(task_id: str, practice_area: str = DEFAULT_AREA) -> Path:
    return gold_dir(practice_area) / f"{task_id}.json"


def validate_area(practice_area: str = DEFAULT_AREA) -> list[str]:
    errors: list[str] = []
    task_paths = iter_task_paths(practice_area)
    if not task_paths:
        errors.append(f"no tasks under {tasks_dir(practice_area)}")
        return errors

    seen: set[str] = set()
    include_items: dict[str, set[str]] = {}
    not_items: dict[str, set[str]] = {}

    for path in task_paths:
        try:
            task = load_task(path)
        except Exception as exc:
            errors.append(f"{path}: {exc}")
            continue
        if task.id in seen:
            errors.append(f"duplicate task id: {task.id}")
        seen.add(task.id)
        if path.stem != task.id:
            errors.append(f"{path}: filename stem must match id {task.id!r}")
        if task.practice_area != practice_area:
            errors.append(
                f"{task.id}: practice_area {task.practice_area!r} != {practice_area!r}"
            )
        gpath = gold_path_for(task.id, practice_area)
        if not gpath.is_file():
            errors.append(f"{task.id}: missing gold file {gpath}")
            continue
        try:
            gold = load_gold(gpath)
        except Exception as exc:
            errors.append(f"{gpath}: {exc}")
            continue
        if gold.id != task.id:
            errors.append(f"{gpath}: gold.id {gold.id!r} != task.id {task.id!r}")
        include_items[task.id] = {i.item for i in task.must_include}
        not_items[task.id] = {i.item for i in task.must_not}
        for matcher in gold.adjudication.include_matchers:
            if matcher.item not in include_items[task.id]:
                errors.append(
                    f"{task.id}: include matcher unknown item {matcher.item!r}"
                )
            if not matcher.any_of:
                errors.append(f"{task.id}: empty include matcher for {matcher.item!r}")
        for matcher in gold.adjudication.not_matchers:
            if matcher.item not in not_items[task.id]:
                errors.append(f"{task.id}: not matcher unknown item {matcher.item!r}")
            if not matcher.any_of:
                errors.append(f"{task.id}: empty not matcher for {matcher.item!r}")
        covered_include = {m.item for m in gold.adjudication.include_matchers}
        missing_include = include_items[task.id] - covered_include
        if missing_include:
            errors.append(
                f"{task.id}: adjudication missing include matchers for {sorted(missing_include)}"
            )
        covered_not = {m.item for m in gold.adjudication.not_matchers}
        missing_not = not_items[task.id] - covered_not
        if missing_not:
            errors.append(
                f"{task.id}: adjudication missing not matchers for {sorted(missing_not)}"
            )
        for trigger in gold.hard_fail_triggers:
            if not trigger.any_of:
                errors.append(f"{task.id}: hard_fail {trigger.id!r} has empty any_of")

    fixtures = fixtures_dir(practice_area)
    if not fixtures.is_dir():
        errors.append(f"missing fixtures directory: {fixtures}")

    return errors
