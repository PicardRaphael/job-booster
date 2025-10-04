# 🚀 JobBooster - AI Job Application Assistant

**JobBooster** est un assistant IA pour booster vos candidatures. Il utilise un système RAG (Retrieval-Augmented Generation) basé sur votre CV, profil LinkedIn et compétences pour générer des contenus de candidature personnalisés et professionnels.

## 🎯 Fonctionnalités

- **Génération de contenus de candidature** :

  - Email de candidature (concis, 150-200 mots)
  - Message LinkedIn (engageant, 100-150 mots)
  - Lettre de motivation (structurée, 300-400 mots)

- **RAG intelligent** :

  - Embeddings multilingues (`intfloat/multilingual-e5-base`)
  - Reranking avec `bclavie/bge-reranker-v2-m3`
  - Stockage vectoriel dans Qdrant

- **Multi-LLM** :

  - OpenAI GPT-4o-mini
  - Google Gemini 1.5 Pro

- **Observabilité complète** :
  - Tracing Langfuse
  - Logs structurés (structlog)
  - Métriques de performance

## 🛠️ Stack Technique

### Backend

- **FastAPI** : API REST haute performance
- **CrewAI** : Orchestration d'agents IA
- **Qdrant** : Base de données vectorielle
- **Langfuse** : Observabilité LLM
- **HuggingFace** : Embeddings et reranking

### Frontend

- **Next.js 15** : App Router + Server Components
- **TypeScript** : Typage strict
- **TailwindCSS** + **shadcn/ui** : UI moderne et accessible
- **TanStack Query** : Gestion d'état et cache

## 📋 Prérequis

- **Docker** et **Docker Compose**
- **Node.js** 18+ (pour le frontend local)
- **Python** 3.11+ (pour le backend local)
- **Clés API** :
  - OpenAI API Key
  - Google API Key (Gemini)
  - Langfuse API Keys

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/votre-username/jobbooster.git
cd jobbooster
```

### 2. Configuration des variables d'environnement

```bash
# Copier les fichiers .env.example
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Éditer .env avec vos clés API
nano .env
```

### 3. Démarrer les services avec Docker Compose

```bash
# Lancer tous les services (Qdrant, Langfuse, Backend)
docker-compose up -d

# Vérifier les logs
docker-compose logs -f backend
```

### 4. Ingérer les données

```bash
# Entrer dans le container backend
docker exec -it jobbooster-backend bash

# Lancer l'ingestion (CV, LinkedIn, compétences)
python scripts/ingest_data.py
```

### 5. Démarrer le frontend

```bash
cd frontend

# Installer les dépendances
npm install

# Démarrer en mode dev
npm run dev
```

L'application est accessible sur [http://localhost:3000](http://localhost:3000)

## 📂 Structure du Projet

```
jobbooster/
├── backend/
│   ├── app/
│   │   ├── core/           # Configuration, logging
│   │   ├── services/       # RAG, embeddings, Qdrant
│   │   ├── agents/         # Agents CrewAI
│   │   ├── models/         # Schémas Pydantic
│   │   ├── api/            # Routes FastAPI
│   │   └── main.py         # Point d'entrée
│   ├── data/               # Fichiers utilisateur (CV, LinkedIn...)
│   ├── scripts/            # Script d'ingestion
│   ├── pyproject.toml      # Dépendances Python
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/            # Next.js App Router
│   │   ├── components/     # Composants React
│   │   ├── hooks/          # Custom hooks
│   │   ├── lib/            # Utilitaires
│   │   └── types/          # Types TypeScript
│   ├── package.json
│   └── next.config.ts
├── docker-compose.yml      # Orchestration services
└── README.md
```

## 🔧 Utilisation

### 1. Préparer vos fichiers

Placez vos fichiers dans `backend/data/` :

- `cv.pdf` : Votre CV (PDF)
- `linkedin.pdf` : Export de votre profil LinkedIn (PDF)
- `dossier_competence.md` : Vos compétences détaillées (Markdown)
- `informations.md` : Informations personnelles et style de communication (Markdown)

### 2. Lancer l'ingestion

```bash
docker exec -it jobbooster-backend python scripts/ingest_data.py
```

### 3. Utiliser l'interface

1. Accédez à [http://localhost:3000](http://localhost:3000)
2. Collez une offre d'emploi dans le textarea
3. Choisissez le type de contenu (Email, LinkedIn ou Lettre)
4. Cliquez sur **Générer**
5. Copiez le résultat généré

## 📊 Observabilité

### Langfuse

Accédez à l'interface Langfuse sur [http://localhost:3001](http://localhost:3001)

- **Traces** : Visualisez le flux complet de génération
- **Prompts** : Analysez les prompts utilisés
- **Coûts** : Suivez les coûts LLM
- **Performance** : Mesurez la latence

### Qdrant

Interface Qdrant sur [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

- Explorez la collection `user_info`
- Testez les recherches vectorielles
- Visualisez les embeddings

## 🧪 Tests

### Backend

```bash
cd backend
poetry install
poetry run pytest
```

### Frontend

```bash
cd frontend
npm test
```

## 🚀 Déploiement

### Backend (Railway/Render)

1. Configurez les variables d'environnement
2. Déployez le Dockerfile backend
3. Connectez à un Qdrant Cloud
4. Exécutez le script d'ingestion

### Frontend (Vercel)

```bash
cd frontend
vercel deploy --prod
```

## 🤝 Contribution

Les contributions sont les bienvenues !

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- [CrewAI](https://www.crewai.com/) pour l'orchestration d'agents
- [Qdrant](https://qdrant.tech/) pour la base vectorielle
- [Langfuse](https://langfuse.com/) pour l'observabilité
- [shadcn/ui](https://ui.shadcn.com/) pour les composants UI

## 📧 Contact

Pour toute question, ouvrez une issue sur GitHub.

---

Fait avec ❤️ par Raphaël PICARD
