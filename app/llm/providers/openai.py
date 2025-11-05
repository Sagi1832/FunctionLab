from __future__ import annotations
import os
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAISettings(BaseModel):
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    timeout: int = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))

class OpenAIClient:
    def __init__(self, settings: OpenAISettings | None = None):
        self.settings = settings or OpenAISettings()
        if not self.settings.api_key:
            raise RuntimeError("OPENAI_API_KEY missing.")
        self.client = OpenAI(api_key=self.settings.api_key)

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(Exception),
    )
    def complete(self, *, system: str, user: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.settings.model,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
            temperature=0.0,
        )
        return resp.choices[0].message.content or ""
