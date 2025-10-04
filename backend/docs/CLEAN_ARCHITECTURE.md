```markdown
# 🏛️ Clean Architecture & SOLID - JobBooster

## 📋 Vue d'ensemble

JobBooster implémente **Clean Architecture** (Hexagonal Architecture) avec les principes **SOLID** pour garantir :
- ✅ Testabilité maximale
- ✅ Indépendance des frameworks
- ✅ Indépendance de la base de données
- ✅ Indépendance de l'UI
- ✅ Évolutivité et maintenabilité

## 🎯 Principes SOLID Appliqués

### 1. **S - Single Responsibility Principle**
Chaque classe a **une seule raison de changer**.

```python
# ✅ BON : Responsabilité unique
class JobOffer:
    """Représente uniquement un job offer (domain entity)."""
    text: str

class JobAnalyzerService:
    """Responsabilité : analyser les job offers."""
    def analyze(self, job_offer: JobOffer) -> JobAnalysis:
        ...

# ❌ MAUVAIS : Multiples responsabilités
class JobOfferManager:
    """Fait tout : validation, analyse, stockage, génération..."""
    def validate(self): ...
    def analyze(self): ...
    def save(self): ...
    def generate_email(self): ...
```

### 2. **O - Open/Closed Principle**
Ouvert à l'extension, fermé à la modification.

```python
# ✅ BON : Extension via interface
class IWriterService(ABC):
    @abstractmethod
    def write(self, ...): ...

class CrewAIWriterAdapter(IWriterService):
    """Implémentation CrewAI."""

class LangChainWriterAdapter(IWriterService):
    """Nouvelle implémentation sans modifier le use case."""

# ❌ MAUVAIS : if/else pour chaque nouveau type
def write_content(writer_type):
    if writer_type == "crewai":
        # Code CrewAI
    elif writer_type == "langchain":
        # Code LangChain
    # Modification à chaque nouveau type !
```

### 3. **L - Liskov Substitution Principle**
Les sous-classes doivent pouvoir remplacer leurs classes parentes.

```python
# ✅ BON : Toute impl de IDocumentRepository est substituable
def use_case(repository: IDocumentRepository):
    docs = repository.search(query)  # Marche avec n'importe quelle impl

# QdrantAdapter, ElasticsearchAdapter, InMemoryAdapter tous interchangeables
```

### 4. **I - Interface Segregation Principle**
Interfaces petites et spécifiques.

```python
# ✅ BON : Interfaces spécifiques
class IAnalyzerService(ABC):
    @abstractmethod
    def analyze(self, job_offer): ...

class IWriterService(ABC):
    @abstractmethod
    def write(self, ...): ...

# ❌ MAUVAIS : Interface monolithique
class IJobService(ABC):
    def analyze(self): ...
    def write(self): ...
    def search(self): ...
    def rerank(self): ...
    # Trop de méthodes !
```

### 5. **D - Dependency Inversion Principle**
Dépendre d'abstractions, pas d'implémentations.

```python
# ✅ BON : Use case dépend d'interfaces (abstractions)
class GenerateContentUseCase:
    def __init__(
        self,
        document_repository: IDocumentRepository,  # Interface !
        analyzer_service: IAnalyzerService,        # Interface !
    ):
        ...

# ❌ MAUVAIS : Use case dépend d'implémentations concrètes
class GenerateContentUseCase:
    def __init__(self):
        self.qdrant = QdrantService()    # Implémentation concrète !
        self.crewai = CrewAIService()    # Implémentation concrète !
```

## 🏗️ Architecture en Couches

```
┌─────────────────────────────────────────────────────┐
│                  API / Controllers                   │  ← Adapters (Input)
│                  (FastAPI Endpoints)                 │
├─────────────────────────────────────────────────────┤
│              Application Layer                       │
│         (Use Cases + Builders + Commands)            │  ← Orchestration
├─────────────────────────────────────────────────────┤
│                Domain Layer                          │
│   (Entities + Interfaces + Business Logic)           │  ← Pure Business
├─────────────────────────────────────────────────────┤
│            Infrastructure Layer                      │
│    (Adapters: Qdrant, CrewAI, LLM, Reranker)       │  ← Adapters (Output)
└─────────────────────────────────────────────────────┘
```

### Flux de Dépendances

```
API → Application → Domain ← Infrastructure
  ↓        ↓           ↑            ↑
  └────────┴───────────┴────────────┘
         Toutes dépendent du Domain
         (Dependency Inversion)
