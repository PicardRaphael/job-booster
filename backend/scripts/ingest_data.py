"""Script to ingest user data into Qdrant."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.logging import get_logger, setup_logging
from scripts.ingest.ingestion_pipeline import IngestionPipeline

setup_logging(debug=True)
logger = get_logger(__name__)


def main() -> None:
    """Run the ingestion pipeline."""
    try:
        pipeline = IngestionPipeline()
        pipeline.ingest()
        logger.info("ingestion_script_completed_successfully")
    except Exception as e:
        logger.error("ingestion_script_failed", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
