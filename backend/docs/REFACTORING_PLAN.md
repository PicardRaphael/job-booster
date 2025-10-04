# Plan de Refactoring - Clean Architecture & SOLID

> **Guide complet pour refactorer JobBooster selon Clean Architecture et les principes SOLID**
>
> Ce document est conçu pour être compréhensible par un développeur débutant.

---

## 📋 Table des matières

1. [Diagnostic des problèmes actuels](#diagnostic)
2. [Architecture cible](#architecture-cible)
3. [Plan d'implémentation](#plan-implementation)
4. [Détails des fichiers à créer](#details-fichiers)
5. [Ordre d'exécution recommandé](#ordre-execution)

---

## 🔍 Diagnostic des problèmes actuels {#diagnostic}

### ❌ Problème 1: Violation du Single Responsibility Principle (SRP)

#### 1.1 Use Case trop large

**Fichier**: `app/application/use_cases/generate_application_content.py`

**Problème**: Le use case `GenerateApplicationContentUseCase` fait **6 responsabilités différentes**:
1. Créer l'entité job offer
2. Analyser l'offre d'emploi
3. Chercher des documents dans Qdrant
4. Reranker les documents
5. Générer le contenu
6. Formater le résultat

**Pourquoi c'est un problème**:
- Impossible de réutiliser juste "l'analyse" sans tout le reste
- Tests compliqués (mock 4 services à chaque fois)
- Modification du reranking = risque de casser la génération
- Violation du principe: "Une classe = une raison de changer"

**Solution**: Créer 4 use cases atomiques + 1 orchestrateur

```
✅ AnalyzeJobOfferUseCase      - Analyser uniquement
✅ SearchDocumentsUseCase       - Chercher uniquement
✅ RerankDocumentsUseCase       - Reranker uniquement
✅ GenerateContentUseCase       - Générer uniquement
✅ GenerateApplicationOrchestrator - Compose les 4 use cases
```

---

#### 1.2 Adapters chargent les configs YAML

**Fichiers**:
- `app/infrastructure/ai/crewai_analyzer_adapter.py` (lignes 35-46)
- `app/infrastructure/ai/crewai_writer_adapter.py` (lignes 36-44)

**Problème**: Les adapters ont la méthode `_load_configs()` qui charge directement les fichiers YAML.

**Pourquoi c'est un problème**:
- L'adapter fait 2 choses: charger config + utiliser CrewAI
- Impossible de tester l'adapter sans fichiers YAML
- Violation SRP: "charger config" est une responsabilité séparée

**Solution**: Créer un `ConfigurationService` dans infrastructure

```python
# ✅ Nouveau service
class ConfigurationService:
    """Charge et parse les configs YAML."""
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]: ...
    def get_task_config(self, task_name: str) -> Dict[str, Any]: ...

# ✅ Adapter injecté avec config
class CrewAIAnalyzerAdapter:
    def __init__(self, llm_provider: ILLMProvider,
                 agent_config: Dict, task_config: Dict):
        # Pas de chargement YAML ici!
```

---

#### 1.3 API endpoint avec logique métier

**Fichier**: `app/api/generation.py` (lignes 47-78)

**Problème**: L'endpoint FastAPI fait:
1. Créer une trace Langfuse
2. Exécuter le use case
3. Vérifier si documents vides → erreur 404
4. Formater les sources
5. Flusher Langfuse

**Pourquoi c'est un problème**:
- L'API ne devrait être qu'un adaptateur HTTP
- La logique "pas de docs = erreur" est une règle métier → Domain
- La création de trace Langfuse devrait être dans un use case dédié
- Impossible de tester la validation sans FastAPI

**Solution**: Créer un `ObservabilityUseCase` et déplacer la validation

```python
# ✅ Use case dédié pour Langfuse
class TraceGenerationUseCase:
    def execute(self, command) -> TraceContext:
        trace = self.langfuse.create_trace(...)
        return TraceContext(trace_id=...)

# ✅ API devient simple
@router.post("")
async def generate_content(request: GenerateRequest):
    trace_context = trace_use_case.execute(...)
    result = generate_use_case.execute(..., trace_context)
    return GenerateResponse(...)  # Mapping simple
```

---

#### 1.4 LLMFactory charge les configs

**Fichier**: `app/core/llm_factory.py` (lignes 38-54)

**Problème**: `LLMFactory` charge directement `llm_config.yaml`

**Pourquoi c'est un problème**:
- Factory devrait juste "créer" des LLMs, pas charger des fichiers
- Le "core" layer ne devrait pas accéder au filesystem (violation Clean Archi)
- Impossible de tester la factory avec une config custom sans modifier le YAML

**Solution**: Injecter la config dans la factory

```python
# ✅ Factory pure (juste création)
class LLMFactory:
    def __init__(self, config: Dict[str, Any]):
        self.config = config  # Injecté, pas chargé!

    def create_llm(self, agent_name: str) -> BaseChatModel:
        # Juste création, pas de I/O
```

---

### ❌ Problème 2: Violation du Dependency Inversion Principle (DIP)

#### 2.1 Services legacy sans interfaces

**Fichiers**:
- `app/services/qdrant_service.py`
- `app/services/reranker.py`
- `app/services/embeddings.py`
- `app/services/langfuse_service.py`

**Problème**: Ces services sont utilisés directement sans interface

```python
# ❌ Container actuel
from app.services.qdrant_service import get_qdrant_service  # Import concret!
from app.services.reranker import get_reranker_service      # Import concret!

def document_repository(self):
    qdrant_service = get_qdrant_service()  # Dépend du concret
    return QdrantAdapter(qdrant_service)
```

**Pourquoi c'est un problème**:
- Le Container dépend de l'implémentation, pas de l'interface
- Impossible de remplacer Qdrant par une autre DB sans changer Container
- Violation DIP: "Dépendre d'abstractions, pas d'implémentations"

**Solution**: Créer des interfaces et migrer vers infrastructure

```python
# ✅ Domain interface
class IEmbeddingService(ABC):
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]: ...
    @abstractmethod
    def get_dimension(self) -> int: ...

# ✅ Infrastructure adapter
class MultilingualEmbeddingAdapter(IEmbeddingService):
    # Implémentation concrète

# ✅ Container dépend de l'interface
def embedding_service(self) -> IEmbeddingService:
    return MultilingualEmbeddingAdapter(...)
```

---

#### 2.2 Pas d'interface pour Langfuse

**Fichier**: `app/services/langfuse_service.py`

**Problème**: Langfuse utilisé directement dans l'API sans abstraction

**Pourquoi c'est un problème**:
- Impossible de changer d'outil d'observability (ex: Datadog, Honeycomb)
- Tests compliqués (besoin de mocker Langfuse directement)
- Couplage fort avec une librairie externe

**Solution**: Créer `IObservabilityService` interface

```python
# ✅ Domain interface
class IObservabilityService(ABC):
    @abstractmethod
    def create_trace(self, name: str, metadata: Dict) -> TraceContext: ...
    @abstractmethod
    def flush(self) -> None: ...

# ✅ Adapter Langfuse
class LangfuseAdapter(IObservabilityService):
    # Implémentation avec Langfuse

# ✅ Facile de créer un NoOpAdapter pour tests
class NoOpObservabilityAdapter(IObservabilityService):
    def create_trace(self, name, metadata):
        return TraceContext(trace_id="test")
```

---

### ❌ Problème 3: Violation de l'Interface Segregation Principle (ISP)

#### 3.1 IWriterService trop large

**Fichier**: `app/domain/services/writer_service.py`

**Problème**: Une seule interface `IWriterService` pour 3 types de contenu différents

```python
# ❌ Interface actuelle
class IWriterService(ABC):
    def write(self, job_offer, analysis, context, content_type): ...
    # content_type peut être: EMAIL, LINKEDIN, LETTER
```

**Pourquoi c'est un problème**:
- Si on veut juste un EmailWriter, on doit implémenter les 3 types
- Violation ISP: "Les clients ne devraient pas dépendre d'interfaces qu'ils n'utilisent pas"
- Impossible d'avoir des implémentations spécialisées par type

**Solution**: Créer 3 interfaces spécialisées

```python
# ✅ Interfaces granulaires
class IEmailWriter(ABC):
    @abstractmethod
    def write_email(self, job_offer, analysis, context) -> str: ...

class ILinkedInWriter(ABC):
    @abstractmethod
    def write_linkedin_post(self, job_offer, analysis, context) -> str: ...

class ILetterWriter(ABC):
    @abstractmethod
    def write_cover_letter(self, job_offer, analysis, context) -> str: ...

# ✅ Composite pour compatibilité
class IContentWriterService(ABC):
    @abstractmethod
    def get_email_writer(self) -> IEmailWriter: ...
    @abstractmethod
    def get_linkedin_writer(self) -> ILinkedInWriter: ...
    @abstractmethod
    def get_letter_writer(self) -> ILetterWriter: ...
```

---

### ❌ Problème 4: Violations Clean Architecture

#### 4.1 Pas de DTOs entre les couches

**Problème**: Les entités du domain sont utilisées directement dans l'API

```python
# ❌ API utilise directement domain entities
from app.domain.entities.job_offer import JobOffer

@router.post("")
def generate(request: GenerateRequest):
    job_offer = JobOffer(text=request.job_offer)  # Domain entity dans API!
```

**Pourquoi c'est un problème**:
- Couplage fort entre API et Domain
- Si on change JobOffer (domain), l'API casse
- Violation Clean Archi: "Les couches externes dépendent des internes, pas l'inverse"

**Solution**: Créer des DTOs (Data Transfer Objects)

```python
# ✅ Application layer DTOs
@dataclass
class JobOfferDTO:
    """DTO pour transférer data entre couches."""
    text: str

# ✅ Use case utilise DTOs
class AnalyzeJobOfferCommand:
    job_offer: JobOfferDTO  # DTO, pas entity!

# ✅ Use case convertit DTO → Entity
class AnalyzeJobOfferUseCase:
    def execute(self, command: AnalyzeJobOfferCommand) -> JobAnalysisDTO:
        # Conversion DTO → Domain Entity
        job_offer = JobOffer(text=command.job_offer.text)
        analysis = self.analyzer.analyze(job_offer)

        # Conversion Domain Entity → DTO
        return JobAnalysisDTO(
            summary=analysis.summary,
            key_skills=analysis.key_skills,
            ...
        )
```

---

#### 4.2 Core layer charge des fichiers (violation de couche)

**Fichier**: `app/core/llm_factory.py` (ligne 40)

**Problème**: Le "core" layer ouvre des fichiers YAML

```python
# ❌ Core layer fait de l'I/O
config_path = Path("app/agents/config/llm_config.yaml")
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
```

**Pourquoi c'est un problème**:
- Le Core layer devrait contenir de la logique pure (config, logging, DI)
- L'accès filesystem = Infrastructure concern
- Violation Clean Archi: "Core ne dépend de rien"

**Solution**: Déplacer chargement config vers Infrastructure

```python
# ✅ Infrastructure: Config Loader
class YAMLConfigurationLoader:
    def load_llm_config(self) -> Dict[str, Any]:
        # I/O ici, c'est infrastructure!

# ✅ Core: Factory reçoit config
class LLMFactory:
    def __init__(self, config: Dict[str, Any]):
        self.config = config  # Pas d'I/O!
```

---

#### 4.3 Builders dans Application layer dépendent de CrewAI

**Fichiers**:
- `app/application/builders/agent_builder.py`
- `app/application/builders/crew_builder.py`

**Problème**: Application layer importe `from crewai import Agent, Crew`

**Pourquoi c'est un problème**:
- Application layer ne devrait dépendre QUE du Domain
- CrewAI est un détail d'infrastructure
- Si on change CrewAI → Autogen, on doit modifier Application layer

**Solution**: Déplacer builders vers Infrastructure

```
❌ Avant:
app/application/builders/
    agent_builder.py    # Importe crewai
    crew_builder.py     # Importe crewai

✅ Après:
app/infrastructure/ai/crewai/
    agent_builder.py    # Ok d'importer crewai ici
    crew_builder.py     # Ok d'importer crewai ici
```

---

## 🎯 Architecture cible {#architecture-cible}

### Nouvelle structure de dossiers

```
backend/app/
│
├── domain/                          # ❤️ Cœur métier (pas de dépendances externes)
│   ├── entities/
│   │   ├── job_offer.py            # Entity (Value Object)
│   │   ├── job_analysis.py         # Entity (Value Object)
│   │   └── generated_content.py    # Entity (Value Object)
│   │
│   ├── value_objects/              # ✨ NOUVEAU
│   │   ├── trace_context.py        # VO: trace_id, metadata
│   │   ├── search_query.py         # VO: query, filters
│   │   └── content_metadata.py     # VO: type, length, quality
│   │
│   ├── repositories/               # Interfaces (Ports)
│   │   ├── document_repository.py  # IDocumentRepository
│   │   ├── embedding_service.py    # ✨ NOUVEAU: IEmbeddingService
│   │   └── llm_provider.py
│   │
│   └── services/                   # Interfaces (Ports)
│       ├── analyzer_service.py     # IAnalyzerService
│       ├── writer_service.py       # IEmailWriter, ILinkedInWriter, ILetterWriter
│       ├── reranker_service.py     # IRerankerService
│       └── observability_service.py # ✨ NOUVEAU: IObservabilityService
│
├── application/                    # 🎯 Cas d'usage (logique applicative)
│   ├── dtos/                       # ✨ NOUVEAU: Data Transfer Objects
│   │   ├── job_offer_dto.py
│   │   ├── job_analysis_dto.py
│   │   ├── document_dto.py
│   │   └── generation_result_dto.py
│   │
│   ├── commands/                   # ✨ NOUVEAU: Commands (CQRS pattern)
│   │   ├── analyze_job_offer_command.py
│   │   ├── search_documents_command.py
│   │   ├── rerank_documents_command.py
│   │   └── generate_content_command.py
│   │
│   ├── use_cases/                  # ✨ REFACTORÉ: Use cases atomiques
│   │   ├── analyze_job_offer.py           # Use case 1
│   │   ├── search_documents.py            # Use case 2
│   │   ├── rerank_documents.py            # Use case 3
│   │   ├── generate_email.py              # Use case 4a
│   │   ├── generate_linkedin.py           # Use case 4b
│   │   ├── generate_cover_letter.py       # Use case 4c
│   │   └── trace_generation.py            # ✨ NOUVEAU: Observability
│   │
│   └── orchestrators/              # ✨ NOUVEAU: Compose use cases
│       └── generate_application_orchestrator.py
│
├── infrastructure/                 # 🔧 Détails techniques (adapters)
│   ├── config/                     # ✨ NOUVEAU: Configuration loading
│   │   ├── yaml_config_loader.py
│   │   └── env_config_loader.py
│   │
│   ├── ai/
│   │   ├── crewai/                 # ✨ DÉPLACÉ depuis application/
│   │   │   ├── agent_builder.py
│   │   │   ├── crew_builder.py
│   │   │   ├── analyzer_adapter.py
│   │   │   ├── email_writer_adapter.py
│   │   │   ├── linkedin_writer_adapter.py
│   │   │   └── letter_writer_adapter.py
│   │   │
│   │   ├── llm_provider_adapter.py
│   │   └── reranker_adapter.py
│   │
│   ├── vector_db/
│   │   ├── qdrant_adapter.py
│   │   └── embedding_adapter.py    # ✨ NOUVEAU: Wraps embeddings service
│   │
│   └── observability/              # ✨ NOUVEAU
│       ├── langfuse_adapter.py
│       └── noop_adapter.py         # Pour tests
│
├── core/                           # ⚙️ Configuration centrale
│   ├── container.py                # ✨ MODIFIÉ: Injection avec tous les nouveaux services
│   ├── config.py                   # Settings (Pydantic)
│   ├── llm_factory.py              # ✨ MODIFIÉ: N'ouvre plus de fichiers
│   └── logging.py
│
└── api/                            # 🌐 Adaptateur HTTP
    ├── generation.py               # ✨ SIMPLIFIÉ: Juste mapping HTTP ↔ Use Cases
    ├── health.py
    └── mappers/                    # ✨ NOUVEAU: Conversion Request/Response ↔ DTOs
        └── generation_mapper.py
```

---

### Diagramme des flux

#### ✅ Flux complet de génération

```
┌─────────────────────────────────────────────────────────────────────┐
│                           API LAYER                                 │
│  POST /generate                                                     │
│  1. Reçoit GenerateRequest                                          │
│  2. Mapper: Request → DTOs                                          │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                                │
│  Orchestrator: GenerateApplicationOrchestrator                      │
│                                                                     │
│  execute(command: GenerateApplicationCommand) {                     │
│    ┌─────────────────────────────────────────────────────┐         │
│    │ 1. TraceGenerationUseCase.execute()                 │         │
│    │    → Create trace, return TraceContext              │         │
│    └─────────────────────────────────────────────────────┘         │
│                         ▼                                           │
│    ┌─────────────────────────────────────────────────────┐         │
│    │ 2. AnalyzeJobOfferUseCase.execute()                 │         │
│    │    Input:  JobOfferDTO                              │         │
│    │    Output: JobAnalysisDTO                           │         │
│    └─────────────────────────────────────────────────────┘         │
│                         ▼                                           │
│    ┌─────────────────────────────────────────────────────┐         │
│    │ 3. SearchDocumentsUseCase.execute()                 │         │
│    │    Input:  SearchQuery (from JobAnalysisDTO)        │         │
│    │    Output: List[DocumentDTO]                        │         │
│    └─────────────────────────────────────────────────────┘         │
│                         ▼                                           │
│    ┌─────────────────────────────────────────────────────┐         │
│    │ 4. RerankDocumentsUseCase.execute()                 │         │
│    │    Input:  List[DocumentDTO]                        │         │
│    │    Output: List[DocumentDTO] (reranked)             │         │
│    └─────────────────────────────────────────────────────┘         │
│                         ▼                                           │
│    ┌─────────────────────────────────────────────────────┐         │
│    │ 5. GenerateEmailUseCase.execute()  (ou LinkedIn, Letter)      │
│    │    Input:  JobAnalysisDTO + List[DocumentDTO]       │         │
│    │    Output: GeneratedContentDTO                      │         │
│    └─────────────────────────────────────────────────────┘         │
│  }                                                                  │
│                                                                     │
│  Return: GenerationResultDTO                                        │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DOMAIN LAYER                                   │
│  - JobOffer entity                                                  │
│  - JobAnalysis entity                                               │
│  - IAnalyzerService interface                                       │
│  - IDocumentRepository interface                                    │
│  - IEmailWriter interface                                           │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   INFRASTRUCTURE LAYER                              │
│  - CrewAIAnalyzerAdapter (implements IAnalyzerService)              │
│  - QdrantAdapter (implements IDocumentRepository)                   │
│  - EmailWriterAdapter (implements IEmailWriter)                     │
│  - LangfuseAdapter (implements IObservabilityService)               │
│                                                                     │
│  External: CrewAI, Qdrant, Langfuse, OpenAI                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📝 Plan d'implémentation {#plan-implementation}

### Phase 1: Créer les DTOs et Commands (Application Layer)

**Objectif**: Découpler les couches avec des objets de transfert

**Fichiers à créer**:

1. `app/application/dtos/job_offer_dto.py`
```python
@dataclass
class JobOfferDTO:
    """DTO pour transférer job offer entre couches."""
    text: str
```

2. `app/application/dtos/job_analysis_dto.py`
```python
@dataclass
class JobAnalysisDTO:
    """DTO pour job analysis."""
    summary: str
    key_skills: List[str]
    position: str
    company: str | None = None
```

3. `app/application/dtos/document_dto.py`
```python
@dataclass
class DocumentDTO:
    """DTO pour document RAG."""
    id: str
    text: str
    score: float
    source: str
    rerank_score: float | None = None
```

4. `app/application/dtos/generation_result_dto.py`
```python
@dataclass
class GenerationResultDTO:
    """DTO pour résultat de génération."""
    content: str
    content_type: str
    sources: List[DocumentDTO]
    trace_id: str | None = None
```

5. `app/application/commands/analyze_job_offer_command.py`
```python
@dataclass
class AnalyzeJobOfferCommand:
    """Command pour analyser job offer."""
    job_offer: JobOfferDTO
    trace_context: TraceContextDTO | None = None
```

6. `app/application/commands/search_documents_command.py`
```python
@dataclass
class SearchDocumentsCommand:
    """Command pour chercher documents."""
    query: str
    limit: int = 10
    score_threshold: float = 0.5
```

7. `app/application/commands/rerank_documents_command.py`
```python
@dataclass
class RerankDocumentsCommand:
    """Command pour reranker documents."""
    query: str
    documents: List[DocumentDTO]
    top_k: int = 5
```

8. `app/application/commands/generate_content_command.py`
```python
@dataclass
class GenerateContentCommand:
    """Command pour générer contenu."""
    job_offer: JobOfferDTO
    analysis: JobAnalysisDTO
    documents: List[DocumentDTO]
    content_type: str  # "email", "linkedin", "letter"
```

---

### Phase 2: Créer les Use Cases atomiques

**Objectif**: Séparer les responsabilités en use cases réutilisables

**Fichiers à créer**:

1. `app/application/use_cases/analyze_job_offer.py`
```python
class AnalyzeJobOfferUseCase:
    """Use case pour analyser une offre d'emploi."""

    def __init__(self, analyzer_service: IAnalyzerService):
        self.analyzer_service = analyzer_service

    def execute(self, command: AnalyzeJobOfferCommand) -> JobAnalysisDTO:
        """
        Analyse job offer et retourne structured analysis.

        Args:
            command: Command avec job offer DTO

        Returns:
            JobAnalysisDTO avec summary, skills, position
        """
        # 1. Convert DTO → Domain Entity
        job_offer = JobOffer(text=command.job_offer.text)

        # 2. Domain service (business logic)
        analysis = self.analyzer_service.analyze(job_offer)

        # 3. Convert Domain Entity → DTO
        return JobAnalysisDTO(
            summary=analysis.summary,
            key_skills=analysis.key_skills,
            position=analysis.position,
            company=analysis.company,
        )
```

2. `app/application/use_cases/search_documents.py`
```python
class SearchDocumentsUseCase:
    """Use case pour chercher documents dans le vector store."""

    def __init__(self, document_repository: IDocumentRepository):
        self.document_repository = document_repository

    def execute(self, command: SearchDocumentsCommand) -> List[DocumentDTO]:
        """
        Cherche documents similaires dans Qdrant.

        Args:
            command: Command avec query et paramètres

        Returns:
            Liste de DocumentDTO
        """
        # 1. Repository call
        results = self.document_repository.search(
            query=command.query,
            limit=command.limit,
            score_threshold=command.score_threshold,
        )

        # 2. Convert dict → DTO
        return [
            DocumentDTO(
                id=doc["id"],
                text=doc["text"],
                score=doc["score"],
                source=doc["source"],
            )
            for doc in results
        ]
```

3. `app/application/use_cases/rerank_documents.py`
```python
class RerankDocumentsUseCase:
    """Use case pour reranker les documents."""

    def __init__(self, reranker_service: IRerankerService):
        self.reranker_service = reranker_service

    def execute(self, command: RerankDocumentsCommand) -> List[DocumentDTO]:
        """
        Rerank documents par pertinence.

        Args:
            command: Command avec query et documents

        Returns:
            Liste de DocumentDTO reranked
        """
        # 1. Convert DTOs → dicts for service
        docs_dicts = [
            {"id": d.id, "text": d.text, "score": d.score, "source": d.source}
            for d in command.documents
        ]

        # 2. Rerank
        reranked = self.reranker_service.rerank(
            query=command.query,
            documents=docs_dicts,
            top_k=command.top_k,
        )

        # 3. Convert back to DTOs
        return [
            DocumentDTO(
                id=doc["id"],
                text=doc["text"],
                score=doc["score"],
                source=doc["source"],
                rerank_score=doc.get("rerank_score"),
            )
            for doc in reranked
        ]
```

4. `app/application/use_cases/generate_email.py`
```python
class GenerateEmailUseCase:
    """Use case pour générer un email de motivation."""

    def __init__(self, email_writer: IEmailWriter):
        self.email_writer = email_writer

    def execute(self, command: GenerateContentCommand) -> str:
        """
        Génère email basé sur job offer et context.

        Args:
            command: Command avec job offer, analysis, documents

        Returns:
            Email content (str)
        """
        # 1. Build context from documents
        context = self._build_context(command.documents)

        # 2. Convert DTOs → Entities
        job_offer = JobOffer(text=command.job_offer.text)
        analysis = JobAnalysis(
            summary=command.analysis.summary,
            key_skills=command.analysis.key_skills,
            position=command.analysis.position,
            company=command.analysis.company,
        )

        # 3. Generate content
        return self.email_writer.write_email(
            job_offer=job_offer,
            analysis=analysis,
            context=context,
        )

    def _build_context(self, documents: List[DocumentDTO]) -> str:
        """Build RAG context string from documents."""
        if not documents:
            return ""

        parts = [
            f"Source: {doc.source}\n{doc.text}"
            for doc in documents
        ]
        return "\n\n".join(parts)
```

5. `app/application/use_cases/generate_linkedin.py` (similaire à generate_email)

6. `app/application/use_cases/generate_cover_letter.py` (similaire à generate_email)

7. `app/application/use_cases/trace_generation.py`
```python
@dataclass
class TraceContextDTO:
    """DTO pour trace context."""
    trace_id: str
    metadata: Dict[str, Any]

class TraceGenerationUseCase:
    """Use case pour créer trace d'observability."""

    def __init__(self, observability_service: IObservabilityService):
        self.observability_service = observability_service

    def execute(self, name: str, metadata: Dict[str, Any]) -> TraceContextDTO:
        """
        Crée trace pour observability.

        Args:
            name: Nom de la trace
            metadata: Metadata associée

        Returns:
            TraceContextDTO avec trace_id
        """
        trace = self.observability_service.create_trace(
            name=name,
            metadata=metadata,
        )

        return TraceContextDTO(
            trace_id=trace.trace_id,
            metadata=metadata,
        )
```

---

### Phase 3: Créer l'Orchestrateur

**Objectif**: Composer les use cases atomiques

**Fichier à créer**: `app/application/orchestrators/generate_application_orchestrator.py`

```python
@dataclass
class GenerateApplicationCommand:
    """Command pour orchestrator."""
    job_offer: JobOfferDTO
    content_type: str  # "email", "linkedin", "letter"

class GenerateApplicationOrchestrator:
    """
    Orchestrateur qui compose les use cases atomiques.

    Responsabilité: Coordonner les use cases, pas faire la logique métier.
    """

    def __init__(
        self,
        trace_use_case: TraceGenerationUseCase,
        analyze_use_case: AnalyzeJobOfferUseCase,
        search_use_case: SearchDocumentsUseCase,
        rerank_use_case: RerankDocumentsUseCase,
        email_use_case: GenerateEmailUseCase,
        linkedin_use_case: GenerateLinkedInUseCase,
        letter_use_case: GenerateCoverLetterUseCase,
    ):
        self.trace_use_case = trace_use_case
        self.analyze_use_case = analyze_use_case
        self.search_use_case = search_use_case
        self.rerank_use_case = rerank_use_case

        # Map content type → use case
        self.writer_use_cases = {
            "email": email_use_case,
            "linkedin": linkedin_use_case,
            "letter": letter_use_case,
        }

    def execute(self, command: GenerateApplicationCommand) -> GenerationResultDTO:
        """
        Exécute le flow complet de génération.

        Flow:
        1. Create trace
        2. Analyze job offer
        3. Search documents
        4. Rerank documents
        5. Generate content
        6. Return result
        """
        logger.info("orchestrator_starting", content_type=command.content_type)

        # 1. Trace
        trace_context = self.trace_use_case.execute(
            name="job_application_generation",
            metadata={
                "content_type": command.content_type,
                "offer_length": len(command.job_offer.text),
            },
        )

        # 2. Analyze
        analysis = self.analyze_use_case.execute(
            AnalyzeJobOfferCommand(
                job_offer=command.job_offer,
                trace_context=trace_context,
            )
        )

        # 3. Search
        search_query = self._build_search_query(analysis)
        documents = self.search_use_case.execute(
            SearchDocumentsCommand(
                query=search_query,
                limit=10,
                score_threshold=0.5,
            )
        )

        # Validation métier: documents requis
        if not documents:
            raise NoDatabaseDocumentsError(
                "Aucune donnée utilisateur trouvée. Veuillez ingérer vos documents."
            )

        # 4. Rerank
        reranked_docs = self.rerank_use_case.execute(
            RerankDocumentsCommand(
                query=search_query,
                documents=documents,
                top_k=5,
            )
        )

        # 5. Generate content (use case spécifique au type)
        writer_use_case = self.writer_use_cases[command.content_type]
        content = writer_use_case.execute(
            GenerateContentCommand(
                job_offer=command.job_offer,
                analysis=analysis,
                documents=reranked_docs,
                content_type=command.content_type,
            )
        )

        # 6. Return result
        logger.info("orchestrator_completed", content_type=command.content_type)
        return GenerationResultDTO(
            content=content,
            content_type=command.content_type,
            sources=reranked_docs,
            trace_id=trace_context.trace_id,
        )

    def _build_search_query(self, analysis: JobAnalysisDTO) -> str:
        """Build search query from analysis."""
        parts = [analysis.position]
        if analysis.key_skills:
            parts.extend(analysis.key_skills[:5])
        if analysis.company:
            parts.append(analysis.company)
        return " ".join(parts)
```

---

### Phase 4: Créer interfaces manquantes (Domain Layer)

**Objectif**: Ajouter abstractions pour services legacy

**Fichiers à créer**:

1. `app/domain/repositories/embedding_service.py`
```python
class IEmbeddingService(ABC):
    """Interface pour embedding service."""

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed texts to vectors."""
        pass

    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """Embed single query."""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        pass
```

2. `app/domain/services/observability_service.py`
```python
@dataclass
class TraceContext:
    """Domain value object for trace."""
    trace_id: str
    metadata: Dict[str, Any]

class IObservabilityService(ABC):
    """Interface pour observability service."""

    @abstractmethod
    def create_trace(self, name: str, metadata: Dict[str, Any]) -> TraceContext:
        """Create trace."""
        pass

    @abstractmethod
    def flush(self) -> None:
        """Flush traces."""
        pass
```

3. **Modifier** `app/domain/services/writer_service.py`
```python
# Séparer en 3 interfaces granulaires

class IEmailWriter(ABC):
    """Interface pour email writer."""

    @abstractmethod
    def write_email(
        self,
        job_offer: JobOffer,
        analysis: JobAnalysis,
        context: str,
    ) -> str:
        pass

class ILinkedInWriter(ABC):
    """Interface pour LinkedIn writer."""

    @abstractmethod
    def write_linkedin_post(
        self,
        job_offer: JobOffer,
        analysis: JobAnalysis,
        context: str,
    ) -> str:
        pass

class ILetterWriter(ABC):
    """Interface pour cover letter writer."""

    @abstractmethod
    def write_cover_letter(
        self,
        job_offer: JobOffer,
        analysis: JobAnalysis,
        context: str,
    ) -> str:
        pass

# Composite interface pour faciliter DI
class IContentWriterService(ABC):
    """Composite interface pour tous les writers."""

    @abstractmethod
    def get_email_writer(self) -> IEmailWriter:
        pass

    @abstractmethod
    def get_linkedin_writer(self) -> ILinkedInWriter:
        pass

    @abstractmethod
    def get_letter_writer(self) -> ILetterWriter:
        pass
```

---

### Phase 5: Migrer services legacy vers Infrastructure

**Objectif**: Wrapper services existants avec interfaces

**Fichiers à créer**:

1. `app/infrastructure/vector_db/embedding_adapter.py`
```python
from app.services.embeddings import get_embedding_service

class MultilingualEmbeddingAdapter(IEmbeddingService):
    """Adapter pour service embeddings existant."""

    def __init__(self):
        self._embedding_service = get_embedding_service()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return self._embedding_service.embed_texts(texts)

    def embed_query(self, query: str) -> List[float]:
        return self._embedding_service.embed_query(query)

    def get_dimension(self) -> int:
        return self._embedding_service.get_dimension()
```

2. `app/infrastructure/observability/langfuse_adapter.py`
```python
from app.services.langfuse_service import get_langfuse_service

class LangfuseAdapter(IObservabilityService):
    """Adapter pour Langfuse."""

    def __init__(self):
        self._langfuse = get_langfuse_service()

    def create_trace(self, name: str, metadata: Dict[str, Any]) -> TraceContext:
        trace = self._langfuse.create_trace(name=name, metadata=metadata)
        return TraceContext(
            trace_id=str(trace.id) if hasattr(trace, "id") else "unknown",
            metadata=metadata,
        )

    def flush(self) -> None:
        self._langfuse.flush()
```

3. `app/infrastructure/observability/noop_adapter.py`
```python
class NoOpObservabilityAdapter(IObservabilityService):
    """Adapter no-op pour tests."""

    def create_trace(self, name: str, metadata: Dict[str, Any]) -> TraceContext:
        return TraceContext(trace_id="noop", metadata=metadata)

    def flush(self) -> None:
        pass  # No-op
```

---

### Phase 6: Créer Configuration Services (Infrastructure)

**Objectif**: Extraire chargement config des adapters et core

**Fichiers à créer**:

1. `app/infrastructure/config/yaml_config_loader.py`
```python
class YAMLConfigurationLoader:
    """Service pour charger configs YAML."""

    def __init__(self, config_dir: Path = Path("app/agents/config")):
        self.config_dir = config_dir

    def load_agents_config(self) -> Dict[str, Any]:
        """Charge agents.yaml."""
        path = self.config_dir / "agents.yaml"
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def load_tasks_config(self) -> Dict[str, Any]:
        """Charge tasks.yaml."""
        path = self.config_dir / "tasks.yaml"
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def load_llm_config(self) -> Dict[str, Any]:
        """Charge llm_config.yaml."""
        path = self.config_dir / "llm_config.yaml"
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get config pour agent spécifique."""
        agents = self.load_agents_config()
        return agents.get(agent_name, {})

    def get_task_config(self, task_name: str) -> Dict[str, Any]:
        """Get config pour task spécifique."""
        tasks = self.load_tasks_config()
        return tasks.get(task_name, {})
```

2. **Modifier** `app/core/llm_factory.py`
```python
# Ne charge plus les fichiers, reçoit config en injection

class LLMFactory:
    """Factory pour créer LLMs (sans I/O)."""

    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initialize with config (injected).

        Args:
            llm_config: Config dict (déjà chargé par ConfigLoader)
        """
        self.config = llm_config
        logger.info("llm_factory_initialized")

    # Reste du code identique...
    # Mais plus de _load_config() !
```

3. **Modifier** adapters CrewAI pour recevoir configs

```python
# app/infrastructure/ai/crewai/analyzer_adapter.py

class CrewAIAnalyzerAdapter(IAnalyzerService):
    """Adapter pour analyzer avec CrewAI."""

    def __init__(
        self,
        llm_provider: ILLMProvider,
        agent_config: Dict[str, Any],  # ✅ Injecté!
        task_config: Dict[str, Any],   # ✅ Injecté!
    ):
        self.llm_provider = llm_provider
        self.agent_config = agent_config
        self.task_config = task_config
        # Plus de _load_configs() !
```

---

### Phase 7: Déplacer Builders vers Infrastructure

**Objectif**: Respecter séparation des couches

**Fichiers à déplacer**:

```bash
# Déplacer
app/application/builders/agent_builder.py
app/application/builders/crew_builder.py

# Vers
app/infrastructure/ai/crewai/agent_builder.py
app/infrastructure/ai/crewai/crew_builder.py
```

**Mettre à jour imports**:
```python
# Avant
from app.application.builders import AgentBuilder, CrewBuilder

# Après
from app.infrastructure.ai.crewai import AgentBuilder, CrewBuilder
```

---

### Phase 8: Séparer Writers par type

**Objectif**: ISP - interfaces granulaires

**Fichiers à créer**:

1. `app/infrastructure/ai/crewai/email_writer_adapter.py`
```python
class EmailWriterAdapter(IEmailWriter):
    """Adapter pour email writer avec CrewAI."""

    def __init__(
        self,
        llm_provider: ILLMProvider,
        agent_config: Dict[str, Any],
        task_config: Dict[str, Any],
    ):
        self.llm_provider = llm_provider
        self.agent_config = agent_config
        self.task_config = task_config

    def write_email(
        self,
        job_offer: JobOffer,
        analysis: JobAnalysis,
        context: str,
    ) -> str:
        """Generate email using CrewAI."""
        llm = self.llm_provider.create_llm("email_writer")
        agent = AgentBuilder().from_config(self.agent_config).with_llm(llm).build()
        task = Task(
            description=self.task_config["description"],
            expected_output=self.task_config["expected_output"],
            agent=agent,
        )
        crew = CrewBuilder().add_agent(agent).add_task(task).build()

        result = crew.kickoff(inputs={
            "job_offer": job_offer.text,
            "analysis": analysis.summary,
            "rag_context": context,
        })

        return str(result)
```

2. `app/infrastructure/ai/crewai/linkedin_writer_adapter.py` (similaire)

3. `app/infrastructure/ai/crewai/letter_writer_adapter.py` (similaire)

4. `app/infrastructure/ai/crewai/content_writer_service.py`
```python
class CrewAIContentWriterService(IContentWriterService):
    """Composite service pour tous les writers."""

    def __init__(
        self,
        email_writer: IEmailWriter,
        linkedin_writer: ILinkedInWriter,
        letter_writer: ILetterWriter,
    ):
        self._email_writer = email_writer
        self._linkedin_writer = linkedin_writer
        self._letter_writer = letter_writer

    def get_email_writer(self) -> IEmailWriter:
        return self._email_writer

    def get_linkedin_writer(self) -> ILinkedInWriter:
        return self._linkedin_writer

    def get_letter_writer(self) -> ILetterWriter:
        return self._letter_writer
```

---

### Phase 9: Refactorer Container

**Objectif**: Injecter toutes les nouvelles dépendances

**Modifier**: `app/core/container.py`

```python
class Container:
    """Dependency Injection Container."""

    def __init__(self):
        # Skip si déjà init
        if self._initialized:
            return

        # === Configuration ===
        self._config_loader: Optional[YAMLConfigurationLoader] = None

        # === Infrastructure Services ===
        self._llm_provider: Optional[ILLMProvider] = None
        self._embedding_service: Optional[IEmbeddingService] = None
        self._document_repository: Optional[IDocumentRepository] = None
        self._observability_service: Optional[IObservabilityService] = None

        # === Domain Services ===
        self._analyzer_service: Optional[IAnalyzerService] = None
        self._reranker_service: Optional[IRerankerService] = None
        self._content_writer_service: Optional[IContentWriterService] = None

        # === Use Cases ===
        self._trace_use_case: Optional[TraceGenerationUseCase] = None
        self._analyze_use_case: Optional[AnalyzeJobOfferUseCase] = None
        self._search_use_case: Optional[SearchDocumentsUseCase] = None
        self._rerank_use_case: Optional[RerankDocumentsUseCase] = None
        self._generate_email_use_case: Optional[GenerateEmailUseCase] = None
        self._generate_linkedin_use_case: Optional[GenerateLinkedInUseCase] = None
        self._generate_letter_use_case: Optional[GenerateCoverLetterUseCase] = None

        # === Orchestrators ===
        self._generate_application_orchestrator: Optional[GenerateApplicationOrchestrator] = None

        self._initialized = True

    # === Configuration ===

    def config_loader(self) -> YAMLConfigurationLoader:
        """Get config loader (singleton)."""
        if self._config_loader is None:
            self._config_loader = YAMLConfigurationLoader()
        return self._config_loader

    # === Infrastructure ===

    def llm_provider(self) -> ILLMProvider:
        """Get LLM provider."""
        if self._llm_provider is None:
            # Charge config via loader
            llm_config = self.config_loader().load_llm_config()
            llm_factory = LLMFactory(llm_config)  # ✅ Injecté!
            self._llm_provider = LLMProviderAdapter(llm_factory)
        return self._llm_provider

    def embedding_service(self) -> IEmbeddingService:
        """Get embedding service."""
        if self._embedding_service is None:
            self._embedding_service = MultilingualEmbeddingAdapter()
        return self._embedding_service

    def observability_service(self) -> IObservabilityService:
        """Get observability service."""
        if self._observability_service is None:
            self._observability_service = LangfuseAdapter()
        return self._observability_service

    # === Domain Services ===

    def analyzer_service(self) -> IAnalyzerService:
        """Get analyzer service."""
        if self._analyzer_service is None:
            llm_provider = self.llm_provider()
            agent_config = self.config_loader().get_agent_config("analyzer")
            task_config = self.config_loader().get_task_config("analyze_offer")
            self._analyzer_service = CrewAIAnalyzerAdapter(
                llm_provider, agent_config, task_config
            )
        return self._analyzer_service

    def content_writer_service(self) -> IContentWriterService:
        """Get content writer service (composite)."""
        if self._content_writer_service is None:
            llm_provider = self.llm_provider()
            config_loader = self.config_loader()

            # Email writer
            email_writer = EmailWriterAdapter(
                llm_provider,
                config_loader.get_agent_config("email_writer"),
                config_loader.get_task_config("write_email"),
            )

            # LinkedIn writer
            linkedin_writer = LinkedInWriterAdapter(
                llm_provider,
                config_loader.get_agent_config("linkedin_writer"),
                config_loader.get_task_config("write_linkedin"),
            )

            # Letter writer
            letter_writer = LetterWriterAdapter(
                llm_provider,
                config_loader.get_agent_config("letter_writer"),
                config_loader.get_task_config("write_letter"),
            )

            # Composite
            self._content_writer_service = CrewAIContentWriterService(
                email_writer, linkedin_writer, letter_writer
            )
        return self._content_writer_service

    # === Use Cases ===

    def trace_use_case(self) -> TraceGenerationUseCase:
        """Get trace use case."""
        if self._trace_use_case is None:
            self._trace_use_case = TraceGenerationUseCase(
                self.observability_service()
            )
        return self._trace_use_case

    def analyze_use_case(self) -> AnalyzeJobOfferUseCase:
        """Get analyze use case."""
        if self._analyze_use_case is None:
            self._analyze_use_case = AnalyzeJobOfferUseCase(
                self.analyzer_service()
            )
        return self._analyze_use_case

    def search_use_case(self) -> SearchDocumentsUseCase:
        """Get search use case."""
        if self._search_use_case is None:
            self._search_use_case = SearchDocumentsUseCase(
                self.document_repository()
            )
        return self._search_use_case

    def rerank_use_case(self) -> RerankDocumentsUseCase:
        """Get rerank use case."""
        if self._rerank_use_case is None:
            self._rerank_use_case = RerankDocumentsUseCase(
                self.reranker_service()
            )
        return self._rerank_use_case

    def generate_email_use_case(self) -> GenerateEmailUseCase:
        """Get generate email use case."""
        if self._generate_email_use_case is None:
            email_writer = self.content_writer_service().get_email_writer()
            self._generate_email_use_case = GenerateEmailUseCase(email_writer)
        return self._generate_email_use_case

    def generate_linkedin_use_case(self) -> GenerateLinkedInUseCase:
        """Get generate LinkedIn use case."""
        if self._generate_linkedin_use_case is None:
            linkedin_writer = self.content_writer_service().get_linkedin_writer()
            self._generate_linkedin_use_case = GenerateLinkedInUseCase(linkedin_writer)
        return self._generate_linkedin_use_case

    def generate_letter_use_case(self) -> GenerateCoverLetterUseCase:
        """Get generate cover letter use case."""
        if self._generate_letter_use_case is None:
            letter_writer = self.content_writer_service().get_letter_writer()
            self._generate_letter_use_case = GenerateCoverLetterUseCase(letter_writer)
        return self._generate_letter_use_case

    # === Orchestrators ===

    def generate_application_orchestrator(self) -> GenerateApplicationOrchestrator:
        """Get generate application orchestrator."""
        if self._generate_application_orchestrator is None:
            self._generate_application_orchestrator = GenerateApplicationOrchestrator(
                trace_use_case=self.trace_use_case(),
                analyze_use_case=self.analyze_use_case(),
                search_use_case=self.search_use_case(),
                rerank_use_case=self.rerank_use_case(),
                email_use_case=self.generate_email_use_case(),
                linkedin_use_case=self.generate_linkedin_use_case(),
                letter_use_case=self.generate_letter_use_case(),
            )
        return self._generate_application_orchestrator
```

---

### Phase 10: Créer API Mappers et refactorer endpoints

**Objectif**: Simplifier API - juste mapping HTTP ↔ DTOs

**Fichiers à créer**:

1. `app/api/mappers/generation_mapper.py`
```python
class GenerationMapper:
    """Mapper entre API models et Application DTOs."""

    @staticmethod
    def request_to_command(request: GenerateRequest) -> GenerateApplicationCommand:
        """Convert API request → Application command."""
        return GenerateApplicationCommand(
            job_offer=JobOfferDTO(text=request.job_offer),
            content_type=request.output_type.value,
        )

    @staticmethod
    def result_to_response(result: GenerationResultDTO) -> GenerateResponse:
        """Convert Application result → API response."""
        sources = [
            SourceDocument(
                id=doc.id,
                text=doc.text[:200] + "..." if len(doc.text) > 200 else doc.text,
                score=doc.rerank_score if doc.rerank_score else doc.score,
                source=doc.source,
            )
            for doc in result.sources
        ]

        return GenerateResponse(
            output=result.content,
            output_type=OutputType(result.content_type),
            sources=sources,
            trace_id=result.trace_id,
        )
```

2. **Modifier** `app/api/generation.py`

```python
"""Content generation endpoints - Clean Architecture."""

from fastapi import APIRouter, HTTPException, status

from app.core.logging import get_logger
from app.core.container import get_container
from app.models import GenerateRequest, GenerateResponse
from app.api.mappers.generation_mapper import GenerationMapper

logger = get_logger(__name__)
router = APIRouter(prefix="/generate", tags=["Generation"])


@router.post("", response_model=GenerateResponse, status_code=status.HTTP_200_OK)
async def generate_content(request: GenerateRequest) -> GenerateResponse:
    """
    Generate job application content.

    Clean Architecture: API = HTTP adapter only
    - Reçoit HTTP request
    - Convertit en Application command (mapper)
    - Exécute orchestrator
    - Convertit résultat en HTTP response (mapper)

    Pas de logique métier ici!
    """
    logger.info(
        "generate_request_received",
        output_type=request.output_type,
        offer_length=len(request.job_offer),
    )

    try:
        # 1. Get orchestrator from DI container
        container = get_container()
        orchestrator = container.generate_application_orchestrator()

        # 2. Map HTTP request → Application command
        command = GenerationMapper.request_to_command(request)

        # 3. Execute orchestrator (business logic)
        result = orchestrator.execute(command)

        # 4. Map Application result → HTTP response
        response = GenerationMapper.result_to_response(result)

        logger.info(
            "generation_completed",
            output_type=request.output_type,
            output_length=len(response.output),
            sources_count=len(response.sources),
        )

        return response

    except NoDatabaseDocumentsError as e:
        # Business exception → HTTP 404
        logger.warning("no_database_documents", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        # Unexpected error → HTTP 500
        logger.error("generation_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération: {str(e)}",
        )
```

---

### Phase 11: Créer exceptions métier (Domain)

**Objectif**: Exceptions spécifiques au domaine

**Fichier à créer**: `app/domain/exceptions.py`

```python
"""Domain exceptions - business errors."""


class DomainException(Exception):
    """Base exception pour domain errors."""
    pass


class NoDatabaseDocumentsError(DomainException):
    """Levée quand aucun document n'est trouvé dans la DB."""

    def __init__(self, message: str = "Aucune donnée utilisateur trouvée"):
        super().__init__(message)
        self.message = message


class InvalidJobOfferError(DomainException):
    """Levée quand job offer invalide."""
    pass


class AnalysisFailedError(DomainException):
    """Levée quand l'analyse échoue."""
    pass
```

---

## 📂 Détails des fichiers à créer/modifier/supprimer {#details-fichiers}

### ✅ Fichiers à CRÉER (nouveaux)

```
Domain Layer:
  app/domain/value_objects/
    trace_context.py
    search_query.py
    content_metadata.py

  app/domain/repositories/
    embedding_service.py

  app/domain/services/
    observability_service.py

  app/domain/exceptions.py

Application Layer:
  app/application/dtos/
    job_offer_dto.py
    job_analysis_dto.py
    document_dto.py
    generation_result_dto.py
    trace_context_dto.py

  app/application/commands/
    analyze_job_offer_command.py
    search_documents_command.py
    rerank_documents_command.py
    generate_content_command.py
    generate_application_command.py

  app/application/use_cases/
    analyze_job_offer.py
    search_documents.py
    rerank_documents.py
    generate_email.py
    generate_linkedin.py
    generate_cover_letter.py
    trace_generation.py

  app/application/orchestrators/
    generate_application_orchestrator.py

Infrastructure Layer:
  app/infrastructure/config/
    yaml_config_loader.py
    env_config_loader.py

  app/infrastructure/ai/crewai/
    agent_builder.py (déplacé)
    crew_builder.py (déplacé)
    email_writer_adapter.py
    linkedin_writer_adapter.py
    letter_writer_adapter.py
    content_writer_service.py

  app/infrastructure/vector_db/
    embedding_adapter.py

  app/infrastructure/observability/
    langfuse_adapter.py
    noop_adapter.py

API Layer:
  app/api/mappers/
    generation_mapper.py
```

### 🔄 Fichiers à MODIFIER

```
Domain Layer:
  app/domain/services/writer_service.py
    → Séparer en IEmailWriter, ILinkedInWriter, ILetterWriter

Application Layer:
  (Pas de modifications, juste ajouts)

Infrastructure Layer:
  app/infrastructure/ai/crewai_analyzer_adapter.py
    → Recevoir configs en injection (pas charger YAML)

  app/infrastructure/ai/crewai_writer_adapter.py
    → Supprimer (remplacé par 3 adapters spécialisés)

Core Layer:
  app/core/container.py
    → Ajouter tous les nouveaux services et use cases

  app/core/llm_factory.py
    → Supprimer _load_config(), recevoir config en injection

API Layer:
  app/api/generation.py
    → Simplifier: utiliser mapper + orchestrator
```

### ❌ Fichiers à SUPPRIMER

```
Application Layer:
  app/application/use_cases/generate_application_content.py
    → Remplacé par use cases atomiques + orchestrator

Infrastructure Layer:
  app/infrastructure/ai/crewai_writer_adapter.py
    → Remplacé par 3 adapters spécialisés (email, linkedin, letter)
```

---

## 🎯 Ordre d'exécution recommandé {#ordre-execution}

### Étape 1: Préparer les fondations (Domain + DTOs)
1. Créer `app/domain/exceptions.py`
2. Créer `app/domain/repositories/embedding_service.py`
3. Créer `app/domain/services/observability_service.py`
4. Modifier `app/domain/services/writer_service.py` (séparer interfaces)
5. Créer tous les DTOs dans `app/application/dtos/`
6. Créer tous les Commands dans `app/application/commands/`

**Pourquoi cet ordre**: Domain = fondation, pas de dépendances

---

### Étape 2: Créer les Use Cases atomiques
7. Créer `app/application/use_cases/analyze_job_offer.py`
8. Créer `app/application/use_cases/search_documents.py`
9. Créer `app/application/use_cases/rerank_documents.py`
10. Créer `app/application/use_cases/generate_email.py`
11. Créer `app/application/use_cases/generate_linkedin.py`
12. Créer `app/application/use_cases/generate_cover_letter.py`
13. Créer `app/application/use_cases/trace_generation.py`

**Pourquoi cet ordre**: Use cases dépendent du Domain (déjà créé)

---

### Étape 3: Créer l'Orchestrateur
14. Créer `app/application/orchestrators/generate_application_orchestrator.py`

**Pourquoi cet ordre**: Orchestrator dépend des use cases

---

### Étape 4: Créer Configuration Services (Infrastructure)
15. Créer `app/infrastructure/config/yaml_config_loader.py`
16. Modifier `app/core/llm_factory.py` (supprimer I/O)

**Pourquoi cet ordre**: Config loader doit exister avant adapters

---

### Étape 5: Migrer/Créer Infrastructure Adapters
17. Créer `app/infrastructure/vector_db/embedding_adapter.py`
18. Créer `app/infrastructure/observability/langfuse_adapter.py`
19. Créer `app/infrastructure/observability/noop_adapter.py`
20. Déplacer `app/application/builders/` → `app/infrastructure/ai/crewai/`
21. Modifier `app/infrastructure/ai/crewai_analyzer_adapter.py` (injection config)
22. Créer `app/infrastructure/ai/crewai/email_writer_adapter.py`
23. Créer `app/infrastructure/ai/crewai/linkedin_writer_adapter.py`
24. Créer `app/infrastructure/ai/crewai/letter_writer_adapter.py`
25. Créer `app/infrastructure/ai/crewai/content_writer_service.py`
26. Supprimer `app/infrastructure/ai/crewai_writer_adapter.py`

**Pourquoi cet ordre**: Adapters dépendent de config loader

---

### Étape 6: Refactorer Container
27. Modifier `app/core/container.py` (ajouter tous les nouveaux services)

**Pourquoi cet ordre**: Container doit wire tout ce qui existe

---

### Étape 7: Refactorer API
28. Créer `app/api/mappers/generation_mapper.py`
29. Modifier `app/api/generation.py` (simplifier)

**Pourquoi cet ordre**: API = dernière couche, dépend de tout

---

### Étape 8: Cleanup
30. Supprimer `app/application/use_cases/generate_application_content.py`
31. Vérifier tous les imports cassés
32. Lancer tests

---

## ✅ Checklist finale

Après refactoring, vérifier:

- [ ] **SRP**: Chaque classe a une seule responsabilité
- [ ] **OCP**: Peut étendre sans modifier (interfaces)
- [ ] **LSP**: Substitution Liskov respectée
- [ ] **ISP**: Interfaces granulaires (IEmailWriter, etc.)
- [ ] **DIP**: Dépendances vers abstractions, pas implémentations
- [ ] **Clean Archi**: Domain → Application → Infrastructure → API
- [ ] **DTOs**: Séparation couches avec DTOs
- [ ] **No I/O in Core**: Core layer ne fait pas d'I/O
- [ ] **Builders in Infra**: Builders dans infrastructure, pas application
- [ ] **Use Cases atomiques**: Chaque use case = 1 responsabilité
- [ ] **Orchestrator**: Compose use cases, pas logique métier
- [ ] **API simple**: API = juste HTTP adapter (mapper + orchestrator)
- [ ] **Exceptions métier**: Domain exceptions pour erreurs business
- [ ] **Tests**: Tous les use cases testables indépendamment

---

## 📚 Ressources pour approfondir

- **Clean Architecture** - Robert C. Martin
- **Domain-Driven Design** - Eric Evans
- **SOLID Principles** - Uncle Bob
- **Hexagonal Architecture** - Alistair Cockburn
- **CQRS Pattern** - Greg Young

---

**Fin du plan de refactoring** 🎉

Ce document contient tout ce qu'un développeur (même débutant) doit savoir pour refactorer JobBooster selon Clean Architecture et SOLID.
