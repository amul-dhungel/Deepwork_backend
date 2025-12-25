"""
Unified AI Service - Supports Claude and Ollama.
"""

from typing import Generator
from ..config import Config
from .ai_providers import ClaudeProvider, OllamaProvider


class AIService:
    """AI service supporting multiple providers."""
    
    def __init__(self, use_ollama: bool = False):
        """
        Initialize AI service.
        
        Args:
            use_ollama: If True, use Ollama instead of Claude
        """
        self.use_ollama = use_ollama
        
        if use_ollama:
            self.ollama = OllamaProvider(
                base_url="http://localhost:11434",
                model="deepseek-v3.1:671b-cloud"
            )
        else:
            self.claude = ClaudeProvider(
                Config.CLAUDE_API_KEY,
                Config.CLAUDE_API_URL,
                Config.CLAUDE_MODEL
            )
    
    def generate(self, prompt: str, provider: str = 'claude') -> str:
        """
        Generate AI response.
        
        Args:
            prompt: The input prompt
            provider: Provider to use ('claude' or 'ollama')
            
        Returns:
            Generated text
        """
        if self.use_ollama or provider == 'ollama':
            return self.ollama.generate(prompt)
        return self.claude.generate(prompt)
    
    def generate_stream(self, prompt: str, provider: str = 'claude', system_prompt: str = None) -> Generator[str, None, None]:
        """
        Generate streaming AI response.
        
        Args:
            prompt: The input prompt
            provider: Provider to use ('claude' or 'ollama')
            system_prompt: Optional system prompt
            
        Yields:
            Text chunks
        """
        if self.use_ollama or provider == 'ollama':
            return self.ollama.generate_stream(prompt, system_prompt)
        return self.claude.generate_stream(prompt, system_prompt)
    
    def check_status(self) -> str:
        """
        Check provider status.
        
        Returns:
            Status string: 'ok', 'error', 'not configured', etc.
        """
        if self.use_ollama:
            return self.ollama.check_status()
        return self.claude.check_status()


# Singleton instances
_ai_service = None
_ollama_service = None


def get_ai_service(use_ollama: bool = False) -> AIService:
    """
    Get or create AI service instance.
    
    Args:
        use_ollama: If True, return Ollama-based service
        
    Returns:
        AIService instance
    """
    global _ai_service, _ollama_service
    
    if use_ollama:
        if _ollama_service is None:
            _ollama_service = AIService(use_ollama=True)
        return _ollama_service
    else:
        if _ai_service is None:
            _ai_service = AIService(use_ollama=False)
        return _ai_service
