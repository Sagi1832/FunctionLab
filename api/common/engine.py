from __future__ import annotations

import importlib
import os
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional, Tuple

from pydantic import BaseModel

# Import LLM schemas from the API repo instead of proxying from engine
from api.llm.schemas import AnalyzeRequest, AnalyzeResponse

ENGINE_NAMESPACE = os.getenv("ENGINE_NAMESPACE", "app")


class EngineUnavailableError(RuntimeError):
    """Raised when the external engine package cannot be imported."""


def _build_module_name(parts: list[str]) -> str:
    return ".".join((ENGINE_NAMESPACE, *parts))


@lru_cache(maxsize=None)
def _resolve(path: str) -> Any:
    segments = path.split(".")
    if len(segments) < 2:
        raise ValueError(f"Engine path '{path}' must include module and attribute")
    module_name = _build_module_name(segments[:-1])
    attr_name = segments[-1]
    module = importlib.import_module(module_name)
    return getattr(module, attr_name)


def _maybe_resolve(path: str) -> Optional[Any]:
    try:
        return _resolve(path)
    except (ModuleNotFoundError, AttributeError):
        return None


def _missing_dependency(name: str) -> EngineUnavailableError:
    return EngineUnavailableError(
        f"Engine dependency '{name}' is unavailable (namespace='{ENGINE_NAMESPACE}')."
    )


def _callable_proxy(path: str, *, name: str) -> Callable[..., Any]:
    def _wrapper(*args: Any, **kwargs: Any) -> Any:
        target = _maybe_resolve(path)
        if target is None:
            raise _missing_dependency(name)
        return target(*args, **kwargs)

    return _wrapper


def _attr_proxy(path: str, *, name: str, fallback: Optional[Any] = None) -> Any:
    target = _maybe_resolve(path)
    if target is not None:
        return target
    if fallback is not None:
        return fallback
    raise _missing_dependency(name)


# ---------- LLM / pipelines ----------

class _InputNormalizerFallback:
    def __call__(self, *args: Any, **kwargs: Any) -> "_InputNormalizerFallback":
        return self

    def run(self, *_args: Any, **_kwargs: Any) -> Any:
        raise _missing_dependency("InputNormalizer")


class _NormalizationRequestFallback(BaseModel):
    text: str
    extra: Dict[str, Any] | None = None


class _NormalizationResultFallback(BaseModel):
    normalized: Optional[str] = None
    metadata: Dict[str, Any] | None = None


class _AnalyzeRequestFallback(BaseModel):
    """Fallback AnalyzeRequest matching the structured schema."""
    raw: str
    var: str = "x"
    action: str
    interval: Optional[Tuple[float, float]] = None
    closed: Optional[Tuple[bool, bool]] = None
    present: bool = True
    narrate: bool = False
    narrate_lang: str = "en"


class _AnalyzeResponseFallback(BaseModel):
    """Fallback AnalyzeResponse matching engine's new schema."""
    action: str
    expr: str
    var: str
    present: str  # required, not optional
    warnings: List[str] = []
    errors: List[str] = []


class MissingParamsErrorFallback(Exception):
    """Fallback exception when engine-specific error is unavailable."""


InputNormalizer = _attr_proxy(
    "llm.agents.input_normalizer_agent.input_normalizer.InputNormalizer",
    name="InputNormalizer",
    fallback=_InputNormalizerFallback,
)
NormalizationRequest = _attr_proxy(
    "llm.schemas.normalization.NormalizationRequest",
    name="NormalizationRequest",
    fallback=_NormalizationRequestFallback,
)
NormalizationResult = _attr_proxy(
    "llm.schemas.normalization.NormalizationResult",
    name="NormalizationResult",
    fallback=_NormalizationResultFallback,
)
# AnalyzeRequest and AnalyzeResponse are imported at the top from api.llm.schemas
# Import the Kafka-based analyze_and_present helper
MissingParamsError = _attr_proxy(
    "llm.pipelines.analyze_and_present.MissingParamsError",
    name="MissingParamsError",
    fallback=MissingParamsErrorFallback,
)


