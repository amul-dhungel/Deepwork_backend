"""
Abstract base class for AI providers.
"""

from abc import ABC, abstractmethod
from typing import Generator, Optional


class BaseAIProvider(ABC):
    """Base class for all AI providers."""
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """Initialize the provider with API credentials."""
        self.api_key = api_key
        self.api_url = api_url
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a response from the AI provider.
        
        Args:
            prompt: The input prompt
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If generation fails
        """
        pass
    
    def generate_stream(self, prompt: str) -> Generator[str, None, None]:
        """
        Generate a streaming response (optional, not all providers support it).
        
        Args:
            prompt: The input prompt
            
        Yields:
            Text chunks as they're generated
        """
        # Default implementation: yield full response at once
        result = self.generate(prompt)
        yield result
    
    @abstractmethod
    def check_status(self) -> str:
        """
        Check if the provider is available and configured.
        
        Returns:
            Status string: 'ok', 'error', 'not configured', etc.
        """
        pass
    
    @property
    def is_configured(self) -> bool:
        """Check if provider has necessary configuration."""
        return self.api_key is not None and self.api_key != ""
