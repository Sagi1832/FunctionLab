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
from api.llm.presenter_service import generate_presentation

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
        # 1) Normalize input using input-normalizer LLM
        # (This happens inside analyze_and_present via the engine)
        
        # 2) Call engine via Kafka to get the raw report
        engine_reply = await analyze_and_present(body)
        # engine_reply is an AnalyzeResponse with report from engine, present=None
        
        # 3) If present is requested, call presenter LLM
        presenter_text: str | None = None
        if body.present:
            try:
                # Extract action value (handle enum)
                action_value = engine_reply.action.value if hasattr(engine_reply.action, "value") else str(engine_reply.action)
                
                presenter_text = await generate_presentation(
                    action=action_value,
                    expr=engine_reply.expr,
                    var=engine_reply.var,
                    report=engine_reply.report,
                )
                
                # If presenter returned empty string, set to None
                if not presenter_text:
                    presenter_text = None
                    
            except Exception as e:
                # Log warning but don't fail the request
                logger.warning(f"Failed to generate presentation text: {e}", exc_info=True)
                presenter_text = None
        
        # 4) Fill 'present' and return
        engine_reply.present = presenter_text
        return engine_reply

    except EngineCallError as ece:
        # Engine returned an error response
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
