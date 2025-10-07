# 🚀 JobBooster Backend - Clean Architecture

API backend pour assister la génération de candidatures avec **FastAPI**, **CrewAI**, **Qdrant** et **Langfuse**.

## 📋 Vue d'Ensemble

JobBooster génère du contenu personnalisé (emails, messages privés LinkedIn, lettres de motivation) à partir d'offres d'emploi en utilisant :

- **RAG (Retrieval-Augmented Generation)** avec vos données personnelles
- **Agents AI** via CrewAI
- **Multi-provider LLM** (OpenAI, Google Gemini, Anthropic Claude)
- **Observabilité** complète via Langfuse

## 🏗️ Architecture

Cette application implémente **Clean Architecture** (Hexagonal Architecture) avec les principes **SOLID**.

```
┌─────────────────────────────────────────┐
│         API (FastAPI Endpoints)         │  ← Presentation Layer
├─────────────────────────────────────────┤
│    Application (Use Cases + DTOs)       │  ← Business Orchestration
├─────────────────────────────────────────┤
│  Domain (Entities + Interfaces)         │  ← Pure Business Logic
├─────────────────────────────────────────┤
│ Infrastructure (Adapters: CrewAI, etc.) │  ← Technology Implementations
└─────────────────────────────────────────┘
```

### Structure des Dossiers

```
app/
├── domain/              # ❤️ Logique métier pure
│   ├── entities/        # Objets métier (JobOffer, JobAnalysis)
│   ├── repositories/    # Interfaces (Ports)
│   └── services/        # Services métier (Interfaces)
│
├── application/         # 🎭 Cas d'usage
│   ├── use_cases/       # Use cases atomiques
│   ├── orchestrators/   # Orchestrateurs (composition de use cases)
│   ├── dtos/            # Data Transfer Objects
│   └── commands/        # Commands (CQRS pattern)
│
├── infrastructure/      # 🔌 Implémentations (Adapters)
│   ├── ai/              # Adapters IA (CrewAI, LLM)
│   ├── vector_db/       # Adapters BDD vectorielle (Qdrant)
│   ├── observability/   # Adapters observabilité (Langfuse)
│   └── config/          # Chargeurs de config (YAML)
│
├── api/                 # 🌐 Endpoints HTTP
│   ├── generation.py    # POST /generate
│   ├── health.py        # GET /health
│   └── mappers/         # Request/Response ↔ DTOs
│
├── core/                # ⚙️ Configuration
│   ├── container.py     # Dependency Injection Container
│   ├── config.py        # Variables d'environnement
│   └── llm_factory.py   # Factory LLM multi-provider
│
└── models/              # 📦 Modèles API (Pydantic)
    ├── requests/        # Request models
    └── responses/       # Response models
```

## 🎯 Principes SOLID Appliqués

- **S**ingle Responsibility : Chaque classe a une seule responsabilité
- **O**pen/Closed : Extension via interfaces, pas de modification
- **L**iskov Substitution : Tous les adapters sont interchangeables
- **I**nterface Segregation : Interfaces granulaires (IEmailWriter, ILinkedInWriter, etc.)
- **D**ependency Inversion : Dépendance sur abstractions, pas implémentations

## 📊 Flux de Génération

```
1. POST /api/v1/generate
   ↓
2. GenerationMapper.request_to_command()
   ↓
3. GenerateApplicationOrchestrator.execute()
   ├─→ AnalyzeJobOfferUseCase (Résumé offre)
   ├─→ SearchDocumentsUseCase (RAG Qdrant)
   ├─→ RerankDocumentsUseCase (Reranking)
   └─→ Generate{Email|LinkedIn|Letter}UseCase
   ↓
4. GenerationMapper.result_to_response()
   ↓
5. Response JSON
```

## 🚀 Démarrage Rapide

### 1. Prérequis

```bash
# Variables d'environnement (.env)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...           # Optionnel (si Gemini)
ANTHROPIC_API_KEY=sk-ant-... # Optionnel (si Claude)

QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION=jobbooster

LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

### 2. Installation

```bash
# Avec Docker
docker-compose up -d

# Ou localement
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. Ingestion de Données

