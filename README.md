# firm-bench

Portable practice-area eval packs for legal AI systems. v0 covers **NSW estate planning** only.

Firms and individuals use a frozen Task pack to compare systems under the same prompts. The product is the pack and the scorer. The in-repo runner is a thin reference, not the product.

## Non-claims

- Not legal advice. Not a substitute for a NSW solicitor.
- Corpus is synthetic. No client files, firm precedents, or AustLII bulk text.
- No public leaderboard in v0. Scorecards are local JSON.
- ChatGPT, Cursor, and Claude plugins are **not shipped** in v0. See [docs/plugins.md](docs/plugins.md).

## Install

```bash
uv sync --all-extras
```

## Validate, run, score

```bash
uv run firm-bench validate
uv run firm-bench run --system canned --out results/demo
uv run firm-bench score results/demo
```

`canned` is an offline fixture system for CI. For a live OpenAI-compatible endpoint:

```bash
export OPENAI_API_KEY=...
# optional: OPENAI_BASE_URL, OPENAI_MODEL
uv run firm-bench run --system openai --out results/live
uv run firm-bench score results/live
```

## Export a portable pack (never includes gold)

```bash
uv run firm-bench export /tmp/firm-bench-pack
```

The pack contains tasks, fixtures, and run instructions. Gold keys stay in-repo for public synthetic cases and are stripped on export.

## Layout

| Path | Role |
|---|---|
| `practice_areas/nsw_estate_planning/tasks/` | Public tasks |
| `practice_areas/nsw_estate_planning/gold/` | Keys for scoring (export-stripped) |
| `practice_areas/nsw_estate_planning/fixtures/` | Synthetic library notes + canned answers |
| `holdout/` | Reserved; empty in v0 |
| `docs/design.md` | Domain model and scoring |
| `docs/practice-areas/nsw-estate-planning.md` | Case set |
| `docs/plugins.md` | Deferred multi-harness install |

## Licence

MIT, matched to [legal-skills](https://github.com/l0cka/legal-skills).
