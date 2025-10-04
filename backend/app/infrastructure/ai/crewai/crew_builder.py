"""Crew Builder - Fluent interface for crew construction."""

from typing import List
from crewai import Agent, Task, Crew, Process

from app.core.logging import get_logger

logger = get_logger(__name__)


class CrewBuilder:
    """
    Builder for CrewAI Crew using Fluent Interface pattern.

    Example:
        crew = (CrewBuilder()
            .add_agent(analyzer)
            .add_task(analyze_task)
            .with_process(Process.sequential)
            .build())
    """

    def __init__(self) -> None:
        """Initialize builder with defaults."""
        self._agents: List[Agent] = []
        self._tasks: List[Task] = []
        self._process: Process = Process.sequential
        self._verbose: bool = True
        self._memory: bool = True

    def add_agent(self, agent: Agent) -> "CrewBuilder":
        """Add an agent to the crew."""
        self._agents.append(agent)
        return self

    def add_agents(self, agents: List[Agent]) -> "CrewBuilder":
        """Add multiple agents to the crew."""
        self._agents.extend(agents)
        return self

    def add_task(self, task: Task) -> "CrewBuilder":
        """Add a task to the crew."""
        self._tasks.append(task)
        return self

    def add_tasks(self, tasks: List[Task]) -> "CrewBuilder":
        """Add multiple tasks to the crew."""
        self._tasks.extend(tasks)
        return self

    def with_process(self, process: Process) -> "CrewBuilder":
        """Set crew process type."""
        self._process = process
        return self

    def with_memory(self, enabled: bool = True) -> "CrewBuilder":
        """Enable/disable crew memory."""
        self._memory = enabled
        return self

    def with_verbose(self, enabled: bool = True) -> "CrewBuilder":
        """Enable/disable verbose mode."""
        self._verbose = enabled
        return self

    def build(self) -> Crew:
        """
        Build and return the configured Crew.

        Returns:
            Configured CrewAI Crew

        Raises:
            ValueError: If no agents or tasks are added
        """
        if not self._agents:
            raise ValueError("Crew must have at least one agent")
        if not self._tasks:
            raise ValueError("Crew must have at least one task")

        logger.info(
            "building_crew",
            agents=len(self._agents),
            tasks=len(self._tasks),
            process=self._process.value,
        )

        crew = Crew(
            agents=self._agents,
            tasks=self._tasks,
            process=self._process,
            verbose=self._verbose,
            memory=self._memory,
        )

        logger.info("crew_built")
        return crew

    def reset(self) -> "CrewBuilder":
        """Reset builder to initial state."""
        self.__init__()
        return self
