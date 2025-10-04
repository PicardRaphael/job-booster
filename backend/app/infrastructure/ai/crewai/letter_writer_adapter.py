"""
Letter Writer Adapter (CrewAI).

Infrastructure Layer - Clean Architecture

Adapter pour g�n�rer des lettres de motivation avec CrewAI.
Impl�mente ILetterWriter du domain.
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
    Adapter CrewAI pour g�n�rer des lettres de motivation.

    Responsabilit� (SRP):
    - G�n�rer des lettres avec CrewAI
    - Une seule raison de changer: si la config CrewAI lettre change

    Pattern Adapter:
    - Adapte CrewAI � l'interface ILetterWriter
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
            llm_provider: Provider pour cr�er LLM
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
        """G�n�re une lettre de motivation avec CrewAI."""
        logger.info("writing_cover_letter_with_crewai")

        # Cr�er l'agent
        llm = self.llm_provider.create_llm("letter_writer")
        agent = (
            AgentBuilder()
            .from_config(self.agent_config)
            .with_llm(llm)
            .build()
        )

        # Cr�er la task
        task = Task(
            description=self.task_config.get("description", "Write cover letter"),
            expected_output=self.task_config.get("expected_output", "Cover letter"),
            agent=agent,
        )

        # Cr�er et ex�cuter le crew
        crew = (
            CrewBuilder()
            .add_agent(agent)
            .add_task(task)
            .with_process(Process.sequential)
            .build()
        )

        inputs = {
            "job_offer": job_offer.text,
            "analysis": analysis.summary,
            "rag_context": context,
        }

        result = crew.kickoff(inputs=inputs)
        letter_content = str(result)

        logger.info("cover_letter_written", length=len(letter_content))

        return letter_content
