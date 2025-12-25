"""
Session management service.
"""

import time
from typing import Dict, Any


class SessionService:
    """Manages user sessions with context and uploaded content."""
    
    def __init__(self):
        """Initialize session store."""
        self._sessions: Dict[str, Dict[str, Any]] = {}
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve or create a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Session data dict
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = {
                "context": "",
                "images": [],
                "docs": [],
                "created_at": time.time()
            }
        return self._sessions[session_id]
    
    def update_context(self, session_id: str, additional_context: str, max_chars: int = 50000):
        """
        Add context to session and trim if necessary.
        
        Args:
            session_id: Session ID
            additional_context: Text to add
            max_chars: Maximum context length
        """
        session = self.get_session(session_id)
        session['context'] += additional_context
        
        # Trim if too large
        if len(session['context']) > max_chars:
            session['context'] = session['context'][-max_chars:]
    
    def add_images(self, session_id: str, images: list):
        """Add images to session."""
        session = self.get_session(session_id)
        session['images'].extend(images)
    
    def add_documents(self, session_id: str, docs: list):
        """Add documents to session."""
        session = self.get_session(session_id)
        session['docs'].extend(docs)
    
    def get_session_count(self) -> int:
        """Get number of active sessions."""
        return len(self._sessions)


# Singleton instance
_session_service = None


def get_session_service() -> SessionService:
    """Get or create session service instance."""
    global _session_service
    if _session_service is None:
        _session_service = SessionService()
    return _session_service
