# firm-bench agent notes

Public OSS eval packs for practice-area legal AI. v0 is NSW estate planning only.

## Layout

- `practice_areas/<id>/tasks` public Task JSON
- `practice_areas/<id>/gold` keys used by `score` (never exported)
- `src/firm_bench` CLI and scorers
- `docs/plugins.md` deferred ChatGPT / Cursor / Claude install story

## Rules

- No comments in code. Intent belongs in `docs/`.
- Synthetic facts only. Pin legislation URLs. Do not paste Act text.
- `export` must never emit `gold/`.
- Hard fails are non-compensable. Boundary breach is any `must_not` item with weight ≥ 3 that matches.
- Rubric score = max(0, (Σ include weights present − Σ must_not weights breached) ÷ Σ include weights).

## Commands

```bash
uv sync --all-extras
uv run firm-bench validate
uv run firm-bench run --system canned --out results/local
uv run firm-bench score results/local
uv run pytest -q
```
