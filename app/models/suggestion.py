"""
Suggestion Model
Shared model for code analysis suggestions.
"""
from pydantic import BaseModel, Field
from typing import Optional


class Suggestion(BaseModel):
    """Model for a code suggestion"""
    type: str = Field(..., description="Type of suggestion (style, performance, etc.)")
    severity: str = Field(..., description="Severity level (low, medium, high)")
    message: str = Field(..., description="Suggestion message")
    line: Optional[int] = Field(None, description="Line number where issue was found")
    suggested_fix: Optional[str] = Field(None, description="Suggested code fix")

    class Config:
        from_attributes = True
