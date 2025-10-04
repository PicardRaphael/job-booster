"""Text chunking service for different document types."""

from pathlib import Path
from typing import Any, Dict, List

import pymupdf4llm
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ChunkerService:
    """Service for chunking documents based on their type."""

    def __init__(self) -> None:
        """Initialize chunking service."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )

        # For Markdown files
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]
        )

    def chunk_pdf(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Chunk PDF file using pymupdf4llm for optimal LLM extraction."""
        logger.info("chunking_pdf", file=str(pdf_path))

        # Extract markdown from PDF
        md_text = pymupdf4llm.to_markdown(str(pdf_path))

        # Split into chunks
        chunks = self.text_splitter.split_text(md_text)

        documents = [
            {
                "text": chunk,
                "source": pdf_path.name,
                "type": "pdf",
                "chunk_index": i,
            }
            for i, chunk in enumerate(chunks)
        ]

        logger.info("pdf_chunked", file=str(pdf_path), chunks=len(documents))
        return documents

    def chunk_markdown(self, md_path: Path) -> List[Dict[str, Any]]:
        """Chunk Markdown file by headers and sections."""
        logger.info("chunking_markdown", file=str(md_path))

        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()

        # First split by headers
        header_splits = self.markdown_splitter.split_text(content)

        # Further split large sections
        chunks = []
        for doc in header_splits:
            if len(doc.page_content) > settings.chunk_size * 2:
                sub_chunks = self.text_splitter.split_text(doc.page_content)
                for sub_chunk in sub_chunks:
                    chunks.append(
                        {
                            "text": sub_chunk,
                            "metadata": doc.metadata,
                        }
                    )
            else:
                chunks.append(
                    {
                        "text": doc.page_content,
                        "metadata": doc.metadata,
                    }
                )

        documents = [
            {
                "text": chunk["text"],
                "source": md_path.name,
                "type": "markdown",
                "chunk_index": i,
                **chunk["metadata"],
            }
            for i, chunk in enumerate(chunks)
        ]

        logger.info("markdown_chunked", file=str(md_path), chunks=len(documents))
        return documents

    def chunk_text(self, text: str, source: str = "text_input") -> List[Dict[str, Any]]:
        """Chunk raw text input."""
        logger.info("chunking_text", source=source, length=len(text))

        chunks = self.text_splitter.split_text(text)

        documents = [
            {
                "text": chunk,
                "source": source,
                "type": "text",
                "chunk_index": i,
            }
            for i, chunk in enumerate(chunks)
        ]

        logger.info("text_chunked", source=source, chunks=len(documents))
        return documents


# Singleton instance
_chunker_service: ChunkerService | None = None


def get_chunker_service() -> ChunkerService:
    """Get or create the singleton chunker service."""
    global _chunker_service
    if _chunker_service is None:
        _chunker_service = ChunkerService()
    return _chunker_service