```bash
# Ingérer CV, LinkedIn, dossier de compétences
python scripts/ingest_data.py
```

### 4. Tester l'API

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "job_offer": "Nous recherchons un développeur Python...",
    "output_type": "email"
  }'
```

## 🎛️ Configuration LLM

Chaque agent peut utiliser un provider différent (OpenAI, Google, Anthropic).

### Fichier `app/agents/config/llm_config.yaml`

```yaml
agents:
  analyzer:
    provider: openai
    model: gpt-4o-mini
    temperature: 0.3

  email_writer:
    provider: openai
    model: gpt-4o-mini
    temperature: 0.7

  linkedin_writer:
    provider: google
    model: gemini-1.5-pro
    temperature: 0.75

  letter_writer:
    provider: anthropic
    model: claude-3-5-sonnet-20241022
    temperature: 0.8
```

### Surcharge via Variables d'Environnement

```bash
# Changer analyzer vers Claude
AGENT_ANALYZER_PROVIDER=anthropic
AGENT_ANALYZER_MODEL=claude-3-5-sonnet-20241022
AGENT_ANALYZER_TEMPERATURE=0.2
```

📖 **Documentation complète** : [docs/LLM_CONFIGURATION.md](docs/LLM_CONFIGURATION.md)

## 📡 Endpoints API

### `POST /api/v1/generate`

Génère du contenu (email, LinkedIn, lettre).

**Request :**

```json
{
  "job_offer": "Nous recherchons un développeur Python...",
  "output_type": "email"
}
```

**Response :**

```json
{
  "output": "Bonjour,\n\nJe candidate pour...",
  "output_type": "email",
  "sources": [
    {
      "id": "cv_chunk_1",
      "text": "Développeur Python avec 5 ans...",
      "score": 0.92,
      "source": "cv.pdf"
    }
  ],
  "trace_id": "langfuse_trace_123"
}
```

### `GET /health`

Vérifie le statut de l'application.

**Response :**

```json
{
  "status": "healthy",
  "qdrant_status": "connected",
  "langfuse_status": "connected"
}
```

## 🧪 Tests

```bash
# Tests unitaires
pytest tests/unit/

# Tests d'intégration
pytest tests/integration/

# Avec coverage
pytest --cov=app tests/
```

## 📚 Documentation

- **[REFACTORING_SUMMARY.md](docs/REFACTORING_SUMMARY.md)** - Résumé complet du refactoring Clean Architecture
- **[LLM_CONFIGURATION.md](docs/LLM_CONFIGURATION.md)** - Configuration avancée des LLMs

## 🎨 Design Patterns Utilisés

| Pattern                          | Localisation            | Pourquoi                    |
| -------------------------------- | ----------------------- | --------------------------- |
| **Clean Architecture**           | Global                  | Séparation des couches      |
| **Hexagonal (Ports & Adapters)** | Domain ↔ Infrastructure | Découplage                  |
| **CQRS**                         | Application             | Commands pour intentions    |
| **Builder**                      | Infrastructure          | AgentBuilder, CrewBuilder   |
| **Factory**                      | Core                    | LLMFactory (multi-provider) |
| **Adapter**                      | Infrastructure          | Wrapper services externes   |
| **Composite**                    | Infrastructure          | ContentWriterService        |
| **Singleton**                    | Core                    | Container (DI)              |
| **Orchestrator**                 | Application             | Composition de use cases    |
| **Mapper**                       | API                     | Request/Response ↔ DTOs     |

## 🔑 Concepts Clés

### Use Cases Atomiques

Chaque use case a une **responsabilité unique** :

- `AnalyzeJobOfferUseCase` - Analyse l'offre d'emploi
- `SearchDocumentsUseCase` - Recherche dans Qdrant
- `RerankDocumentsUseCase` - Rerank les résultats
- `GenerateEmailUseCase` - Génère un email
- `GenerateLinkedInUseCase` - Génère un message privé LinkedIn
- `GenerateCoverLetterUseCase` - Génère une lettre

### Orchestrator

`GenerateApplicationOrchestrator` **compose** les use cases atomiques pour exécuter le workflow complet.

### Dependency Injection

Le `Container` gère toutes les dépendances :

```python
container = get_container()
orchestrator = container.generate_application_orchestrator()
result = orchestrator.execute(command)
```

### DTOs (Data Transfer Objects)

Découplent les couches :

- API Request → DTO → Command
- Use Case Result → DTO → API Response

## 🛠️ Ajouter une Fonctionnalité

### Exemple : Ajouter génération de tweet

#### 1. Domain : Créer interface

```python
# app/domain/services/writer_service.py
class ITweetWriter(ABC):
    @abstractmethod
    def write_tweet(self, offer: JobOffer, analysis: JobAnalysis, context: str) -> str:
        pass
