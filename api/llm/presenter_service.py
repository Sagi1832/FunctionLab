from __future__ import annotations

import logging

from openai import AsyncOpenAI

import importlib
from api.common.engine import _build_module_name
from config.settings import settings

logger = logging.getLogger(__name__)

# Proxy to engine prompts (same pattern as InputNormalizer)
def _get_presenter_prompt():
    """Get presenter prompt module from engine."""
    try:
        module_name = _build_module_name(["llm", "prompts", "presenter_llm_prompt"])
        return importlib.import_module(module_name)
    except (ModuleNotFoundError, ImportError):
        return None


async def generate_presentation(
    *,
    action: str,
    expr: str,
    var: str,
    report: dict,
) -> str:
    """Build the presenter text."""
    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set, skipping presenter")
        return ""

    presenter_mod = _get_presenter_prompt()
    
    if presenter_mod is None:
        logger.warning("Presenter prompt module not available from engine")
        return ""

    try:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Use build_presenter_user_prompt from the prompt module
        # This follows the same pattern as InputNormalizer
        try:
            user_message = presenter_mod.build_user_prompt(
                action=action,
                expr=expr,
                var=var,
                report=report,
            )
            system_prompt = presenter_mod.SYSTEM_PROMPT
        except AttributeError as e:
            logger.error(f"Presenter prompt module missing required attributes: {e}")
            return ""
        except Exception as e:
            logger.error(f"Error building presenter user prompt: {e}", exc_info=True)
            return ""
        
        logger.debug("Calling OpenAI presenter")
        completion = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
        )
        
        presenter_text = completion.choices[0].message.content or ""
        return presenter_text
        
    except Exception as e:
        logger.warning(f"Error in generate_presentation: {e}", exc_info=True)
        return ""

