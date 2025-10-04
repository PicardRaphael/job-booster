# 📐 Architecture Summary - JobBooster

## 🎯 Architecture Appliquée

**JobBooster** implémente :
- ✅ **Clean Architecture** (Hexagonal Architecture)
- ✅ **SOLID Principles**
- ✅ **Design Patterns** (Builder, Adapter, Factory, DI, Command)
- ✅ **Domain-Driven Design** (Entities, Services, Repositories)

## 📊 Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│                    (FastAPI Endpoints)                       │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐       │
│  │ /generate   │  │  /health    │  │   /status    │       │
│  └─────────────┘  └─────────────┘  └──────────────┘       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓ Commands/DTOs
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│                  (Use Cases + Builders)                      │
│                                                              │
│  ┌───────────────────────────────────────────────────┐     │
│  │  GenerateApplicationContentUseCase                 │     │
│  │  • execute(command) → result                       │     │
│  └───────────────────────────────────────────────────┘     │
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                │
│  │ AgentBuilder │         │ CrewBuilder  │                │
│  │ (Fluent API) │         │ (Fluent API) │                │
│  └──────────────┘         └──────────────┘                │
└────────────────────────┬────────────────────────────────────┘
                         │ Uses ↓
┌─────────────────────────────────────────────────────────────┐
│                      DOMAIN LAYER                            │
│                   (Pure Business Logic)                      │
│                                                              │
│  Entities (Value Objects):                                  │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│  │ JobOffer   │  │ JobAnalysis  │  │ GeneratedContent│    │
│  └────────────┘  └──────────────┘  └─────────────────┘    │
│                                                              │
│  Repositories (Ports/Interfaces):                           │
│  ┌──────────────────────┐  ┌───────────────────┐          │
│  │ IDocumentRepository  │  │  ILLMProvider     │          │
│  └──────────────────────┘  └───────────────────┘          │
│                                                              │
│  Services (Ports/Interfaces):                               │
│  ┌─────────────────┐  ┌────────────────┐  ┌──────────┐   │
│  │ IAnalyzerService│  │ IWriterService │  │IReranker │   │
│  └─────────────────┘  └────────────────┘  └──────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ Implemented by ↓
┌─────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                        │
│                  (Adapters/Implementations)                  │
│                                                              │
│  AI Adapters:                                               │
│  ┌────────────────────────┐  ┌──────────────────────┐     │
│  │ CrewAIAnalyzerAdapter  │  │ CrewAIWriterAdapter  │     │
│  │ (implements IAnalyzer) │  │ (implements IWriter) │     │
│  └────────────────────────┘  └──────────────────────┘     │
│                                                              │
│  ┌───────────────────┐  ┌──────────────────────┐          │
│  │ LLMProviderAdapter│  │  RerankerAdapter     │          │
│  └───────────────────┘  └──────────────────────┘          │
│                                                              │
│  Database Adapters:                                         │
│  ┌──────────────────────────────────┐                      │
│  │     QdrantAdapter                │                      │
│  │  (implements IDocumentRepository)│                      │
│  └──────────────────────────────────┘                      │
│                                                              │
│  External Services:                                         │
│  ┌──────────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Qdrant   │  │ CrewAI  │  │ OpenAI   │  │ Langfuse │  │
│  └──────────┘  └─────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Flux de Dépendances

```
Infrastructure → Domain ← Application ← Presentation
       ↓            ↑          ↓            ↓
       └────────────┴──────────┴────────────┘
          Toutes pointent vers le Domain
          (Dependency Inversion Principle)
```

## 🎨 Design Patterns

| Pattern | Où | Pourquoi |
|---------|-----|---------|
| **Builder** | `AgentBuilder`, `CrewBuilder` | Construction fluide d'objets complexes |
| **Adapter** | Toute l'infra (`*Adapter.py`) | Adapte les technologies aux interfaces domain |
| **Factory** | `LLMFactory` | Création configurée de LLMs |
| **Dependency Injection** | `Container` | Gestion centralisée des dépendances |
| **Command** | `GenerateContentCommand` | Encapsule les requêtes |
| **Repository** | `IDocumentRepository` | Abstraction de la persistence |

## 📦 Structure des Dossiers

```
backend/app/
│
├── 🏛️ domain/                  # Cœur métier (pur Python)
│   ├── entities/               # Objets métier immutables
│   ├── repositories/           # Interfaces (Ports)
│   └── services/               # Services métier (Ports)
│
├── 🎭 application/              # Orchestration
│   ├── use_cases/              # Cas d'usage métier
│   └── builders/               # Builders (fluent API)
│
├── 🔌 infrastructure/           # Implémentations (Adapters)
│   ├── ai/                     # AI services
│   └── vector_db/              # Vector databases
│
├── 🌐 api/                      # HTTP Endpoints
│   ├── generation.py
│   └── health.py
│
├── ⚙️ core/                     # Configuration
│   ├── container.py            # DI Container
│   ├── config.py
│   └── llm_factory.py
│
└── 📦 models/                   # API DTOs
    ├── requests/
    └── responses/
```

