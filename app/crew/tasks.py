"""
Crew AI Tasks
Define as tarefas que podem ser executadas pelos agentes.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    """Status de uma task"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class CodeAnalysisTask:
    """
    Task para análise de código Python.

    Esta task utiliza o CodeAdvisorAgent para analisar código
    e retornar sugestões de melhoria.
    """

    def __init__(
        self,
        code_snippet: str,
        task_id: Optional[str] = None,
        description: Optional[str] = None
    ):
        self.task_id = task_id or f"task-{datetime.utcnow().timestamp()}"
        self.description = description or "Analyze Python code for improvements"
        self.code_snippet = code_snippet
        self.expected_output = "List of code improvement suggestions with severity and fixes"
        self.agent_role = "Code Quality Specialist"
        self.status = TaskStatus.PENDING
        self.created_at = datetime.utcnow()
        self.result = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte task para dicionário"""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "code_snippet": self.code_snippet,
            "expected_output": self.expected_output,
            "agent_role": self.agent_role,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "result": self.result
        }

    def execute(self) -> Dict[str, Any]:
        """
        Simula execução da task.

        Em produção, isso chamaria a API do agente.
        """
        self.status = TaskStatus.IN_PROGRESS

        # Simulação - em produção chamaria POST /analyze-code
        self.result = {
            "status": "completed",
            "message": "Code analysis completed",
            "endpoint": "POST /analyze-code",
            "data": {
                "code_snippet": self.code_snippet
            }
        }

        self.status = TaskStatus.COMPLETED
        return self.result


class DocumentationTask:
    """
    Task para gerar documentação de código.
    """

    def __init__(
        self,
        code_snippet: str,
        doc_type: str = "docstring",
        task_id: Optional[str] = None
    ):
        self.task_id = task_id or f"task-{datetime.utcnow().timestamp()}"
        self.description = f"Generate {doc_type} for provided code"
        self.code_snippet = code_snippet
        self.doc_type = doc_type
        self.expected_output = f"{doc_type} documentation"
        self.agent_role = "Documentation Specialist"
        self.status = TaskStatus.PENDING

    def to_dict(self) -> Dict[str, Any]:
        """Converte task para dicionário"""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "doc_type": self.doc_type,
            "expected_output": self.expected_output,
            "agent_role": self.agent_role,
            "status": self.status.value
        }


class TestGenerationTask:
    """
    Task para gerar testes unitários.
    """

    def __init__(
        self,
        code_snippet: str,
        test_framework: str = "pytest",
        task_id: Optional[str] = None
    ):
        self.task_id = task_id or f"task-{datetime.utcnow().timestamp()}"
        self.description = f"Generate {test_framework} tests for provided code"
        self.code_snippet = code_snippet
        self.test_framework = test_framework
        self.expected_output = "Comprehensive unit tests"
        self.agent_role = "Test Automation Specialist"
        self.status = TaskStatus.PENDING

    def to_dict(self) -> Dict[str, Any]:
        """Converte task para dicionário"""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "test_framework": self.test_framework,
            "expected_output": self.expected_output,
            "agent_role": self.agent_role,
            "status": self.status.value
        }


class CodeReviewTask:
    """
    Task completa de revisão de código.

    Combina análise, documentação e testes.
    """

    def __init__(
        self,
        code_snippet: str,
        include_docs: bool = True,
        include_tests: bool = True,
        task_id: Optional[str] = None
    ):
        self.task_id = task_id or f"review-{datetime.utcnow().timestamp()}"
        self.description = "Complete code review with analysis, docs, and tests"
        self.code_snippet = code_snippet
        self.include_docs = include_docs
        self.include_tests = include_tests
        self.subtasks: List[Any] = []
        self.status = TaskStatus.PENDING

        # Criar subtasks
        self._create_subtasks()

    def _create_subtasks(self):
        """Cria as subtasks necessárias"""
        # Sempre inclui análise
        self.subtasks.append(CodeAnalysisTask(
            code_snippet=self.code_snippet,
            task_id=f"{self.task_id}-analysis"
        ))

        # Documentação opcional
        if self.include_docs:
            self.subtasks.append(DocumentationTask(
                code_snippet=self.code_snippet,
                task_id=f"{self.task_id}-docs"
            ))

        # Testes opcionais
        if self.include_tests:
            self.subtasks.append(TestGenerationTask(
                code_snippet=self.code_snippet,
                task_id=f"{self.task_id}-tests"
            ))

    def to_dict(self) -> Dict[str, Any]:
        """Converte task para dicionário"""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "include_docs": self.include_docs,
            "include_tests": self.include_tests,
            "subtasks": [task.to_dict() for task in self.subtasks],
            "status": self.status.value
        }

    def execute_all(self) -> List[Dict[str, Any]]:
        """Executa todas as subtasks"""
        self.status = TaskStatus.IN_PROGRESS
        results = []

        for task in self.subtasks:
            if hasattr(task, 'execute'):
                result = task.execute()
                results.append(result)

        self.status = TaskStatus.COMPLETED
        return results


# Registry de tasks disponíveis
AVAILABLE_TASKS = {
    "code_analysis": CodeAnalysisTask,
    "documentation": DocumentationTask,
    "test_generation": TestGenerationTask,
    "code_review": CodeReviewTask
}


def create_task(task_type: str, **kwargs) -> Any:
    """
    Factory function para criar tasks.

    Args:
        task_type: Tipo da task
        **kwargs: Parâmetros da task

    Returns:
        Instância da task

    Examples:
        >>> task = create_task('code_analysis', code_snippet='def example(): pass')
        >>> task = create_task('code_review', code_snippet='...', include_tests=True)
    """
    if task_type not in AVAILABLE_TASKS:
        raise ValueError(
            f"Task type '{task_type}' not found. "
            f"Available: {list(AVAILABLE_TASKS.keys())}"
        )

    return AVAILABLE_TASKS[task_type](**kwargs)


def list_task_types() -> List[Dict[str, str]]:
    """
    Lista todos os tipos de tasks disponíveis.

    Returns:
        Lista com informações dos tipos de tasks
    """
    return [
        {
            "type": "code_analysis",
            "description": "Analyze Python code for improvements",
            "agent": "Code Quality Specialist"
        },
        {
            "type": "documentation",
            "description": "Generate code documentation",
            "agent": "Documentation Specialist"
        },
        {
            "type": "test_generation",
            "description": "Generate unit tests",
            "agent": "Test Automation Specialist"
        },
        {
            "type": "code_review",
            "description": "Complete code review (analysis + docs + tests)",
            "agent": "Multiple agents"
        }
    ]
