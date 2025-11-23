import logging
from typing import Optional, Tuple

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

    def run(self, payload: AnalyzeResult, user_interval: Optional[Tuple[float, float]] = None) -> str:
        """Convert AnalyzeResult to presenter text via the LLM.
        
        Args:
            payload: The analysis result to present
            user_interval: Optional user-requested interval [a, b] for clipping monotonicity intervals
        """
        user = build_user_prompt(
            action=payload.action.value,
            expr=payload.expr,
            var=payload.var,
            report=payload.report,
            user_interval=user_interval,
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
