# 🏗️ Refactoring Architecture - JobBooster

## 📋 Vue d'ensemble

Ce document décrit le refactoring majeur de l'architecture pour améliorer la maintenabilité et l'évolutivité du code.

## ✅ Modifications Principales

### 1. **Structure Modulaire des Modèles**

**Avant :**
```
app/models/
  └── schemas.py  (tout dans un fichier)
```

**Après :**
```
app/models/
  ├── requests/
  │   ├── __init__.py
  │   └── generation.py  (GenerateRequest, OutputType)
  └── responses/
      ├── __init__.py
      ├── generation.py  (GenerateResponse, SourceDocument)
      └── health.py      (HealthResponse)
```

**Avantages :**
- ✅ Séparation claire request/response
- ✅ Facile d'ajouter de nouveaux endpoints
- ✅ Imports explicites

### 2. **Agents Modulaires**

**Avant :**
```
app/agents/crews/
  └── job_application_crew.py  (tous les agents dans un fichier)
```

**Après :**
```
app/agents/agents/
  ├── __init__.py
  ├── analyzer.py
  ├── email_writer.py
  ├── linkedin_writer.py
  └── letter_writer.py
```

**Avantages :**
- ✅ Un fichier = un agent
- ✅ Configuration centralisée via YAML
- ✅ Facile de tester individuellement

### 3. **Tasks Modulaires**

**Avant :**
Tout dans `job_application_crew.py`

**Après :**
```
app/agents/tasks/
  ├── __init__.py
  ├── analyze_offer.py
  ├── write_email.py
  ├── write_linkedin.py
  └── write_letter.py
```

**Avantages :**
- ✅ Un fichier = une task
- ✅ Configuration centralisée via YAML
- ✅ Réutilisable

### 4. **Workflow Orchestrator**

**Nouveau système RAG intelligent :**

```
app/workflows/
  ├── __init__.py
  └── generation.py  (GenerationWorkflow)
```

**Flux amélioré :**
```
1. Analyzer Agent
   └─> Résumé structuré de l'offre d'emploi
       └─> 2. RAG Retrieval (avec résumé)
           └─> 3. Reranking
               └─> 4. Writer Agent (avec contexte enrichi)
```

**Avant :**
```
RAG → Rerank → Analyzer + Writer ensemble
```

**Maintenant :**
```
Analyzer résume → RAG avec résumé → Rerank → Writer avec contexte
```

**Avantages :**
- ✅ Meilleure qualité du RAG (résumé structuré vs texte brut)
- ✅ Context plus pertinent pour les writers
- ✅ Séparation claire des responsabilités
- ✅ Testable indépendamment

### 5. **API Simplifiée**

**Avant (generation.py) :**
- 130 lignes
- Logique RAG + CrewAI mélangée
- Difficile à tester

**Après (generation.py) :**
- 100 lignes
- Délègue au `GenerationWorkflow`
- Simple et lisible

```python
# Avant
qdrant = get_qdrant_service()
search_results = qdrant.search(...)
reranker = get_reranker_service()
reranked = reranker.rerank(...)
crew_manager = JobApplicationCrew()
crew = crew_manager.build_crew_for_output(...)
result = crew.kickoff(...)

# Après
workflow = GenerationWorkflow()
output, sources = workflow.generate(
    job_offer=request.job_offer,
    output_type=request.output_type.value,
)
```

## 📦 Structure Finale

