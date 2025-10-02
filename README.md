# Code Advisor Agent

**Agente especializado em análise e otimização de código Python para plataforma de Advisors**

## 📋 Descrição

O Code Advisor Agent é um microserviço desenvolvido em Python com FastAPI que fornece análise automática de código Python, oferecendo sugestões de otimização baseadas em boas práticas, PEP 8 e padrões de qualidade de código.

### Funcionalidades Principais

- ✅ **Análise de Código**: Analisa snippets Python e identifica problemas e melhorias
- 📊 **Múltiplos Critérios**: Avalia estilo, performance, complexidade e boas práticas
- 💾 **Histórico Persistente**: Armazena todas as análises em PostgreSQL
- 🔌 **API REST**: Interface simples e bem documentada
- 🤖 **Integração Crew AI**: Preparado para orquestração em workflows complexos
- 🚀 **Escalável**: Arquitetura preparada para crescimento

## 🏗️ Arquitetura

```
code-advisor-agent/
├── app/
│   ├── api/              # Endpoints da API REST
│   │   └── routes.py     # Rotas /analyze-code e /health
│   ├── services/         # Lógica de negócio
│   │   └── code_analyzer.py  # Analisador de código Python
│   ├── database/         # Conexão e configuração do banco
│   │   └── connection.py
│   ├── models/           # Modelos de dados
│   │   └── analysis.py
│   ├── crew/             # Integração com Crew AI
│   │   └── integration.py
│   └── main.py           # Aplicação FastAPI
├── database/
│   └── init.sql          # Script de inicialização do PostgreSQL
├── files/                # Arquivos estáticos (logo, etc)
│   └── logo.jpg          # Logo exibido na documentação
├── requirements.txt      # Dependências Python
├── docker-compose.yml    # Orquestração de containers
├── Dockerfile            # Imagem Docker da aplicação
└── README.md             # Este arquivo
```

### 🎨 Personalização

Para adicionar sua logo na documentação da API:
1. Coloque o arquivo `logo.jpg` na pasta `files/`
2. A logo aparecerá automaticamente em `/docs` (Swagger UI)
3. Também estará disponível em `/static/logo.jpg`

## 🚀 Como Executar

### Pré-requisitos

- Python 3.11+
- Docker e Docker Compose (recomendado)
- PostgreSQL 15+ (se não usar Docker)

### Opção 1: Docker Compose (Recomendado)

```bash
# 1. Clone o repositório
git clone <repository-url>
cd code-advisor-agent

# 2. Configure as variáveis de ambiente (opcional)
cp .env.example .env

# 3. Inicie os serviços
docker-compose up -d

# 4. Verifique os logs
docker-compose logs -f api

# 5. Acesse a documentação da API
# http://localhost:8000/docs
```

### Opção 2: Instalação Local

```bash
# 1. Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure o banco de dados PostgreSQL
# Certifique-se que o PostgreSQL está rodando na porta 5432

# 4. Crie o banco de dados
createdb code_advisor

# 5. Execute o script de inicialização
psql -d code_advisor -f database/init.sql

# 6. Configure a variável de ambiente
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/code_advisor

# 7. Inicie a aplicação
uvicorn app.main:app --reload

# 8. Acesse http://localhost:8000/docs
```

## 📡 API Endpoints

### Code Analysis Endpoints

#### 1. POST /analyze-code

Analisa um snippet de código Python e retorna sugestões.

**Request:**
```json
{
  "code_snippet": "def sum(a,b):\n  return a+b"
}
```

**Response:**
```json
{
  "analysis_id": 1,
  "code_snippet": "def sum(a,b):\n  return a+b",
  "suggestions": [
    {
      "type": "style",
      "severity": "medium",
      "message": "Function 'sum' should use snake_case naming (PEP 8)",
      "line": 1
    },
    {
      "type": "style",
      "severity": "low",
      "message": "Missing spaces around assignment operator (PEP 8)",
      "line": 1
    }
  ],
  "analyzed_at": "2025-10-02T10:30:00",
  "summary": "Found 2 suggestion(s): 1 medium priority, 1 low priority"
}
```

### 2. GET /health

