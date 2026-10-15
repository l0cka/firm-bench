from __future__ import annotations

import json
from pathlib import Path

import pytest

from firm_bench.export import build_export_tree
from firm_bench.paths import DEFAULT_AREA, REPO_ROOT
from firm_bench.run import run_area
from firm_bench.schema import RunRecord
from firm_bench.score import score_results, score_run
from firm_bench.scorers.hard_fail import evaluate_hard_fails
from firm_bench.scorers.rubric import score_rubric
from firm_bench.validate import gold_path_for, load_gold, load_task, validate_area


def test_validate_nsw_area() -> None:
    errors = validate_area(DEFAULT_AREA)
    assert errors == []


def test_export_strips_gold(tmp_path: Path) -> None:
    pack = build_export_tree(tmp_path / "out", DEFAULT_AREA)
    assert not (pack / "gold").exists()
    assert (pack / "tasks").is_dir()
    assert (pack / "manifest.json").is_file()
    manifest = json.loads((pack / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["contains_gold"] is False
    task_ids = {p.stem for p in (pack / "tasks").glob("*.json")}
    assert task_ids == {
        "nsw-estate-001",
        "nsw-estate-002",
        "nsw-estate-003",
        "nsw-estate-004",
        "nsw-estate-005",
        "nsw-estate-006",
    }
    blob = "\n".join(
        p.read_text(encoding="utf-8")
        for p in pack.rglob("*")
        if p.is_file()
    )
    assert '"hard_fail_triggers"' not in blob
    assert '"adjudication"' not in blob


def test_canned_run_scorecard(tmp_path: Path) -> None:
    out = run_area(DEFAULT_AREA, system_id="canned", out_dir=tmp_path / "runs")
    card = score_results(out, DEFAULT_AREA)
    assert len(card.cases) == 6
    assert (out / "scorecard.json").is_file()
    for case in card.cases:
        assert "hard_fail" in case.model_dump()
        assert "boundary_breach" in case.model_dump()
        assert case.hard_fail is False
        assert case.boundary_breach is False
        assert case.status_ok is True
        assert case.effective_pass is True


def test_hard_fail_non_compensable() -> None:
    task = load_task(
        REPO_ROOT
        / "practice_areas"
        / DEFAULT_AREA
        / "tasks"
        / "nsw-estate-002.json"
    )
    gold = load_gold(gold_path_for("nsw-estate-002"))
    bad = (
        "STATUS: DRAFT READY FOR SOLICITOR REVIEW\n"
        "one client only separate run NSW-WILL-PREC-v9 Firm Estates Library\n"
        "instruction table cannot be determined SOLICITOR REVIEW\n"
        "BOTH_SPOUSES_DRAFTED will for Lena and will for Theo\n"
    )
    rubric = score_rubric(task, gold, bad)
    hits = evaluate_hard_fails(gold, bad)
    run = RunRecord(
        task_id="nsw-estate-002",
        system_id="test",
        harness_id="test",
        prompt_hash="x",
        artifacts={"text": bad},
    )
    case = score_run(run)
    assert "both_spouses_one_run" in hits
    assert case.hard_fail is True
    assert case.effective_pass is False
    assert rubric["boundary_breach"] is True or case.hard_fail is True


def test_rubric_weight_formula() -> None:
    task = load_task(
        REPO_ROOT
        / "practice_areas"
        / DEFAULT_AREA
        / "tasks"
        / "nsw-estate-001.json"
    )
    gold = load_gold(gold_path_for("nsw-estate-001"))
    text = Path(
        REPO_ROOT
        / "practice_areas"
        / DEFAULT_AREA
        / "fixtures"
        / "canned"
        / "nsw-estate-001.txt"
    ).read_text(encoding="utf-8")
    result = score_rubric(task, gold, text)
    total = sum(i.weight for i in task.must_include)
    got = sum(i.weight for i in task.must_include if any(
        m.item == i.item and m.present for m in result["item_marks"] if m.kind == "must_include"
    ))
    lost = sum(i.weight for i in task.must_not if any(
        m.item == i.item and m.present for m in result["item_marks"] if m.kind == "must_not"
    ))
    expected = max(0.0, (got - lost) / total)
    assert result["rubric_score"] == pytest.approx(expected)
    assert result["rubric_score"] == pytest.approx(1.0)
