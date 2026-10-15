from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from firm_bench.adapters.canned import CannedAdapter
from firm_bench.adapters.openai_compatible import OpenAICompatibleAdapter
from firm_bench.paths import DEFAULT_AREA, RESULTS
from firm_bench.schema import RunRecord, Task
from firm_bench.validate import iter_task_paths, load_task


def prompt_hash(task: Task) -> str:
    payload = json.dumps(
        {"id": task.id, "prompt": task.prompt, "inputs": task.inputs},
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def get_adapter(system_id: str, practice_area: str):
    if system_id == "canned":
        return CannedAdapter(practice_area)
    if system_id in {"openai", "openai-compatible"}:
        return OpenAICompatibleAdapter()
    raise ValueError(f"unknown system_id: {system_id}")


def run_area(
    practice_area: str = DEFAULT_AREA,
    *,
    system_id: str = "canned",
    out_dir: Path | None = None,
) -> Path:
    adapter = get_adapter(system_id, practice_area)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    results = out_dir or (RESULTS / f"{practice_area}-{adapter.system_id}-{stamp}")
    results.mkdir(parents=True, exist_ok=True)

    runs: list[RunRecord] = []
    for path in iter_task_paths(practice_area):
        task = load_task(path)
        error = None
        artifacts: dict = {}
        try:
            artifacts = adapter.complete(task)
        except Exception as exc:
            error = str(exc)
            artifacts = {"text": ""}
        record = RunRecord(
            task_id=task.id,
            system_id=adapter.system_id,
            harness_id=adapter.harness_id,
            prompt_hash=prompt_hash(task),
            artifacts=artifacts,
            error=error,
        )
        runs.append(record)
        (results / f"{task.id}.json").write_text(
            record.model_dump_json(indent=2) + "\n",
            encoding="utf-8",
        )

    (results / "runs.jsonl").write_text(
        "".join(r.model_dump_json() + "\n" for r in runs),
        encoding="utf-8",
    )
    return results
