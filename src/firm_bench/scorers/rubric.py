from __future__ import annotations

import re

from firm_bench.schema import Gold, ItemMark, Task


def _any_match(patterns: list[str], text: str) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) for pattern in patterns)


def score_rubric(task: Task, gold: Gold, text: str) -> dict:
    include_map = {m.item: m.any_of for m in gold.adjudication.include_matchers}
    not_map = {m.item: m.any_of for m in gold.adjudication.not_matchers}

    marks: list[ItemMark] = []
    got = 0.0
    for item in task.must_include:
        patterns = include_map.get(item.item, [])
        present = _any_match(patterns, text) if patterns else False
        if present:
            got += item.weight
        marks.append(
            ItemMark(item=item.item, weight=item.weight, present=present, kind="must_include")
        )

    lost = 0.0
    boundary_breach = False
    for item in task.must_not:
        patterns = not_map.get(item.item, [])
        breached = _any_match(patterns, text) if patterns else False
        if breached:
            lost += item.weight
            if item.weight >= 3:
                boundary_breach = True
        marks.append(
            ItemMark(item=item.item, weight=item.weight, present=breached, kind="must_not")
        )

    total = sum(i.weight for i in task.must_include) or 1.0
    rubric_score = max(0.0, (got - lost) / total)
    status_ok = bool(re.search(task.expected_status_regex, text))
    return {
        "rubric_score": rubric_score,
        "status_ok": status_ok,
        "boundary_breach": boundary_breach,
        "item_marks": marks,
    }
