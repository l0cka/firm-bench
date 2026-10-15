from __future__ import annotations

import re

from firm_bench.schema import Gold


def evaluate_hard_fails(gold: Gold, text: str) -> list[str]:
    hit: list[str] = []
    for trigger in gold.hard_fail_triggers:
        if any(
            re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
            for pattern in trigger.any_of
        ):
            hit.append(trigger.id)
    return hit
