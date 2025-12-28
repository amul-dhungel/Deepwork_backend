"""
Infographic Generation Routes

API endpoints for vibrant infographic generation using 4-agent architecture.
"""

from flask import Blueprint, request, jsonify
from app.services.agents.copywriting_agent import CopywritingAgent
from app.rag.llm_service import NewspaperLLMService

infographic_bp = Blueprint('infographic', __name__)


@infographic_bp.route('/api/infographic/analyze-text', methods=['POST'])
def analyze_text():
    """
    Analyze text to extract semantic structure and determine visual archetype.
    
    Request Body:
    {
        "text": "Selected paragraph text..."
    }
    
    Response:
    {
        "archetype": "timeline|process|comparison|hierarchy|metrics|network",
        "metadata": {
            "semantic_type": "sequential",
            "tone": "professional",
            "complexity": "moderate"
        },
        "structure": {
            "title": "...",
            "events": [...] or "nodes": [...] depending on archetype
        }
    }
    """
    
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text or len(text.strip()) < 10:
            return jsonify({
                'error': 'Text is required and must be at least 10 characters'
            }), 400
        
        # Initialize LLM service
        llm_service = NewspaperLLMService()
        
        # Initialize Copywriting Agent
        agent = CopywritingAgent(llm_service.ai_service)
        
        # Analyze text
        analysis = agent.analyze(text)
        
        return jsonify(analysis), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Analysis failed: {str(e)}'
        }), 500


@infographic_bp.route('/api/infographic/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for infographic service.
    """
    return jsonify({
        'status': 'healthy',
        'service': 'infographic-generation',
        'agents': ['copywriting', 'layout', 'illustration', 'creative-director']
    }), 200
