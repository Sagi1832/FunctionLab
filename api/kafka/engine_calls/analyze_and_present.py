from api.lifecycle import engine_client
from api.llm.schemas import AnalyzeRequest, AnalyzeResponse


async def analyze_and_present(
    body: AnalyzeRequest,
) -> AnalyzeResponse:
    """Call engine via Kafka to analyze and present a math expression.
    
    The 'analyze_and_present' string is the engine function name.
    The user's action (domain, derivative, etc.) is preserved in the body.
    """
    # Call the engine
    engine_reply = await engine_client.call_engine(
        action="analyze_and_present",
        payload=body.model_dump(),
    )
    
    # If the engine client wraps the result inside {"ok": True, "result": {...}},
    # unwrap it. Otherwise just use the reply as-is.
    if isinstance(engine_reply, dict) and "result" in engine_reply:
        report_payload = engine_reply["result"]
    else:
        report_payload = engine_reply
    
    # Now build AnalyzeResponse explicitly
    return AnalyzeResponse(
        action=body.action,
        expr=body.raw,
        var=body.var,
        report=report_payload,
        warnings=[],
        errors=[],
        present=None,
    )

