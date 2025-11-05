from __future__ import annotations
from typing import Optional

from app.llm.agents.base import Agent
from app.llm.providers.openai import OpenAIClient
from app.llm.prompts import input_normalizer as prompt_mod
from app.llm.schemas.normalization import NormalizationRequest, NormalizationResult
from .helpers import _sanitize_expression, _fallback_normalize



class InputNormalizer(Agent[NormalizationRequest, NormalizationResult]):
    def __init__(self, client: Optional[OpenAIClient] = None):
        self.client = client or OpenAIClient()

    def run(self, payload: NormalizationRequest) -> NormalizationResult:
        try:
            system = prompt_mod.SYSTEM_PROMPT
            user = prompt_mod.user_prompt(expr=payload.raw, var=payload.var)
            text = (self.client.complete(system=system, user=user) or "").strip()
            if not text:
                raise ValueError("Empty LLM response")
            expr = _sanitize_expression(text, payload.var)
            if not expr:
                raise ValueError("Sanitized expression is empty")
            return NormalizationResult(expr=expr, var=payload.var)
        except Exception:
            expr = _fallback_normalize(payload.raw, payload.var)
            expr = _sanitize_expression(expr, payload.var)
            return NormalizationResult(expr=expr, var=payload.var)
