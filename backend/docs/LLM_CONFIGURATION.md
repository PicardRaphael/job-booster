# 🎛️ Configuration LLM Avancée - Clean Architecture

## 📋 Vue d'ensemble

JobBooster utilise une architecture **Clean Architecture** avec multi-provider LLM.

La configuration LLM se fait via :
1. **Fichier YAML** : `app/agents/config/llm_config.yaml` (configuration de base)
2. **Variables d'environnement** : Surcharge dynamique via `AGENT_<NAME>_<PARAM>` (optionnel)

Chaque agent peut utiliser **n'importe quel provider** (OpenAI, Google, Anthropic) avec une configuration complètement personnalisée.

## 🏗️ Architecture

```
LLMFactory (Core)
    ↓
LLMProviderAdapter (Infrastructure)
    ↓
CrewAI Adapters (Infrastructure)
    ↓
Use Cases (Application)
```

La **LLMFactory** crée des LLMs configurés qui sont injectés dans les **adapters** via le **Container** (Dependency Injection).

## 📁 Fichier de Configuration

### Structure (Nouveau Format)

```yaml
# Configuration par agent (n'importe quel provider)
agents:
  analyzer:
    provider: openai
    model: gpt-4o-mini
    temperature: 0.3
    max_tokens: 1500
    top_p: 0.9
    frequency_penalty: 0.0
    presence_penalty: 0.0

  email_writer:
    provider: openai
    model: gpt-4o-mini
    temperature: 0.7
    max_tokens: 1000
    top_p: 0.95
    frequency_penalty: 0.3
    presence_penalty: 0.2

  linkedin_writer:
    provider: google
    model: gemini-1.5-pro
    temperature: 0.75
    max_output_tokens: 800
    top_p: 0.95
    top_k: 40

  letter_writer:
    provider: anthropic  # Anthropic Claude supporté !
    model: claude-3-5-sonnet-20241022
    temperature: 0.8
    max_tokens: 2500
    top_p: 0.95

# Configuration par défaut
default:
  provider: openai
  model: gpt-4o-mini
  temperature: 0.7
  max_tokens: 2000
  top_p: 1.0
```

## 🌍 Providers Supportés

### 1. OpenAI (GPT-4o-mini, GPT-4, etc.)

| Paramètre | Type | Plage | Description |
|-----------|------|-------|-------------|
| `provider` | string | `openai` | Provider OpenAI |
| `model` | string | - | `gpt-4o-mini`, `gpt-4o`, `gpt-4-turbo` |
| `temperature` | float | 0.0 - 2.0 | Contrôle la créativité |
| `max_tokens` | int | 1 - 4096+ | Nombre max de tokens générés |
| `top_p` | float | 0.0 - 1.0 | Nucleus sampling |
| `frequency_penalty` | float | -2.0 - 2.0 | Pénalise les répétitions |
| `presence_penalty` | float | -2.0 - 2.0 | Encourage nouveaux sujets |

### 2. Google Gemini

| Paramètre | Type | Plage | Description |
|-----------|------|-------|-------------|
| `provider` | string | `google` | Provider Google |
| `model` | string | - | `gemini-1.5-pro`, `gemini-1.5-flash` |
| `temperature` | float | 0.0 - 2.0 | Contrôle la créativité |
| `max_output_tokens` | int | 1 - 8192+ | Nombre max de tokens générés |
| `top_p` | float | 0.0 - 1.0 | Nucleus sampling |
| `top_k` | int | 1 - 100 | Nombre de tokens considérés |

### 3. Anthropic Claude

| Paramètre | Type | Plage | Description |
|-----------|------|-------|-------------|
| `provider` | string | `anthropic` | Provider Anthropic |
| `model` | string | - | `claude-3-5-sonnet-20241022`, `claude-3-opus` |
| `temperature` | float | 0.0 - 1.0 | Contrôle la créativité |
| `max_tokens` | int | 1 - 4096+ | Nombre max de tokens générés |
| `top_p` | float | 0.0 - 1.0 | Nucleus sampling |

## 🎯 Recommandations par Agent

### Analyzer (Extraction d'informations)

```yaml
analyzer:
  temperature: 0.3      # Déterministe
  max_tokens: 1500      # Suffisant pour analyse
  top_p: 0.9
  frequency_penalty: 0.0
  presence_penalty: 0.0
```

