"""LLM provider interface (Port)."""

from abc import ABC, abstractmethod
from langchain_core.language_models import BaseChatModel


class ILLMProvider(ABC):
    """
    Interface for LLM providers.

    This is a Port in Hexagonal Architecture.
    Implementations are Adapters.
    """

    @abstractmethod
    def create_llm(self, agent_name: str) -> BaseChatModel:
        """
        Create LLM for specific agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Configured LLM instance
        """
        pass
