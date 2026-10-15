# Plugins (deferred)

v0 does not ship ChatGPT, Cursor, or Claude plugin packages.

## Pack contract plugins must wrap

A future plugin is a thin installer that:

1. Loads exported Task JSON (and fixtures) from a firm-bench pack.
2. Runs the host model or agent against each `prompt` / `inputs` pair.
3. Writes run artifacts the scorer already understands (`task_id`, `system_id`, `harness_id`, `prompt_hash`, `artifacts.text`, optional `tool_trace`).
4. Never bundles or uploads Gold keys.

The same pack feeds every harness. Case files stay free of Claude CLI flags, Cursor MCP IDs, and ChatGPT GPT-builder fields.

## Planned surfaces (later)

| Harness | Likely shape |
|---|---|
| Claude | Skill or plugin directory that loads the pack and writes artifacts |
| Cursor | Skill or rule pack that points at exported tasks |
| ChatGPT | GPT or Actions wrapper that consumes the same Task JSON |

Default until that phase: documentation only. Do not add empty `plugins/` trees unless a harness requires a minimal manifest to validate the idea.

## Reference runner today

`firm-bench run --system canned` and `--system openai` exist so CI and local checks work. They are convenience adapters, not the plugin product.
