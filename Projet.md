# AGENT-GLOBAL.md — Job Booster Agent IA (Mise à jour)

## 🎯 But

Outil d’aide à la candidature **flexible**.

- **Input** : offre d’emploi (collée dans un **textarea**) ou document **Markdown (.md)** uploadé.
  _(Pas de PDF en entrée pour l’offre, uniquement .md ou texte brut)_.
- **Output** : génération sélective (checkbox utilisateur) :

  - Email de candidature
  - Message LinkedIn
  - Lettre de motivation

- **Contexte** : RAG sur CV (PDF fourni côté backend), profil LinkedIn (PDF), infos personnelles clés.
- **Observabilité complète** via Langfuse.
- **Multi-LLM** : chaque agent peut utiliser un LLM différent (OpenAI ou Gemini).

---

## ⚙️ Stack

- **Backend** : FastAPI (Python 3.11), CrewAI (orchestration agents), Qdrant, Langfuse, Pydantic.
- **NLP** : HuggingFace (PyTorch).

  - **Embeddings** : `intfloat/multilingual-e5-base`.
  - **Reranker** : `bclavie/bge-reranker-v2-m3`.
  - **Chunking** : dépend du format :

    - **Markdown (.md)** : découpage par sections/titres (`#`, `##`) avec `RecursiveCharacterTextSplitter`.
    - **PDF (CV, LinkedIn)** : découpage en blocs de 300–500 tokens avec overlap 50–80, en respectant paragraphes et sections.

- **LLM providers** :

  - **OpenAI** (`gpt-4.1-mini`, `o4-mini` en fallback raisonnement).
  - **Google Gemini** (palier gratuit, API Gemini Pro).

- **Frontend** : Next.js 15 (TypeScript, TailwindCSS, shadcn/ui, React Query).
- **Déploiement** : Docker Compose (FastAPI + Qdrant + Langfuse), Vercel (frontend), Railway/Render (backend).

---

## 📐 Principes

- SOLID strict partout.
- Clean Architecture backend (fichiers courts, découplés).
- Feature-based architecture frontend (composants réutilisables).
- Observabilité Langfuse (prompts, tokens, coûts, erreurs).
- Multi-LLM support (routing agents → OpenAI ou Gemini).
- Sécurité stricte (.env, clés séparées par provider).

---

## 🔄 Flux

1. **Ingestion statique** : CV + LinkedIn (PDFs côté backend) + infos → chunk → embeddings → Qdrant.
2. **Appel utilisateur** : offre d’emploi via textarea ou upload `.md` + sélection outputs (checkbox : email / LinkedIn / lettre).
3. **Parsing & Chunking** :

   - Si `.md` → découpage par titres/sections.
   - Si texte brut (textarea) → découpage 400–600 tokens avec overlap 50.
   - Si PDF (CV/LinkedIn, backend only) → découpage 300–500 tokens, overlap 50–80.

4. **RAG Pipeline** : embeddings (`e5-base`) → Qdrant → reranking (`bge-reranker-v2-m3`).
5. **CrewAI orchestration** :

   - `AnalyzerAgent` (OpenAI recommandé).
   - `EmailAgent` (OpenAI par défaut, peut basculer Gemini).
   - `LinkedInAgent` (Gemini possible).
   - `LetterAgent` (OpenAI conseillé).
   - Les agents ne sont invoqués que si l’utilisateur a coché leur output.

6. **Résultats** : retour uniquement des générations demandées.
7. **Logs Langfuse** : trace complète (prompts, modèles utilisés, coûts, latence, erreurs).
