#!/usr/bin/env python3
"""
Script de test pour vérifier la récupération RAG depuis Qdrant.

Usage:
    python test_rag_retrieval.py
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire backend au path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.container import get_container
from app.application.commands import SearchDocumentsCommand, RerankDocumentsCommand


async def test_rag_retrieval():
    """Test complet du workflow RAG."""
    print("=" * 80)
    print("🔍 TEST DE RÉCUPÉRATION RAG DEPUIS QDRANT")
    print("=" * 80)
    print()

    # === Configuration du test ===
    test_queries = [
        "lettre motivation RULESET LETTER React Next.js développeur fullstack",
        "email RULESET EMAIL candidature",
        "RULESET GLOBAL signature Raphaël Picard",
        "React TypeScript IA LangChain expérience",
    ]

    container = get_container()
    search_use_case = container.search_documents_use_case()
    rerank_use_case = container.rerank_documents_use_case()

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"📝 TEST {i}/{len(test_queries)}: {query}")
        print(f"{'='*80}\n")

        # === ÉTAPE 1: Recherche Qdrant ===
        print("🔎 ÉTAPE 1: Recherche dans Qdrant (top 10)")
        print("-" * 80)

        search_command = SearchDocumentsCommand(
            query=query,
            limit=10,
            score_threshold=0.3,
        )

        try:
            documents = await search_use_case.execute(search_command)
            print(f"✅ Documents trouvés: {len(documents)}")
            print()

            if not documents:
                print("⚠️  AUCUN DOCUMENT TROUVÉ!")
                print("   Vérifiez que les documents sont bien indexés dans Qdrant.")
                continue

            # Afficher les résultats de recherche
            for j, doc in enumerate(documents, 1):
                print(f"📄 Document {j}/10:")
                print(f"   ID: {doc.id}")
                print(f"   Score: {doc.score:.4f}")
                print(f"   Source: {doc.source}")
                print(f"   Texte (premiers 200 chars):")
                print(f"   {doc.text[:200]}...")
                print()

        except Exception as e:
            print(f"❌ Erreur lors de la recherche: {e}")
            import traceback
            traceback.print_exc()
            continue

        # === ÉTAPE 2: Reranking ===
        print("🎯 ÉTAPE 2: Reranking (top 5)")
        print("-" * 80)

        rerank_command = RerankDocumentsCommand(
            query=query,
            documents=documents,
            top_k=10,
        )

        try:
            reranked_docs = await rerank_use_case.execute(rerank_command)
            print(f"✅ Documents après reranking: {len(reranked_docs)}")
            print()

            # Afficher les résultats reranked
            for j, doc in enumerate(reranked_docs, 1):
                print(f"🏆 Document {j}/5 (après reranking):")
                print(f"   ID: {doc.id}")
                print(f"   Score Qdrant: {doc.score:.4f}")
                print(f"   Rerank Score: {doc.rerank_score:.4f if doc.rerank_score else 'N/A'}")
                print(f"   Source: {doc.source}")
                print(f"   Texte complet:")
                print(f"   {'-'*76}")
                print(f"   {doc.text}")
                print(f"   {'-'*76}")
                print()

            # === ANALYSE DES RÉSULTATS ===
            print("📊 ANALYSE DES RÉSULTATS")
            print("-" * 80)

            # Vérifier présence des RULESETS
            rulesets_found = {
                "RULESET: LETTER": False,
                "RULESET: EMAIL": False,
                "RULESET: LINKEDIN": False,
                "RULESET: GLOBAL": False,
            }

            for doc in reranked_docs:
                for ruleset in rulesets_found.keys():
                    if ruleset in doc.text or f"[{ruleset}]" in doc.text:
                        rulesets_found[ruleset] = True

            print("RULESETS trouvés:")
            for ruleset, found in rulesets_found.items():
                status = "✅" if found else "❌"
                print(f"   {status} {ruleset}")

            print()

            # Vérifier présence d'expériences
            experience_keywords = ["Royal Canin", "Freelance", "SchoolMouv", "React", "TypeScript", "Python"]
            experiences_found = []
            for keyword in experience_keywords:
                if any(keyword in doc.text for doc in reranked_docs):
                    experiences_found.append(keyword)

            if experiences_found:
                print(f"Expériences/Compétences trouvées: {', '.join(experiences_found)}")
            else:
                print("⚠️  Aucune expérience/compétence trouvée")

            print()

        except Exception as e:
            print(f"❌ Erreur lors du reranking: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print("✅ FIN DES TESTS")
    print("=" * 80)


async def test_specific_query():
    """Test avec une query spécifique pour une lettre de motivation."""
    print("=" * 80)
    print("🎯 TEST SPÉCIFIQUE: Query pour Lettre de Motivation")
    print("=" * 80)
    print()

    # Query similaire à celle générée par l'orchestrator
    query = (
        "Développeur Fullstack React TypeScript Python FastAPI IA LangChain "
        "RAG agents automatisation innovation autonomie lettre motivation "
        "RULESET LETTER Structure signature React Next.js TypeScript IA Python"
    )

    print(f"Query: {query}")
    print()

    container = get_container()
    search_use_case = container.search_documents_use_case()
    rerank_use_case = container.rerank_documents_use_case()

    # Recherche
    search_command = SearchDocumentsCommand(
        query=query,
        limit=10,
        score_threshold=0.5,
    )

    documents = await search_use_case.execute(search_command)
    print(f"📊 Documents trouvés (Qdrant): {len(documents)}")

    if not documents:
        print("❌ PROBLÈME: Aucun document trouvé!")
        print("   Solutions possibles:")
        print("   1. Vérifiez que les documents sont ingérés: python -m app.scripts.ingest_documents")
        print("   2. Vérifiez Qdrant: http://localhost:6333/dashboard")
        print("   3. Baissez le score_threshold (actuellement 0.5)")
        return

    # Reranking
    rerank_command = RerankDocumentsCommand(
        query=query,
        documents=documents,
        top_k=10,
    )

    reranked_docs = await rerank_use_case.execute(rerank_command)
    print(f"🎯 Documents après reranking: {len(reranked_docs)}")
    print()

    # Vérifier RULESET LETTER
    ruleset_letter = next(
        (doc for doc in reranked_docs if "RULESET: LETTER" in doc.text or "[RULESET: LETTER]" in doc.text),
        None
    )

    if ruleset_letter:
        print("✅ RULESET: LETTER trouvé!")
        print(f"   Score: {ruleset_letter.rerank_score or ruleset_letter.score:.4f}")
        print(f"   Longueur: {len(ruleset_letter.text)} caractères")
        print()
    else:
        print("❌ RULESET: LETTER NON TROUVÉ!")
        print("   Le LLM n'aura pas accès aux règles de rédaction!")
        print()

    # Afficher le contexte complet qui serait passé au LLM
    print("=" * 80)
    print("�� CONTEXTE COMPLET QUI SERAIT PASSÉ AU LLM")
    print("=" * 80)

    context_parts = []
    for doc in reranked_docs:
        context_parts.append(doc.text)

    full_context = "\n\n---\n\n".join(context_parts)
    print(full_context)
    print()
    print(f"Longueur totale du contexte: {len(full_context)} caractères")


async def check_qdrant_health():
    """Vérifier que Qdrant est accessible et contient des documents."""
    print("=" * 80)
    print("🏥 VÉRIFICATION SANTÉ QDRANT")
    print("=" * 80)
    print()

    try:
        from app.services.qdrant_service import get_qdrant_service

        qdrant = get_qdrant_service()

        # Vérifier la collection
        print("📦 Collection: user_info")

        # Compter les documents
        try:
            from qdrant_client.models import Filter

            result = qdrant.client.count(
                collection_name=qdrant.collection_name
            )

            print(f"✅ Documents dans la collection: {result.count}")
            print()

            if result.count == 0:
                print("⚠️  COLLECTION VIDE!")
                print("   Lancez: python -m app.scripts.ingest_documents")
                print()
                return False

        except Exception as e:
            print(f"❌ Erreur lors du comptage: {e}")
            return False

        # Tester une recherche simple
        print("🔍 Test de recherche simple...")
        test_results = qdrant.client.search(
            collection_name=qdrant.collection_name,
            query_vector=[0.1] * 768,  # Vecteur bidon pour tester
            limit=1
        )

        if test_results:
            print(f"✅ Qdrant répond correctement")
            print(f"   Premier document: {test_results[0].payload.get('source', 'N/A')}")
            print()
            return True
        else:
            print("⚠️  Qdrant ne retourne aucun résultat")
            return False

    except Exception as e:
        print(f"❌ Erreur de connexion à Qdrant: {e}")
        print("   Vérifiez que Qdrant est lancé: docker-compose up -d")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Menu principal."""
    print("\n" + "=" * 80)
    print("🧪 SCRIPT DE TEST RAG - Job Booster")
    print("=" * 80)
    print()
    print("Que voulez-vous tester ?")
    print()
    print("1. Santé Qdrant (vérifier connexion et nombre de documents)")
    print("2. Test complet avec plusieurs queries")
    print("3. Test spécifique pour lettre de motivation")
    print("4. Tout tester")
    print()

    choice = input("Votre choix (1-4): ").strip()

    if choice == "1":
        await check_qdrant_health()
    elif choice == "2":
        await test_rag_retrieval()
    elif choice == "3":
        await test_specific_query()
    elif choice == "4":
        healthy = await check_qdrant_health()
        if healthy:
            await test_rag_retrieval()
            await test_specific_query()
    else:
        print("❌ Choix invalide")


if __name__ == "__main__":
    asyncio.run(main())
