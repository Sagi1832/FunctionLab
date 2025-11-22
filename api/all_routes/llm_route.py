from __future__ import annotations

import os
import logging
import traceback

from fastapi import APIRouter, HTTPException
from api.llm.schemas import AnalyzeRequest, AnalyzeResponse
from api.common.engine import (
    InputNormalizer,
    NormalizationRequest,
    NormalizationResult,
)
from api.kafka.engine_calls.analyze_and_present import analyze_and_present
from api.kafka.client import EngineCallError

router = APIRouter()
logger = logging.getLogger(__name__)
ENV = os.getenv("ENV", "dev").lower()



@router.post("/llm/normalize", response_model=NormalizationResult)
def llm_normalize(body: NormalizationRequest) -> NormalizationResult:
    """Normalize a free-text math input into a SymPy-safe expression using the LLM."""
    agent = InputNormalizer()
    return agent.run(body)



@router.post("/llm/analyze", response_model=AnalyzeResponse)
async def llm_analyze(body: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze a free-text math input using the LLM."""
    try:
        engine_reply = await analyze_and_present(body)
        return engine_reply

    except EngineCallError as ece:
        raise HTTPException(status_code=400, detail=str(ece))

    except Exception:
        logger.exception("Unhandled error in /llm/analyze")
        if ENV == "dev":
            _raise_500_with_traceback()
        raise HTTPException(status_code=500, detail="Internal server error")


def _raise_500_with_traceback() -> None:
    """Raise a 500 error with the traceback."""
    tb = traceback.format_exc()
    raise HTTPException(status_code=500, detail=f"Internal server error\n{tb}")
