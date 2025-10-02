"""
Code Advisor Agent - Main API Application
FastAPI application for analyzing Python code and providing optimization suggestions.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from app.api.routes import router
from app.api.crew_routes import router as crew_router
from app.database.connection import init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - database connection"""
    await init_db()
    yield
    await close_db()

app = FastAPI(
    title="Code Advisor Agent",
    description="""
    ## 🤖 AI-Powered Python Code Analysis

    Analise código Python e receba sugestões de otimização baseadas em boas práticas, PEP 8 e padrões de qualidade.

    ### 📚 Recursos
    - ✅ Análise de código em tempo real
    - ✅ Detecção de violações PEP 8
    - ✅ Sugestões de performance
    - ✅ Verificação de complexidade
    - ✅ Histórico completo de análises

    ### 🔗 Endpoints Principais
    - `POST /analyze-code` - Analisa código Python
    - `GET /health` - Status do serviço
    - `GET /history` - Lista todas as análises
    - `GET /history/{id}` - Busca análise específica
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Analysis",
            "description": "Operações de análise de código Python"
        },
        {
            "name": "Health",
            "description": "Verificação de saúde do serviço"
        },
        {
            "name": "History",
            "description": "Gerenciamento de histórico de análises"
        }
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (for logo and assets)
static_path = Path(__file__).parent.parent / "files"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Include API routes
app.include_router(router)
app.include_router(crew_router)


# Custom OpenAPI schema to include logo
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add logo to OpenAPI schema
    openapi_schema["info"]["x-logo"] = {
        "url": "/logo.jpg",
        "altText": "Advisor Agent"
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
