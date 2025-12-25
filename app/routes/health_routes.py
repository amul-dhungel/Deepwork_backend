"""
Health check and model status routes.
"""

from flask import Blueprint, jsonify
from ..services import get_ai_service, get_session_service

bp = Blueprint('health', __name__)


@bp.route('/api/health', methods=['GET'])
def health_check():
    """
    Health Check
    ---
    tags:
      - Health
    responses:
      200:
        description: Service is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: "ok"
            service:
              type: string
            active_sessions:
              type: integer
    """
    session_service = get_session_service()
    
    return jsonify({
        "status": "ok",
        "service": "AI Word Assistant Backend (Flask + REST)",
        "active_sessions": session_service.get_session_count()
    })


@bp.route('/api/models/status', methods=['GET'])
def get_models_status():
    """
    Check AI Model Status
    ---
    tags:
      - Health
    responses:
      200:
        description: AI model availability status
        schema:
          type: object
          properties:
            claude:
              type: string
              example: "ok"
              description: Claude model status (ok/error)
    """
    ai_service = get_ai_service()
    claude_status = ai_service.check_status()
    
    return jsonify({
        "claude": claude_status
    })