```

#### 2. Application : Créer use case

```python
# app/application/use_cases/generate_tweet.py
class GenerateTweetUseCase:
    def __init__(self, writer: ITweetWriter):
        self.writer = writer

    def execute(self, command: GenerateContentCommand) -> str:
        return self.writer.write_tweet(...)
```

#### 3. Infrastructure : Créer adapter

```python
# app/infrastructure/ai/crewai/tweet_writer_adapter.py
class TweetWriterAdapter(ITweetWriter):
    def write_tweet(self, offer, analysis, context):
        # Implémentation CrewAI
        pass
```

#### 4. Container : Wire le use case

```python
# app/core/container.py
def tweet_use_case(self) -> GenerateTweetUseCase:
    writer = self.content_writer_service().get_tweet_writer()
    return GenerateTweetUseCase(writer)
```

#### 5. API : Ajouter endpoint

```python
# app/api/generation.py
# Ajouter "tweet" dans OutputType enum
# Le mapper et orchestrator gèrent automatiquement
```

## 🧑‍💻 Pour Développeurs Débutants

Le code est conçu pour être **ultra-lisible** :

### Ordre de Lecture

1. **Domain** (`domain/`) - Comprendre les concepts métier
2. **Application** (`application/`) - Comprendre les use cases
3. **Infrastructure** (`infrastructure/`) - Voir les implémentations
4. **API** (`api/`) - Voir les endpoints

### Nommage

- **Noms explicites** : `analyze_job_offer_use_case` (verbe + objet + use case)
- **Interfaces** : Préfixe `I` (ex: `IAnalyzerService`)
- **Adapters** : Suffixe `Adapter` (ex: `QdrantAdapter`)
- **DTOs** : Suffixe `DTO` (ex: `JobOfferDTO`)
- **Commands** : Suffixe `Command` (ex: `AnalyzeJobOfferCommand`)

### Documentation

Chaque fichier contient :

- **Module docstring** : Couche + responsabilité + pourquoi
- **Class docstring** : Rôle + pattern + exemple
- **Method docstrings** : Args, Returns, Raises, Examples
- **Inline comments** : Expliquent le "pourquoi"

## 🔐 Sécurité

- ✅ Secrets dans `.env` (jamais committé)
- ✅ Validation Pydantic des inputs
- ✅ Pas de stockage des offres d'emploi
- ✅ Observabilité pour audit (Langfuse)

## 📈 Performance

- ✅ **Lazy initialization** : Services créés à la demande
- ✅ **Singleton container** : Une seule instance
- ✅ **Reranking** : Top 5 documents les plus pertinents
- ✅ **Embeddings FR** : Optimisés pour français

## 🌍 Observabilité

Toutes les générations sont tracées dans **Langfuse** :

- Trace ID retourné dans response
- Metadata : job offer résumé, content type
- Tokens et coûts trackés
- Erreurs capturées

## 🐛 Troubleshooting

### Erreur "No database documents"

```bash
# Réingérer les données
python scripts/ingest_data.py
```

### Erreur LLM provider

```bash
# Vérifier les API keys
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Vérifier la config
cat app/agents/config/llm_config.yaml
```

### Erreur Qdrant

```bash
# Vérifier Qdrant running
docker ps | grep qdrant

# Vérifier collection
curl http://localhost:6333/collections/jobbooster
```

## 📝 License

MIT

## 👥 Contributeurs

Team JobBooster

---

**Version** : 3.0.0 (Clean Architecture + SOLID)
**Dernière mise à jour** : 2025-10-04
