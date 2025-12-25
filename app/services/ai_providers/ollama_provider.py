"""
Ollama AI Provider
"""
import requests
from typing import Generator
from .base_provider import BaseAIProvider


class OllamaProvider(BaseAIProvider):
    """Ollama local AI provider."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "deepseek-v3.1:671b-cloud"):
        """
        Initialize Ollama provider.
        
        Args:
            base_url: Ollama API base URL
            model: Model name to use
        """
        self.base_url = base_url
        self.model = model
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate response using Ollama.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result.get('response', '')
        except Exception as e:
            raise Exception(f"Ollama generation failed: {str(e)}")
    
    def generate_stream(self, prompt: str, system_prompt: str = None) -> Generator[str, None, None]:
        """
        Generate streaming response using Ollama.
        
        Args:
            prompt: Input prompt
            system_prompt: Optional system prompt
            
        Yields:
            Text chunks
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(url, json=payload, stream=True, timeout=120)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    import json
                    data = json.loads(line)
                    if 'response' in data:
                        yield data['response']
        except Exception as e:
            raise Exception(f"Ollama streaming failed: {str(e)}")
    
    def check_status(self) -> str:
        """
        Check Ollama status.
        
        Returns:
            Status string: 'ok', 'error', or 'not configured'
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return 'ok'
            return 'error'
        except:
            return 'not configured'
