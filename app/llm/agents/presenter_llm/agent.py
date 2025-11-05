import json
import logging
from typing import Optional

from app.llm.agents.base import Agent
from app.llm.schemas.analyze import AnalyzeResult
from app.llm.providers.openai import OpenAIClient
from app.llm.prompts.presenter_llm_prompt import SYSTEM_PROMPT, build_user_prompt
from app.llm.agents.presenter_llm.presenter_helpers import prepare_analysis_data

logger = logging.getLogger(__name__)


def _strip_code_fences(md: str) -> str:
    """Remove surrounding triple-backtick fences from an LLM response if present."""
    md = md.strip()
    if not md.startswith("```"):
        return md

    lines = md.splitlines()
    lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


class LLMPresenter(Agent[AnalyzeResult, str]):
    """Agent that converts AnalyzeResult to a Markdown document using an LLM."""

    def __init__(self, client: Optional[OpenAIClient] = None) -> None:
        """Initialize the LLM presenter."""
        self.client = client or OpenAIClient()

    def run(self, payload: AnalyzeResult) -> str:
        """Convert AnalyzeResult to a clean Markdown string."""
        analysis_data = prepare_analysis_data(payload)
        analysis_json = json.dumps(analysis_data, indent=2, ensure_ascii=False)
        logger.debug("LLM presenter - prepared JSON: %s", analysis_json)

        system = SYSTEM_PROMPT
        user = build_user_prompt(analysis_json)

        try:
            response = self.client.complete(system=system, user=user)
        except Exception as e:
            logger.error("LLM presenter - provider error: %s", e, exc_info=True)
            raise

        if not response or not isinstance(response, str):
            logger.error("LLM presenter - empty or non-string response")
            raise ValueError("Empty LLM response")

        markdown = _strip_code_fences(response).rstrip()

        if not markdown:
            logger.error("LLM presenter - response became empty after stripping fences")
            raise ValueError("LLM response contained no Markdown content")

        logger.debug("LLM presenter - final Markdown length: %d chars", len(markdown))
        return markdown
