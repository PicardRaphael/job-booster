"""LLM provider adapter."""

from langchain_core.language_models import BaseChatModel

from app.domain.repositories.llm_provider import ILLMProvider
from app.core.llm_factory import LLMFactory
from app.core.logging import get_logger

logger = get_logger(__name__)


class LLMProviderAdapter(ILLMProvider):
    """
    LLM provider adapter implementing domain interface.

    Adapter for LLMFactory.
    """

    def __init__(self, llm_factory: LLMFactory) -> None:
        """
        Initialize adapter with LLM factory.

        Args:
            llm_factory: LLM factory instance
        """
        self.llm_factory = llm_factory
        logger.info("llm_provider_adapter_initialized")

    def create_llm(self, agent_name: str) -> BaseChatModel:
        """Create LLM for specific agent."""
        return self.llm_factory.create_llm_for_agent(agent_name)
