"""
AI generation routes (generate, summarize, refine, image generation).
"""

from flask import Blueprint, request, jsonify
from ..services import get_ai_service, get_session_service, get_image_service
from ..utils import markdown_to_html
import json

bp = Blueprint('generation', __name__)


@bp.route('/api/generate', methods=['POST', 'OPTIONS'])
def generate_report():
    """Generate AI reports/documents."""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    session_id = request.headers.get('X-Session-ID')
    if not session_id:
        return jsonify({"error": "Missing X-Session-ID header"}), 400
    
    session_service = get_session_service()
    ai_service = get_ai_service()
    session = session_service.get_session(session_id)
    
    # Parse JSON properly - handle different cases
    try:
        data = request.get_json(force=True)
        if data is None:
            data = {}
    except Exception as e:
        print(f"JSON parsing error: {e}")
        data = {}
    
    # Extract options
    options = data.get('options', {})
    include_table = options.get('includeTable', False)
    include_mermaid = options.get('includeMermaid', False)
    
    topic = data.get("topic")
    purpose = data.get("purpose")
    tone = data.get("tone")
    key_points = data.get("key_points", [])
    
    # Build context
    image_context = "\n".join([f"Image '{img['name']}' available at: {img['url']}" for img in session['images']])
    
    context_str = ""
    if session['context'] or image_context:
        context_str = f"\nUse these uploaded documents as context/source material:\n{session['context']}\n\nAvailable Images:\n{image_context}\n"
    
    # Build prompt
    default_key_points = "  * Detailed analysis of key metrics\n  * Strategic insights\n  * Data-driven recommendations"
    key_points_str = chr(10).join([f"  * {point}" for point in key_points]) if key_points else default_key_points
    
    prompt = f"""
    Act as an expert {data.get('role', 'Senior Data Analyst/Researcher')}. You are preparing a comprehensive professional report for {data.get('audience', 'Executive Stakeholders')}.

    **REPORT SPECIFICATIONS:**
    - **Primary Topic:** {topic}
    - **Core Objective:** {purpose if purpose else f"To provide a comprehensive analysis of {topic}"}
    - **Key Data/Content Requirements:** 
    {key_points_str}

    {context_str}

    **STRUCTURE & FORMATTING:**
    Generate a research report following this structure. 
    **Use Standard Markdown Formatting.**
    
    STRICT RESPONSE FORMATTING RULES (CRITICAL):
    1. **Output ONLY the report content.** Do not include "Here is your report" or similar.
    2. Start with `# Title`.
    3. Use `## Section` and `### Subsection`.
    4. Use `**bold**` for key terms.
    5. Use `- ` for bullet points.
    6. Use ` ```language ` for code blocks.
    7. **CRITICAL**: Insert **DOUBLE NEWLINES** between every section, paragraph, and header.

    Report Structure:
    1. **# Report Title**
    2. **## Executive Summary**
    3. **## Introduction**
    4. **## Findings & Analysis**
    5. **## Recommendations**
    6. **## Conclusion**

    **Content Requirements**:
    - Tone: {tone}
    - Perspective: Third-person professional.
    
    **SPECIAL INSTRUCTIONS:**
    """
    
    # Add special instructions conditionally
    if include_table:
        prompt += "\n - Include a Markdown Table for data comparison."
    if include_mermaid:
        prompt += "\n - If asked to visualize, describe the diagram textually."
    
    provider = data.get("modelProvider", "gemini")
    
    try:
        response_text = ai_service.generate(prompt, provider)
        html_response = markdown_to_html(response_text)
        return jsonify({"content": html_response})
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


@bp.route('/api/summarize', methods=['POST'])
def summarize_document():
    """Summarize documents."""
    session_id = request.headers.get('X-Session-ID')
    if not session_id:
        return jsonify({"error": "Missing X-Session-ID header"}), 400
    
    session_service = get_session_service()
    ai_service = get_ai_service()
    session = session_service.get_session(session_id)
    data = request.json
    
    provider = data.get("modelProvider", "gemini")
    format_type = data.get("format", "paragraph")
    
    if not session.get('context'):
        return jsonify({"error": "No documents uploaded yet"}), 400
    
    prompt = f"""
    Task: Summarize the uploaded research documents below. 
    
    --- Documents ---
    {session['context']}
    --- End ---
    
    Requirements:
    - Format: {format_type.capitalize()}
    - Include: Key findings, methods, and conclusions
    - Length: Concise but comprehensive (1-2 pages max)
    - Do NOT include introductions like "Here is the summary", just provide the summary directly.
    
    Generate the summary now:
    """
    
    try:
        summary = ai_service.generate(prompt, provider)
        return jsonify({"summary": summary})
    except Exception as e:
        error_msg = str(e)
        status_code = 500
        if "429" in error_msg or "Quota" in error_msg:
            status_code = 429
        
        response = jsonify({"error": error_msg})
        response.status_code = status_code
        return response


