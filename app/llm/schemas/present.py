from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class PresentResult(BaseModel):
    """Complete presentation result with LLM-generated Markdown."""
    title: str = Field(..., description="Overall title for the analysis")
    expr: str = Field(..., description="The mathematical expression being analyzed")
    var: str = Field(..., description="The primary variable in the expression")
    warnings: List[str] = Field(default_factory=list, description="Any warnings from the analysis")
    errors: List[str] = Field(default_factory=list, description="Any errors from the analysis")
    doc_md: str = Field(..., description="LLM-generated Markdown document")
    narration: Optional[str] = Field(None, description="Optional natural language summary of the analysis")