```

## 📁 Structure des Dossiers

```
app/
├── domain/                    # ❤️ Cœur métier (pur Python)
│   ├── entities/              # Objets métier
│   │   ├── job_offer.py
│   │   ├── job_analysis.py
│   │   └── generated_content.py
│   ├── repositories/          # Interfaces (Ports)
│   │   ├── document_repository.py
│   │   └── llm_provider.py
│   └── services/              # Services métier (interfaces)
│       ├── analyzer_service.py
│       ├── writer_service.py
│       └── reranker_service.py
│
├── application/               # 🎭 Cas d'usage
│   ├── use_cases/             # Orchestration métier
│   │   └── generate_application_content.py
│   └── builders/              # Builder Pattern
│       ├── agent_builder.py
│       └── crew_builder.py
│
├── infrastructure/            # 🔌 Implémentations (Adapters)
│   ├── ai/                    # AI services adapters
│   │   ├── llm_provider_adapter.py
│   │   ├── crewai_analyzer_adapter.py
│   │   ├── crewai_writer_adapter.py
│   │   └── reranker_adapter.py
│   └── vector_db/             # Vector DB adapters
│       └── qdrant_adapter.py
│
├── api/                       # 🌐 HTTP Endpoints (Adapters)
│   ├── generation.py
│   └── health.py
│
├── core/                      # ⚙️ Configuration
│   ├── container.py           # Dependency Injection
│   ├── config.py
│   └── llm_factory.py
│
└── models/                    # 📦 API Models (DTOs)
    ├── requests/
    └── responses/
```

## 🎨 Design Patterns Appliqués

### 1. **Builder Pattern**

Construction fluide d'objets complexes.

```python
# Agent Builder
agent = (AgentBuilder()
    .with_role("Analyzer")
    .with_goal("Extract information")
    .with_llm(llm)
    .with_memory(True)
    .build())

# Crew Builder
crew = (CrewBuilder()
    .add_agent(analyzer)
    .add_task(task)
    .with_process(Process.sequential)
    .build())
```

**Avantages :**
- ✅ Interface fluide et lisible
- ✅ Construction étape par étape
- ✅ Validation à la fin (build)
- ✅ Réutilisable et extensible

### 2. **Adapter Pattern**

Adapte les technologies externes aux interfaces du domaine.

```python
# Port (Domain)
class IDocumentRepository(ABC):
    @abstractmethod
    def search(self, query): ...

# Adapter (Infrastructure)
class QdrantAdapter(IDocumentRepository):
    def __init__(self, qdrant_service: QdrantService):
        self.qdrant = qdrant_service

    def search(self, query):
        return self.qdrant.search(query)
```

### 3. **Dependency Injection**

Container gérant toutes les dépendances.

```python
class Container:
    def llm_provider(self) -> ILLMProvider:
        if self._llm_provider is None:
            self._llm_provider = LLMProviderAdapter(get_llm_factory())
        return self._llm_provider

    def generate_content_use_case(self) -> GenerateApplicationContentUseCase:
        return GenerateApplicationContentUseCase(
            document_repository=self.document_repository(),
            analyzer_service=self.analyzer_service(),
            writer_service=self.writer_service(),
            reranker_service=self.reranker_service(),
        )
```

### 4. **Command Pattern**

Encapsule les requêtes en objets.

```python
@dataclass
class GenerateContentCommand:
    """Command pour générer du contenu."""
    job_offer_text: str
    content_type: str

# Usage
command = GenerateContentCommand(
    job_offer_text="...",
    content_type="email"
)
result = use_case.execute(command)
```

### 5. **Factory Pattern**

Création d'objets LLM configurés.

```python
class LLMFactory:
    def create_llm_for_agent(self, agent_name: str) -> BaseChatModel:
        config = self._get_agent_config(agent_name)
        provider = config.get("provider")

        if provider == "openai":
            return self._create_openai_llm(config)
        elif provider == "anthropic":
            return self._create_anthropic_llm(config)
```

## 🔄 Flux Complet d'une Requête

```
1. HTTP Request
   POST /api/v1/generate
   ↓
2. API Adapter (generation.py)
   - Validation
   - Crée Command
   ↓
3. Use Case (Application)
   command = GenerateContentCommand(...)
   result = use_case.execute(command)
   ↓
