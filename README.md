# JobBooster 🚀

> Générez des candidatures personnalisées et percutantes grâce à l'intelligence artificielle et au RAG (Retrieval-Augmented Generation).

## 📋 Table des matières

- [Vue d'ensemble](#-vue-densemble)
- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Technologies](#-technologies)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Structure du projet](#-structure-du-projet)

## 🎯 Vue d'ensemble

JobBooster est une application web intelligente qui génère automatiquement des contenus de candidature personnalisés (emails, messages LinkedIn, lettres de motivation) en s'appuyant sur votre profil professionnel et l'offre d'emploi visée.

### Comment ça marche ?

1. **Vous fournissez** : Une offre d'emploi (texte ou fichier .md)
2. **L'IA analyse** : Vos documents personnels (CV, profil LinkedIn, compétences)
3. **Vous obtenez** : Un contenu sur-mesure et professionnel

### Workflow technique

```
Offre d'emploi → Analyse → Recherche vectorielle (Qdrant)
              → Reranking → Génération LLM → Contenu personnalisé
```

**Exemple** : Vous collez une offre pour un poste de développeur Python. JobBooster récupère automatiquement vos expériences pertinentes, vos compétences Python, et génère un email de candidature qui met en avant ces éléments.

## ✨ Fonctionnalités

### Génération de contenu

- ✅ **Email de candidature** - Concis et percutant
- ✅ **Message LinkedIn** - Engageant pour les recruteurs
- ✅ **Lettre de motivation** - Structurée et complète

### Mode d'entrée flexible

- 📝 **Textarea** - Collez directement le texte de l'offre
- 📄 **Upload .md** - Importez un fichier markdown

### Intelligence artificielle

- 🔍 **RAG (Retrieval-Augmented Generation)** - Génération basée sur vos vraies données
- 🎯 **Recherche sémantique** - Trouve les informations les plus pertinentes
- 🏆 **Reranking** - Optimise la pertinence des sources
- 🤖 **Multi-LLM** - Support Anthropic, OpenAI, Google Gemini

### Suivi et traçabilité

- 📊 **Langfuse** - Observabilité complète des générations
- 📈 **Sources** - Affichage des documents utilisés avec scores
- 🆔 **Trace ID** - Suivi de chaque génération

## 🏗️ Architecture

### Clean Architecture (Hexagonal)

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│  (FastAPI Routes, Pydantic Models, Next.js Pages)       │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                   Application Layer                      │
│    (Orchestrators, Use Cases, Commands, DTOs)          │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                     Domain Layer                         │
│      (Business Logic, Interfaces, Exceptions)           │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                 Infrastructure Layer                     │
│   (Qdrant, LangChain, HuggingFace, API Clients)        │
└─────────────────────────────────────────────────────────┘
```

**Avantages** :
- ✅ **Testabilité** - Logique métier isolée
- ✅ **Maintenabilité** - Séparation des responsabilités
- ✅ **Évolutivité** - Ajout facile de nouvelles fonctionnalités
- ✅ **Indépendance** - Changement d'infra sans toucher au métier

## 🛠️ Technologies

### Backend

| Technologie | Usage | Version |
|------------|-------|---------|
| **Python** | Langage | 3.13+ |
| **FastAPI** | Framework web | Latest |
| **Pydantic** | Validation | 2.x |
| **LangChain** | Orchestration LLM | Latest |
| **Qdrant** | Vector database | Cloud |
| **HuggingFace** | Embeddings & Reranking | Inference API |
| **Langfuse** | Observabilité | Latest |
| **Loguru** | Logging structuré | Latest |

**Modèles IA** :
- Embeddings : sentence-transformers/multilingual-e5-base (768 dim)
- Reranker : BAAI/bge-reranker-base
- LLM : Claude 3.5 Sonnet / GPT-4 / Gemini

### Frontend

| Technologie | Usage | Version |
|------------|-------|---------|
| **Next.js** | Framework React | 15.x |
| **TypeScript** | Langage | 5.x |
| **Tailwind CSS** | Styling | 4.x |
| **shadcn/ui** | Composants UI | Latest |
| **React Query** | State management | Latest |
| **Lucide** | Icônes | Latest |

---

**Développé avec ❤️ par Raphael PICARD**
