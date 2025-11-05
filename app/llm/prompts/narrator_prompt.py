from typing import Dict, Any


NARRATOR_SYSTEM_PROMPT = """You are the FunctionLab Narrator. Given a PresentResult JSON, write 1–3 natural sentences that summarize the result in the requested language.

Output plain text only. No Markdown, no code fences, no headings, no lists.
Be concise, factual, and friendly; do not add proofs or extra math.
Use only the data provided. Do not invent values. Preserve +∞ and −∞ exactly.
If monotonicity/extrema exist, briefly mention rising/falling intervals and the extrema.
Optionally mention one or two other key findings (domain, limits, asymptotes, intercepts), but keep it short.
If the input is empty or inconsistent, return: "No presentable results were produced."
"""


def build_narrator_user_message(present_result: Dict[str, Any], language: str = "en") -> str:
    """Build the user message for the Narrator agent."""
    minimal_result = {
        "title": present_result.get("title", ""),
        "expr": present_result.get("expr", ""),
        "var": present_result.get("var", "x"),
        "action": present_result.get("action", ""),
        "doc_md": present_result.get("doc_md", ""),
        "warnings": present_result.get("warnings", []),
        "errors": present_result.get("errors", [])
    }
    
    import json
    result_json = json.dumps(minimal_result, indent=2)
    
    return f"""PresentResult JSON:
{result_json}

Return a single brief paragraph in {language}. Plain text only."""
