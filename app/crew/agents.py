"""
Crew AI Agents
Define os agentes disponíveis para a plataforma de Advisors.
"""
from typing import Dict, Any, List
from datetime import datetime


class CodeAdvisorAgent:
    """
    Agente especializado em análise de código Python.

    Responsabilidades:
    - Analisar código Python
    - Identificar violações PEP 8
    - Sugerir otimizações de performance
    - Avaliar complexidade de código
    """

    def __init__(self):
        self.agent_id = "code-advisor-001"
        self.role = "Code Quality Specialist"
        self.goal = "Analyze Python code and provide optimization suggestions"
        self.backstory = """
        Expert Python developer with 10+ years of experience in code review and
        quality assurance. Deep knowledge of PEP 8, design patterns, and performance
        optimization. Specializes in identifying code smells and suggesting improvements.
        """
        self.capabilities = [
            "Python code analysis",
            "PEP 8 compliance checking",
            "Performance optimization suggestions",
            "Best practices validation",
            "Code complexity analysis",
            "Security vulnerability detection"
        ]
        self.tools = [
            {
                "name": "analyze_code",
                "description": "Analyze Python code for improvements",
                "endpoint": "POST /analyze-code",
                "parameters": {
                    "code_snippet": "Python code to analyze"
                }
            },
            {
                "name": "get_history",
                "description": "Retrieve analysis history",
                "endpoint": "GET /history/{analysis_id}",
                "parameters": {
                    "analysis_id": "ID of the analysis to retrieve"
                }
            },
            {
                "name": "list_analyses",
                "description": "List all analyses",
                "endpoint": "GET /history",
                "parameters": {
                    "limit": "Number of results (default: 50)",
                    "offset": "Pagination offset (default: 0)"
                }
            }
        ]

    def get_config(self) -> Dict[str, Any]:
        """Retorna configuração do agente para Crew AI"""
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "capabilities": self.capabilities,
            "tools": self.tools,
            "verbose": True,
            "allow_delegation": False
        }


class DocumentationAgent:
    """
    Agente para gerar documentação de código (exemplo).

    Este é um exemplo de como adicionar novos agentes ao sistema.
    """

    def __init__(self):
        self.agent_id = "doc-generator-001"
        self.role = "Documentation Specialist"
        self.goal = "Generate comprehensive code documentation"
        self.backstory = """
        Technical writer with expertise in creating clear, concise documentation
        for Python projects. Specializes in docstrings, README files, and API docs.
        """
        self.capabilities = [
            "Generate docstrings",
            "Create README files",
            "API documentation",
            "Code examples"
        ]

    def get_config(self) -> Dict[str, Any]:
        """Retorna configuração do agente"""
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "capabilities": self.capabilities,
            "verbose": True,
            "allow_delegation": True
        }


class TestGeneratorAgent:
    """
    Agente para gerar testes automatizados (exemplo).
    """

    def __init__(self):
        self.agent_id = "test-generator-001"
        self.role = "Test Automation Specialist"
        self.goal = "Generate comprehensive unit tests for Python code"
        self.backstory = """
        QA engineer with expertise in test-driven development and pytest.
        Focuses on creating robust, maintainable test suites.
        """
        self.capabilities = [
            "Unit test generation",
            "Integration test creation",
            "Test coverage analysis",
            "Mock object creation"
        ]

    def get_config(self) -> Dict[str, Any]:
        """Retorna configuração do agente"""
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "capabilities": self.capabilities,
            "verbose": True,
            "allow_delegation": False
        }


# Registry de agentes disponíveis
AVAILABLE_AGENTS = {
    "code_advisor": CodeAdvisorAgent,
    "documentation": DocumentationAgent,
    "test_generator": TestGeneratorAgent
}


def get_agent(agent_type: str) -> Any:
    """
    Factory function para criar agentes.

    Args:
        agent_type: Tipo do agente ('code_advisor', 'documentation', etc)

    Returns:
        Instância do agente solicitado

    Raises:
        ValueError: Se o tipo de agente não existe
    """
    if agent_type not in AVAILABLE_AGENTS:
        raise ValueError(f"Agent type '{agent_type}' not found. Available: {list(AVAILABLE_AGENTS.keys())}")

    return AVAILABLE_AGENTS[agent_type]()


def list_agents() -> List[Dict[str, Any]]:
    """
    Lista todos os agentes disponíveis.

    Returns:
        Lista com informações de todos os agentes
    """
    agents_info = []
    for agent_type, agent_class in AVAILABLE_AGENTS.items():
        agent = agent_class()
        agents_info.append({
            "type": agent_type,
            "agent_id": agent.agent_id,
            "role": agent.role,
            "goal": agent.goal,
            "capabilities": agent.capabilities
        })

    return agents_info
