"""
Configuration management for WordAssistantAI backend.
Loads all environment variables and API keys.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration from environment variables."""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '8000'))
    
    # Folders
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    IMAGE_CACHE_FOLDER = os.path.join(os.getcwd(), 'image_cache')
    
    # AI Provider API Keys
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GROK_API_KEY = os.getenv('GROK_API_KEY')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    LLAMA_API_KEY = os.getenv('LLAMA_API_KEY', '')
    ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
    MANUS_API_KEY = os.getenv('MANUS_API_KEY')
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    STABILITY_API_KEY = os.getenv('STABILITY_API_KEY')
    
    # API Endpoints
    GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent'
    OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'
    GROK_API_URL = 'https://api.x.ai/v1/chat/completions'
    DEEPSEEK_API_URL = 'https://api.deepseek.com/chat/completions'
    LLAMA_API_URL = 'https://api.groq.com/openai/v1/chat/completions'
    MANUS_API_URL = 'https://api.manus.ai/v1/tasks'
    OLLAMA_API_URL = 'http://localhost:11434/api/chat'
    ZHIPU_API_URL = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
    CLAUDE_API_URL = 'https://api.anthropic.com/v1/messages'
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-opus-4-20250514')
    
    # Session Configuration
    MAX_CONTEXT_CHARS = 50000
    
    @classmethod
    def init_app(cls):
        """Initialize application folders."""
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(cls.IMAGE_CACHE_FOLDER, exist_ok=True)