**Pourquoi ?**
- **Temperature basse (0.3)** : Extraction factuelle, pas de créativité nécessaire
- **top_p 0.9** : Résultats cohérents et prévisibles

### Email Writer (Contenu professionnel court)

```yaml
email_writer:
  temperature: 0.7      # Équilibré
  max_tokens: 1000      # Email concis
  top_p: 0.95
  frequency_penalty: 0.3  # Évite répétitions
  presence_penalty: 0.2
```

**Pourquoi ?**
- **Temperature moyenne (0.7)** : Balance entre créativité et cohérence
- **frequency_penalty 0.3** : Évite phrases répétitives
- **max_tokens 1000** : Limite pour email court

### LinkedIn Writer (Message engageant)

```yaml
linkedin_writer:
  temperature: 0.75     # Légèrement créatif
  max_output_tokens: 800
  top_p: 0.95
  top_k: 40
```

**Pourquoi ?**
- **Temperature 0.75** : Ton conversationnel mais pro
- **max_output_tokens 800** : Message LinkedIn court

### Letter Writer (Lettre longue et structurée)

```yaml
letter_writer:
  temperature: 0.8      # Plus créatif
  max_tokens: 2500      # Lettre complète
  top_p: 0.95
  frequency_penalty: 0.2
  presence_penalty: 0.3
```

**Pourquoi ?**
- **Temperature 0.8** : Créativité pour lettre engageante
- **max_tokens 2500** : Lettre de 300-400 mots
- **presence_penalty 0.3** : Diversité des sujets abordés

## 📊 Guide des Températures

```
0.0 ──────────────────────────────────── 2.0
│         │         │         │         │
Factuel  Équilibré Créatif  Très      Chaos
                            créatif

Cas d'usage :
├─ 0.0-0.3 : Extraction, analyse, JSON
├─ 0.4-0.7 : Contenu professionnel général
├─ 0.8-1.2 : Contenu créatif, storytelling
└─ 1.3-2.0 : Brainstorming, idées originales
```

## 🔧 Utilisation dans le Code (Clean Architecture)

### Via le Container (Dependency Injection)

```python
from app.core.container import get_container

# Le container gère toutes les dépendances
container = get_container()

# LLMFactory est injecté dans les adapters
llm_provider = container.llm_provider()  # LLMProviderAdapter

# Les adapters utilisent le LLMProvider
email_writer_adapter = container.content_writer_service().get_email_writer()
# → Créé avec LLM configuré automatiquement
```

### Dans les Adapters (Infrastructure)

```python
# app/infrastructure/ai/crewai/email_writer_adapter.py
class EmailWriterAdapter(IEmailWriter):
    def __init__(self, llm_provider: ILLMProvider, agent_config: Dict, task_config: Dict):
        self.llm_provider = llm_provider
        self.agent_config = agent_config
        self.task_config = task_config

    def write_email(self, job_offer, analysis, context):
        # Créer LLM via provider (détecte automatiquement le provider YAML)
        llm = self.llm_provider.create_llm("email_writer")

        # Créer agent avec LLM configuré
        agent = AgentBuilder().from_config(self.agent_config).with_llm(llm).build()

        # Créer task
        task = Task(description=self.task_config["description"], agent=agent)

        # Créer crew
        crew = CrewBuilder().add_agent(agent).add_task(task).build()

        # Exécuter
        result = crew.kickoff(inputs={...})
        return str(result)
```

### LLMFactory (Core Layer)

```python
# app/core/llm_factory.py
class LLMFactory:
    def __init__(self, llm_config: Dict[str, Any]):
        """Config injectée, pas chargée (Clean Architecture)."""
        self.config = llm_config

    def create_llm_for_agent(self, agent_name: str) -> BaseChatModel:
        """Crée LLM pour agent (détecte provider automatiquement)."""
        config = self._get_agent_config(agent_name)
        provider = config.get("provider", "openai")

        if provider == "openai":
            return self._create_openai_llm(config)
        elif provider == "google":
            return self._create_google_llm(config)
        elif provider == "anthropic":
            return self._create_anthropic_llm(config)
```

## 🔄 Surcharge via Variables d'Environnement

### Format

```bash
AGENT_<AGENT_NAME>_<PARAM>=value
```

### Exemples

