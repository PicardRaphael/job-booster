# AGENT-BACKEND.md — FastAPI + CrewAI + Qdrant + Langfuse (Version FR)

## 🎯 Objectif

- API backend pour assister la candidature.
- Orchestration via **CrewAI** (Agents + Tasks + Crew).
- Un seul output choisi côté front (checkbox) : email OU LinkedIn OU lettre.
- Tous les agents reçoivent le **contexte de l’offre analysée** (jamais stockée en BDD) + **RAG (Qdrant)** pour infos personnelles.
- Observabilité complète via Langfuse.

---

## 📂 Données ingérées

- `cv.pdf` → chunk + embeddings FR → Qdrant
- `linkedin.pdf` → idem
- `dossier_competence.md` → chunk Markdown → embeddings FR → Qdrant
- `informations.md` (style d’écriture, contraintes comme _pas d’emoji_) → chunk → embeddings FR → Qdrant

⚠️ Tous les embeddings et rerankings sont faits avec des modèles FR multilingues.

---

## 🔎 RAG (Qdrant + HuggingFace)

- **Stockage** : uniquement CV, LinkedIn, dossier de compétences, infos personnelles (jamais l’offre utilisateur).
- **Workflow RAG** :

  1. `AnalyzerAgent` extrait les mots-clés de l’offre (FR).
  2. `query_chunks()` → recherche dans Qdrant (multilingual embeddings).
  3. Résultats renvoyés par similarité.
  4. **Reranking** via `bclavie/bge-reranker-v2-m3` (FR-friendly).
  5. Contexte reranké injecté dans l’agent writer (email/LinkedIn/lettre).

---

## 🤖 Agents CrewAI

```python
analyzer = Agent(
    role="Analyzer",
    goal="Analyser l’offre et extraire les infos clés",
    backstory="Expert RH et tech",
    llm="openai:gpt-4.1-mini"
)

email_writer = Agent(
    role="Email Writer",
    goal="Rédiger un email de candidature FR",
    backstory="Consultant en communication",
    llm="openai:gpt-4.1-mini"
)

linkedin_writer = Agent(
    role="LinkedIn Writer",
    goal="Rédiger un message LinkedIn FR",
    backstory="Coach carrière",
    llm="gemini:pro"
)

letter_writer = Agent(
    role="Letter Writer",
    goal="Rédiger une lettre de motivation FR",
    backstory="RH expérimenté",
    llm="openai:gpt-4.1-mini"
)
```

---

## 🌐 Endpoints

```python
@router.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    crew = build_crew(req.output)

    rag_context = query_chunks(req.offer_analysis.keywords, lang="fr")
    reranked = rerank(req.offer_analysis.keywords, rag_context, lang="fr")

    result = crew.kickoff(inputs={
        "offer_analysis": req.offer_analysis.dict(),
        "rag_context": reranked
    })

    return GenerateResponse(result=result, sources=[s["id"] for s in reranked])
```

---

## 📊 Observabilité

- **Langfuse** : trace chaque agent.
- **Structlog** : logs JSON.
- **Spans** : Analyzer + Writer sélectionné.
- Suivi tokens/costs pour OpenAI et Gemini.