@bp.route('/api/refine', methods=['POST'])
def refine_text():
    """Refine and improve text."""
    data = request.json
    text = data.get("text")
    instructions = data.get("instructions", "Improve clarity and professionalism")
    provider = data.get("modelProvider", "gemini")
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    ai_service = get_ai_service()
    
    prompt = f"""
    Refine the following text based on these instructions: {instructions}
    
    Original Text:
    {text}
    
    Refined version:
    """
    
    try:
        refined = ai_service.generate(prompt, provider)
        return jsonify({"refinedText": refined})
    except Exception as e:
        error_msg = str(e)
        status_code = 500
        if "429" in error_msg or "Quota" in error_msg:
            status_code = 429
        
        response = jsonify({"error": error_msg})
        response.status_code = status_code
        return response


@bp.route('/api/generate_card_image', methods=['POST'])
def generate_card_image():
    """Generate AI image for card design."""
    data = request.json
    user_prompt = data.get('prompt', '')
    style = data.get('style', 'digital-art')
    
    if not user_prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    try:
        image_service = get_image_service()
        result = image_service.generate_image(user_prompt, style)
        
        if result.get('success'):
            return jsonify({
                'image_base64': result['image_base64'],
                'cached': result['cached'],
                'cost': result['cost']
            })
        else:
            return jsonify({
                'error': result.get('error', 'Image generation failed')
            }), 500
    
    except Exception as e:
        print(f"Image generation error: {str(e)}")
        return jsonify({"error": str(e)}), 500
"""
Academic Report Streaming Endpoint
Generates comprehensive research reports with tables and diagrams
"""

from flask import Response
import time
import re