```bash
# Changer le provider de l'analyzer vers Anthropic
AGENT_ANALYZER_PROVIDER=anthropic
AGENT_ANALYZER_MODEL=claude-3-5-sonnet-20241022
AGENT_ANALYZER_TEMPERATURE=0.2

# Augmenter max_tokens pour email_writer
AGENT_EMAIL_WRITER_MAX_TOKENS=1500

# Utiliser GPT-4 pour letter_writer
AGENT_LETTER_WRITER_MODEL=gpt-4o
AGENT_LETTER_WRITER_TEMPERATURE=0.9
```

### Hiérarchie de Configuration

```
default (YAML)
    ↓
agents.<agent_name> (YAML)
    ↓
AGENT_<NAME>_<PARAM> (ENV)  ← Priorité la plus haute
```

**Exemple :**
```yaml
# llm_config.yaml
agents:
  analyzer:
    provider: openai
    temperature: 0.3
```

```bash
# .env
AGENT_ANALYZER_PROVIDER=anthropic  # Override le provider
AGENT_ANALYZER_TEMPERATURE=0.2      # Override la température
```

**Résultat :** L'analyzer utilisera Claude avec température 0.2

## 🎨 Personnalisation

### Ajouter un nouvel agent

1. **Définir dans `llm_config.yaml` :**

```yaml
agents:
  resume_analyzer:
    provider: anthropic
    model: claude-3-5-sonnet-20241022
    temperature: 0.2    # Très factuel
    max_tokens: 2000
    top_p: 0.85
```

2. **Utiliser dans le code :**

```python
llm = self.llm_factory.create_llm_for_agent("resume_analyzer")
```

### Changer de provider facilement

**Via YAML :**
```yaml
agents:
  analyzer:
    provider: google  # Changé de openai à google
    model: gemini-1.5-pro
    temperature: 0.3
```

**Via ENV :**
```bash
AGENT_ANALYZER_PROVIDER=anthropic
AGENT_ANALYZER_MODEL=claude-3-5-sonnet-20241022
```

## 🧪 Tests de Configuration

### Vérifier le chargement via Container

```bash
# Lancer Python dans le container
docker exec -it jobbooster-backend python

>>> from app.core.container import get_container
>>> container = get_container()
>>> llm_provider = container.llm_provider()
>>> llm = llm_provider.create_llm("analyzer")
>>> print(llm.__class__.__name__)  # ChatOpenAI, ChatGoogleGenerativeAI ou ChatAnthropic
>>> print(llm.temperature)  # 0.3
```

### Tester un Use Case

```python
from app.core.container import get_container

# Obtenir orchestrator (contient tous les use cases)
container = get_container()
orchestrator = container.generate_application_orchestrator()

# Vérifier les LLMs utilisés
analyzer_service = container.analyzer_service()
# → CrewAIAnalyzerAdapter avec LLM configuré

email_writer = container.content_writer_service().get_email_writer()
# → EmailWriterAdapter avec LLM configuré
```

### Tester les ENV overrides

```bash
# Avec override
AGENT_ANALYZER_PROVIDER=anthropic \
AGENT_ANALYZER_TEMPERATURE=0.1 \
docker exec -it jobbooster-backend python -c "
from app.core.container import get_container
container = get_container()
llm_provider = container.llm_provider()
llm = llm_provider.create_llm('analyzer')
print(f'Provider: {llm.__class__.__name__}')
print(f'Temperature: {llm.temperature}')
"
```

## 🚨 Erreurs Communes

### 1. Configuration non trouvée

**Erreur :**
```
llm_config_not_found: Using defaults
```

**Solution :**
- Vérifier que `app/agents/config/llm_config.yaml` existe
- Vérifier les permissions du fichier

### 2. Agent non défini

Si agent non trouvé dans YAML → utilise config `default`

```python
# "unknown_agent" n'existe pas dans YAML
llm = factory.create_llm_for_agent("unknown_agent")
# → Utilise "default" automatiquement (provider: openai par défaut)
```

### 3. Provider non supporté

**Erreur :**
```
ValueError: Unsupported LLM provider: mistral
```

**Solution :**
- Vérifier que le provider est bien `openai`, `google` ou `anthropic`
- Ajouter le support du nouveau provider dans `LLMFactory`

### 4. Paramètre invalide

**Erreur :**
```
ValueError: temperature must be between 0 and 2
```

**Solution :**
- Vérifier les plages de valeurs dans ce document
- Corriger dans `llm_config.yaml` ou ENV

### 5. API Key manquante

**Erreur :**
```
ValidationError: ANTHROPIC_API_KEY field required
```

