"""
LinkedIn Writer Adapter (CrewAI).

Infrastructure Layer - Clean Architecture

Adapter pour générer des posts LinkedIn avec CrewAI.
Implémente ILinkedInWriter du domain.
"""

from typing import Any, Dict

from crewai import Process, Task

from app.core.logging import get_logger
from app.domain.entities.job_analysis import JobAnalysis
from app.domain.entities.job_offer import JobOffer
from app.domain.repositories.llm_provider import ILLMProvider
from app.domain.services.writer_service import ILinkedInWriter
from app.infrastructure.ai.crewai import AgentBuilder, CrewBuilder

logger = get_logger(__name__)


class LinkedInWriterAdapter(ILinkedInWriter):
    """
    Adapter CrewAI pour générer des posts LinkedIn.

    Responsabilité (SRP):
    - Générer des posts LinkedIn avec CrewAI
    - Une seule raison de changer: si la config CrewAI LinkedIn change

    Pattern Adapter:
    - Adapte CrewAI à l'interface ILinkedInWriter
    - Utilise AgentBuilder et CrewBuilder (infrastructure)
    - Respecte Interface Segregation (juste LinkedIn)
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
            agent_config: Config de l'agent linkedin_writer (depuis YAML)
            task_config: Config de la task write_linkedin (depuis YAML)
        """
        self.llm_provider = llm_provider
        self.agent_config = agent_config
        self.task_config = task_config
        logger.info("linkedin_writer_adapter_initialized")

    def write_linkedin_post(
        self,
        job_offer: JobOffer,
        analysis: JobAnalysis,
        context: str,
    ) -> str:
        """Génère un post LinkedIn avec CrewAI."""
        logger.info("writing_linkedin_post_with_crewai")

        # Créer l'agent
        llm = self.llm_provider.create_llm("linkedin_writer")
        agent = (
            AgentBuilder()
            .from_config(self.agent_config)
            .with_llm(llm)
            .build()
        )

        # Créer la task
        task = Task(
            description=self.task_config.get("description", "Write LinkedIn post"),
            expected_output=self.task_config.get("expected_output", "LinkedIn post"),
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

        inputs = {
            "job_offer": job_offer.text,
            "analysis": analysis.summary,
            "rag_context": context,
        }

        result = crew.kickoff(inputs=inputs)
        linkedin_content = str(result)

        logger.info("linkedin_post_written", length=len(linkedin_content))

        return linkedin_content
