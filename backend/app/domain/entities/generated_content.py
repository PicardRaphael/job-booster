"""Generated content domain entity."""

from dataclasses import dataclass
from enum import Enum
from typing import List


class ContentType(str, Enum):
    """Type of generated content."""
    EMAIL = "email"
    LINKEDIN = "linkedin"
    LETTER = "letter"


@dataclass
class SourceDocument:
    """Source document from RAG."""
    id: str
    text: str
    score: float
    source: str


@dataclass(frozen=True)
class GeneratedContent:
    """
    Generated content domain entity.

    Represents the final generated application content.
    """

    content: str
    content_type: ContentType
    sources: List[SourceDocument]

    def __post_init__(self) -> None:
        """Validate generated content."""
        if not self.content:
            raise ValueError("Content cannot be empty")

    def get_preview(self, length: int = 200) -> str:
        """Get preview of content."""
        if len(self.content) <= length:
            return self.content
        return self.content[:length] + "..."
