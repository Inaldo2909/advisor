# Arquitetura do Code Advisor Agent

## Visão Geral

O Code Advisor Agent segue uma arquitetura de microserviço com separação clara de responsabilidades, projetada para escalabilidade e manutenibilidade.

## Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                        Cliente                              │
│  (Crew AI, API Client, Frontend, CLI)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP/REST
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Layer                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Routes (app/api/routes.py)                          │   │
│  │  - POST /analyze-code                                │   │
│  │  - GET /health                                       │   │
│  │  - GET /history/{id}                                 │   │
│  └──────────────┬───────────────────────────────────────┘   │
└─────────────────┼───────────────────────────────────────────┘
                  │
                  │ Pydantic Models
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  Service Layer                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  CodeAnalyzer (app/services/code_analyzer.py)        │   │
│  │  - analyze()                                         │   │
│  │  - _check_naming_conventions()                       │   │
│  │  - _check_complexity()                               │   │
│  │  - _check_best_practices()                           │   │
│  │  - _check_performance()                              │   │
│  │  - _check_style()                                    │   │
│  └──────────────┬───────────────────────────────────────┘   │
└─────────────────┼───────────────────────────────────────────┘
                  │
                  │ Analysis Results
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  Database Layer                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Connection Pool (app/database/connection.py)        │   │
│  │  - AsyncPG Pool                                      │   │
│  │  - get_db_connection()                               │   │
│  └──────────────┬───────────────────────────────────────┘   │
└─────────────────┼───────────────────────────────────────────┘
                  │
                  │ SQL Queries
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   PostgreSQL                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Table: analysis_history                             │   │
│  │  - id (SERIAL)                                       │   │
│  │  - code_snippet (TEXT)                               │   │
│  │  - suggestions (JSONB)                               │   │
│  │  - created_at (TIMESTAMP)                            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Crew AI Integration Layer                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  CrewAIAgent (app/crew/integration.py)               │   │
│  │  - Workflow orchestration                            │   │
│  │  - Task management                                   │   │
│  │  - Agent registration                                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Camadas da Aplicação

### 1. API Layer (FastAPI)
- **Responsabilidade**: Expor endpoints REST, validar requests, serializar responses
- **Tecnologia**: FastAPI + Pydantic
- **Arquivos**: `app/api/routes.py`, `app/main.py`

### 2. Service Layer
- **Responsabilidade**: Lógica de negócio, análise de código
- **Tecnologia**: Python + AST
- **Arquivos**: `app/services/code_analyzer.py`

### 3. Database Layer
- **Responsabilidade**: Persistência de dados, gerenciamento de conexões
- **Tecnologia**: AsyncPG + PostgreSQL
- **Arquivos**: `app/database/connection.py`

### 4. Integration Layer
- **Responsabilidade**: Integração com sistemas externos (Crew AI)
- **Tecnologia**: Python
- **Arquivos**: `app/crew/integration.py`

## Fluxo de Dados

### Análise de Código

```
1. Cliente envia POST /analyze-code
   ↓
2. FastAPI valida request (Pydantic)
   ↓
3. Routes.py chama CodeAnalyzer.analyze()
   ↓
4. CodeAnalyzer executa checks:
   - Parse AST
   - Check naming conventions
   - Check complexity
   - Check best practices
   - Check performance
   - Check style
   ↓
5. Retorna lista de Suggestions
   ↓
6. Routes.py salva no PostgreSQL
   ↓
7. Retorna CodeAnalysisResponse ao cliente
```

## Padrões de Design

### 1. Dependency Injection
```python
# Database connection é injetada
conn = await get_db_connection()
```

### 2. Repository Pattern
```python
# Database layer abstrai queries SQL
async def save_analysis(code, suggestions):
    conn = await get_db_connection()
    await conn.execute(query, code, suggestions)
```

### 3. Service Layer Pattern
```python
# Lógica de negócio isolada
class CodeAnalyzer:
    def analyze(self, code: str) -> List[Suggestion]:
        # Business logic here
```

### 4. DTO (Data Transfer Objects)
```python
# Pydantic models como DTOs
class CodeAnalysisRequest(BaseModel):
    code_snippet: str
```

## Escalabilidade

### Horizontal Scaling

