"""
Generate Cover Letter Use Case.

Application Layer - Clean Architecture

Use case atomique pour générer une lettre de motivation.
Responsabilité unique: Génération de lettre uniquement.
"""

from typing import List

from app.application.commands import GenerateContentCommand
from app.application.dtos import DocumentDTO
from app.core.logging import get_logger
from app.domain.entities.job_analysis import JobAnalysis
from app.domain.entities.job_offer import JobOffer
from app.domain.services.writer_service import ILetterWriter
from app.infrastructure.observability.langfuse_decorator import trace_span


logger = get_logger(__name__)


class GenerateCoverLetterUseCase:
    """
    Use Case: Générer une lettre de motivation.

    Responsabilité (SRP):
    - Générer uniquement des lettres de motivation
    - Une seule raison de changer: si le format lettre change

    Flow:
    1. Construire le contexte RAG depuis documents
    2. Convertir DTOs → Entities
    3. Appeler le writer service
    4. Retourner le contenu généré

    Pourquoi ce use case séparé?
    - Interface Segregation: Dépend de ILetterWriter uniquement
    - Réutilisable: On peut générer une lettre indépendamment
    - Testable: Mock ILetterWriter facilement
    """

    def __init__(self, letter_writer: ILetterWriter):
        """
        Injecte le writer de lettres.

        Args:
            letter_writer: Writer pour générer lettres (interface)
                          Ex: LetterWriterAdapter (avec CrewAI)
        """
        self.letter_writer = letter_writer

    @trace_span("GenerateCoverLetterUseCase")
    def execute(self, command: GenerateContentCommand) -> str:
        """
        Génère une lettre de motivation.

        Args:
            command: Command contenant job_offer, analysis, documents

        Returns:
            Lettre de motivation (str)
            Format: Lettre formelle avec en-tête, corps, signature

        Raises:
            ContentGenerationError: Si la génération échoue

        Example:
            >>> command = GenerateContentCommand(
            ...     job_offer=JobOfferDTO(...),
            ...     analysis=JobAnalysisDTO(...),
            ...     documents=[doc1, doc2, doc3],
            ...     content_type="letter"
            ... )
            >>> letter = use_case.execute(command)
            >>> print(letter)
            "Madame, Monsieur,\\n\\nJe vous adresse ma candidature..."
        """
        logger.info("generate_cover_letter_use_case_started")

        # Étape 1: Construire contexte RAG
        context = self._build_rag_context(command.documents)

        # Étape 2: Convertir DTOs → Entities (validation)
        job_offer = JobOffer(text=command.job_offer.text)
        analysis = JobAnalysis(
            summary=command.analysis.summary,
            key_skills=command.analysis.key_skills,
            position=command.analysis.position,
            company=command.analysis.company,
        )

        # Étape 3: Appeler le writer
        letter_content = self.letter_writer.write_cover_letter(
            job_offer=job_offer,
            analysis=analysis,
            context=context,
        )

        logger.info(
            "generate_cover_letter_use_case_completed",
            content_length=len(letter_content),
        )

        return letter_content

    def _build_rag_context(self, documents: List[DocumentDTO]) -> str:
        """
        Construit un contexte RAG ULTRA-STRUCTURÉ et PERTINENT.

        STRATÉGIE OPTIMISÉE avec nouveau système de chunking:
        1. Utilise le metadata "type" et "ruleset_type" des chunks
        2. Priorise les RULESETS LETTER + GLOBAL
        3. Construit un contexte cohérent et complet

        Args:
            documents: Liste de documents reranked par pertinence

        Returns:
            Contexte structuré et optimisé (str)

        Note:
            Les documents sont déjà triés par pertinence (reranker).
            On va les catégoriser et les structurer pour l'agent writer.
        """
        if not documents:
            logger.warning("generate_cover_letter_no_rag_context")
            return ""

        # === CATÉGORISATION INTELLIGENTE AVEC METADATA ===

        # 1. RULESETs - Utilise le nouveau metadata "ruleset_type"
        ruleset_global = [doc for doc in documents if
                         getattr(doc, "metadata", {}).get("type") == "ruleset" and
                         getattr(doc, "metadata", {}).get("ruleset_type") == "global"]

        ruleset_letter = [doc for doc in documents if
                         getattr(doc, "metadata", {}).get("type") == "ruleset" and
                         getattr(doc, "metadata", {}).get("ruleset_type") == "letter"]

        ruleset_signature = [doc for doc in documents if
                            getattr(doc, "metadata", {}).get("type") == "ruleset" and
                            getattr(doc, "metadata", {}).get("ruleset_type") == "signature"]

        # Fallback pour les anciens chunks sans metadata (backward compatibility)
        if not ruleset_letter:
            ruleset_letter = [doc for doc in documents if
                            "[RULESET: LETTER]" in doc.text or
                            "RULESET: LETTER" in doc.text]

        if not ruleset_global:
            ruleset_global = [doc for doc in documents if
                            "[RULESET: GLOBAL]" in doc.text or
                            "RULESET: GLOBAL" in doc.text]

        if not ruleset_signature:
            ruleset_signature = [doc for doc in documents if
                               "[RULESET: SIGNATURE]" in doc.text or
                               "raphaelpicard@outlook.fr" in doc.text]

        # 2. Informations personnelles (type = "profile" depuis le header de informations.md)
        info_perso = [doc for doc in documents if
                     getattr(doc, "metadata", {}).get("source") == "informations.md" and
                     getattr(doc, "metadata", {}).get("type") == "profile"]

        # 3. Expériences professionnelles (par pertinence)
        experiences_royal_canin = [doc for doc in documents if "Royal Canin" in doc.text]
        experiences_freelance = [doc for doc in documents if "Raphaël PICARD EI" in doc.text or "Freelance" in doc.text]
        experiences_schoolmouv = [doc for doc in documents if "SchoolMouv" in doc.text]
        experiences_other = [doc for doc in documents if
                            "Aixia" in doc.text or
                            "Leasys" in doc.text or
                            any(keyword in doc.text for keyword in ["Projet :", "Mission :", "Fonction :"])]

        # 4. Compétences techniques
        competences_frontend = [doc for doc in documents if
                               any(tech in doc.text for tech in ["React", "Next.js", "TypeScript", "Tailwind", "Storybook"])]
        competences_backend = [doc for doc in documents if
                              any(tech in doc.text for tech in ["Node.js", "FastAPI", "Python", "PostgreSQL", "API REST"])]
        competences_ia = [doc for doc in documents if
                         any(tech in doc.text for tech in ["IA", "LangChain", "RAG", "agents", "LLM", "CrewAI", "OpenAI"])]

        # 5. Formations et certifications
        formations = [doc for doc in documents if
                     any(keyword in doc.text for keyword in ["HuggingFace", "O'Clock", "Certification", "Formation"])]

        # === CONSTRUCTION DU CONTEXTE STRUCTURÉ ===
        context_parts = []

        # SECTION 1: RULESET LETTER (CRUCIAL - règles de rédaction)
        if ruleset_letter:
            context_parts.append("=== [RULESET: LETTER - RÈGLES DE RÉDACTION] ===\n" +
                                ruleset_letter[0].text)  # 1 seul chunk complet
            logger.info("ruleset_letter_found")
        else:
            logger.warning("ruleset_letter_not_found")

        # SECTION 2: RULESET GLOBAL (infos perso, ton, style)
        if ruleset_global:
            context_parts.append("=== [RULESET: GLOBAL - RÈGLES GÉNÉRALES] ===\n" +
                                ruleset_global[0].text)  # 1 seul chunk complet
            logger.info("ruleset_global_found")
        else:
            logger.warning("ruleset_global_not_found")

        # SECTION 3: COMPÉTENCES TECHNIQUES PERTINENTES
        all_competences = competences_frontend + competences_backend + competences_ia
        if all_competences:
            # Déduplication
            seen_texts = set()
            unique_competences = []
            for doc in all_competences:
                if doc.text not in seen_texts:
                    seen_texts.add(doc.text)
                    unique_competences.append(doc)

            context_parts.append("=== [COMPÉTENCES TECHNIQUES PERTINENTES] ===\n" +
                                "\n".join(doc.text for doc in unique_competences[:3]))  # Top 3

        # SECTION 4: EXPÉRIENCES PROFESSIONNELLES PERTINENTES
        all_experiences = (experiences_freelance[:2] +  # Priorité freelance IA
                          experiences_royal_canin[:2] +   # Puis Royal Canin (React)
                          experiences_schoolmouv[:1] +    # SchoolMouv
                          experiences_other[:1])          # Autres

        if all_experiences:
            # Déduplication
            seen_texts = set()
            unique_experiences = []
            for doc in all_experiences:
                if doc.text not in seen_texts:
                    seen_texts.add(doc.text)
                    unique_experiences.append(doc)

            context_parts.append("=== [EXPÉRIENCES PROFESSIONNELLES PERTINENTES] ===\n" +
                                "\n".join(doc.text for doc in unique_experiences[:4]))  # Top 4 expériences

        # SECTION 5: FORMATIONS (si pertinentes)
        if formations:
            context_parts.append("=== [FORMATIONS ET CERTIFICATIONS] ===\n" +
                                "\n".join(doc.text for doc in formations[:2]))  # Top 2

        # SECTION 6: SIGNATURE
        if ruleset_signature:
            context_parts.append("=== [SIGNATURE] ===\n" +
                                ruleset_signature[0].text)  # 1 seul chunk complet

        final_context = "\n\n".join(context_parts)
        logger.info("rag_context_built",
                   sections=len(context_parts),
                   total_length=len(final_context),
                   ruleset_letter_found=len(ruleset_letter) > 0,
                   ruleset_global_found=len(ruleset_global) > 0)

        return final_context