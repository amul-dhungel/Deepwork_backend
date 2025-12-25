"""
Poster Ingestion Service for RAG System
Loads poster metadata JSON files and creates embeddings for retrieval.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class PosterIngestionService:
    """Service for ingesting poster metadata into vector store."""
    
    def __init__(self, data_dir: str = "data/posters"):
        self.data_dir = Path(data_dir)
        self.posters = []
        
    def load_posters(self) -> List[Dict[str, Any]]:
        """Load all poster JSON files from data directory."""
        logger.info(f"Loading posters from {self.data_dir}")
        
        if not self.data_dir.exists():
            logger.error(f"Poster directory not found: {self.data_dir}")
            return []
        
        poster_files = list(self.data_dir.glob("*.json"))
        logger.info(f"Found {len(poster_files)} poster files")
        
        posters = []
        for file_path in poster_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    poster_data = json.load(f)
                    poster_data['_id'] = file_path.stem  # Use filename as ID
                    poster_data['_file'] = str(file_path)
                    posters.append(poster_data)
            except Exception as e:
                logger.warning(f"Failed to load {file_path}: {e}")
                continue
        
        self.posters = posters
        logger.info(f"Successfully loaded {len(posters)} posters")
        return posters
    
    def create_poster_description(self, poster: Dict[str, Any]) -> str:
        """Create text description of poster for embedding."""
        sections = poster.get('section', {})
        
        # Extract section information
        section_count = len(sections)
        section_types = []
        section_positions = []
        
        for key, section in sections.items():
            category = section.get('category', 'unknown')
            section_types.append(category)
            
            xy = section.get('xy', [0, 0, 0, 0])
            section_positions.append(f"{category} at ({xy[0]}, {xy[1]}) size {xy[2]}x{xy[3]}")
        
        # Calculate overall dimensions
        if sections:
            max_x = max(s.get('xy', [0, 0, 0, 0])[0] + s.get('xy', [0, 0, 0, 0])[2] for s in sections.values())
            max_y = max(s.get('xy', [0, 0, 0, 0])[1] + s.get('xy', [0, 0, 0, 0])[3] for s in sections.values())
        else:
            max_x, max_y = 0, 0
        
        # Create description
        description = f"""Poster Layout Design
Total Sections: {section_count}
Section Types: {', '.join(set(section_types))}
Dimensions: {max_x} x {max_y}
Layout Structure:
{chr(10).join(section_positions)}

This poster contains {section_count} sections including {', '.join(set(section_types))}.
Suitable for academic presentations, research posters, and scientific conferences.
"""
        
        return description
    
    def prepare_documents(self) -> List[Dict[str, Any]]:
        """Prepare poster documents for vector store ingestion."""
        if not self.posters:
            self.load_posters()
        
        documents = []
        for poster in self.posters:
            doc = {
                'id': poster['_id'],
                'text': self.create_poster_description(poster),
                'metadata': {
                    'file': poster['_file'],
                    'section_count': len(poster.get('section', {})),
                    'sections': ','.join(poster.get('section', {}).keys()),  # Convert to string
                    'poster_data': json.dumps(poster)  # Store full poster JSON
                }
            }
            documents.append(doc)
        
        logger.info(f"Prepared {len(documents)} documents for ingestion")
        return documents

def ingest_posters_to_chroma(chroma_client, collection_name: str = "poster_layouts"):
    """Ingest all posters into ChromaDB collection."""
    from chromadb.utils import embedding_functions
    
    # Create or get collection
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    try:
        collection = chroma_client.get_collection(
            name=collection_name,
            embedding_function=embedding_function
        )
        logger.info(f"Using existing collection: {collection_name}")
    except:
        collection = chroma_client.create_collection(
            name=collection_name,
            embedding_function=embedding_function,
            metadata={"description": "Poster layout designs for RAG retrieval"}
        )
        logger.info(f"Created new collection: {collection_name}")
    
    # Load and prepare posters
    ingestion_service = PosterIngestionService()
    documents = ingestion_service.prepare_documents()
    
    if not documents:
        logger.error("No documents to ingest")
        return 0
    
    # Add to collection in batches
    batch_size = 100
    total_added = 0
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        
        ids = [doc['id'] for doc in batch]
        texts = [doc['text'] for doc in batch]
        metadatas = [doc['metadata'] for doc in batch]
        
        try:
            collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas
            )
            total_added += len(batch)
            logger.info(f"Added batch {i//batch_size + 1}: {len(batch)} posters")
        except Exception as e:
            logger.error(f"Failed to add batch: {e}")
            continue
    
    logger.info(f"Successfully ingested {total_added} posters into {collection_name}")
    return total_added
