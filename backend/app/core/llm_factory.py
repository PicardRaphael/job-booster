"""
LLM Factory with flexible configuration and ENV override support.

Core Layer - Clean Architecture

Factory pour créer des instances de LLM configurées par agent.
IMPORTANT: Ne fait PLUS d'I/O - reçoit la config en injection.
"""

import os
from typing import Any, Dict

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class LLMFactory:
    """
    Factory pour créer des instances LLM configurées par agent.

    Responsabilité (SRP):
    - Créer des LLMs avec la bonne configuration
    - Appliquer les overrides d'environnement
    - Une seule raison de changer: si les providers LLM changent

    Support multi-providers:
    - OpenAI (GPT-4, GPT-4o, GPT-4o-mini)
    - Google Gemini (gemini-1.5-pro, gemini-1.5-flash)
    - Anthropic Claude (claude-3-5-sonnet, claude-3-opus)

    Configuration hierarchy:
    1. Default (YAML)
    2. Agent-specific (YAML)
    3. Environment variables (override tout)

    ENV overrides format:
        AGENT_<AGENT_NAME>_<PARAM>=value
        Ex: AGENT_ANALYZER_PROVIDER=anthropic
            AGENT_ANALYZER_TEMPERATURE=0.2

    IMPORTANT - Clean Architecture:
    Cette factory NE CHARGE PAS les fichiers YAML.
    Elle reçoit la config en injection (déjà chargée par YAMLConfigurationLoader).
    Cela respecte la séparation des responsabilités:
    - Infrastructure: Charge fichiers YAML (YAMLConfigurationLoader)
    - Core: Crée LLMs depuis config (LLMFactory)
    """

    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initialise la factory avec une config déjà chargée.

        Args:
            llm_config: Configuration LLM (déjà chargée depuis YAML)
                       Format attendu:
                       {
                           "default": {"provider": "openai", ...},
                           "agents": {
                               "analyzer": {"temperature": 0.3, ...},
                               ...
                           }
                       }

        Example:
            >>> # Dans le Container
            >>> config_loader = YAMLConfigurationLoader()
            >>> llm_config = config_loader.load_llm_config()
            >>> factory = LLMFactory(llm_config)  # ← Injection, pas I/O!
        """
        self.config = llm_config
        logger.info("llm_factory_initialized", agents_count=len(llm_config.get("agents", {})))

    def _get_env_override(self, agent_name: str, param: str) -> Any | None:
        """
        Récupère un override d'environnement pour un paramètre.

        Format: AGENT_<AGENT_NAME>_<PARAM>=value

        Args:
            agent_name: Nom de l'agent (ex: "analyzer")
            param: Nom du paramètre (ex: "temperature")

        Returns:
            Valeur convertie au bon type, ou None si pas d'override

        Example:
            >>> # export AGENT_ANALYZER_TEMPERATURE=0.2
            >>> factory._get_env_override("analyzer", "temperature")
            0.2  # ← Converti en float
        """
        env_key = f"AGENT_{agent_name.upper()}_{param.upper()}"
        value = os.getenv(env_key)

        if value is None:
            return None

        # Convertir au bon type selon le paramètre
        try:
            if param in ["temperature", "top_p", "frequency_penalty", "presence_penalty"]:
                return float(value)
            elif param in ["max_tokens", "max_output_tokens", "top_k"]:
                return int(value)
            else:
                return value  # String (provider, model)
        except ValueError as e:
            logger.warning(
                "env_override_conversion_failed",
                agent_name=agent_name,
                param=param,
                value=value,
                error=str(e),
            )
            return None

    def _get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Récupère la configuration merged pour un agent.

        Hiérarchie (ordre de priorité croissant):
        1. Config default (YAML)
        2. Config agent (YAML)
        3. ENV overrides (le plus prioritaire)

        Args:
            agent_name: Nom de l'agent

        Returns:
            Dict avec config merged

        Example:
            >>> # YAML default: {"temperature": 0.7}
            >>> # YAML agent: {"temperature": 0.3}
            >>> # ENV: AGENT_ANALYZER_TEMPERATURE=0.2
            >>> config = factory._get_agent_config("analyzer")
            >>> print(config["temperature"])
            0.2  # ← ENV gagne
        """
        # Étape 1: Config default
        default_config = self.config.get("default", {})

        # Étape 2: Config agent-specific
        agents_config = self.config.get("agents", {})
        agent_config = agents_config.get(agent_name, {})

        # Merge: default écrasé par agent
        merged = {**default_config, **agent_config}

        # Étape 3: Appliquer ENV overrides
        env_params = [
            "provider",
            "model",
            "temperature",
            "max_tokens",
            "max_output_tokens",
            "top_p",
            "top_k",
            "frequency_penalty",
            "presence_penalty",
        ]

        for param in env_params:
            env_value = self._get_env_override(agent_name, param)
            if env_value is not None:
                merged[param] = env_value
                logger.info(
                    "env_override_applied",
                    agent_name=agent_name,
                    param=param,
                    value=env_value,
                )

        return merged

    def _create_openai_llm(self, config: Dict[str, Any]) -> ChatOpenAI:
        """
        Crée une instance ChatOpenAI.

        Args:
            config: Config avec model, temperature, etc.

        Returns:
            Instance ChatOpenAI configurée
        """
        return ChatOpenAI(
            model=config.get("model", settings.openai_model),
            api_key=settings.openai_api_key,
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 2000),
            top_p=config.get("top_p", 1.0),
            frequency_penalty=config.get("frequency_penalty", 0.0),
            presence_penalty=config.get("presence_penalty", 0.0),
        )

    def _create_google_llm(self, config: Dict[str, Any]) -> ChatGoogleGenerativeAI:
        """
        Crée une instance ChatGoogleGenerativeAI (Gemini).

        Args:
            config: Config avec model, temperature, etc.

        Returns:
            Instance ChatGoogleGenerativeAI configurée
        """
        return ChatGoogleGenerativeAI(
            model=config.get("model", settings.gemini_model),
            google_api_key=settings.google_api_key,
            temperature=config.get("temperature", 0.7),
            max_output_tokens=config.get("max_output_tokens", 2000),
            top_p=config.get("top_p", 1.0),
            top_k=config.get("top_k", 40),
        )

    def _create_anthropic_llm(self, config: Dict[str, Any]) -> ChatAnthropic:
        """
        Crée une instance ChatAnthropic (Claude).

        Args:
            config: Config avec model, temperature, etc.

        Returns:
            Instance ChatAnthropic configurée
        """
        return ChatAnthropic(
            model=config.get("model", "claude-3-5-sonnet-20241022"),
            anthropic_api_key=settings.anthropic_api_key,
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 2000),
            top_p=config.get("top_p", 1.0),
        )

    def create_llm_for_agent(self, agent_name: str) -> BaseChatModel:
        """
        Crée une instance LLM pour un agent spécifique.

        Détecte automatiquement le provider et crée le bon LLM.

        Args:
            agent_name: Nom de l'agent (ex: "analyzer", "email_writer")

        Returns:
            Instance LLM configurée (ChatOpenAI, ChatGoogleGenerativeAI, ou ChatAnthropic)

        Raises:
            ValueError: Si le provider n'est pas supporté

        Example:
            >>> llm = factory.create_llm_for_agent("analyzer")
            >>> response = llm.invoke("Analyse cette offre...")
        """
        # Récupérer config merged (default + agent + env)
        config = self._get_agent_config(agent_name)
        provider = config.get("provider", "openai")

        logger.info(
            "creating_llm_for_agent",
            agent_name=agent_name,
            provider=provider,
            model=config.get("model"),
            temperature=config.get("temperature"),
        )

        # Créer le LLM selon le provider
        if provider == "openai":
            return self._create_openai_llm(config)
        elif provider == "google":
            return self._create_google_llm(config)
        elif provider == "anthropic":
            return self._create_anthropic_llm(config)
        else:
            raise ValueError(
                f"Provider LLM non supporté: {provider}. "
                f"Providers supportés: openai, google, anthropic"
            )


# ============================================================================
# LEGACY SINGLETON (garde pour compatibilité, sera supprimé après migration)
# ============================================================================

_llm_factory: LLMFactory | None = None


def get_llm_factory() -> LLMFactory:
    """
    Récupère la factory singleton (LEGACY).

    DEPRECATED: Cette fonction charge encore le YAML directement.
    Utiliser plutôt le Container qui injecte la config.

    Returns:
        Instance singleton de LLMFactory
    """
    global _llm_factory

    if _llm_factory is None:
        # Charge config directement (LEGACY - à supprimer)
        from pathlib import Path
        import yaml

        config_path = Path("app/agents/config/llm_config.yaml")

        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                llm_config = yaml.safe_load(f)
        else:
            # Config par défaut si fichier absent
            llm_config = {
                "default": {
                    "provider": "openai",
                    "model": settings.openai_model,
                    "temperature": 0.7,
                },
                "agents": {},
            }

        _llm_factory = LLMFactory(llm_config)

    return _llm_factory
