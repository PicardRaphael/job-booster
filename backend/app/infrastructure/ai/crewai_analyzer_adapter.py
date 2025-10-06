"""
CrewAI Analyzer Adapter.

Infrastructure Layer - Clean Architecture

Adapter pour analyser les offres d'emploi avec CrewAI.
Implémente IAnalyzerService du domain.
"""

import json
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

    def analyze(self, job_offer: JobOffer, content_type: str) -> JobAnalysis:
        """
        Analyse une offre d'emploi avec CrewAI.

        Args:
            job_offer: Offre d'emploi à analyser (entity)
            content_type: Type de contenu demandé (letter, email, linkedin)

        Returns:
            JobAnalysis avec summary, skills, position, company, content_type

        Example:
            >>> job_offer = JobOffer(text="Développeur Python...")
            >>> analysis = adapter.analyze(job_offer, "letter")
            >>> print(analysis.position)
            "Développeur Python"
            >>> print(analysis.key_skills)
            ["Python", "FastAPI", "Docker"]
            >>> print(analysis.content_type)
            "letter"
        """
        logger.info("analyzing_job_offer_with_crewai", content_type=content_type)

        # Créer l'agent avec Builder pattern
        llm = self.llm_provider.create_llm("analyzer")
        analyzer_agent = (
            AgentBuilder()
            .from_config(self.agent_config)
            .with_llm(llm)
            .build()
        )

        # Créer la task
        task = Task(
            description=self.task_config.get("description", "Analyze job offer").format(
                job_offer=job_offer.text
            ),
            expected_output=self.task_config.get("expected_output", "Analysis"),
            agent=analyzer_agent,
        )

        # Créer et exécuter le crew
        crew = (
            CrewBuilder()
            .add_agent(analyzer_agent)
            .add_task(task)
            .with_process(Process.sequential)
            .build()
        )

        result = crew.kickoff(inputs={"job_offer": job_offer.text, "agent": content_type})
        raw_output = str(result)
        logger.info("analysis_completed", output_length=len(raw_output))

        # 4. Parsing du JSON renvoyé
        try:
            # Try to extract JSON from the output (it might be wrapped in markdown or text)
            # First, try direct parsing
            parsed = json.loads(raw_output)
            logger.info("analysis_parsed_successfully", method="direct")
        except json.JSONDecodeError:
            # Try to find JSON in code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_output, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group(1))
                    logger.info("analysis_parsed_successfully", method="code_block")
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON in code block")
                    parsed = {}
            else:
                # Try to find JSON anywhere in the text
                json_match = re.search(r'\{[^{}]*"poste"[^{}]*\}', raw_output, re.DOTALL)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group(0))
                        logger.info("analysis_parsed_successfully", method="regex")
                    except json.JSONDecodeError:
                        logger.warning("Invalid JSON output from analyzer")
                        parsed = {}
                else:
                    logger.warning("No JSON found in analyzer output")
                    parsed = {}

        # Log what we got
        logger.info("parsed_analysis",
                   has_position=bool(parsed.get("poste")),
                   has_company=bool(parsed.get("entreprise")),
                   keys=list(parsed.keys()) if parsed else [])

        # 5. Construction de l'entité JobAnalysis avec toutes les infos
        # Extract position with fallback
        position = parsed.get("poste")
        if not position:
            # Try to extract from summary
            logger.warning("position_missing_from_json_trying_fallback")
            # Use first 100 chars of job offer as fallback
            position = "Developer"  # Safe default

        return JobAnalysis(
            summary=raw_output,
            key_skills=parsed.get("compétences") or parsed.get("technologies") or [],
            position=position,
            company=parsed.get("entreprise"),
            missions=parsed.get("missions", []),
            sector=parsed.get("secteur"),
            soft_skills=parsed.get("soft_skills", []),
            values=parsed.get("valeurs", []),
            tone=parsed.get("ton_recruteur"),
            content_type=content_type,
        )