Verifica o status do serviço e conectividade com o banco.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-02T10:30:00",
  "database": "connected",
  "version": "1.0.0"
}
```

#### 3. GET /history

Lista todas as análises (com paginação).

**Query Parameters:**
- `limit` - Número de resultados (default: 50, max: 100)
- `offset` - Offset para paginação (default: 0)
- `order_by` - Ordenação (created_at_desc, created_at_asc, id_desc, id_asc)

#### 4. GET /history/{analysis_id}

Recupera uma análise específica do histórico.

**Response:**
```json
{
  "id": 1,
  "code_snippet": "def sum(a,b):\n  return a+b",
  "suggestions": [...],
  "created_at": "2025-10-02T10:30:00"
}
```

### Crew AI Endpoints

#### 1. GET /crew/agents

Lista todos os agentes disponíveis na plataforma.

**Response:**
```json
{
  "total": 3,
  "agents": [
    {
      "type": "code_advisor",
      "agent_id": "code-advisor-001",
      "role": "Code Quality Specialist",
      "goal": "Analyze Python code and provide optimization suggestions",
      "capabilities": ["Python code analysis", "PEP 8 compliance", ...]
    }
  ]
}
```

#### 2. GET /crew/agents/{agent_type}

Detalhes de um agente específico (code_advisor, documentation, test_generator).

#### 3. GET /crew/tasks/types

Lista todos os tipos de tasks disponíveis.

**Response:**
```json
{
  "total": 4,
  "task_types": [
    {
      "type": "code_analysis",
      "description": "Analyze Python code for improvements",
      "agent": "Code Quality Specialist"
    },
    {
      "type": "documentation",
      "description": "Generate code documentation",
      "agent": "Documentation Specialist"
    }
  ]
}
```

#### 4. POST /crew/tasks

Cria uma nova task.

**Request:**
```json
{
  "task_type": "code_analysis",
  "code_snippet": "def example():\n    pass"
}
```

#### 5. POST /crew/tasks/{task_type}/execute

Cria e executa uma task imediatamente.

**Request:**
```json
{
  "task_type": "code_review",
  "code_snippet": "def example():\n    pass",
  "include_docs": true,
  "include_tests": true
}
```

#### 6. GET /crew/workflows/example

Retorna exemplo de workflow completo com múltiplos agentes.

## 🧪 Testando a Aplicação

### Usando cURL

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test code analysis
curl -X POST http://localhost:8000/analyze-code \
  -H "Content-Type: application/json" \
  -d '{
    "code_snippet": "def example():\n  x=1\n  return x"
  }'
```

### Usando Python

```python
import requests

# Analyze code
response = requests.post(
    "http://localhost:8000/analyze-code",
    json={
        "code_snippet": """
def calculate_sum(numbers):
    total=0
    for n in numbers:
        total=total+n
    return total
"""
    }
)

print(response.json())
```

### Usando Swagger UI

Acesse `http://localhost:8000/docs` para uma interface interativa completa.

## 🤖 Integração com Crew AI

O agente foi projetado para integração com Crew AI workflows. Veja o exemplo completo em `app/crew/integration.py`.

### Exemplo de Integração

```python
from app.crew.integration import CrewAIAgent, CrewWorkflow

# Criar o agente
code_advisor = CrewAIAgent(
    agent_id="code-advisor-001",
    role="Code Quality Specialist",
    goal="Analyze Python code and provide optimization suggestions"
)

# Adicionar a um workflow
workflow = CrewWorkflow(workflow_name="Code Review Pipeline")
workflow.add_agent(code_advisor)

# Definir steps
workflow.define_workflow([
    {
        "step": 1,
        "agent_role": "Code Quality Specialist",
        "action": "analyze_code",
        "input": "code_snippet"
    }
])

# Executar
result = workflow.execute_workflow({
    "code_snippet": "def example(): pass"
})
```

### Configuração para Crew AI

O agente expõe as seguintes capacidades para orquestração:

- **Endpoint de Análise**: `POST /analyze-code`
- **Health Check**: `GET /health`
- **Histórico**: `GET /history/{id}`
- **Protocolo**: REST API com JSON
- **Autenticação**: Pode ser estendido com API Keys

## 🔧 Decisões Técnicas

### 1. FastAPI
**Justificativa**: Framework moderno, assíncrono, com validação automática (Pydantic) e documentação OpenAPI integrada. Ideal para microserviços e APIs REST.

### 2. PostgreSQL
**Justificativa**: Banco relacional robusto com suporte a JSONB para armazenar sugestões estruturadas. Permite queries complexas e análises futuras.

### 3. AsyncPG
**Justificativa**: Driver PostgreSQL assíncrono de alta performance, aproveitando o modelo async/await do Python para melhor escalabilidade.

