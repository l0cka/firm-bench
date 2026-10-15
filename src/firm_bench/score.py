from __future__ import annotations

import json
from pathlib import Path

from firm_bench.paths import DEFAULT_AREA
from firm_bench.schema import CaseScore, RunRecord, Scorecard
from firm_bench.scorers import evaluate_hard_fails, score_rubric
from firm_bench.validate import gold_path_for, load_gold, load_task, tasks_dir


def score_run(
    run: RunRecord,
    practice_area: str = DEFAULT_AREA,
) -> CaseScore:
    task_path = tasks_dir(practice_area) / f"{run.task_id}.json"
    task = load_task(task_path)
    gold = load_gold(gold_path_for(run.task_id, practice_area))
    text = ""
    if isinstance(run.artifacts, dict):
        text = str(run.artifacts.get("text") or "")
    if run.error and not text:
        text = f"ERROR: {run.error}"

    rubric = score_rubric(task, gold, text)
    hard_fail_ids = evaluate_hard_fails(gold, text)
    hard_fail = bool(hard_fail_ids)
    effective_pass = (
        (not hard_fail)
        and rubric["status_ok"]
        and (not rubric["boundary_breach"])
        and rubric["rubric_score"] >= 0.7
    )
    return CaseScore(
        task_id=run.task_id,
        system_id=run.system_id,
        harness_id=run.harness_id,
        rubric_score=rubric["rubric_score"],
        status_ok=rubric["status_ok"],
        hard_fail=hard_fail,
        hard_fail_ids=hard_fail_ids,
        boundary_breach=rubric["boundary_breach"],
        item_marks=rubric["item_marks"],
        effective_pass=effective_pass,
    )


def load_runs(results_dir: Path) -> list[RunRecord]:
    jsonl = results_dir / "runs.jsonl"
    if jsonl.is_file():
        runs: list[RunRecord] = []
        for line in jsonl.read_text(encoding="utf-8").splitlines():
            if line.strip():
                runs.append(RunRecord.model_validate(json.loads(line)))
        return runs
    runs = []
    for path in sorted(results_dir.glob("*.json")):
        if path.name in {"scorecard.json"}:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            runs.extend(RunRecord.model_validate(row) for row in data)
        else:
            runs.append(RunRecord.model_validate(data))
    return runs


def score_results(
    results_dir: Path,
    practice_area: str = DEFAULT_AREA,
) -> Scorecard:
    runs = load_runs(results_dir)
    if not runs:
        raise ValueError(f"no run artifacts in {results_dir}")
    cases = [score_run(run, practice_area) for run in runs]
    n = len(cases)
    system_id = cases[0].system_id
    harness_id = cases[0].harness_id
    card = Scorecard(
        practice_area=practice_area,
        system_id=system_id,
        harness_id=harness_id,
        cases=cases,
        suite_rubric_mean=sum(c.rubric_score for c in cases) / n,
        suite_hard_fail_count=sum(1 for c in cases if c.hard_fail),
        suite_boundary_breach_count=sum(1 for c in cases if c.boundary_breach),
        suite_effective_pass_count=sum(1 for c in cases if c.effective_pass),
    )
    out = results_dir / "scorecard.json"
    out.write_text(card.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return card
