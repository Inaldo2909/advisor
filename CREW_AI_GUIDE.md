# Guia de Agents e Tasks - Crew AI

## 📁 Estrutura de Pastas

```
code-advisor-agent/
├── app/
│   └── crew/
│       ├── __init__.py
│       ├── agents.py          # ← Definição dos AGENTS
│       ├── tasks.py           # ← Definição das TASKS
│       └── integration.py     # ← Integração e workflows
└── app/api/
    └── crew_routes.py         # ← Endpoints HTTP para Crew AI
```

## 🤖 Agents (app/crew/agents.py)

### Agents Disponíveis

#### 1. **CodeAdvisorAgent**
- **ID**: `code-advisor-001`
- **Role**: Code Quality Specialist
- **Capabilities**:
  - Python code analysis
  - PEP 8 compliance checking
  - Performance optimization suggestions
  - Best practices validation
  - Code complexity analysis

**Tools**:
- `analyze_code` - POST /analyze-code
- `get_history` - GET /history/{id}
- `list_analyses` - GET /history

#### 2. **DocumentationAgent** (exemplo)
- **ID**: `doc-generator-001`
- **Role**: Documentation Specialist
- **Capabilities**:
  - Generate docstrings
  - Create README files
  - API documentation

#### 3. **TestGeneratorAgent** (exemplo)
- **ID**: `test-generator-001`
- **Role**: Test Automation Specialist
- **Capabilities**:
  - Unit test generation
  - Integration test creation
  - Test coverage analysis

### Como usar Agents

```python
from app.crew.agents import get_agent, list_agents

# Listar todos os agents
agents = list_agents()

# Obter um agent específico
agent = get_agent('code_advisor')
config = agent.get_config()

# Acessar capabilities
print(agent.capabilities)
print(agent.tools)
```

### Factory Pattern

```python
# Registry de agents
AVAILABLE_AGENTS = {
    "code_advisor": CodeAdvisorAgent,
    "documentation": DocumentationAgent,
    "test_generator": TestGeneratorAgent
}

# Criar novo agent
agent = get_agent('code_advisor')
```

## 📋 Tasks (app/crew/tasks.py)

### Tasks Disponíveis

#### 1. **CodeAnalysisTask**
Analisa código Python e retorna sugestões.

```python
from app.crew.tasks import CodeAnalysisTask

task = CodeAnalysisTask(
    code_snippet="def example(): pass",
    task_id="custom-id",  # opcional
    description="Analyze this code"  # opcional
)

# Executar
result = task.execute()

# Converter para dict
task_dict = task.to_dict()
```

#### 2. **DocumentationTask**
Gera documentação para código.

```python
task = DocumentationTask(
    code_snippet="def example(): pass",
    doc_type="docstring"  # ou "readme"
)
```

#### 3. **TestGenerationTask**
Gera testes unitários.

```python
task = TestGenerationTask(
    code_snippet="def add(a, b): return a + b",
    test_framework="pytest"
)
```

#### 4. **CodeReviewTask**
Task completa que combina análise, docs e testes.

```python
task = CodeReviewTask(
    code_snippet="def example(): pass",
    include_docs=True,
    include_tests=True
)

# Executa todas as subtasks
results = task.execute_all()

# Ver subtasks
for subtask in task.subtasks:
    print(subtask.to_dict())
```

### Factory Pattern para Tasks

```python
from app.crew.tasks import create_task, list_task_types

# Listar tipos disponíveis
task_types = list_task_types()

# Criar task via factory
task = create_task(
    'code_analysis',
    code_snippet='def example(): pass'
)

# Task completa
task = create_task(
    'code_review',
    code_snippet='...',
    include_docs=True,
    include_tests=True
)
```

## 🌐 Endpoints HTTP

### Agents

```bash
# Listar todos os agents
GET /crew/agents

# Detalhes de um agent
GET /crew/agents/code_advisor
GET /crew/agents/documentation
GET /crew/agents/test_generator
```

### Tasks

```bash
# Listar tipos de tasks
GET /crew/tasks/types

# Criar uma task
POST /crew/tasks
{
  "task_type": "code_analysis",
  "code_snippet": "def example(): pass"
}

# Criar E executar task
POST /crew/tasks/code_analysis/execute
{
  "task_type": "code_analysis",
  "code_snippet": "def example(): pass"
}

# Task completa (code review)
POST /crew/tasks/code_review/execute
{
  "task_type": "code_review",
  "code_snippet": "def example(): pass",
  "include_docs": true,
  "include_tests": true
}
```

### Workflows

```bash
# Ver exemplo de workflow
GET /crew/workflows/example
```

## 🔧 Como Adicionar Novos Agents

