"""
YAML Configuration Loader.

Infrastructure Layer - Clean Architecture

Service pour charger les configurations depuis fichiers YAML.
Responsabilité unique: I/O de fichiers YAML.
"""

from pathlib import Path
from typing import Any, Dict

import yaml

from app.core.logging import get_logger

logger = get_logger(__name__)


class YAMLConfigurationLoader:
    """
    Chargeur de configurations YAML.

    Responsabilité (SRP):
    - Charger et parser les fichiers YAML de configuration
    - Une seule raison de changer: si le format des fichiers change

    Pourquoi ce service?
    - Centralise le chargement de configs (DRY)
    - Respecte SRP: sépare I/O de la logique métier
    - Facilite les tests (mock le loader au lieu de mocker files)
    - Permet de changer de format facilement (YAML → JSON, DB, etc.)

    Note:
    Ce service est dans Infrastructure car l'accès filesystem
    est un détail d'implémentation. Le Domain ne doit pas savoir
    qu'on utilise YAML.
    """

    def __init__(self, config_dir: Path | str = Path("app/agents/config")):
        """
        Initialise le loader avec le dossier de configs.

        Args:
            config_dir: Chemin vers le dossier contenant les YAML
                       Default: app/agents/config
                       Peut être changé pour tests (test/fixtures/config)
        """
        self.config_dir = Path(config_dir)
        logger.info("yaml_config_loader_initialized", config_dir=str(self.config_dir))

    def load_agents_config(self) -> Dict[str, Any]:
        """
        Charge la configuration des agents depuis agents.yaml.

        Returns:
            Dict avec config de tous les agents
            Format:
            {
                "analyzer": {"role": "...", "goal": "...", ...},
                "email_writer": {"role": "...", "goal": "...", ...},
                ...
            }

        Raises:
            FileNotFoundError: Si agents.yaml n'existe pas
            yaml.YAMLError: Si le fichier est mal formaté

        Example:
            >>> loader = YAMLConfigurationLoader()
            >>> config = loader.load_agents_config()
            >>> print(config["analyzer"]["role"])
            "Job Offer Analyzer"
        """
        return self._load_yaml_file("agents.yaml")

    def load_tasks_config(self) -> Dict[str, Any]:
        """
        Charge la configuration des tasks depuis tasks.yaml.

        Returns:
            Dict avec config de toutes les tasks
            Format:
            {
                "analyze_offer": {"description": "...", "expected_output": "...", ...},
                "write_email": {"description": "...", "expected_output": "...", ...},
                ...
            }

        Raises:
            FileNotFoundError: Si tasks.yaml n'existe pas
            yaml.YAMLError: Si le fichier est mal formaté

        Example:
            >>> loader = YAMLConfigurationLoader()
            >>> config = loader.load_tasks_config()
            >>> print(config["analyze_offer"]["description"])
            "Analyze the job offer..."
        """
        return self._load_yaml_file("tasks.yaml")

    def load_llm_config(self) -> Dict[str, Any]:
        """
        Charge la configuration des LLMs depuis llm_config.yaml.

        Returns:
            Dict avec config LLM par agent
            Format:
            {
                "default": {"provider": "openai", "model": "gpt-4o-mini", ...},
                "agents": {
                    "analyzer": {"provider": "openai", "temperature": 0.3, ...},
                    ...
                }
            }

        Raises:
            FileNotFoundError: Si llm_config.yaml n'existe pas
            yaml.YAMLError: Si le fichier est mal formaté

        Example:
            >>> loader = YAMLConfigurationLoader()
            >>> config = loader.load_llm_config()
            >>> print(config["agents"]["analyzer"]["temperature"])
            0.3
        """
        return self._load_yaml_file("llm_config.yaml")

    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Récupère la config d'un agent spécifique.

        Args:
            agent_name: Nom de l'agent (ex: "analyzer", "email_writer")

        Returns:
            Dict avec la config de l'agent
            Retourne dict vide si agent n'existe pas

        Example:
            >>> loader = YAMLConfigurationLoader()
            >>> config = loader.get_agent_config("analyzer")
            >>> print(config["role"])
            "Job Offer Analyzer"
        """
        agents_config = self.load_agents_config()
        return agents_config.get(agent_name, {})

    def get_task_config(self, task_name: str) -> Dict[str, Any]:
        """
        Récupère la config d'une task spécifique.

        Args:
            task_name: Nom de la task (ex: "analyze_offer", "write_email")

        Returns:
            Dict avec la config de la task
            Retourne dict vide si task n'existe pas

        Example:
            >>> loader = YAMLConfigurationLoader()
            >>> config = loader.get_task_config("analyze_offer")
            >>> print(config["description"])
            "Analyze the job offer..."
        """
        tasks_config = self.load_tasks_config()
        return tasks_config.get(task_name, {})

    def _load_yaml_file(self, filename: str) -> Dict[str, Any]:
        """
        Charge un fichier YAML et retourne son contenu.

        Méthode privée utilisée par toutes les méthodes publiques.

        Args:
            filename: Nom du fichier (ex: "agents.yaml")

        Returns:
            Dict avec le contenu du YAML

        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            yaml.YAMLError: Si le fichier est mal formaté

        Note:
            Cette méthode est private (préfixe _) car elle est un
            détail d'implémentation. Les clients utilisent les méthodes
            publiques (load_agents_config, etc.).
        """
        file_path = self.config_dir / filename

        logger.info("loading_yaml_file", path=str(file_path))

        # Vérifier que le fichier existe
        if not file_path.exists():
            logger.error("yaml_file_not_found", path=str(file_path))
            raise FileNotFoundError(f"Config file not found: {file_path}")

        # Charger et parser le YAML
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            logger.info(
                "yaml_file_loaded",
                path=str(file_path),
                keys_count=len(config) if isinstance(config, dict) else 0,
            )

            return config if config is not None else {}

        except yaml.YAMLError as e:
            logger.error(
                "yaml_parse_error",
                path=str(file_path),
                error=str(e),
            )
            raise
