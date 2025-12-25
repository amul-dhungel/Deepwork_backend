"""
Vector Store Service - ChromaDB Integration
Handles all vector database operations for newspaper search
"""
import chromadb
from sentence_transformers import SentenceTransformer
import json
import os
from typing import List, Dict, Optional


class NewspaperVectorStore:
    """Manages ChromaDB vector database for newspaper embeddings"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize ChromaDB and embedding model
        
        Args:
            persist_directory: Directory to store ChromaDB data
        """
        self.persist_directory = persist_directory
        self.model_name = 'all-MiniLM-L6-v2'
        
        # Initialize embedding model
        print(f"📦 Loading embedding model: {self.model_name}...")
        self.model = SentenceTransformer(self.model_name)
        print("✅ Embedding model loaded")
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection("newspapers")
            print(f"✅ Loaded existing collection with {self.collection.count()} newspapers")
        except:
            self.collection = self.client.create_collection(
                name="newspapers",
                metadata={"hnsw:space": "cosine"}
            )
            print("✅ Created new newspapers collection")
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Convert text to embedding vector
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding
        """
        return self.model.encode(text).tolist()
    
    def add_newspaper(self, newspaper_json: dict, newspaper_id: str) -> None:
        """
        Add a single newspaper to the vector database
        
        Args:
            newspaper_json: Full newspaper JSON data
            newspaper_id: Unique identifier for the newspaper
        """
        # Create searchable text
        text = self._create_searchable_text(newspaper_json)
        
        # Create embedding
        embedding = self.create_embedding(text)
        
        # Extract metadata
        metadata = self._extract_metadata(newspaper_json)
        
        # Store in ChromaDB
        self.collection.add(
            ids=[newspaper_id],
            embeddings=[embedding],
            documents=[json.dumps(newspaper_json)],
            metadatas=[metadata]
        )
        
        print(f"✅ Added: {metadata['title']} - {metadata['date']}")
    
    def search(self, query: str, n_results: int = 5, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Search for newspapers using semantic search
        
        Args:
            query: Search query
            n_results: Number of results to return
            filters: Optional metadata filters (e.g., {"state": "Arizona"})
            
        Returns:
            List of newspaper results with metadata and similarity scores
        """
        # Convert query to embedding
        query_embedding = self.create_embedding(query)
        
        # Build search parameters
        search_params = {
            "query_embeddings": [query_embedding],
            "n_results": n_results
        }
        
        # Add filters if provided
        if filters:
            search_params["where"] = filters
        
        # Search ChromaDB
        results = self.collection.query(**search_params)
        
        # Parse and format results
        newspapers = []
        for i in range(len(results['ids'][0])):
            newspaper_json = json.loads(results['documents'][0][i])
            newspapers.append({
                "id": results['ids'][0][i],
                "json": newspaper_json,
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i],
                "similarity": 1 - results['distances'][0][i]
            })
        
        return newspapers
    
    def get_count(self) -> int:
        """Get total number of newspapers in database"""
        return self.collection.count()
    
    def delete_all(self) -> None:
        """Delete all newspapers from the collection"""
        self.client.delete_collection("newspapers")
        self.collection = self.client.create_collection(
            name="newspapers",
            metadata={"hnsw:space": "cosine"}
        )
        print("✅ Deleted all newspapers")
    
    def _create_searchable_text(self, newspaper_json: dict) -> str:
        """
        Create searchable text from newspaper JSON
        
        Args:
            newspaper_json: Full newspaper JSON
            
        Returns:
            Concatenated searchable text
        """
        parts = []
        
        # Add title and metadata
        lccn = newspaper_json.get('lccn', {})
        parts.append(f"Title: {lccn.get('title', '')}")
        parts.append(f"State: {lccn.get('state', '')}")
        
        # Add date
        edition = newspaper_json.get('edition', {})
        parts.append(f"Date: {edition.get('date', '')}")
        
        # Add all headlines
        articles = newspaper_json.get('full articles', [])
        headlines = [a.get('headline', '') for a in articles if a.get('headline')]
        if headlines:
            parts.append(f"Headlines: {' '.join(headlines)}")
        
        # Add article snippets (first 200 chars of each)
        article_snippets = [a.get('article', '')[:200] for a in articles if a.get('article')]
        if article_snippets:
            parts.append(f"Content: {' '.join(article_snippets)}")
        
        return ' '.join(parts)
    
    def _extract_metadata(self, newspaper_json: dict) -> Dict:
        """
        Extract metadata from newspaper JSON
        
        Args:
            newspaper_json: Full newspaper JSON
            
        Returns:
            Dictionary of metadata
        """
        return {
            "title": newspaper_json.get('lccn', {}).get('title', 'Unknown'),
            "state": newspaper_json.get('lccn', {}).get('state', 'Unknown'),
            "date": newspaper_json.get('edition', {}).get('date', 'Unknown'),
            "page": str(newspaper_json.get('page_number', 1)),
            "article_count": len(newspaper_json.get('full articles', []))
        }