4. Use Case Orchestration
   a. job_offer = JobOffer(text)        # Domain Entity
   b. analysis = analyzer.analyze(...)   # Domain Service
   c. docs = repository.search(...)      # Repository (Port)
   d. reranked = reranker.rerank(...)    # Domain Service
   e. content = writer.write(...)        # Domain Service
   ↓
5. Infrastructure Adapters
   - CrewAIAnalyzerAdapter → CrewAI
   - QdrantAdapter → Qdrant
   - RerankerAdapter → Reranker
   - CrewAIWriterAdapter → CrewAI
   ↓
6. Domain Entities
   GeneratedContent(content, type, sources)
   ↓
7. API Response
   GenerateResponse(output, sources, trace_id)
```

## 💡 Avantages de cette Architecture

### Testabilité

```python
# Test du use case avec mocks (pas besoin de Qdrant réel !)
def test_generate_content_use_case():
    # Arrange
    mock_repository = Mock(spec=IDocumentRepository)
    mock_analyzer = Mock(spec=IAnalyzerService)
    mock_writer = Mock(spec=IWriterService)
    mock_reranker = Mock(spec=IRerankerService)

    use_case = GenerateApplicationContentUseCase(
        document_repository=mock_repository,
        analyzer_service=mock_analyzer,
        writer_service=mock_writer,
        reranker_service=mock_reranker,
    )

    # Act
    command = GenerateContentCommand(...)
    result = use_case.execute(command)

    # Assert
    assert result.content == "..."
```

### Indépendance des Frameworks

- Changer CrewAI → LangGraph ? Créer `LangGraphAnalyzerAdapter`
- Changer Qdrant → Pinecone ? Créer `PineconeAdapter`
- Aucune modification du domaine ou use case !

### Évolutivité

```python
# Ajouter un nouveau writer (GPT-4)
class GPT4WriterAdapter(IWriterService):
    def write(self, ...):
        # Implémentation GPT-4

# Utiliser dans le container
def writer_service(self) -> IWriterService:
    return GPT4WriterAdapter(...)  # Plug & play !
```

## 📊 Comparaison Avant/Après

### Avant (Monolithique)

```python
# ❌ Couplage fort
class GenerationWorkflow:
    def __init__(self):
        self.qdrant = get_qdrant_service()    # Concrete
        self.reranker = get_reranker_service()  # Concrete

    def generate(self, ...):
        # Création agent inline
        agent = create_analyzer_agent()
        # Logique métier mélangée avec infra
        results = self.qdrant.search(...)
        # Difficile à tester
```

### Après (Clean Architecture)

```python
# ✅ Découplage via interfaces
class GenerateApplicationContentUseCase:
    def __init__(
        self,
        document_repository: IDocumentRepository,  # Interface
        analyzer_service: IAnalyzerService,        # Interface
        writer_service: IWriterService,            # Interface
        reranker_service: IRerankerService,        # Interface
    ):
        # Dependency Injection
        self.repository = document_repository
        self.analyzer = analyzer_service
        self.writer = writer_service
        self.reranker = reranker_service

    def execute(self, command):
        # Pure business logic
        job_offer = JobOffer(command.job_offer_text)
        analysis = self.analyzer.analyze(job_offer)
        docs = self.repository.search(...)
        # Testable, extensible, maintenable
```

## 🎓 Principes Clés à Retenir

1. **Domain au centre** : Toutes les couches dépendent du domain
2. **Interfaces (Ports)** : Définir les contrats dans le domain
3. **Adapters** : Implémenter les interfaces dans l'infrastructure
4. **Use Cases** : Orchestrer la logique métier
5. **DI Container** : Gérer toutes les dépendances
6. **Entities** : Objets métier immutables
7. **Builders** : Construction fluide d'objets complexes

## 🚀 Pour Ajouter une Fonctionnalité

1. **Créer l'entity** dans `domain/entities/`
2. **Définir l'interface** dans `domain/repositories/` ou `domain/services/`
3. **Créer le use case** dans `application/use_cases/`
4. **Implémenter l'adapter** dans `infrastructure/`
5. **Wirer dans le container** dans `core/container.py`
6. **Exposer l'API** dans `api/`

## 📚 Ressources

- [Clean Architecture (Uncle Bob)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Design Patterns](https://refactoring.guru/design-patterns)

---

**Architecture par** : Team JobBooster
**Date** : 2025-10-03
**Version** : 3.0.0 (Clean Architecture)
```
