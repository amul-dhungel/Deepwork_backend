"""
Poster Generation Routes
API endpoints for RAG-based poster generation
"""

from flask import Blueprint, request, jsonify
from ..rag.rag_service import NewspaperRAGService
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('poster', __name__, url_prefix='/api/poster')

# Initialize RAG service
rag_service = NewspaperRAGService()

@bp.route('/ingest', methods=['POST'])
def ingest_posters():
    """Ingest all poster metadata files into vector database"""
    try:
        count = rag_service.ingest_posters()
        return jsonify({
            'success': True,
            'message': f'Successfully ingested {count} posters',
            'count': count
        })
    except Exception as e:
        logger.error(f"Poster ingestion failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/search', methods=['POST'])
def search_posters():
    """Search for similar poster layouts"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        n_results = data.get('n_results', 5)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        posters = rag_service.search_posters(query, n_results)
        
        return jsonify({
            'success': True,
            'posters': posters,
            'count': len(posters)
        })
    except Exception as e:
        logger.error(f"Poster search failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/generate', methods=['POST'])
def generate_poster():
    """Generate a poster layout based on user query"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        theme = data.get('theme', 'blue')
        return_suggestions = data.get('return_suggestions', False)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        result = rag_service.generate_poster_layout(query, theme, return_suggestions)
        
        return jsonify({
            'success': True,
            **result
        })
    except Exception as e:
        logger.error(f"Poster generation failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/generate_custom', methods=['POST'])
def generate_custom_poster():
    """Generate custom poster using RAG + LLM"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        theme = data.get('theme', 'blue')
        if not query:
            return jsonify({'success': False, 'error': 'Query required'}), 400
        result = rag_service.generate_custom_poster_layout(query, theme)
        return jsonify({'success': True, **result})
    except Exception as e:
        logger.error(f"Custom poster generation failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
