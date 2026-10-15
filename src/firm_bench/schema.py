from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class WeightedItem(BaseModel):
    item: str
    weight: float


class Task(BaseModel):
    id: str
    practice_area: str
    jurisdiction: str
    archetype: str
    prompt: str
    inputs: list[dict[str, Any]] = Field(default_factory=list)
    expected_status_regex: str
    must_include: list[WeightedItem]
    must_not: list[WeightedItem]
    tools: list[str] = Field(default_factory=list)
    provenance: list[str] = Field(default_factory=list)
    author_notes: str = ""

    @field_validator("must_include")
    @classmethod
    def must_include_nonempty(cls, value: list[WeightedItem]) -> list[WeightedItem]:
        if not value:
            raise ValueError("must_include must contain at least one item")
        return value


class PatternMatcher(BaseModel):
    item: str
    any_of: list[str]


class HardFailTrigger(BaseModel):
    id: str
    description: str
    any_of: list[str]


class Adjudication(BaseModel):
    include_matchers: list[PatternMatcher] = Field(default_factory=list)
    not_matchers: list[PatternMatcher] = Field(default_factory=list)


class Gold(BaseModel):
    id: str
    hard_fail_triggers: list[HardFailTrigger] = Field(default_factory=list)
    acceptable_answer_families: list[str] = Field(default_factory=list)
    prohibited_assumptions: list[str] = Field(default_factory=list)
    required_escalations: list[str] = Field(default_factory=list)
    instruction_truth: dict[str, Any] = Field(default_factory=dict)
    adjudication: Adjudication = Field(default_factory=Adjudication)
    licence_notes: str = ""


class RunRecord(BaseModel):
    task_id: str
    system_id: str
    harness_id: str
    prompt_hash: str
    artifacts: dict[str, Any]
    tool_trace: list[dict[str, Any]] | None = None
    error: str | None = None


class ItemMark(BaseModel):
    item: str
    weight: float
    present: bool
    kind: str


class CaseScore(BaseModel):
    task_id: str
    system_id: str
    harness_id: str
    rubric_score: float
    status_ok: bool
    hard_fail: bool
    hard_fail_ids: list[str] = Field(default_factory=list)
    boundary_breach: bool
    item_marks: list[ItemMark] = Field(default_factory=list)
    effective_pass: bool


class Scorecard(BaseModel):
    practice_area: str
    system_id: str
    harness_id: str
    cases: list[CaseScore]
    suite_rubric_mean: float
    suite_hard_fail_count: int
    suite_boundary_breach_count: int
    suite_effective_pass_count: int
