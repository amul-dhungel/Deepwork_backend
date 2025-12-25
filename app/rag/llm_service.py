"""
LLM Service for RAG
Handles LLM interactions for newspaper analysis and recommendations
"""
from typing import Dict, List


class NewspaperLLMService:
    """Manages LLM operations for newspaper search and analysis"""
    
    def __init__(self):
        """Initialize AI service with Ollama"""
        from app.services import get_ai_service
        self.ai_service = get_ai_service(use_ollama=True)
    
    def generate_search_summary(self, query: str, newspapers: List[Dict]) -> str:
        """
        Generate LLM summary of search results
        
        Args:
            query: User's search query
            newspapers: List of newspaper results from vector search
            
        Returns:
            LLM-generated summary
        """
        # Create context from newspapers
        context = self._format_newspapers_for_context(newspapers)
        
        # Create prompt
        prompt = f"""You are a helpful assistant that helps users find historical newspapers.

User Query: "{query}"

{context}

Based on the newspapers above, provide a helpful summary that:
1. Explains which newspapers match the query and why
2. Highlights the most relevant articles
3. Suggests which newspaper the user should explore

Keep your response concise and helpful (2-3 sentences)."""
        
        # Get LLM response
        return self.ai_service.generate(prompt)
    
    def recommend_best_newspaper(self, intent: str, newspapers: List[Dict]) -> Dict:
        """
        Use LLM to recommend the best newspaper
        
        Args:
            intent: User's intent/description
            newspapers: List of newspaper candidates
            
        Returns:
            Dictionary with recommended newspaper and explanation
        """
        # Create detailed context
        context = "Available newspapers:\n\n"
        for i, result in enumerate(newspapers, 1):
            meta = result['metadata']
            articles = result['json'].get('full articles', [])
            
            context += f"{i}. {meta['title']} - {meta['date']}\n"
            headlines = [a.get('headline', 'Untitled')[:50] for a in articles[:5]]
            context += f"   Articles: {', '.join(headlines)}\n\n"
        
        # Create prompt
        prompt = f"""You are an expert at analyzing historical newspapers.

User wants: "{intent}"

{context}

Which newspaper is the BEST match? Respond with:
1. The number of the newspaper (1-{len(newspapers)})
2. A brief explanation of why it's the best match

Format: 
NUMBER: [number]
REASON: [explanation]"""
        
        llm_response = self.ai_service.generate(prompt)
        
        # Parse LLM response
        try:
            number_line = [line for line in llm_response.split('\n') if 'NUMBER:' in line][0]
            recommended_index = int(number_line.split(':')[1].strip()) - 1
            recommended_newspaper = newspapers[recommended_index]
        except:
            # Fallback to first result
            recommended_newspaper = newspapers[0]
        
        return {
            "newspaper": recommended_newspaper,
            "explanation": llm_response
        }
    
    def summarize_newspaper(self, newspaper_json: Dict) -> str:
        """
        Generate LLM summary of a newspaper
        
        Args:
            newspaper_json: Full newspaper JSON
            
        Returns:
            LLM-generated summary
        """
        # Extract key information
        title = newspaper_json.get('lccn', {}).get('title', 'Unknown')
        date = newspaper_json.get('edition', {}).get('date', 'Unknown')
        articles = newspaper_json.get('full articles', [])
        
        # Create context
        context = f"Newspaper: {title}\nDate: {date}\n\nArticles:\n"
        for i, article in enumerate(articles, 1):
            headline = article.get('headline', 'Untitled')
            text = article.get('article', '')[:300]
            context += f"\n{i}. {headline}\n{text}...\n"
        
        # Create prompt
        prompt = f"""Summarize this historical newspaper in 2-3 sentences:

{context}

Focus on the main topics and themes covered."""
        
        return self.ai_service.generate(prompt)
    
    def answer_question(self, newspaper_json: Dict, question: str) -> str:
        """
        Answer a question about a specific newspaper
        
        Args:
            newspaper_json: Full newspaper JSON
            question: User's question
            
        Returns:
            LLM answer
        """
        # Create context
        title = newspaper_json.get('lccn', {}).get('title', 'Unknown')
        date = newspaper_json.get('edition', {}).get('date', 'Unknown')
        articles = newspaper_json.get('full articles', [])
        
        context = f"Newspaper: {title} ({date})\n\nArticles:\n"
        for article in articles:
            headline = article.get('headline', 'Untitled')
            text = article.get('article', '')
            context += f"\nHeadline: {headline}\nContent: {text}\n"
        
        # Create prompt
        prompt = f"""You are analyzing a historical newspaper.

{context}

User Question: "{question}"

Answer the question based on the newspaper content above. Be specific and cite which articles you're referencing."""
        
        return self.ai_service.generate(prompt)
    
    def _format_newspapers_for_context(self, newspapers: List[Dict]) -> str:
        """Format newspapers for LLM context"""
        context = "Here are the most relevant newspapers:\n\n"
        for i, result in enumerate(newspapers, 1):
            metadata = result['metadata']
            articles = result['json'].get('full articles', [])
            
            context += f"{i}. {metadata['title']} ({metadata['date']})\n"
            context += f"   State: {metadata['state']}, Page: {metadata['page']}\n"
            context += f"   Articles ({len(articles)}):\n"
            
            for article in articles[:3]:  # First 3 articles
                headline = article.get('headline', 'Untitled')
                if headline:
                    context += f"   - {headline}\n"
            
            context += "\n"
        
        return context
