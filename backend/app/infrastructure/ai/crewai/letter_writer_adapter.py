"""
Letter Writer Adapter (CrewAI).

Infrastructure Layer - Clean Architecture

Adapter pour générer des lettres de motivation avec CrewAI.
Implémente ILetterWriter du domain.
"""

from typing import Any, Dict

from crewai import Process, Task

from app.core.logging import get_logger
from app.domain.entities.job_analysis import JobAnalysis
from app.domain.entities.job_offer import JobOffer
from app.domain.repositories.llm_provider import ILLMProvider
from app.domain.services.writer_service import ILetterWriter
from app.infrastructure.ai.crewai import AgentBuilder, CrewBuilder

logger = get_logger(__name__)


class LetterWriterAdapter(ILetterWriter):
    """
    Adapter CrewAI pour générer des lettres de motivation.

    Responsabilité (SRP):
    - Générer des lettres avec CrewAI
    - Une seule raison de changer: si la config CrewAI lettre change

    Pattern Adapter:
    - Adapte CrewAI à l'interface ILetterWriter
    - Utilise AgentBuilder et CrewBuilder (infrastructure)
    - Respecte Interface Segregation (juste lettres)
    """

    def __init__(
        self,
        llm_provider: ILLMProvider,
        agent_config: Dict[str, Any],
        task_config: Dict[str, Any],
    ):
        """
        Initialise l'adapter avec config et LLM provider.

        Args:
            llm_provider: Provider pour créer LLM
            agent_config: Config de l'agent letter_writer (depuis YAML)
            task_config: Config de la task write_letter (depuis YAML)
        """
        self.llm_provider = llm_provider
        self.agent_config = agent_config
        self.task_config = task_config
        logger.info("letter_writer_adapter_initialized")

    def write_cover_letter(
        self,
        job_offer: JobOffer,
        analysis: JobAnalysis,
        context: str,
    ) -> str:
        """Génère une lettre de motivation avec CrewAI."""
        logger.info("writing_cover_letter_with_crewai")

        # Créer l'agent
        llm = self.llm_provider.create_llm("letter_writer")
        agent = (
            AgentBuilder()
            .from_config(self.agent_config)
            .with_llm(llm)
            .build()
        )

        # Créer la task
        task = Task(
            description=self.task_config.get("description", "Write cover letter"),
            expected_output=self.task_config.get("expected_output", "Cover letter"),
            agent=agent,
        )

        # Créer et exécuter le crew
        crew = (
            CrewBuilder()
            .add_agent(agent)
            .add_task(task)
            .with_process(Process.sequential)
            .build()
        )

        # Passer les inputs au runtime avec analyse complète structurée
        analysis_parts = [
            f"ENTREPRISE: {analysis.company or 'Non spécifiée'}",
            f"POSTE: {analysis.position}",
            f"SECTEUR: {analysis.sector or 'Non spécifié'}",
            "",
            f"RÉSUMÉ: {analysis.summary}",
        ]

        if analysis.missions:
            analysis_parts.append(f"\nMISSIONS: {', '.join(analysis.missions[:5])}")

        if analysis.key_skills:
            analysis_parts.append(f"\nCOMPÉTENCES TECHNIQUES: {', '.join(analysis.key_skills[:8])}")

        if analysis.soft_skills:
            analysis_parts.append(f"\nSOFT SKILLS: {', '.join(analysis.soft_skills[:5])}")

        if analysis.values:
            analysis_parts.append(f"\nVALEURS ENTREPRISE: {', '.join(analysis.values[:4])}")

        if analysis.tone:
            analysis_parts.append(f"\nTON RECRUTEUR: {analysis.tone}")

        analysis_text = "\n".join(analysis_parts)

        inputs = {
            "job_offer": job_offer.text,
            "analysis": analysis_text,
            "rag_context": context,
        }

        logger.info("letter_rag_context_length", length=len(context))

        result = crew.kickoff(inputs=inputs)
        letter_content = str(result)

        logger.info("cover_letter_written", length=len(letter_content))

        return letter_content
