"""
Job analysis domain entity.

Domain Layer - Clean Architecture
This entity represents structured analysis results from a job offer.
Core business object used for RAG retrieval and content generation.
"""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)  # Immutable value object (DDD pattern)
class JobAnalysis:
    """
    Job analysis domain entity.

    Represents the analyzed and structured information extracted from a job offer.
    This is the result of the Analyzer agent's work.

    Attributes:
        summary: Comprehensive summary of the job offer
        key_skills: List of required technical and soft skills
        position: Job title/position name
        company: Company name (optional)

    Raises:
        ValueError: If required fields are missing

    Example:
        >>> analysis = JobAnalysis(
        ...     summary="Senior Python Developer needed...",
        ...     key_skills=["Python", "FastAPI", "Docker"],
        ...     position="Senior Python Developer",
        ...     company="TechCorp"
        ... )
        >>> query = analysis.get_search_query()
        >>> print(query)
        Senior Python Developer Python FastAPI Docker TechCorp
    """

    summary: str  # Complete summary of job requirements
    key_skills: List[str]  # Technical and soft skills required
    position: str  # Job title/role
    company: str | None = None  # Company name (optional)

    def __post_init__(self) -> None:
        """
        Validate job analysis after initialization.

        Domain entities must always be in a valid state.
        This enforces business invariants.

        Raises:
            ValueError: If required fields are empty
        """
        # Business rule: Summary is mandatory
        if not self.summary:
            raise ValueError("Summary cannot be empty")

        # Business rule: Position is mandatory
        if not self.position:
            raise ValueError("Position cannot be empty")

    def get_search_query(self) -> str:
        """
        Generate optimized search query for RAG retrieval.

        Combines position, top skills, and company name into a query
        optimized for semantic search in the vector database.

        This is a DOMAIN SERVICE method - it encapsulates business logic
        for how to transform analysis into a search query.

        Returns:
            Space-separated string with position, top 5 skills, and company

        Example:
            >>> analysis = JobAnalysis(
            ...     summary="...",
            ...     key_skills=["Python", "React", "Docker", "AWS", "K8s", "Go"],
            ...     position="Full Stack Developer",
            ...     company="Acme Corp"
            ... )
            >>> analysis.get_search_query()
            "Full Stack Developer Python React Docker AWS K8s Acme Corp"
        """
        # Start with position (most important)
        parts = [self.position]

        # Add top 5 skills (limit to avoid query explosion)
        if self.key_skills:
            parts.extend(self.key_skills[:5])  # Top 5 skills only

        # Add company if available (helps personalization)
        if self.company:
            parts.append(self.company)

        # Join all parts into a single query string
        return " ".join(parts)
