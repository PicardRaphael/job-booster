"""Markdown document processor."""

from pathlib import Path
from typing import Any, Dict, List

from app.core.logging import get_logger
from app.services.chunker import get_chunker_service

logger = get_logger(__name__)


class MarkdownProcessor:
    """Process Markdown documents and extract chunks."""

    def __init__(self) -> None:
        """Initialize Markdown processor."""
        self.chunker = get_chunker_service()

    def process_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Process a single Markdown file.

        Args:
            file_path: Path to Markdown file

        Returns:
            List of document chunks with metadata
        """
        if not file_path.exists():
            logger.warning("markdown_not_found", path=str(file_path))
            return []

        logger.info("processing_markdown", file=file_path.name)

        try:
            chunks = self.chunker.chunk_markdown(file_path)
            logger.info("markdown_processed", file=file_path.name, chunks=len(chunks))
            return chunks
        except Exception as e:
            logger.error("markdown_processing_failed", file=file_path.name, error=str(e))
            return []