### 1. Criar classe do Agent em `agents.py`

```python
class MyNewAgent:
    def __init__(self):
        self.agent_id = "my-agent-001"
        self.role = "My Agent Role"
        self.goal = "What this agent does"
        self.backstory = "Agent background"
        self.capabilities = ["capability1", "capability2"]
        self.tools = [
            {
                "name": "tool_name",
                "description": "What it does",
                "endpoint": "POST /my-endpoint"
            }
        ]

    def get_config(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "capabilities": self.capabilities,
            "tools": self.tools
        }
```

### 2. Registrar no AVAILABLE_AGENTS

```python
AVAILABLE_AGENTS = {
    "code_advisor": CodeAdvisorAgent,
    "documentation": DocumentationAgent,
    "test_generator": TestGeneratorAgent,
    "my_new_agent": MyNewAgent  # ← Adicionar aqui
}
```

## 🔧 Como Adicionar Novas Tasks

### 1. Criar classe da Task em `tasks.py`

```python
class MyNewTask:
    def __init__(self, code_snippet: str, task_id: Optional[str] = None):
        self.task_id = task_id or f"task-{datetime.utcnow().timestamp()}"
        self.description = "What this task does"
        self.code_snippet = code_snippet
        self.expected_output = "Expected result"
        self.agent_role = "Agent that executes this"
        self.status = TaskStatus.PENDING

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "status": self.status.value
        }

    def execute(self) -> Dict[str, Any]:
        self.status = TaskStatus.IN_PROGRESS
        # Lógica de execução
        result = {"message": "Task completed"}
        self.status = TaskStatus.COMPLETED
        return result
```

### 2. Registrar no AVAILABLE_TASKS

```python
AVAILABLE_TASKS = {
    "code_analysis": CodeAnalysisTask,
    "documentation": DocumentationTask,
    "test_generation": TestGenerationTask,
    "code_review": CodeReviewTask,
    "my_new_task": MyNewTask  # ← Adicionar aqui
}
```

## 🚀 Exemplos de Uso

### Exemplo 1: Análise Simples

```bash
curl -X POST http://localhost:8000/crew/tasks/code_analysis/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "code_analysis",
    "code_snippet": "def sum(a,b):\n  return a+b"
  }'
```

### Exemplo 2: Code Review Completo

```bash
curl -X POST http://localhost:8000/crew/tasks/code_review/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "code_review",
    "code_snippet": "def calculate_total(items):\n    total=0\n    for item in items:\n        total+=item\n    return total",
    "include_docs": true,
    "include_tests": true
  }'
```

### Exemplo 3: Workflow com Python

```python
import httpx
import asyncio

async def execute_workflow():
    async with httpx.AsyncClient() as client:
        # Step 1: Analisar código
        analysis = await client.post(
            "http://localhost:8000/analyze-code",
            json={"code_snippet": "def example(): pass"}
        )

        # Step 2: Criar task de documentação
        docs = await client.post(
            "http://localhost:8000/crew/tasks/documentation/execute",
            json={
                "task_type": "documentation",
                "code_snippet": "def example(): pass"
            }
        )

        return {
            "analysis": analysis.json(),
            "documentation": docs.json()
        }

# Executar
result = asyncio.run(execute_workflow())
```

## 📊 Status das Tasks

```python
class TaskStatus(Enum):
    PENDING = "pending"        # Criada, aguardando execução
    IN_PROGRESS = "in_progress"  # Em execução
    COMPLETED = "completed"    # Concluída com sucesso
    FAILED = "failed"          # Falhou na execução
```

## 🔗 Integração com Crew AI Real

O código atual é uma **simulação**. Para integração real com Crew AI:

1. Instalar biblioteca: `pip install crewai`
2. Substituir simulações por chamadas reais
3. Configurar API keys e credenciais
4. Implementar callbacks e webhooks

```python
# Exemplo de integração real (futuro)
from crewai import Agent, Task, Crew

agent = Agent(
    role='Code Quality Specialist',
    goal='Analyze Python code',
    backstory='...',
    tools=[analyze_code_tool]
)

task = Task(
    description='Analyze this code',
    agent=agent
)

crew = Crew(
    agents=[agent],
    tasks=[task]
)

result = crew.kickoff()
```

## 📚 Recursos Adicionais

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Logs**: Verifique logs da aplicação para debugging
- **Tests**: Execute `pytest tests/` para validar

---

**Resumo**:
- **Agents** estão em `app/crew/agents.py`
- **Tasks** estão em `app/crew/tasks.py`
- **Endpoints** estão em `app/api/crew_routes.py`
- Acesse `/crew/*` para todas as funcionalidades Crew AI
