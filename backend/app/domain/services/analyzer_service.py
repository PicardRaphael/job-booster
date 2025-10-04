"""Analyzer service interface."""

from abc import ABC, abstractmethod
from app.domain.entities.job_offer import JobOffer
from app.domain.entities.job_analysis import JobAnalysis


class IAnalyzerService(ABC):
    """Interface for job offer analysis service."""

    @abstractmethod
    def analyze(self, job_offer: JobOffer) -> JobAnalysis:
        """
        Analyze job offer and extract structured information.

        Args:
            job_offer: Job offer to analyze

        Returns:
            Structured job analysis
        """
        pass
