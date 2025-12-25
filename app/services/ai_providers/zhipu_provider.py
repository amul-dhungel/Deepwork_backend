"""
Zhipu AI Provider.
"""

import requests
import time
import hmac
import hashlib
import base64
import json
from .base_provider import BaseAIProvider


class ZhipuProvider(BaseAIProvider):
    """Zhipu AI provider with JWT token generation."""
    
    def __init__(self, api_key: str, api_url: str):
        super().__init__(api_key, api_url)
        self.model = "glm-4-flash"
    
    def _generate_token(self, exp_seconds: int = 600) -> str:
        """Generate JWT token for Zhipu API."""
        try:
            id, secret = self.api_key.split(".")
        except Exception:
            raise Exception("Invalid Zhipu API Key format.")
        
        payload = {
            "api_key": id,
            "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
            "timestamp": int(round(time.time() * 1000)),
        }
        
        headers_jwt = {
            "alg": "HS256",
            "sign_type": "SIGN"
        }
        
        def b64url(data):
            return base64.urlsafe_b64encode(data).rstrip(b'=')
        
        segments = []
        segments.append(b64url(json.dumps(headers_jwt).encode('utf-8')))
        segments.append(b64url(json.dumps(payload).encode('utf-8')))
        
        signing_input = b'.'.join(segments)
        signature = hmac.new(secret.encode('utf-8'), signing_input, hashlib.sha256).digest()
        
        segments.append(b64url(signature))
        return b'.'.join(segments).decode('utf-8')
    
    def generate(self, prompt: str) -> str:
        """Generate response from Zhipu API."""
        if not self.is_configured:
            raise Exception("Zhipu API Key not configured.")
        
        token = self._generate_token()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        
        try:
            print(f"Sending request to Zhipu...")
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
                raise Exception(f"Zhipu Error {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Network error communicating with Zhipu: {e}")
            raise Exception(f"Zhipu Network Error: {str(e)}")
    
    def check_status(self) -> str:
        """Check Zhipu API status."""
        if not self.is_configured:
            return "not configured"
        
        try:
            self.generate("Hi")
            return "ok"
        except Exception:
            return "error"
