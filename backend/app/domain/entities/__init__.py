"""Domain entities - Pure business objects."""

from app.domain.entities.job_analysis import JobAnalysis
from app.domain.entities.job_offer import JobOffer
from app.domain.entities.generated_content import GeneratedContent

__all__ = ["JobOffer", "JobAnalysis", "GeneratedContent"]
