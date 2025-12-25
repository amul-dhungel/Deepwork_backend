"""
Script to ingest poster metadata into ChromaDB
Run this once to populate the vector database
"""

from app.rag.rag_service import NewspaperRAGService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Ingest all posters into ChromaDB"""
    logger.info("Starting poster ingestion...")
    
    rag_service = NewspaperRAGService()
    count = rag_service.ingest_posters()
    
    logger.info(f"✅ Ingestion complete! {count} posters added to vector database")
    logger.info("You can now use /api/poster/generate to create posters")

if __name__ == "__main__":
    main()
