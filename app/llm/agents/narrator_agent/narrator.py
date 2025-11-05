from __future__ import annotations
from typing import Dict, Any, Optional
import logging
from app.llm.agents.base import Agent
from app.llm.providers.openai import OpenAIClient
from app.llm.prompts.narrator_prompt import NARRATOR_SYSTEM_PROMPT, build_narrator_user_message

logger = logging.getLogger(__name__)


class NarratorAgent(Agent[Dict[str, Any], Optional[str]]):
    """Agent that generates natural language summaries of PresentResult data."""
    def __init__(self, llm_client: Optional[OpenAIClient] = None):
        """Initialize the NarratorAgent."""
        self.llm_client = llm_client or OpenAIClient()
    
    def run(self, present_result: Dict[str, Any], language: str = "en") -> Optional[str]:
        """Generate a natural language summary of the PresentResult."""
        try:
            user_message = build_narrator_user_message(present_result, language)
            narration = self.llm_client.complete(
                system=NARRATOR_SYSTEM_PROMPT,
                user=user_message
            )
            
            if not narration or not narration.strip():
                logger.warning("Narrator returned empty response")
                return None
            
            narration = narration.strip()
            
            if any(marker in narration for marker in ['```', '**', '*', '#', '`']):
                logger.warning(f"Narrator returned markdown content, cleaning: {narration[:100]}...")
                narration = narration.replace('**', '').replace('*', '').replace('`', '')
                narration = narration.replace('#', '').replace('```', '')
                narration = narration.strip()
            
            return narration
            
        except Exception as e:
            logger.error(f"Narrator failed: {str(e)}")
            return None
