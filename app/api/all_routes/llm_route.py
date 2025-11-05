from __future__ import annotations

import os
import logging
import traceback

from fastapi import APIRouter, HTTPException
from app.llm.agents.input_normalizer_agent.input_normalizer import InputNormalizer
from app.llm.schemas.normalization import NormalizationRequest, NormalizationResult
from app.llm.schemas.analyze import AnalyzeRequest, AnalyzeResponse
from app.llm.pipelines.analyze_and_present import analyze_and_present, MissingParamsError

router = APIRouter()
logger = logging.getLogger(__name__)
ENV = os.getenv("ENV", "dev").lower()


@router.post("/llm/normalize", response_model=NormalizationResult)
def llm_normalize(body: NormalizationRequest) -> NormalizationResult:
    """Normalize a free-text math input into a SymPy-safe expression using the LLM."""
    agent = InputNormalizer()
    return agent.run(body)



@router.post("/llm/analyze", response_model=AnalyzeResponse)
def llm_analyze(body: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze a free-text math input using the LLM."""
    try:
        return analyze_and_present(body)

    except MissingParamsError as mpe:
        raise HTTPException(status_code=400, detail=str(mpe))

    except Exception:
        logger.exception("Unhandled error in /llm/analyze")
        if ENV == "dev":
            _raise_500_with_traceback()
        raise HTTPException(status_code=500, detail="Internal server error")


def _raise_500_with_traceback() -> None:
    """Raise a 500 error with the traceback."""
    tb = traceback.format_exc()
    raise HTTPException(status_code=500, detail=f"Internal server error\n{tb}")
