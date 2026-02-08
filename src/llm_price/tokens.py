from __future__ import annotations

import os

import requests
import tiktoken

from llm_price.types import TokenUsage


def _openai_tokenize(text: str, model: str) -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def _approximate_tokens(text: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def _gemini_count_tokens_api(model: str, prompt: str, completion: str | None) -> int | None:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:countTokens"
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    if completion:
        payload["contents"].append({"parts": [{"text": completion}]})
    response = requests.post(url, params={"key": api_key}, json=payload, timeout=30)
    if response.status_code != 200:
        return None
    data = response.json()
    return int(data.get("totalTokens", 0))


def estimate_tokens(
    provider: str,
    model: str,
    *,
    prompt: str,
    completion: str | None = None,
) -> tuple[TokenUsage, str | None]:
    normalized = provider.lower()
    if normalized == "openai":
        prompt_tokens = _openai_tokenize(prompt, model)
        completion_tokens = _openai_tokenize(completion or "", model)
        return TokenUsage(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens), None
    if normalized == "google":
        total_tokens = _gemini_count_tokens_api(model, prompt, completion)
        if total_tokens is not None:
            return (
                TokenUsage(prompt_tokens=total_tokens, completion_tokens=0),
                "Gemini CountTokens API returns total tokens; completion split not available",
            )
        prompt_tokens = _approximate_tokens(prompt)
        completion_tokens = _approximate_tokens(completion or "")
        return (
            TokenUsage(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens),
            "Token counts are approximate; set GOOGLE_API_KEY for official Gemini CountTokens",
        )
    raise ValueError(f"Unsupported provider '{provider}'")