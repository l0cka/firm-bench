# Design

## Why this shape

Buyers compare systems on a frozen prompt pack. Harness plugins come later. v0 therefore centres on harness-agnostic Task JSON, separate Gold keys, and a scorer that reads run artifacts any harness can write.

## Domain model

**Task** (exportable): `id`, `practice_area`, `jurisdiction`, `archetype`, `prompt`, `inputs`, `expected_status_regex`, weighted `must_include` / `must_not`, `tools`, `provenance`, `author_notes`.

**Gold** (never exported): `hard_fail_triggers`, `acceptable_answer_families`, `prohibited_assumptions`, `required_escalations`, `instruction_truth`, `adjudication` (regex matchers aligned to Task items), `licence_notes`.

**Run**: `task_id`, `system_id`, `harness_id`, `prompt_hash`, `artifacts` (at least `text`), optional `tool_trace`, optional `error`.

**Score**: per-item marks, `rubric_score`, `status_ok`, non-compensable `hard_fail`, `boundary_breach`, `effective_pass`, plus suite aggregates.

## Scoring

Same weight formula as legal-skills rubrics:

`score = max(0, (Σ weights of must_include items present − Σ weights of must_not items breached) ÷ Σ must_include weights)`

A breached `must_not` item with weight ≥ 3 sets `boundary_breach`.

Hard-fail triggers are evaluated separately. Any hit sets `hard_fail`. Hard fails are non-compensable: `effective_pass` is false regardless of rubric score.

v0 adjudication is offline regex matchers in Gold so CI can score the canned system without a judge model. A later judge arm can reuse the same Task weights.

## Boundaries

- CLI and JSON files are the trust boundary. Pydantic parses into typed models.
- Scorers are pure functions over Task, Gold, and response text.
- Adapters only produce artifacts. They do not score.
- `export` copies tasks and fixtures, writes pack instructions, and refuses gold paths.

## Contamination and holdout

Prompts are public. Treat model outputs on this pack as contaminated for training if gold remains private. `holdout/` is reserved for later unpublished cases.

## Alternatives considered

1. **Typed models + pure scorers + thin CLI** (chosen). Small public surface; illegal states fail at parse.
2. **JSON Schema files + imperative scripts.** More flexible, weaker in-process types, easier for mismatched field drift across CLIs.

Plugins as first-class v0 packages were rejected. The pack contract is enough for a later thin wrapper per harness.
