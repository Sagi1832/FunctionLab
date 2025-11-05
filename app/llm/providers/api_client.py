from __future__ import annotations  
import os
from typing import Any, Dict, Optional
import httpx

from .API_methods import APIMethodsMixin  

def _env_base_url() -> str:
    """Resolve the base URL of the API from env vars."""
    base = os.getenv("API_BASE_URL")
    if base:
        return base.rstrip("/")
    port = os.getenv("PORT", "8000")
    return f"http://127.0.0.1:{port}"



class APIClient(APIMethodsMixin):
    """Thin HTTP client for the API."""
    def __init__(self, base_url: Optional[str] = None, timeout: float = 15.0) -> None:
        self._base_url = (base_url or _env_base_url()).rstrip("/")
        self._timeout = timeout
        self._client = httpx.Client(base_url=self._base_url, timeout=self._timeout)

    def _post(self, path: str, json: Dict[str, Any]) -> Dict[str, Any]:
        """POST {base_url}{path} with JSON and return parsed JSON (or raise)."""
        resp = self._client.post(path, json=json)
        resp.raise_for_status()
        return resp.json()

    def close(self) -> None:
        """Close the client."""
        self._client.close()

    def __enter__(self) -> "APIClient":
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        """Exit the context manager."""
        self.close()
