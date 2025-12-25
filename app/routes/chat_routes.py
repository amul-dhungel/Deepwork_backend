"""
Chat and streaming chat routes.
"""

import json
from flask import Blueprint, request, jsonify, Response, stream_with_context
from ..services import get_ai_service, get_session_service

bp = Blueprint('chat', __name__)


@bp.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """Standard chat endpoint."""
    session_id = request.headers.get('X-Session-ID')
    if not session_id:
        return jsonify({"error": "Missing X-Session-ID header"}), 400
    
    session_service = get_session_service()
    ai_service = get_ai_service()
    session = session_service.get_session(session_id)
    data = request.json
    message = data.get("message")
    
    # Use session context
    context = session.get("context", "")
    images = session.get("images", [])
    
    provider = data.get("modelProvider", "claude")
    
    try:
        # Construct prompt with context
        image_context = "\n".join([f"Image '{img['name']}' available at: {img['url']}" for img in images])
        
        if context or image_context:
            prompt = f"""Context from documents:
{context}

Available Images:
{image_context}

Question: {message}

Provide a clear, expert-level response. Use proper HTML formatting with headings, paragraphs, lists, and tables. Embed images using <img> tags where relevant. Base answers on the provided context."""
        else:
            prompt = message
        
        response_text = ai_service.generate(prompt, provider)
        return jsonify({"reply": response_text})
        
    except Exception as e:
        error_msg = str(e)
        status_code = 500
        if "429" in error_msg or "Quota" in error_msg:
            status_code = 429
        elif "403" in error_msg:
            status_code = 403
        
        response = jsonify({"error": error_msg})
        response.status_code = status_code
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


@bp.route('/api/stream_chat', methods=['POST'])
def stream_chat():
    """Streaming chat endpoint."""
    data = request.json
    prompt = data.get("prompt")
    provider = data.get("modelProvider", "claude")
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    # Extract system prompt and user request from the frontend format
    # Frontend sends: "[SYSTEM: {agent_prompt}]\n\n[USER REQUEST: {user_input}]"
    system_prompt = None
    user_request = prompt
    
    if prompt.startswith('[SYSTEM:'):
        try:
            # Parse out the system and user parts
            parts = prompt.split('[USER REQUEST:')
            if len(parts) == 2:
                system_part = parts[0].replace('[SYSTEM:', '').replace(']', '').strip()
                user_part = parts[1].replace(']', '').strip()
                
                system_prompt = system_part
                user_request = user_part
        except Exception as e:
            pass  # Fall back to using original prompt
    
    # Build the final prompt with Excalidraw instructions for diagrams
    final_prompt = f"""{user_request}

**DIAGRAM FORMAT** (when visual diagrams are needed):
Output raw Excalidraw JSON only - NO markdown wrappers:
{{"type": "excalidraw", "version": 2, "source": "AI", "elements": [rectangles, arrows, text_labels]}}

Use colors: Blue (#a5d8ff) primary, Green (#51cf66) success, Yellow (#ffd43b) highlights.
Label all shapes clearly. Space elements 50px+ apart."""
    
    ai_service = get_ai_service()
    
    def generate():
        try:
            # First yield a "starting" signal
            yield json.dumps({"type": "start"}) + "\n"
            
            # Stream content - pass system_prompt if available
            if system_prompt:
                for chunk in ai_service.generate_stream(final_prompt, provider, system_prompt):
                    yield json.dumps({"type": "chunk", "content": chunk}) + "\n"
            else:
                for chunk in ai_service.generate_stream(final_prompt, provider):
                    yield json.dumps({"type": "chunk", "content": chunk}) + "\n"
            
            # Final signal
            yield json.dumps({"type": "done"}) + "\n"
        except Exception as e:
            yield json.dumps({"type": "error", "error": str(e)}) + "\n"
    
    return Response(stream_with_context(generate()), mimetype='application/x-ndjson')


