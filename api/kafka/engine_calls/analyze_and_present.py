from api.lifecycle import engine_client
from api.llm.schemas import AnalyzeRequest, AnalyzeResponse


async def analyze_and_present(
    body: AnalyzeRequest,
) -> AnalyzeResponse:
    """Call engine via Kafka to analyze and present a math expression.
    
    The engine handles:
    - Input normalization (LLM)
    - Calculus computation
    - Presenter LLM
    
    Returns an AnalyzeResponse with action, expr, var, present, warnings, errors.
    """
    # Call the engine via Kafka
    engine_reply_dict = await engine_client.call_engine(
        action="analyze_and_present",
        payload=body.model_dump(),
    )
    
    return AnalyzeResponse.model_validate(engine_reply_dict)

