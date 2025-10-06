"""Text chunking service for different document types (corrected version)."""

import re
from pathlib import Path
from typing import Any, Dict, List

import pymupdf4llm
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ChunkerService:
    """Service for chunking documents based on their type (Markdown-aware)."""

    def __init__(self) -> None:
        """Initialize chunking service."""
        # Text splitter for fallback or large blocks
        self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["##", "###", "\n\n", "\n", ".", "!", "?"]
        )


        # Markdown structure splitter
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
                ("####", "Header 4"),
            ]
        )

    # ----------------------------------------------------------------------
    # PDF CHUNKING
    # ----------------------------------------------------------------------
    def chunk_pdf(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Chunk PDF file using pymupdf4llm for optimal LLM extraction."""
        logger.info("chunking_pdf", file=str(pdf_path))

        md_text = pymupdf4llm.to_markdown(str(pdf_path))
        chunks = self.text_splitter.split_text(md_text)

        documents = [
            {
                "text": chunk.strip(),
                "source": pdf_path.name,
                "type": "profile",
                "chunk_index": i,
            }
            for i, chunk in enumerate(chunks)
        ]

        logger.info("pdf_chunked", file=str(pdf_path), chunks=len(documents))
        return documents

    # ----------------------------------------------------------------------
    # MARKDOWN CHUNKING
    # ----------------------------------------------------------------------
    def chunk_markdown(self, md_path: Path) -> List[Dict[str, Any]]:
        """
        Chunk Markdown file by headers and sections, preserving hierarchy.

        STRATÉGIE OPTIMISÉE:
        1. Parse TOUTES les sections markdown par headers
        2. Marque les sections [RULESET: XXX] avec metadata spécial
        3. Garde tout le reste du contenu normalement
        """
        logger.info("chunking_markdown", file=str(md_path))

        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Chunking intelligent qui détecte et marque les RULESETS
        return self._chunk_markdown_with_ruleset_detection(content, md_path)

    def _chunk_markdown_with_ruleset_detection(self, content: str, md_path: Path) -> List[Dict[str, Any]]:
        """
        Chunke TOUT le markdown par headers ET détecte les sections RULESET.

        Stratégie:
        1. Parse toutes les sections par headers (## ou ###)
        2. Détecte si une section contient [RULESET: XXX]
        3. Marque avec metadata approprié (type + ruleset_type)
        4. Garde TOUT le contenu
        """
        import re

        # Split by Markdown headers (récupère TOUTES les sections)
        header_splits = self.markdown_splitter.split_text(content)
        documents: List[Dict[str, Any]] = []
        ruleset_count = 0

        for doc in header_splits:
            text_content = doc.page_content.strip()

            # Détecte si cette section est un RULESET
            # Cherche dans le contenu ET dans les metadata (car le header peut être séparé)
            ruleset_match = re.search(r'\[RULESET:\s*([^\]]+)\]', text_content)

            # Si pas trouvé dans le contenu, cherche dans les metadata headers
            if not ruleset_match:
                for header_value in doc.metadata.values():
                    if isinstance(header_value, str):
                        ruleset_match = re.search(r'\[RULESET:\s*([^\]]+)\]', header_value)
                        if ruleset_match:
                            break

            if ruleset_match:
                # C'est une section RULESET
                ruleset_name = ruleset_match.group(1).strip().lower()

                # Garde la section COMPLÈTE (jamais divisée)
                documents.append({
                    "text": text_content,
                    "source": md_path.name,
                    "type": "ruleset",
                    "ruleset_type": ruleset_name,  # "global", "letter", "email", etc.
                    "chunk_index": len(documents),
                    **doc.metadata,
                })
                ruleset_count += 1
                logger.debug("ruleset_chunk_detected", ruleset=ruleset_name, length=len(text_content))
            else:
                # Section normale (pas RULESET)
                # Si trop long, on subdivise
                if len(text_content) > settings.chunk_size * 2:
                    sub_chunks = self.text_splitter.split_text(text_content)

                    # Préserver les headers du parent
                    parent_headers = " > ".join([f"{k}: {v}" for k, v in doc.metadata.items()])

                    for sub_chunk in sub_chunks:
                        documents.append({
                            "text": f"{parent_headers}\n\n{sub_chunk.strip()}" if parent_headers else sub_chunk.strip(),
                            "source": md_path.name,
                            "type": "profile",
                            "chunk_index": len(documents),
                            **doc.metadata,
                        })
                else:
                    # Section normale de taille OK
                    documents.append({
                        "text": text_content,
                        "source": md_path.name,
                        "type": "profile",
                        "chunk_index": len(documents),
                        **doc.metadata,
                    })

        logger.info("markdown_chunked_with_ruleset_detection",
                   file=str(md_path),
                   total_chunks=len(documents),
                   rulesets_found=ruleset_count)

        return documents

    # ----------------------------------------------------------------------
    # RAW TEXT CHUNKING
    # ----------------------------------------------------------------------
    def chunk_text(self, text: str, source: str = "text_input") -> List[Dict[str, Any]]:
        """Chunk raw text input."""
        logger.info("chunking_text", source=source, length=len(text))
        clean_text = re.sub(r'\s+', ' ', text).strip()

        chunks = self.text_splitter.split_text(clean_text)
        documents = [
            {
                "text": chunk.strip(),
                "source": source,
                "type": "profile",
                "chunk_index": i,
            }
            for i, chunk in enumerate(chunks)
        ]

        logger.info("text_chunked", source=source, chunks=len(documents))
        return documents


# ----------------------------------------------------------------------
# SINGLETON ACCESS
# ----------------------------------------------------------------------
_chunker_service: ChunkerService | None = None


def get_chunker_service() -> ChunkerService:
    """Get or create the singleton chunker service."""
    global _chunker_service
    if _chunker_service is None:
        _chunker_service = ChunkerService()
    return _chunker_service