```
backend/app/
├── agents/
│   ├── agents/          # Agents individuels
│   │   ├── analyzer.py
│   │   ├── email_writer.py
│   │   ├── linkedin_writer.py
│   │   └── letter_writer.py
│   ├── tasks/           # Tasks individuelles
│   │   ├── analyze_offer.py
│   │   ├── write_email.py
│   │   ├── write_linkedin.py
│   │   └── write_letter.py
│   ├── config/          # Configurations YAML
│   │   ├── agents.yaml
│   │   ├── tasks.yaml
│   │   └── llm_config.yaml
│   └── crews/           # Peut rester pour crews custom
│
├── models/
│   ├── requests/        # Modèles de requêtes
│   │   └── generation.py
│   └── responses/       # Modèles de réponses
│       ├── generation.py
│       └── health.py
│
├── workflows/           # Orchestration de haut niveau
│   └── generation.py    # Workflow RAG intelligent
│
├── api/                 # Endpoints API
│   ├── health.py
│   └── generation.py
│
├── services/            # Services techniques
│   ├── embeddings.py
│   ├── qdrant_service.py
│   ├── reranker.py
│   ├── chunker.py
│   └── langfuse_service.py
│
└── core/                # Configuration et utilitaires
    ├── config.py
    ├── logging.py
    └── llm_factory.py
```

## 🚀 Nouveau Flux de Génération

### Étape 1 : Analyzer Summarize
```python
analyzer_agent = create_analyzer_agent()
summary = analyzer.run(job_offer)
# Résultat: Structure JSON avec poste, compétences clés, etc.
```

### Étape 2 : RAG avec Résumé
```python
search_results = qdrant.search(query=summary, limit=10)
# Utilise le résumé structuré au lieu du texte brut
```

### Étape 3 : Reranking
```python
reranked = reranker.rerank(query=summary, documents=search_results, top_k=5)
# Garde les 5 documents les plus pertinents
```

### Étape 4 : Writer avec Contexte
```python
writer_agent = create_email_writer_agent()
output = writer.run(
    job_offer=job_offer,
    analysis=summary,
    rag_context=reranked_context
)
```

## 💡 Avantages du Refactoring

### Maintenabilité
- ✅ **Fichiers petits** : 40-60 lignes par fichier
- ✅ **Responsabilité unique** : Chaque fichier fait une chose
- ✅ **Facile à retrouver** : Structure logique claire

### Évolutivité
- ✅ **Ajouter un agent** : Créer un fichier dans `agents/`
- ✅ **Ajouter une task** : Créer un fichier dans `tasks/`
- ✅ **Nouveau workflow** : Créer un fichier dans `workflows/`

### Testabilité
- ✅ **Tests unitaires** : Un agent = un test
- ✅ **Mocking facile** : Interfaces claires
- ✅ **Tests d'intégration** : Workflow testable séparément

### Performance
- ✅ **RAG plus intelligent** : Résumé structuré → meilleurs résultats
- ✅ **Context optimisé** : Seulement le contenu pertinent
- ✅ **Réutilisable** : Pas de duplication

## 🔄 Migration

### Imports Mis à Jour

**Avant :**
```python
from app.models.schemas import GenerateRequest, GenerateResponse
from app.agents.crews import JobApplicationCrew
```

**Après :**
```python
from app.models import GenerateRequest, GenerateResponse
from app.workflows import GenerationWorkflow
```

### Utilisation API

**L'API reste identique pour le frontend :**
```bash
POST /api/v1/generate
{
  "job_offer": "...",
  "output_type": "email"
}
```

**Aucun changement côté frontend nécessaire !**

## 📝 Checklist pour Développeurs

Quand vous ajoutez une fonctionnalité :

- [ ] Créer un agent dans `app/agents/agents/`
- [ ] Ajouter sa config dans `app/agents/config/agents.yaml`
- [ ] Créer sa task dans `app/agents/tasks/`
- [ ] Ajouter config task dans `app/agents/config/tasks.yaml`
- [ ] Configurer LLM dans `app/agents/config/llm_config.yaml`
- [ ] Intégrer dans workflow si nécessaire

## 🎯 Prochaines Étapes

1. ✅ Tests unitaires pour chaque agent
2. ✅ Tests d'intégration pour workflows
3. ✅ Documentation API complète
4. ✅ Monitoring Langfuse

---

**Date de refactoring** : 2025-10-03
**Version** : 2.0.0
**Impact** : Architecture complète
