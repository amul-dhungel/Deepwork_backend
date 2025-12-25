"""
Mock routes for testing and development.
"""

from flask import Blueprint, jsonify, Response, send_file
import os
import time
import json

bp = Blueprint('mock', __name__, url_prefix='/api/mock')

# Path to mock responses directory
MOCK_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'mock_responses')

@bp.route('/newspaper', methods=['GET'])
def get_newspaper():
    """Serve newspaper HTML sample."""
    newspaper_path = os.path.join(MOCK_DIR, 'newspaper_sample.html')
    return send_file(newspaper_path, mimetype='text/html')

@bp.route('/newspaper_layout', methods=['GET'])
def get_newspaper_layout():
    """Serve newspaper layout JSON with bbox coordinates."""
    layout_path = os.path.join(MOCK_DIR, 'newspaper_1964.json')
    return send_file(layout_path, mimetype='application/json')

@bp.route('/poster_layout', methods=['GET'])
def get_poster_layout():
    """Serve academic poster metadata JSON."""
    poster_path = os.path.join(MOCK_DIR, 'poster_sample.json')
    return send_file(poster_path, mimetype='application/json')

@bp.route('/report', methods=['GET'])
def get_mock_report():
    """Serve mock AI report for development testing."""
    try:
        mock_file = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', 
            'mock_responses', 
            'ai_report_corrected.md'
        )
        
        with open(mock_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'success': True,
            'content': content
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/stream_report', methods=['GET'])
def stream_mock_report():
    """Stream mock AI report with structured events (text_chunk, artifact)."""
    def generate():
        import re
        try:
            mock_file = os.path.join(
                os.path.dirname(__file__), 
                '..', '..', 
                'mock_responses', 
                'ai_report_sample.md'
            )
            
            with open(mock_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Regex to split content by special block markers
            # Captures the delimiters so we know which is which
            pattern = re.compile(r'(excali_start[\s\S]*?excali_end|table_start[\s\S]*?table_end)')
            parts = pattern.split(content)
            
            chunk_size = 20 # Character chunk size for text simulation

            for part in parts:
                if not part:
                    continue
                    
                if part.startswith('excali_start'):
                    # Extract JSON content
                    json_str = part.replace('excali_start', '').replace('excali_end', '').strip()
                    payload = {
                        "type": "artifact",
                        "artifact_type": "excalidraw",
                        "payload": json_str
                    }
                    yield f'data: {json.dumps(payload)}\n\n'
                    time.sleep(0.1) # Simulate processing time

                elif part.startswith('table_start'):
                    # Extract HTML content
                    html_str = part.replace('table_start', '').replace('table_end', '').strip()
                    payload = {
                        "type": "artifact",
                        "artifact_type": "table",
                        "payload": html_str
                    }
                    yield f'data: {json.dumps(payload)}\n\n'
                    time.sleep(0.1)

                else:
                    # Regular Text - Stream it in chunks
                    text_content = part
                    for i in range(0, len(text_content), chunk_size):
                        chunk = text_content[i:i + chunk_size]
                        payload = {
                            "type": "text_chunk",
                            "content": chunk
                        }
                        yield f'data: {json.dumps(payload)}\n\n'
                        time.sleep(0.02) # Typing speed

            # Send completion event
            yield f'data: {json.dumps({"type": "done"})}\n\n'
            
        except Exception as e:
            yield f'data: {json.dumps({"type": "error", "error": str(e)})}\n\n'
    
    return Response(generate(), mimetype='text/event-stream')
