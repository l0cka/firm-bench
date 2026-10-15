from __future__ import annotations

import json
import os
from typing import Any

import httpx

from firm_bench.schema import Task


class OpenAICompatibleAdapter:
    system_id = "openai-compatible"
    harness_id = "firm-bench-reference"

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        self.base_url = (
            base_url
            or os.environ.get("FIRM_BENCH_OPENAI_BASE_URL")
            or os.environ.get("OPENAI_BASE_URL")
            or "https://api.openai.com/v1"
        ).rstrip("/")
        self.api_key = (
            api_key
            or os.environ.get("FIRM_BENCH_OPENAI_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
            or ""
        )
        self.model = (
            model
            or os.environ.get("FIRM_BENCH_OPENAI_MODEL")
            or os.environ.get("OPENAI_MODEL")
            or "gpt-4o-mini"
        )
        self.timeout = timeout

    def complete(self, task: Task) -> dict[str, Any]:
        if not self.api_key:
            raise RuntimeError(
                "OPENAI_API_KEY or FIRM_BENCH_OPENAI_API_KEY is required for "
                "the openai-compatible adapter"
            )
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a legal drafting assistant under solicitor supervision. "
                    "Follow the user task exactly. Prefer fail-closed status tokens "
                    "when facts are missing or the request is out of scope."
                ),
            },
            {"role": "user", "content": task.prompt},
        ]
        if task.inputs:
            messages.append(
                {
                    "role": "user",
                    "content": "Supporting inputs (JSON):\n"
                    + json.dumps(task.inputs, indent=2),
                }
            )
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}/chat/completions"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        text = message.get("content") or ""
        return {
            "text": text,
            "model": self.model,
            "raw_id": data.get("id"),
        }
