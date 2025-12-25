"""
OpenAI GPT Provider.
"""

import requests
from .base_provider import BaseAIProvider


class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT provider."""
    
    def __init__(self, api_key: str, api_url: str):
        super().__init__(api_key, api_url)
        self.model = "gpt-4o-mini"
    
    def generate(self, prompt: str) -> str:
        """Generate response from OpenAI API."""
        if not self.is_configured:
            raise Exception("OpenAI API Key not configured.")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        try:
            print(f"Sending request to OpenAI ({self.model})...")
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                raise Exception(f"OpenAI Error {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Network error communicating with OpenAI: {e}")
            raise Exception(f"OpenAI Network Error: {str(e)}")
    
    def check_status(self) -> str:
        """Check OpenAI API status."""
        if not self.is_configured:
            return "not configured"
        
        try:
            self.generate("Hi")
            return "ok"
        except Exception:
            return "error"