## ✅ SOLID Compliance

| Principe | Application | Exemple |
|----------|-------------|---------|
| **S**ingle Responsibility | Chaque classe = 1 responsabilité | `JobOffer` (entity), `IAnalyzerService` (service) |
| **O**pen/Closed | Ouvert extension via interfaces | Ajouter `GPT4WriterAdapter` sans modifier use case |
| **L**iskov Substitution | Tous les adapters substituables | Tout `IDocumentRepository` fonctionne |
| **I**nterface Segregation | Interfaces petites et ciblées | `IAnalyzerService`, `IWriterService` séparés |
| **D**ependency Inversion | Use cases dépendent d'interfaces | `GenerateContentUseCase(repository: IDocumentRepository)` |

## 🚀 Exemple Complet

### 1. Requête HTTP

```bash
POST /api/v1/generate
{
  "job_offer": "Nous recherchons...",
  "output_type": "email"
}
```

### 2. API Endpoint (Presentation)

```python
@router.post("/generate")
async def generate_content(request: GenerateRequest):
    container = get_container()
    use_case = container.generate_content_use_case()

    command = GenerateContentCommand(
        job_offer_text=request.job_offer,
        content_type=request.output_type.value
    )

    result = use_case.execute(command)
    return GenerateResponse(...)
```

### 3. Use Case (Application)

```python
class GenerateApplicationContentUseCase:
    def __init__(
        self,
        document_repository: IDocumentRepository,
        analyzer_service: IAnalyzerService,
        writer_service: IWriterService,
        reranker_service: IRerankerService,
    ):
        self.repository = document_repository
        self.analyzer = analyzer_service
        self.writer = writer_service
        self.reranker = reranker_service

    def execute(self, command):
        # 1. Create entity
        job_offer = JobOffer(command.job_offer_text)

        # 2. Analyze
        analysis = self.analyzer.analyze(job_offer)

        # 3. Search documents
        docs = self.repository.search(analysis.get_search_query())

        # 4. Rerank
        reranked = self.reranker.rerank(...)

        # 5. Generate content
        content = self.writer.write(job_offer, analysis, context, type)

        return GenerateContentResult(content, reranked)
```

### 4. Domain (Entities & Interfaces)

```python
# Entity
@dataclass(frozen=True)
class JobOffer:
    text: str

# Interface (Port)
class IAnalyzerService(ABC):
    @abstractmethod
    def analyze(self, job_offer: JobOffer) -> JobAnalysis:
        pass
```

### 5. Infrastructure (Adapters)

```python
# Adapter
class CrewAIAnalyzerAdapter(IAnalyzerService):
    def __init__(self, llm_provider: ILLMProvider):
        self.llm_provider = llm_provider

    def analyze(self, job_offer: JobOffer) -> JobAnalysis:
        llm = self.llm_provider.create_llm("analyzer")
        agent = AgentBuilder().with_llm(llm).build()
        # CrewAI logic
        return JobAnalysis(...)
```

### 6. DI Container

```python
class Container:
    def generate_content_use_case(self):
        return GenerateApplicationContentUseCase(
            document_repository=self.document_repository(),
            analyzer_service=self.analyzer_service(),
            writer_service=self.writer_service(),
            reranker_service=self.reranker_service(),
        )
```

## 💡 Avantages

### ✅ Testabilité

```python
# Test avec mocks, pas besoin de vraies dépendances
mock_repo = Mock(spec=IDocumentRepository)
use_case = GenerateContentUseCase(
    document_repository=mock_repo,
    ...
)
```

### ✅ Évolutivité

```python
# Changer d'AI ? Créer un nouvel adapter
class LangGraphWriterAdapter(IWriterService):
    def write(self, ...):
        # LangGraph logic
```

### ✅ Maintenabilité

- Code découplé
- Responsabilités claires
- Facile à comprendre et modifier

## 📈 Métriques

- **Couplage** : ⬇️ Faible (via interfaces)
- **Cohésion** : ⬆️ Haute (SRP)
- **Testabilité** : ⬆️ Maximale (DI)
- **Complexité** : ⬇️ Contrôlée (séparation couches)

---

**Version** : 3.0.0 (Clean Architecture + SOLID)
**Date** : 2025-10-03
