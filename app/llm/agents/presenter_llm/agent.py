import logging
from typing import Optional

from app.llm.agents.base import Agent
from app.llm.schemas.analyze import AnalyzeResult
from app.llm.providers.openai import OpenAIClient
from app.llm.prompts.presenter_llm_prompt import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


class LLMPresenter(Agent[AnalyzeResult, str]):
    """Agent that converts AnalyzeResult to a Markdown document using an LLM."""

    def __init__(self, client: Optional[OpenAIClient] = None) -> None:
        """Initialize the LLM presenter."""
        self.client = client or OpenAIClient()
        self.model = self.client.settings.model

    def run(self, payload: AnalyzeResult) -> str:
        """Convert AnalyzeResult to presenter text via the LLM."""
        user = build_user_prompt(
            action=payload.action.value,
            expr=payload.expr,
            var=payload.var,
            report=payload.report,
        )

        try:
            completion = self.client.client.chat.completions.create(
                model=self.model,
                temperature=0,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user},
                ],
            )
        except Exception as exc:
            logger.exception("LLM presenter failed: %s", exc)
            raise

        message = completion.choices[0].message.content if completion.choices else ""
        return message or ""
