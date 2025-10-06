"""
Agent Builder - Fluent Interface Pattern.

Application Layer - Clean Architecture
Implements the Builder pattern for constructing complex CrewAI Agent objects.

This provides a fluent, readable API for building agents step-by-step,
avoiding telescoping constructors and improving code clarity.

Design Pattern: Builder + Fluent Interface
"""

from typing import Dict, Any, Optional
from crewai import Agent
from langchain_core.language_models import BaseChatModel

from app.core.logging import get_logger

logger = get_logger(__name__)


class AgentBuilder:
    """
    Builder for CrewAI Agent using Fluent Interface pattern.

    Provides a clean, readable way to construct agents with many parameters.
    Each method returns self, allowing method chaining.

    Why Builder Pattern?
    - Agents have many optional parameters (10+)
    - Avoids long constructor calls: Agent(param1, param2, ..., param10)
    - Provides clear, self-documenting code
    - Allows step-by-step construction with validation

    Example:
        >>> llm = llm_factory.create_llm("analyzer")
        >>> agent = (AgentBuilder()
        ...     .with_role("Senior Job Analyzer")
        ...     .with_goal("Extract key information from job offers")
        ...     .with_backstory("Expert in HR with 15 years experience")
        ...     .with_llm(llm)
        ...     .with_memory(True)
        ...     .with_verbose(True)
        ...     .build())
    """

    def __init__(self) -> None:
        """
        Initialize builder with default values.

        All optional parameters are set to None or sensible defaults.
        Required parameters (role, goal, llm) must be set before build().
        """
        # === Required Parameters (validated in build()) ===
        self._role: Optional[str] = None  # Agent's role/title
        self._goal: Optional[str] = None  # What the agent should achieve
        self._llm: Optional[BaseChatModel] = None  # LLM to use

        # === Optional Parameters (with defaults) ===
        self._backstory: Optional[str] = None  # Agent's background story
        self._allow_delegation: bool = False  # Can agent delegate tasks?
        self._verbose: bool = True  # Detailed logging?
        self._memory: bool = True  # Remember past interactions?
        self._config: Dict[str, Any] = {}  # Additional config

        # === Custom Templates (for advanced prompt control) ===
        self._system_template: Optional[str] = None  # Custom system template
        self._prompt_template: Optional[str] = None  # Custom prompt template
        self._response_template: Optional[str] = None  # Custom response template

    def with_role(self, role: str) -> "AgentBuilder":
        """
        Set agent role/title.

        Args:
            role: Role description (e.g., "Senior Python Developer Analyst")

        Returns:
            Self for method chaining
        """
        self._role = role
        return self  # Enable fluent interface

    def with_goal(self, goal: str) -> "AgentBuilder":
        """
        Set agent goal/objective.

        Args:
            goal: What the agent should accomplish

        Returns:
            Self for method chaining
        """
        self._goal = goal
        return self

    def with_backstory(self, backstory: str) -> "AgentBuilder":
        """
        Set agent backstory/context.

        Args:
            backstory: Agent's background and expertise

        Returns:
            Self for method chaining
        """
        self._backstory = backstory
        return self

    def with_llm(self, llm: BaseChatModel) -> "AgentBuilder":
        """
        Set LLM for the agent.

        Args:
            llm: Configured LangChain LLM instance

        Returns:
            Self for method chaining
        """
        self._llm = llm
        return self

    def with_delegation(self, allow: bool = True) -> "AgentBuilder":
        """
        Enable/disable task delegation.

        Args:
            allow: Whether agent can delegate tasks to other agents

        Returns:
            Self for method chaining
        """
        self._allow_delegation = allow
        return self

    def with_memory(self, enabled: bool = True) -> "AgentBuilder":
        """Enable/disable memory."""
        self._memory = enabled
        return self

    def with_verbose(self, enabled: bool = True) -> "AgentBuilder":
        """Enable/disable verbose mode."""
        self._verbose = enabled
        return self

    def from_config(self, config: Dict[str, Any]) -> "AgentBuilder":
        """Load configuration from dict."""
        self._config = config
        self._role = config.get("role", self._role)
        self._goal = config.get("goal", self._goal)
        self._backstory = config.get("backstory", self._backstory)
        self._allow_delegation = config.get("allow_delegation", self._allow_delegation)
        self._verbose = config.get("verbose", self._verbose)
        self._memory = config.get("memory", self._memory)

        # Load custom templates if present
        self._system_template = config.get("system_template", self._system_template)
        self._prompt_template = config.get("prompt_template", self._prompt_template)
        self._response_template = config.get("response_template", self._response_template)

        return self

    def build(self) -> Agent:
        """
        Build and return the configured Agent.

        Returns:
            Configured CrewAI Agent

        Raises:
            ValueError: If required fields are missing
        """
        if not self._role:
            raise ValueError("Agent role is required")
        if not self._goal:
            raise ValueError("Agent goal is required")
        if not self._llm:
            raise ValueError("Agent LLM is required")

        logger.info("building_agent", role=self._role)

        # Build agent with custom templates if provided
        agent_params = {
            "role": self._role,
            "goal": self._goal,
            "backstory": self._backstory or "Expert in their field",
            "llm": self._llm,
            "allow_delegation": self._allow_delegation,
            "verbose": self._verbose,
            "memory": self._memory,
        }

        # Add custom templates only if they are set
        if self._system_template:
            agent_params["system_template"] = self._system_template
        if self._prompt_template:
            agent_params["prompt_template"] = self._prompt_template
        if self._response_template:
            agent_params["response_template"] = self._response_template

        agent = Agent(**agent_params)

        logger.info("agent_built", role=self._role, has_custom_templates=bool(self._prompt_template))
        return agent

    def reset(self) -> "AgentBuilder":
        """Reset builder to initial state."""
        self.__init__()
        return self
