"""
Data Models for Code Analysis
Defines the database schema and data models.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class AnalysisHistory(BaseModel):
    """Model for analysis history stored in database"""
    id: int
    code_snippet: str
    suggestions: List[dict]
    created_at: datetime

    class Config:
        from_attributes = True
