from __future__ import annotations

import importlib
import os
from functools import lru_cache
from typing import Any, Callable, Dict, Optional
from api.kafka.engine_calls.analyze_and_present import analyze_and_present

from pydantic import BaseModel

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
    prompt: str
    options: Dict[str, Any] | None = None


class _AnalyzeResponseFallback(BaseModel):
    summary: Dict[str, Any] | None = None


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
AnalyzeRequest = _attr_proxy(
    "llm.schemas.analyze.AnalyzeRequest",
    name="AnalyzeRequest",
    fallback=_AnalyzeRequestFallback,
)
AnalyzeResponse = _attr_proxy(
    "llm.schemas.analyze.AnalyzeResponse",
    name="AnalyzeResponse",
    fallback=_AnalyzeResponseFallback,
)
# Import the Kafka-based analyze_and_present helper
MissingParamsError = _attr_proxy(
    "llm.pipelines.analyze_and_present.MissingParamsError",
    name="MissingParamsError",
    fallback=MissingParamsErrorFallback,
)


