"""
Main RAG Service
Combines vector search and LLM for intelligent newspaper search
"""
import os
import json
from typing import List, Dict, Optional
from .vector_store import NewspaperVectorStore
from .llm_service import NewspaperLLMService


class NewspaperRAGService:
    """
    Main RAG service that combines ChromaDB vector search with LLM intelligence
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize RAG service
        
        Args:
            persist_directory: Directory for ChromaDB storage
        """
        self.vector_store = NewspaperVectorStore(persist_directory)
        self.llm_service = NewspaperLLMService()
    
    def search_with_llm(self, query: str, n_results: int = 5, filters: Optional[Dict] = None) -> Dict:
        """
        Search newspapers and generate LLM summary
        
        Args:
            query: User's search query
            n_results: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            Dictionary with newspapers and LLM summary
        """
        # Step 1: Vector search
        newspapers = self.vector_store.search(query, n_results, filters)
        
        # Step 2: Generate LLM summary
        llm_summary = self.llm_service.generate_search_summary(query, newspapers)
        
        return {
            "query": query,
            "newspapers": newspapers,
            "llm_summary": llm_summary,
            "count": len(newspapers)
        }
    
    def recommend_newspaper(self, intent: str, n_candidates: int = 10) -> Dict:
        """
        Get LLM recommendation for best newspaper
        
        Args:
            intent: User's intent/description
            n_candidates: Number of candidates to consider
            
        Returns:
            Dictionary with recommended newspaper and explanation
        """
        # Step 1: Get candidates from vector search
        newspapers = self.vector_store.search(intent, n_candidates)
        
        # Step 2: Get LLM recommendation
        recommendation = self.llm_service.recommend_best_newspaper(intent, newspapers)
        
        return {
            **recommendation,
            "all_options": newspapers
        }
    
    def summarize_newspaper(self, newspaper_json: Dict) -> str:
        """
        Generate LLM summary of a newspaper
        
        Args:
            newspaper_json: Full newspaper JSON
            
        Returns:
            LLM-generated summary
        """
        return self.llm_service.summarize_newspaper(newspaper_json)
    
    def answer_question(self, newspaper_json: Dict, question: str) -> str:
        """
        Answer a question about a specific newspaper
        
        Args:
            newspaper_json: Full newspaper JSON
            question: User's question
            
        Returns:
            LLM answer
        """
        return self.llm_service.answer_question(newspaper_json, question)
    
    def ingest_newspaper(self, newspaper_json: Dict, newspaper_id: str) -> None:
        """
        Add a single newspaper to the vector database
        
        Args:
            newspaper_json: Full newspaper JSON
            newspaper_id: Unique identifier
        """
        self.vector_store.add_newspaper(newspaper_json, newspaper_id)
    
    def ingest_from_directory(self, directory: str = "./mock_responses") -> int:
        """
        Ingest all newspaper JSONs from a directory
        
        Args:
            directory: Directory containing newspaper JSON files
            
        Returns:
            Number of newspapers ingested
        """
        count = 0
        for filename in os.listdir(directory):
            if filename.endswith('.json'):  # Accept all JSON files
                filepath = os.path.join(directory, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        newspaper_json = json.load(f)
                    
                    newspaper_id = filename.replace('.json', '')
                    self.ingest_newspaper(newspaper_json, newspaper_id)
                    count += 1
                except Exception as e:
                    print(f"âŒ Error ingesting {filename}: {e}")
        
        print(f"\nâœ… Total newspapers ingested: {count}")
        return count
    
    def get_status(self) -> Dict:
        """
        Get RAG system status
        
        Returns:
            Dictionary with system status
        """
        return {
            "status": "ready",
            "newspaper_count": self.vector_store.get_count(),
            "embedding_model": self.vector_store.model_name,
            "llm": "Connected"
        }
    
    def clear_database(self) -> None:
        """Delete all newspapers from the database"""
        self.vector_store.delete_all()
    
    # ===== POSTER METHODS =====
    
    def ingest_posters(self) -> int:
        """
        Ingest all poster metadata files into ChromaDB
        
        Returns:
            Number of posters ingested
        """
        from ..services.poster_ingestion import ingest_posters_to_chroma
        import chromadb
        
        # Use same ChromaDB client
        client = chromadb.PersistentClient(path=self.vector_store.persist_directory)
        count = ingest_posters_to_chroma(client, collection_name="poster_layouts")
        return count
    
    def search_posters(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Search for similar poster layouts
        
        Args:
            query: User's poster description
            n_results: Number of results to return
            
        Returns:
            List of matching poster layouts
        """
        import chromadb
        from chromadb.utils import embedding_functions
        
        client = chromadb.PersistentClient(path=self.vector_store.persist_directory)
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        try:
            collection = client.get_collection(
                name="poster_layouts",
                embedding_function=embedding_function
            )
        except:
            return []
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        posters = []
        if results and results['documents']:
            for i in range(len(results['ids'][0])):
                poster_data_str = results['metadatas'][0][i].get('poster_data', '{}')
                poster_data = json.loads(poster_data_str)
                posters.append({
                    'id': results['ids'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else 0,
                    'poster_json': poster_data
                })
        
        return posters
    
    def generate_poster_layout(self, query: str, theme: str = "blue", return_suggestions: bool = False) -> Dict:
        """
        Generate a poster layout based on user query
        
        Args:
            query: User's poster description
            theme: Color theme for the poster
            
        Returns:
            Dictionary with poster JSON and theme
        """
        # Search for similar posters
        similar_posters = self.search_posters(query, n_results=4 if return_suggestions else 3)
        
        if not similar_posters:
            # Return default poster if no matches
            default_result = {
                "poster_json": self._get_default_poster(),
                "theme": theme,
                "source": "default"
            }
            if return_suggestions:
                return {"suggestions": [default_result]}
            return default_result
        
        if return_suggestions:
            # Return 4 suggestions with different themes
            themes = ['blue', 'green', 'purple', 'orange']
            suggestions = []
            for i, poster in enumerate(similar_posters[:4]):
                suggestions.append({
                    "id": f"poster_{i}",
                    "poster_json": poster['poster_json'],
                    "theme": themes[i],
                    "source": "rag",
                    "similarity_score": 1 - poster['distance'],
                    "matched_id": poster['id']
                })
            return {"suggestions": suggestions}
        
        # Use the best match (lowest distance)
        best_match = similar_posters[0]
        
        return {
            "poster_json": best_match['poster_json'],
            "theme": theme,
            "source": "rag",
            "similarity_score": 1 - best_match['distance'],
            "matched_id": best_match['id']
        }
    
    def _get_default_poster(self) -> Dict:
        """Get default poster template"""
        return {
            "section": {
                "0": {
                    "category": "title",
                    "title": "Your Poster Title",
                    "xy": [0, 0, 900, 80]
                },
                "1": {
                    "category": "introduction",
                    "title": "Introduction section content",
                    "xy": [10, 100, 280, 200]
                },
                "2": {
                    "category": "methods",
                    "title": "Methods section content",
                    "xy": [310, 100, 280, 200]
                },
                "3": {
                    "category": "results",
                    "title": "Results section content",
                    "xy": [610, 100, 280, 200]
                }
            }
        }

    
    def generate_custom_poster_layout(self, query: str, theme: str = "blue") -> Dict:
        """Generate custom poster using RAG + LLM hybrid"""
        from ..services.poster_llm_service import PosterLLMService
        similar_posters = self.search_posters(query, n_results=2)
        llm_service = PosterLLMService()
        custom_poster = llm_service.generate_custom_layout(query, similar_posters)
        return {
            "poster_json": custom_poster,
            "theme": theme,
            "source": "llm_generated",
            "reference_count": len(similar_posters)
        }
