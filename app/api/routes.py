"""
API Routes for Code Advisor Agent
Defines the REST API endpoints for code analysis.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from app.services.code_analyzer import CodeAnalyzer
from app.database.connection import get_db_connection
from app.models.analysis import AnalysisHistory
from app.models.suggestion import Suggestion

router = APIRouter()
code_analyzer = CodeAnalyzer()


class CodeAnalysisRequest(BaseModel):
    """Request model for code analysis"""
    code_snippet: str = Field(..., description="Python code to analyze", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "code_snippet": "def sum(a,b):\n  return a+b"
            }
        }


class CodeAnalysisResponse(BaseModel):
    """Response model for code analysis"""
    analysis_id: int
    code_snippet: str
    suggestions: List[Suggestion]
    analyzed_at: datetime
    summary: str
    has_suggestions: bool = Field(..., description="Whether any suggestions were found")


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: datetime
    database: str
    version: str


@router.post("/analyze-code", response_model=CodeAnalysisResponse, status_code=status.HTTP_200_OK, tags=["Analysis"])
async def analyze_code(request: CodeAnalysisRequest):
    """
    Analyze Python code and return optimization suggestions.

    This endpoint receives a Python code snippet, analyzes it for potential
    improvements based on best practices, and stores the analysis in the database.
    """
    try:
        # Analyze the code
        suggestions = code_analyzer.analyze(request.code_snippet)

        # Store in database
        conn = await get_db_connection()
        try:
            # Insert analysis into database
            import json
            suggestions_json = json.dumps([s.dict() for s in suggestions])

            query = """
                INSERT INTO analysis_history (code_snippet, suggestions, created_at)
                VALUES ($1, $2::jsonb, $3)
                RETURNING id, created_at
            """

            result = await conn.fetchrow(
                query,
                request.code_snippet,
                suggestions_json,
                datetime.utcnow()
            )

            analysis_id = result['id']
            created_at = result['created_at']

            # Generate summary
            if not suggestions:
                summary = "Code looks good! No issues found."
            else:
                high_count = sum(1 for s in suggestions if s.severity == "high")
                medium_count = sum(1 for s in suggestions if s.severity == "medium")
                low_count = sum(1 for s in suggestions if s.severity == "low")

                summary = f"Found {len(suggestions)} suggestion(s): "
                parts = []
                if high_count > 0:
                    parts.append(f"{high_count} high priority")
                if medium_count > 0:
                    parts.append(f"{medium_count} medium priority")
                if low_count > 0:
                    parts.append(f"{low_count} low priority")
                summary += ", ".join(parts)

            return CodeAnalysisResponse(
                analysis_id=analysis_id,
                code_snippet=request.code_snippet,
                suggestions=suggestions,
                analyzed_at=created_at,
                summary=summary,
                has_suggestions=len(suggestions) > 0
            )

        finally:
            await conn.close()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing code: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns the status of the service and database connectivity.
    """
    db_status = "disconnected"

    try:
        conn = await get_db_connection()
        await conn.fetchval("SELECT 1")
        db_status = "connected"
        await conn.close()
    except Exception:
        db_status = "error"

    return HealthResponse(
        status="ok" if db_status == "connected" else "degraded",
        timestamp=datetime.utcnow(),
        database=db_status,
        version="1.0.0"
    )


@router.get("/history", tags=["History"])
async def list_all_analyses(
    limit: int = 50,
    offset: int = 0,
    order_by: str = "created_at_desc"
):
    """
    List all code analyses from history.

    Query Parameters:
    - limit: Maximum number of results to return (default: 50, max: 100)
    - offset: Number of results to skip for pagination (default: 0)
    - order_by: Sort order - 'created_at_desc', 'created_at_asc', 'id_desc', 'id_asc' (default: created_at_desc)

    Returns paginated list of all analyses with metadata.
    """
    try:
        # Validate and limit max results
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 1

        # Validate order_by
        order_mapping = {
            "created_at_desc": "created_at DESC",
            "created_at_asc": "created_at ASC",
            "id_desc": "id DESC",
            "id_asc": "id ASC"
        }
        order_clause = order_mapping.get(order_by, "created_at DESC")

        conn = await get_db_connection()
        try:
            # Get total count
            count_query = "SELECT COUNT(*) FROM analysis_history"
            total_count = await conn.fetchval(count_query)

            # Get paginated results
            query = f"""
                SELECT
                    id,
                    code_snippet,
                    suggestions,
                    created_at,
                    jsonb_array_length(suggestions) as suggestions_count
                FROM analysis_history
                ORDER BY {order_clause}
                LIMIT $1 OFFSET $2
            """

            results = await conn.fetch(query, limit, offset)

            analyses = []
            for row in results:
                analyses.append({
                    "id": row['id'],
                    "code_snippet": row['code_snippet'],
                    "suggestions": row['suggestions'],
                    "suggestions_count": row['suggestions_count'],
                    "created_at": row['created_at']
                })

            return {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "count": len(analyses),
                "analyses": analyses
            }

        finally:
            await conn.close()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing analyses: {str(e)}"
        )


@router.get("/history/{analysis_id}", tags=["History"])
async def get_analysis_history(analysis_id: int):
    """
    Retrieve a specific analysis from history.

    Returns the details of a previously performed code analysis.
    """
    try:
        conn = await get_db_connection()
        try:
            query = """
                SELECT id, code_snippet, suggestions, created_at
                FROM analysis_history
                WHERE id = $1
            """

            result = await conn.fetchrow(query, analysis_id)

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Analysis {analysis_id} not found"
                )

            return {
                "id": result['id'],
                "code_snippet": result['code_snippet'],
                "suggestions": result['suggestions'],
                "created_at": result['created_at']
            }

        finally:
            await conn.close()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analysis: {str(e)}"
        )
