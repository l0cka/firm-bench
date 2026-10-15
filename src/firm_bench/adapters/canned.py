from __future__ import annotations

import json

from firm_bench.paths import DEFAULT_AREA, fixtures_dir
from firm_bench.schema import Task


class CannedAdapter:
    system_id = "canned"
    harness_id = "firm-bench-reference"

    def __init__(self, practice_area: str = DEFAULT_AREA) -> None:
        self.practice_area = practice_area
        self._root = fixtures_dir(practice_area) / "canned"

    def complete(self, task: Task) -> dict:
        path = self._root / f"{task.id}.txt"
        if not path.is_file():
            raise FileNotFoundError(f"missing canned fixture: {path}")
        text = path.read_text(encoding="utf-8")
        meta_path = self._root / f"{task.id}.meta.json"
        meta = {}
        if meta_path.is_file():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        return {"text": text, "fixture": path.name, "meta": meta}
