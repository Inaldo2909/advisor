"""
Crew AI Routes
Endpoints para gerenciar agents e tasks do Crew AI.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.crew.agents import list_agents, get_agent, AVAILABLE_AGENTS
from app.crew.tasks import create_task, list_task_types, AVAILABLE_TASKS

router = APIRouter(prefix="/crew", tags=["Crew AI"])


class TaskCreateRequest(BaseModel):
    """Request para criar uma nova task"""
    task_type: str = Field(..., description="Type of task (code_analysis, documentation, etc)")
    code_snippet: str = Field(..., description="Code to process")
    include_docs: Optional[bool] = Field(False, description="Include documentation (for code_review)")
    include_tests: Optional[bool] = Field(False, description="Include tests (for code_review)")

    class Config:
        json_schema_extra = {
            "example": {
                "task_type": "code_analysis",
                "code_snippet": "def example():\n    pass"
            }
        }


@router.get("/agents")
async def get_all_agents():
    """
    Lista todos os agentes disponíveis.

    Retorna informações sobre cada agente registrado no sistema,
    incluindo capabilities e tools disponíveis.
    """
    try:
        agents = list_agents()
        return {
            "total": len(agents),
            "agents": agents
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing agents: {str(e)}"
        )


@router.get("/agents/{agent_type}")
async def get_agent_details(agent_type: str):
    """
    Obtém detalhes de um agente específico.

    Args:
        agent_type: Tipo do agente (code_advisor, documentation, test_generator)
    """
    try:
        agent = get_agent(agent_type)
        config = agent.get_config()

        return {
            "agent_type": agent_type,
            "config": config,
            "tools": getattr(agent, 'tools', [])
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting agent details: {str(e)}"
        )


@router.get("/tasks/types")
async def get_task_types():
    """
    Lista todos os tipos de tasks disponíveis.

    Retorna informações sobre os tipos de tasks que podem ser criadas
    e quais agentes são responsáveis por cada tipo.
    """
    try:
        task_types = list_task_types()
        return {
            "total": len(task_types),
            "task_types": task_types
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing task types: {str(e)}"
        )


@router.post("/tasks")
async def create_new_task(request: TaskCreateRequest):
    """
    Cria uma nova task para ser executada por um agente.

    A task será criada e pode ser executada posteriormente.
    """
    try:
        # Preparar kwargs baseado no tipo de task
        kwargs = {
            "code_snippet": request.code_snippet
        }

        # Adicionar parâmetros específicos para code_review
        if request.task_type == "code_review":
            kwargs["include_docs"] = request.include_docs
            kwargs["include_tests"] = request.include_tests

        # Criar a task
        task = create_task(request.task_type, **kwargs)

        return {
            "message": "Task created successfully",
            "task": task.to_dict()
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating task: {str(e)}"
        )


@router.post("/tasks/{task_type}/execute")
async def execute_task(task_type: str, request: TaskCreateRequest):
    """
    Cria e executa uma task imediatamente.

    Este endpoint cria a task e já executa, retornando o resultado.
    """
    try:
        # Preparar kwargs
        kwargs = {
            "code_snippet": request.code_snippet
        }

        if task_type == "code_review":
            kwargs["include_docs"] = request.include_docs
            kwargs["include_tests"] = request.include_tests

        # Criar a task
        task = create_task(task_type, **kwargs)

        # Executar
        if hasattr(task, 'execute'):
            result = task.execute()
        elif hasattr(task, 'execute_all'):
            result = task.execute_all()
        else:
            result = {"message": "Task created but no execution method available"}

        return {
            "message": "Task executed successfully",
            "task": task.to_dict(),
            "result": result
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing task: {str(e)}"
        )


@router.get("/workflows/example")
async def get_workflow_example():
    """
    Retorna um exemplo de workflow usando múltiplos agentes e tasks.

    Este é um exemplo de como orquestrar múltiplos agentes em um workflow.
    """
    return {
        "workflow_name": "Complete Code Review Pipeline",
        "description": "Workflow completo de revisão de código com múltiplos agentes",
        "steps": [
            {
                "step": 1,
                "agent": "Code Quality Specialist",
                "task": "code_analysis",
                "description": "Analisar código para problemas de qualidade",
                "endpoint": "POST /analyze-code"
            },
            {
                "step": 2,
                "agent": "Documentation Specialist",
                "task": "documentation",
                "description": "Gerar documentação para o código",
                "depends_on": "step_1"
            },
            {
                "step": 3,
                "agent": "Test Automation Specialist",
                "task": "test_generation",
                "description": "Gerar testes unitários",
                "depends_on": "step_1"
            }
        ],
        "example_usage": {
            "curl": """
curl -X POST http://localhost:8000/crew/tasks/code_review/execute \\
  -H "Content-Type: application/json" \\
  -d '{
    "task_type": "code_review",
    "code_snippet": "def example(): pass",
    "include_docs": true,
    "include_tests": true
  }'
            """.strip()
        }
    }