**Solution :**
```bash
# Ajouter la clé API dans .env
ANTHROPIC_API_KEY=sk-ant-api03-...
```

## 📈 Monitoring des Paramètres

### Logs structurés

```json
{
  "event": "creating_llm_for_agent",
  "agent_name": "analyzer",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "temperature": 0.3,
  "timestamp": "2025-10-03T..."
}
```

```json
{
  "event": "env_override_applied",
  "agent_name": "analyzer",
  "param": "temperature",
  "value": 0.2,
  "timestamp": "2025-10-03T..."
}
```

### Langfuse

Tous les appels LLM sont tracés avec leurs paramètres :
- Temperature utilisée
- Tokens générés
- Coût estimé
- Latence

## 💡 Best Practices

1. **Commencer avec les defaults** puis ajuster
2. **Temperature basse** pour tâches factuelles
3. **Temperature moyenne-haute** pour créativité
4. **max_tokens adapté** au type de contenu
5. **Choisir le bon provider** selon le cas d'usage :
   - OpenAI : Rapide, fiable, bon rapport qualité/prix
   - Google Gemini : Long contexte, multimodal
   - Anthropic Claude : Raisonnement complexe, sécurité
6. **ENV pour surcharge temporaire** (dev/test)
7. **YAML pour configuration stable** (production)
8. **Tester et itérer** selon les résultats
9. **Monitor via Langfuse** pour optimiser

## 🚀 Cas d'Usage Avancés

### Utiliser différents providers par agent

```yaml
agents:
  analyzer:
    provider: anthropic  # Claude pour analyse précise
    model: claude-3-5-sonnet-20241022
    temperature: 0.2

  email_writer:
    provider: openai  # GPT pour génération rapide
    model: gpt-4o-mini
    temperature: 0.7

  linkedin_writer:
    provider: google  # Gemini pour ton conversationnel
    model: gemini-1.5-pro
    temperature: 0.75
```

### A/B testing via ENV

```bash
# Test A : OpenAI
AGENT_EMAIL_WRITER_PROVIDER=openai
AGENT_EMAIL_WRITER_MODEL=gpt-4o-mini

# Test B : Claude
AGENT_EMAIL_WRITER_PROVIDER=anthropic
AGENT_EMAIL_WRITER_MODEL=claude-3-5-sonnet-20241022
```

## 🔗 Ressources

- [OpenAI API Parameters](https://platform.openai.com/docs/api-reference/chat/create)
- [Gemini API Parameters](https://ai.google.dev/docs/gemini_api_overview)
- [Anthropic API Parameters](https://docs.anthropic.com/claude/reference/messages_post)
- [Temperature Explained](https://platform.openai.com/docs/guides/text-generation/parameter-details)

## 📝 Résumé

**Configuration flexible des LLM par agent (Clean Architecture) :**
- ✅ Fichier YAML pour config de base
- ✅ Variables ENV pour surcharge dynamique
- ✅ Support multi-providers (OpenAI, Google, Anthropic)
- ✅ Hiérarchie claire : default < agent < ENV
- ✅ Dependency Injection via Container
- ✅ LLMFactory injecté dans adapters (pas chargement I/O)
- ✅ Logs structurés pour debugging
- ✅ Monitoring Langfuse intégré

**Architecture :**
```
YAMLConfigurationLoader (Infrastructure)
    ↓ Charge config
LLMFactory (Core)
    ↓ Crée LLMs
LLMProviderAdapter (Infrastructure)
    ↓ Injecté dans
CrewAI Adapters (Infrastructure)
    ↓ Utilisé par
Use Cases (Application)
```

**Format ENV :**
```bash
AGENT_<AGENT_NAME>_<PARAM>=value
```

**Exemple complet :**
```yaml
# llm_config.yaml
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

```bash
# .env (override)
AGENT_ANALYZER_PROVIDER=anthropic
AGENT_ANALYZER_MODEL=claude-3-5-sonnet-20241022
AGENT_ANALYZER_TEMPERATURE=0.2
```

**Utilisation dans le code :**
```python
# Via Container (Dependency Injection)
from app.core.container import get_container

container = get_container()
orchestrator = container.generate_application_orchestrator()
# Tous les LLMs sont automatiquement configurés et injectés !
```

---

**Documentation par** : Team JobBooster
**Dernière mise à jour** : 2025-10-04
**Architecture** : Clean Architecture + SOLID
