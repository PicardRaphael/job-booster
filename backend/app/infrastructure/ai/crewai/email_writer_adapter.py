"""
Email Writer Adapter (CrewAI).

Infrastructure Layer - Clean Architecture

Adapter pour générer des emails avec CrewAI.
Implémente IEmailWriter du domain.
"""

from typing import Any, Dict

from crewai import Process, Task

from app.core.logging import get_logger
from app.domain.entities.job_analysis import JobAnalysis
from app.domain.entities.job_offer import JobOffer
from app.domain.repositories.llm_provider import ILLMProvider
from app.domain.services.writer_service import IEmailWriter
from app.infrastructure.ai.crewai import AgentBuilder, CrewBuilder
logger = get_logger(__name__)

class EmailWriterAdapter(IEmailWriter):
    """
    Adapter CrewAI pour générer des emails.

    Responsabilité (SRP):
    - Générer des emails avec CrewAI
    - Une seule raison de changer: si la config CrewAI email change

    Pattern Adapter:
    - Adapte CrewAI à l'interface IEmailWriter
    - Utilise AgentBuilder et CrewBuilder (infrastructure)
    - Respecte Interface Segregation (juste emails)
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
            agent_config: Config de l'agent email_writer (depuis YAML)
            task_config: Config de la task write_email (depuis YAML)
        """
        self.llm_provider = llm_provider
        self.agent_config = agent_config
        self.task_config = task_config
        logger.info("email_writer_adapter_initialized")

    def write_email(
        self,
        job_offer: JobOffer,
        analysis: JobAnalysis,
        context: str,
    ) -> str:
        """Génère un email de motivation avec CrewAI."""
        logger.info("writing_email_with_crewai")

        # Créer l'agent
        llm = self.llm_provider.create_llm("email_writer")
        agent = (
            AgentBuilder()
            .from_config(self.agent_config)
            .with_llm(llm)
            .build()
        )

        # Créer la task
        task = Task(
            description=self.task_config.get("description", "Write email"),
            expected_output=self.task_config.get("expected_output", "Email"),
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
        email_content = str(result)

        logger.info("email_written", length=len(email_content))

        return email_content
