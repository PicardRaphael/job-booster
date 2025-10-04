# 📚 Pipeline d'Ingestion de Documents

Ce dossier contient le pipeline complet pour ingérer vos documents personnels (CV, LinkedIn, compétences) dans la base vectorielle Qdrant.

## 🎯 Objectif

Transformer vos documents textuels en vecteurs numériques (embeddings) pour permettre une recherche sémantique rapide et pertinente lors de la génération d'emails de candidature.

## 📋 Flow Complet

```
Documents sources (PDF/Markdown)
        ↓
    Extraction du texte
        ↓
    Chunking (découpage intelligent)
        ↓
    Génération d'embeddings (vectorisation)
        ↓
    Stockage dans Qdrant
```

## 🔧 Composants

### 1. **pdf_processor.py** - Traitement des PDFs

**Rôle** : Extraire et chunker le contenu des fichiers PDF.

**Fonctionnement** :
- Utilise `pymupdf4llm` pour extraire le texte en format Markdown
- Préserve la structure (titres, paragraphes, listes)
- Délègue le chunking au `Chunker`

**Fichiers traités** :
- `data/cv.pdf` → CV du candidat
- `data/linkedin.pdf` → Profil LinkedIn exporté

### 2. **markdown_processor.py** - Traitement des Markdown

**Rôle** : Extraire et chunker le contenu des fichiers Markdown.

**Fonctionnement** :
- Lit directement le fichier `.md`
- Délègue le chunking au `Chunker`

**Fichiers traités** :
- `data/dossier_competence.md` → Compétences détaillées
- `data/informations.md` → Informations personnelles

### 3. **app/services/chunker.py** - Découpage Intelligent

**Rôle** : Découper les documents en morceaux (chunks) de taille optimale.

**Pourquoi chunker ?**
- Les LLMs ont une limite de tokens
- Les petits chunks améliorent la précision de la recherche
- Évite de perdre du contexte avec un découpage trop petit

**Stratégie** :
- **Chunk Size** : 400 caractères (configurable via `CHUNK_SIZE`)
- **Overlap** : 50 caractères (configurable via `CHUNK_OVERLAP`)
- **Séparateurs** : Markdown-aware (headers, paragraphes, listes)

**Exemple** :
```
Texte original (1000 chars)
    ↓
Chunk 1 (0-400)
Chunk 2 (350-750)  ← 50 chars de chevauchement
Chunk 3 (700-1000)
```

**Avantages de l'overlap** :
- Évite de couper les phrases importantes
- Maintient le contexte entre les chunks
- Améliore la qualité de la recherche

### 4. **app/services/embeddings.py** - Génération d'Embeddings

**Rôle** : Transformer le texte en vecteurs numériques.

**Modèle utilisé** : `intfloat/multilingual-e5-base`
- **Type** : Sentence Transformer
- **Dimension** : 768
- **Langues** : Français, Anglais, 100+ langues
- **Spécialité** : Recherche sémantique multilingue

**Fonctionnement** :
```python
texte = "Développeur Python avec 5 ans d'expérience"
    ↓
embedding = [0.123, -0.456, 0.789, ..., 0.321]  # 768 dimensions
```

**Pourquoi des embeddings ?**
- Capture le **sens** du texte, pas juste les mots
- Permet la recherche sémantique : "dev python" ≈ "développeur Python"
- Les vecteurs similaires sont proches dans l'espace vectoriel

### 5. **app/services/qdrant_service.py** - Stockage Vectoriel

**Rôle** : Gérer la base de données vectorielle Qdrant.