```
              ┌─────────────-┐
              │ Load Balancer│
              └──────┬───────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼───┐   ┌────▼───┐   ┌────▼───┐
   │  API 1 │   │  API 2 │   │  API 3 │
   └────┬───┘   └────┬───┘   └────┬───┘
        │            │            │
        └────────────┼────────────┘
                     │
              ┌──────▼───────┐
              │  PostgreSQL  │
              │  (Primary)   │
              └──────┬───────┘
                     │
        ┌────────────┼────────────┐
   ┌────▼───┐   ┌────▼───┐   ┌────▼───┐
   │Replica1│   │Replica2│   │Replica3│
   └────────┘   └────────┘   └────────┘
```

### Caching Strategy

```
┌────────────┐
│   Client   │
└─────┬──────┘
      │
      ▼
┌─────────────┐    Cache Hit    ┌──────────┐
│  API Layer  │ ◄───────────────┤  Redis   │
└─────┬───────┘                 └──────────┘
      │ Cache Miss
      │
      ▼
┌──────────────┐
│ Code Analyzer│
└─────┬────────┘
      │
      ▼
┌──────────────┐
│  PostgreSQL  │
└──────────────┘
```

## Segurança

### 1. Input Validation
- Pydantic valida todos os inputs
- Limite de tamanho de código (configurável)
- Sanitização de SQL via parametrized queries

### 2. Rate Limiting (Futuro)
```python
@limiter.limit("10/minute")
async def analyze_code(...):
    pass
```

### 3. Authentication (Futuro)
```python
@require_api_key
async def analyze_code(...):
    pass
```

## Monitoramento

### Métricas Sugeridas

1. **Request Metrics**
   - Total de requests
   - Request duration
   - Error rate

2. **Analysis Metrics**
   - Média de sugestões por análise
   - Tipos de sugestões mais comuns
   - Tempo de análise

3. **Database Metrics**
   - Connection pool usage
   - Query duration
   - Number of active connections

### Logging Strategy

```python
import logging

# Structured logging
logger.info("code_analyzed", extra={
    "analysis_id": analysis_id,
    "suggestions_count": len(suggestions),
    "duration_ms": duration
})
```

## Integração Crew AI

### Agent Registration

```python
{
    "agent_id": "code-advisor-001",
    "role": "Code Quality Specialist",
    "capabilities": ["code_analysis", "pep8_validation"],
    "endpoints": {
        "analyze": "POST /analyze-code",
        "health": "GET /health"
    }
}
```

### Workflow Integration

```python
# Crew AI chama o agente via HTTP
async def crew_workflow_step():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://code-advisor:8000/analyze-code",
            json={"code_snippet": code}
        )
        return response.json()
```

## Trade-offs e Decisões

### 1. AsyncPG vs SQLAlchemy
**Escolha**: AsyncPG
**Razão**: Performance superior, async nativo, queries mais simples
**Trade-off**: Menos abstração, mais SQL manual

### 2. AST vs Regex para análise
**Escolha**: AST (Abstract Syntax Tree)
**Razão**: Análise precisa, entende estrutura do código
**Trade-off**: Mais complexo, mas muito mais confiável

### 3. JSONB vs Tabelas relacionais para suggestions
**Escolha**: JSONB
**Razão**: Flexibilidade, estrutura variável de sugestões
**Trade-off**: Menos normalização, mas queries GIN eficientes

## Evolução Futura

### Fase 1 (Atual)
- ✅ API REST básica
- ✅ Análise estática de código
- ✅ Persistência PostgreSQL
- ✅ Integração Crew AI simulada

### Fase 2 (Próximos passos)
- 🔲 Cache com Redis
- 🔲 Rate limiting
- 🔲 Autenticação API Key
- 🔲 Métricas Prometheus

### Fase 3 (Médio prazo)
- 🔲 Análise ML-powered
- 🔲 Sugestões de refactoring automático
- 🔲 Integração com GitHub Actions
- 🔲 Dashboard de analytics

## Referências

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [AsyncPG Documentation](https://magicstack.github.io/asyncpg/)
- [Python AST Module](https://docs.python.org/3/library/ast.html)
- [PEP 8 Style Guide](https://pep8.org/)
