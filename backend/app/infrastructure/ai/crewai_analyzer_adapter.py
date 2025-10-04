"""
CrewAI Analyzer Adapter.

Infrastructure Layer - Clean Architecture

Adapter pour analyser les offres d'emploi avec CrewAI.
Implémente IAnalyzerService du domain.
"""

from typing import Any, Dict

from crewai import Process, Task

from app.core.logging import get_logger
from app.domain.entities.job_analysis import JobAnalysis
from app.domain.entities.job_offer import JobOffer
from app.domain.repositories.llm_provider import ILLMProvider
from app.domain.services.analyzer_service import IAnalyzerService
from app.infrastructure.ai.crewai import AgentBuilder, CrewBuilder

logger = get_logger(__name__)


class CrewAIAnalyzerAdapter(IAnalyzerService):
    """
    Adapter CrewAI pour analyse d'offres d'emploi.

    Responsabilité (SRP):
    - Analyser les offres avec CrewAI
    - Une seule raison de changer: si la config CrewAI analyzer change

    Pattern Adapter:
    - Adapte CrewAI à l'interface IAnalyzerService
    - Utilise AgentBuilder et CrewBuilder (infrastructure)
    - Ne charge PLUS les configs YAML (reçoit en injection)

    IMPORTANT - Clean Architecture:
    Avant: L'adapter chargeait les YAML (violation SRP)
    Maintenant: L'adapter reçoit les configs en injection
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
            agent_config: Config de l'agent analyzer (depuis YAML, injectée)
            task_config: Config de la task analyze_offer (depuis YAML, injectée)

        Example:
            >>> # Dans le Container
            >>> config_loader = YAMLConfigurationLoader()
            >>> agent_config = config_loader.get_agent_config("analyzer")
            >>> task_config = config_loader.get_task_config("analyze_offer")
            >>> adapter = CrewAIAnalyzerAdapter(
            ...     llm_provider=llm_provider,
            ...     agent_config=agent_config,  # ← Injection!
            ...     task_config=task_config      # ← Injection!
            ... )
        """
        self.llm_provider = llm_provider
        self.agent_config = agent_config
        self.task_config = task_config
        logger.info("crewai_analyzer_adapter_initialized")

    def analyze(self, job_offer: JobOffer) -> JobAnalysis:
        """
        Analyse une offre d'emploi avec CrewAI.

        Args:
            job_offer: Offre d'emploi à analyser (entity)

        Returns:
            JobAnalysis avec summary, skills, position, company

        Example:
            >>> job_offer = JobOffer(text="Développeur Python...")
            >>> analysis = adapter.analyze(job_offer)
            >>> print(analysis.position)
            "Développeur Python"
            >>> print(analysis.key_skills)
            ["Python", "FastAPI", "Docker"]
        """
        logger.info("analyzing_job_offer_with_crewai")

        # Créer l'agent avec Builder pattern
        llm = self.llm_provider.create_llm("analyzer")
        agent = (
            AgentBuilder()
            .from_config(self.agent_config)
            .with_llm(llm)
            .build()
        )

        # Créer la task
        task = Task(
            description=self.task_config.get("description", "Analyze job offer"),
            expected_output=self.task_config.get("expected_output", "Analysis"),
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

        result = crew.kickoff(inputs={"job_offer": job_offer.text})
        summary = str(result)

        # TODO: Parser la sortie structurée du LLM
        # Pour l'instant, retour simple avec valeurs hardcodées
        logger.info("analysis_completed", summary_length=len(summary))

        return JobAnalysis(
            summary=summary,
            key_skills=["Python", "FastAPI"],  # TODO: Extraire du summary
            position="Software Engineer",  # TODO: Extraire du summary
            company=None,  # TODO: Extraire du summary
        )
