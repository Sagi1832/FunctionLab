from typing import List, Tuple


def h1(title: str) -> str:
    """Create a level 1 Markdown header."""
    return f"# {title}\n"


def h2(title: str) -> str:
    """Create a level 2 Markdown header."""
    return f"## {title}\n"


def h3(title: str) -> str:
    """Create a level 3 Markdown header."""
    return f"### {title}\n"


def bullet(items: List[str]) -> str:
    """Create a bullet list from a list of lines."""
    if not items:
        return "No results.\n"
    
    return "\n".join(f"• {item}" for item in items) + "\n"


def kv_lines(pairs: List[Tuple[str, str]]) -> str:
    """Create key-value lines for short sections."""
    if not pairs:
        return "No results.\n"
    
    return "\n".join(f"• {key}: {value}" for key, value in pairs) + "\n"


def inline(code: str) -> str:
    """Wrap short math/code snippets in inline code formatting."""
    return f"`{code}`"


def section(title: str, body_md: str) -> str:
    """Compose a heading and body text."""
    return h2(title) + body_md
