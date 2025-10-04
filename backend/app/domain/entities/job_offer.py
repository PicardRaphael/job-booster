"""
Job offer domain entity.

Domain Layer - Clean Architecture
This entity represents a job offer in the business domain.
It contains only business logic, no infrastructure concerns.
"""

from dataclasses import dataclass


@dataclass(frozen=True)  # Immutable value object (DDD pattern)
class JobOffer:
    """
    Job offer domain entity.

    Represents a job offer in the domain model.
    This is a VALUE OBJECT (immutable) following DDD principles.

    Attributes:
        text: The complete job offer text from the user

    Raises:
        ValueError: If job offer text is too short (< 50 characters)

    Example:
        >>> job_offer = JobOffer(text="Nous recherchons un dev Python...")
        >>> print(job_offer)
        Nous recherchons un dev Python...
    """

    text: str  # Job offer content (minimum 50 characters)

    def __post_init__(self) -> None:
        """
        Validate job offer after initialization.

        This enforces business rules at the domain level.
        Domain entities should always be in a valid state.

        Raises:
            ValueError: If text is empty or too short
        """
        # Business rule: Job offer must be substantial (minimum 50 chars)
        if not self.text or len(self.text) < 50:
            raise ValueError("Job offer text must be at least 50 characters")

    def __str__(self) -> str:
        """
        String representation of job offer.

        Returns:
            First 100 characters of the job offer text
        """
        # Return preview of job offer (first 100 chars)
        return self.text[:100] + "..." if len(self.text) > 100 else self.text
