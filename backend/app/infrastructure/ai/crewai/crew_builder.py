"""Crew Builder - Fluent interface for crew construction."""

from typing import List, Optional
from crewai import Agent, Task, Crew, Process

from app.core.logging import get_logger

logger = get_logger(__name__)


class CrewBuilder:
    """
    Builder for CrewAI Crew using Fluent Interface pattern.
    """

    def __init__(self) -> None:
        """Initialize builder with defaults."""
        self._agents: List[Agent] = []
        self._tasks: List[Task] = []
        self._process: Process = Process.sequential
        self._verbose: bool = True
        self._memory: Optional[bool] = None  # <── None = force disable fallback CrewMemory()

    def add_agent(self, agent: Agent) -> "CrewBuilder":
        self._agents.append(agent)
        return self

    def add_agents(self, agents: List[Agent]) -> "CrewBuilder":
        self._agents.extend(agents)
        return self

    def add_task(self, task: Task) -> "CrewBuilder":
        self._tasks.append(task)
        return self

    def add_tasks(self, tasks: List[Task]) -> "CrewBuilder":
        self._tasks.extend(tasks)
        return self

    def with_process(self, process: Process) -> "CrewBuilder":
        self._process = process
        return self

    def with_memory(self, enabled: bool = False) -> "CrewBuilder":
        """
        Enable/disable crew memory.
        Default: False (to prevent Chroma instantiation).
        """
        self._memory = enabled
        return self

    def with_verbose(self, enabled: bool = True) -> "CrewBuilder":
        self._verbose = enabled
        return self

    def build(self) -> Crew:
        """
        Build and return the configured Crew.
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
            memory_enabled=bool(self._memory),
        )

        crew = Crew(
            agents=self._agents,
            tasks=self._tasks,
            process=self._process,
            verbose=self._verbose,
            memory=self._memory if self._memory else False,  # <── force disable memory
        )

        logger.info("crew_built", memory_enabled=self._memory)
        return crew

    def reset(self) -> "CrewBuilder":
        self.__init__()
        return self