### 4. Arquitetura em Camadas
**Justificativa**: Separação clara entre API, serviços, modelos e database facilita manutenção, testes e evolução do código.

### 5. Docker Compose
**Justificativa**: Simplifica desenvolvimento e deployment, garantindo ambiente consistente e isolado.

## 📈 Escalabilidade

### Estratégias Implementadas

1. **Connection Pool**: Pool de conexões assíncronas com PostgreSQL (min: 2, max: 10)
2. **Índices de Banco**: Índices em `created_at` e `suggestions` (GIN) para queries rápidas
3. **Arquitetura Stateless**: API sem estado permite escalonamento horizontal

### Melhorias Futuras

Para crescimento em produção, considerar:

#### 1. Cache com Redis
```python
# Exemplo de implementação
import redis.asyncio as redis

cache = redis.from_url("redis://localhost:6379")

async def analyze_with_cache(code_snippet: str):
    cache_key = f"analysis:{hash(code_snippet)}"

    # Check cache
    cached = await cache.get(cache_key)
    if cached:
        return json.loads(cached)

    # Analyze and cache
    result = analyzer.analyze(code_snippet)
    await cache.setex(cache_key, 3600, json.dumps(result))
    return result
```

#### 2. Fila de Mensagens (RabbitMQ/Celery)
```python
# Para análises assíncronas de longa duração
from celery import Celery

celery_app = Celery('code_advisor', broker='amqp://localhost')

@celery_app.task
def async_code_analysis(code_snippet: str, analysis_id: int):
    result = analyzer.analyze(code_snippet)
    # Store result
    return result
```

#### 3. Load Balancing
```yaml
# nginx.conf
upstream code_advisor_backend {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    location / {
        proxy_pass http://code_advisor_backend;
    }
}
```

#### 4. Monitoramento
- **Prometheus**: Métricas de performance
- **Grafana**: Dashboards de monitoramento
- **Sentry**: Tracking de erros

#### 5. Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/analyze-code")
@limiter.limit("10/minute")
async def analyze_code(request: Request, ...):
    ...
```

## 📊 Banco de Dados

### Schema

```sql
CREATE TABLE analysis_history (
    id SERIAL PRIMARY KEY,
    code_snippet TEXT NOT NULL,
    suggestions JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_analysis_created_at ON analysis_history(created_at DESC);
CREATE INDEX idx_analysis_suggestions ON analysis_history USING GIN (suggestions);
```

### Queries Úteis

```sql
-- Total de análises
SELECT COUNT(*) FROM analysis_history;

-- Análises por dia
SELECT DATE(created_at), COUNT(*)
FROM analysis_history
GROUP BY DATE(created_at);

-- Média de sugestões por análise
SELECT AVG(jsonb_array_length(suggestions)) FROM analysis_history;
```

## 🛠️ Desenvolvimento

### Executar Testes

```bash
# Instalar dependências de dev
pip install pytest pytest-asyncio httpx

# Executar testes
pytest tests/

# Com coverage
pytest --cov=app tests/
```

### Linting e Formatação

```bash
# Black (formatter)
black app/

# Flake8 (linter)
flake8 app/

# MyPy (type checking)
mypy app/
```

### Adicionar Novas Validações

Para adicionar novos tipos de análise, edite `app/services/code_analyzer.py`:

```python
def _check_new_validation(self, tree: ast.AST, code: str):
    """Sua nova validação"""
    for node in ast.walk(tree):
        # Lógica de análise
        if condition:
            self.suggestions.append(Suggestion(
                type="new_type",
                severity="high",
                message="Mensagem da sugestão",
                line=node.lineno
            ))
```

## 🐳 Gerenciamento Docker

```bash
# Iniciar serviços
docker-compose up -d

# Parar serviços
docker-compose down

# Ver logs
docker-compose logs -f

# Rebuild após mudanças
docker-compose up -d --build

# Acessar PgAdmin (opcional)
docker-compose --profile tools up -d
# Acesse http://localhost:5050
```

## 📝 Variáveis de Ambiente

Configure no arquivo `.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/code_advisor
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto foi desenvolvido como parte do desafio técnico para Head de Inovação.

## 👥 Autor

Desenvolvido para o desafio técnico da plataforma de Advisors.

---

**Documentação adicional**: Acesse `/docs` quando a aplicação estiver rodando para ver a documentação interativa completa da API.