**Collection** : `user_info`
- **Dimension** : 768 (correspond au modèle d'embeddings)
- **Distance** : COSINE (mesure la similarité angulaire)
- **IDs** : Entiers auto-générés (0, 1, 2, ...)

**Structure d'un point** :
```json
{
  "id": 42,
  "vector": [0.123, -0.456, ..., 0.321],
  "payload": {
    "text": "Développeur Python avec 5 ans d'expérience",
    "source": "cv.pdf",
    "chunk_index": 5
  }
}
```

**Opérations** :
- `ensure_collection()` : Crée la collection si elle n'existe pas
- `upsert_documents()` : Insère/Met à jour les documents
- `search()` : Recherche par similarité vectorielle

### 6. **ingestion_pipeline.py** - Orchestrateur

**Rôle** : Coordonner tout le processus d'ingestion.

**Étapes** :
1. **Validation** : Vérifie que le dossier `data/` existe
2. **Traitement** :
   - PDF → chunks
   - Markdown → chunks
3. **Collection** : Rassemble tous les chunks
4. **Vectorisation** : Génère les embeddings
5. **Stockage** : Insère dans Qdrant

**Métadonnées ajoutées** :
- `source` : Nom du fichier source
- `chunk_index` : Position du chunk dans le document
- `text` : Contenu textuel du chunk

## 🚀 Utilisation

### Prérequis

1. **Préparer vos fichiers dans `data/`** :
```
backend/data/
├── cv.pdf
├── linkedin.pdf
├── dossier_competence.md
└── informations.md
```

2. **Configurer le `.env`** :
```env
# Qdrant (local ou cloud)
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your_api_key
QDRANT_COLLECTION=user_info

# Chunking
CHUNK_SIZE=400
CHUNK_OVERLAP=50

# Embeddings (sentence-transformers local)
EMBEDDING_MODEL=intfloat/multilingual-e5-base
```

### Lancer l'ingestion

```bash
cd backend
python scripts/ingest_data.py
```

### Résultat attendu

```
✅ Documents traités : 100 chunks
   - cv.pdf : 19 chunks
   - linkedin.pdf : 45 chunks
   - dossier_competence.md : 21 chunks
   - informations.md : 15 chunks

✅ Embeddings générés : 100 vecteurs (768 dimensions)
✅ Stockés dans Qdrant : collection 'user_info'
```

## 🔍 Recherche Sémantique (après ingestion)

Une fois les données ingérées, vous pouvez faire des recherches :

```python
from app.services.qdrant_service import get_qdrant_service

qdrant = get_qdrant_service()

# Recherche sémantique
results = qdrant.search(
    query="expérience en Python et FastAPI",
    limit=5,
    score_threshold=0.7
)

# Retourne les 5 chunks les plus pertinents
for result in results:
    print(f"Score: {result['score']}")
    print(f"Text: {result['text']}")
    print(f"Source: {result['source']}")
```

## 🛠️ Configuration Avancée

### Ajuster le chunking

**Chunks plus grands** (meilleur contexte, moins précis) :
```env
CHUNK_SIZE=800
CHUNK_OVERLAP=100
```

**Chunks plus petits** (plus précis, moins de contexte) :
```env
CHUNK_SIZE=200
CHUNK_OVERLAP=25
```

### Changer le modèle d'embeddings

**Modèle plus performant** (plus lourd) :
```env
EMBEDDING_MODEL=intfloat/multilingual-e5-large  # 1024 dimensions
```

⚠️ Si vous changez de modèle, **recréez la collection** :
```python
self.qdrant.ensure_collection(recreate=True)
```

### Recréer la collection

Si vous avez une erreur de dimension :
```
Vector dimension error: expected dim: X, got Y
```

Modifiez `ingestion_pipeline.py` :
```python
self.qdrant.ensure_collection(recreate=True)
```

## 📊 Monitoring

### Logs structurés

Le pipeline log chaque étape en JSON :
```json
{"event": "pdf_chunked", "file": "cv.pdf", "chunks": 19}
{"event": "embedding_texts", "count": 100}
{"event": "documents_upserted", "count": 100}
```

### Vérifier Qdrant

Via l'API REST :
```bash
curl $QDRANT_URL/collections/user_info
```

Via le Dashboard Qdrant (si cluster cloud) :
- https://cloud.qdrant.io

## 🐛 Troubleshooting

### Erreur "collection not found"

```bash
# Recréer la collection
python scripts/ingest_data.py
```

### Erreur "dimension mismatch"

Changé de modèle d'embeddings ? Recréez la collection :
```python
self.qdrant.ensure_collection(recreate=True)
```

### Erreur "file not found"

Vérifiez que vos fichiers sont dans `backend/data/` :
```bash
ls -la data/
```

### Performance lente

Le téléchargement du modèle sentence-transformers la première fois peut prendre du temps (~250MB).

Cache du modèle : `~/.cache/huggingface/`

## 📈 Prochaines Étapes

1. **RAG Pipeline** : Utiliser ces embeddings pour la génération d'emails
2. **Reranking** : Affiner les résultats de recherche
3. **Mise à jour** : Ajouter des documents sans tout ré-ingérer
4. **Versioning** : Gérer plusieurs versions de vos documents

## 🔗 Liens Utiles

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Sentence Transformers](https://www.sbert.net/)
- [LangChain Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