@bp.route('/api/generate/academic_report', methods=['POST', 'OPTIONS'])
def stream_academic_report():
    """Stream LLM-generated academic report with tables and Excalidraw diagrams."""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    # Extract request data BEFORE creating generator (must be in request context)
    data = request.get_json(force=True) or {}
    topic = data.get('topic', 'Artificial Intelligence')
    
    def generate():
        try:
            # Get Ollama AI service
            from app.services import get_ai_service
            ai_service = get_ai_service(use_ollama=True)
            
            # Comprehensive prompt for 5000-word report with structure
            prompt = f"""Generate a comprehensive academic research report on: {topic}

CRITICAL REQUIREMENTS:
1. Total length: approximately 5000 words
2. Include EXACTLY 2 HTML tables with proper styling
3. Include EXACTLY 2 Excalidraw diagrams as JSON
4. Use proper academic structure with sections
5. Include APA-style references

STRUCTURE:
# {topic}: A Comprehensive Analysis

## Abstract
(200 words summary)

## 1. Introduction
(800 words - background, significance, research questions)

## 2. Literature Review  
(1200 words - current state of research, key findings)

table_start
<p style="color:#0066cc; font-weight:600; margin:10px 0 5px 0;">Table 1: Key Research Studies</p>
<table style="width:100%; border-collapse:collapse; margin:20px 0; border:1px solid #ddd;">
<thead style="background:#f0f0f0;"><tr><th style="border:1px solid #ddd; padding:8px;">Study</th><th style="border:1px solid #ddd; padding:8px;">Year</th><th style="border:1px solid #ddd; padding:8px;">Key Finding</th></tr></thead>
<tbody>
<tr><td style="border:1px solid #ddd; padding:8px;">Author et al.</td><td style="border:1px solid #ddd; padding:8px;">2023</td><td style="border:1px solid #ddd; padding:8px;">Finding description</td></tr>
</tbody>
</table>
table_end

## 3. Methodology
(1000 words - research approach, data collection, analysis methods)

excali_start
{{"type": "excalidraw", "version": 2, "source": "AI", "elements": [{{"id": "method1", "type": "rectangle", "x": 100, "y": 100, "width": 180, "height": 80, "strokeColor": "#1e1e1e", "backgroundColor": "#a5d8ff", "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid", "roughness": 0, "opacity": 100, "roundness": {{"type": 3}}}}, {{"id": "text1", "type": "text", "x": 130, "y": 125, "width": 120, "height": 25, "text": "Data Collection", "fontSize": 16, "fontFamily": 1, "textAlign": "center", "strokeColor": "#1e1e1e"}}, {{"id": "arrow1", "type": "arrow", "x": 280, "y": 140, "width": 80, "height": 0, "strokeColor": "#1e1e1e", "strokeWidth": 2}}, {{"id": "method2", "type": "rectangle", "x": 360, "y": 100, "width": 180, "height": 80, "strokeColor": "#1e1e1e", "backgroundColor": "#ffd8a8", "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid", "roughness": 0, "opacity": 100, "roundness": {{"type": 3}}}}, {{"id": "text2", "type": "text", "x": 400, "y": 125, "width": 100, "height": 25, "text": "Analysis", "fontSize": 16, "fontFamily": 1, "textAlign": "center", "strokeColor": "#1e1e1e"}}]}}
excali_end

## 4. Results
(1200 words - findings, data analysis, patterns)

table_start
<p style="color:#0066cc; font-weight:600; margin:10px 0 5px 0;">Table 2: Research Findings Summary</p>
<table style="width:100%; border-collapse:collapse; margin:20px 0; border:1px solid #ddd;">
<thead style="background:#f0f0f0;"><tr><th style="border:1px solid #ddd; padding:8px;">Category</th><th style="border:1px solid #ddd; padding:8px;">Result</th><th style="border:1px solid #ddd; padding:8px;">Significance</th></tr></thead>
<tbody>
<tr><td style="border:1px solid #ddd; padding:8px;">Category A</td><td style="border:1px solid #ddd; padding:8px;">Result data</td><td style="border:1px solid #ddd; padding:8px;">High</td></tr>
</tbody>
</table>
table_end

## 5. Discussion
(1000 words - interpretation, implications, limitations)

excali_start
{{"type": "excalidraw", "version": 2, "source": "AI", "elements": [{{"id": "concept1", "type": "ellipse", "x": 150, "y": 100, "width": 120, "height": 120, "strokeColor": "#1e1e1e", "backgroundColor": "#b2f2bb", "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid", "roughness": 0, "opacity": 100}}, {{"id": "text3", "type": "text", "x": 175, "y": 145, "width": 70, "height": 25, "text": "Core Idea", "fontSize": 14, "fontFamily": 1, "textAlign": "center", "strokeColor": "#1e1e1e"}}, {{"id": "concept2", "type": "ellipse", "x": 320, "y": 100, "width": 120, "height": 120, "strokeColor": "#1e1e1e", "backgroundColor": "#ffc9c9", "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid", "roughness": 0, "opacity": 100}}, {{"id": "text4", "type": "text", "x": 340, "y": 145, "width": 80, "height": 25, "text": "Impact", "fontSize": 14, "fontFamily": 1, "textAlign": "center", "strokeColor": "#1e1e1e"}}, {{"id": "line1", "type": "line", "x": 270, "y": 160, "width": 50, "height": 0, "strokeColor": "#1e1e1e", "strokeWidth": 2, "points": [[0, 0], [50, 0]]}}]}}
excali_end

## 6. Conclusion
(600 words - summary, future research directions)

## References
(APA format, 10-15 sources)

CRITICAL: Output the EXACT structure above with actual content. Use the markers table_start/table_end and excali_start/excali_end EXACTLY as shown."""


            print(f"🎓 Generating academic report on: {topic}")
            print(f"📝 Using Ollama DeepSeek streaming...")
            
            # Stream content directly from Ollama
            chunk_size = 30
            
            for chunk in ai_service.ollama.generate_stream(prompt):
                # Send chunks directly to frontend
                for i in range(0, len(chunk), chunk_size):
                    text_chunk = chunk[i:i + chunk_size]
                    payload = {
                        "type": "text_chunk",
                        "content": text_chunk
                    }
                    yield f'data: {json.dumps(payload)}\n\n'
                    time.sleep(0.02)  # Smooth typing effect
            
            # Send completion
            yield f'data: {json.dumps({"type": "done"})}\n\n'
            print("✅ Academic report streaming complete")
            
        except Exception as e:
            print(f"❌ Error generating academic report: {str(e)}")
            import traceback
            traceback.print_exc()
            yield f'data: {json.dumps({"type": "error", "error": str(e)})}\n\n'
    
    return Response(generate(), mimetype='text/event-stream')
