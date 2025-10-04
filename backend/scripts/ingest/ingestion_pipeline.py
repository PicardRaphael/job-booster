"""Ingestion pipeline orchestrator."""

from pathlib import Path
from typing import Any, Dict, List

from app.core.config import settings
from app.core.logging import get_logger
from app.services.qdrant_service import get_qdrant_service
from scripts.ingest.markdown_processor import MarkdownProcessor
from scripts.ingest.pdf_processor import PDFProcessor

logger = get_logger(__name__)


class IngestionPipeline:
    """Orchestrate the ingestion of user documents."""

    def __init__(self, data_dir: Path | None = None) -> None:
        """
        Initialize ingestion pipeline.

        Args:
            data_dir: Directory containing user documents
        """
        self.data_dir = data_dir or Path(settings.data_dir)
        self.pdf_processor = PDFProcessor()
        self.markdown_processor = MarkdownProcessor()
        self.qdrant = get_qdrant_service()

    def validate_data_directory(self) -> None:
        """Validate that data directory exists."""
        if not self.data_dir.exists():
            logger.error("data_directory_not_found", path=str(self.data_dir))
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")

        logger.info("data_directory_validated", path=str(self.data_dir))

    def process_cv(self) -> List[Dict[str, Any]]:
        """Process CV PDF file."""
        cv_path = self.data_dir / "cv.pdf"
        return self.pdf_processor.process_file(cv_path)

    def process_linkedin(self) -> List[Dict[str, Any]]:
        """Process LinkedIn PDF file."""
        linkedin_path = self.data_dir / "linkedin.pdf"
        return self.pdf_processor.process_file(linkedin_path)

    def process_competences(self) -> List[Dict[str, Any]]:
        """Process competences Markdown file."""
        competences_path = self.data_dir / "dossier_competence.md"
        return self.markdown_processor.process_file(competences_path)

    def process_informations(self) -> List[Dict[str, Any]]:
        """Process informations Markdown file."""
        informations_path = self.data_dir / "informations.md"
        return self.markdown_processor.process_file(informations_path)

    def collect_all_documents(self) -> tuple[List[str], List[Dict[str, Any]]]:
        """
        Collect and process all documents.

        Returns:
            Tuple of (document texts, metadata list)
        """
        all_chunks: List[Dict[str, Any]] = []

        # Process all document types
        all_chunks.extend(self.process_cv())
        all_chunks.extend(self.process_linkedin())
        all_chunks.extend(self.process_competences())
        all_chunks.extend(self.process_informations())

        if not all_chunks:
            logger.warning("no_documents_found")
            return [], []

        # Separate texts and metadata
        documents = [chunk["text"] for chunk in all_chunks]
        metadatas = [{k: v for k, v in chunk.items() if k != "text"} for chunk in all_chunks]

        logger.info("documents_collected", total=len(documents))

        return documents, metadatas

    def ingest(self) -> None:
        """Run the complete ingestion pipeline."""
        logger.info("starting_ingestion_pipeline")

        # Validate directory
        self.validate_data_directory()

        # Ensure Qdrant collection exists (recreate to fix dimension mismatch)
        self.qdrant.ensure_collection(recreate=True)

        # Collect all documents
        documents, metadatas = self.collect_all_documents()

        if not documents:
            logger.warning("no_documents_to_ingest")
            return

        # Upsert to Qdrant
        logger.info("upserting_to_qdrant", count=len(documents))
        self.qdrant.upsert_documents(
            documents=documents,
            metadatas=metadatas,
        )

        logger.info("ingestion_completed", documents_ingested=len(documents))
