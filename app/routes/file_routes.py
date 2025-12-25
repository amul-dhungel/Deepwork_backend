"""
File upload and serving routes.
"""

import os
import uuid
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from ..config import Config
from ..services import get_session_service, get_file_service

bp = Blueprint('files', __name__)


@bp.route('/uploads/<path:filename>')
def serve_file(filename):
    """Serve uploaded files."""
    return send_from_directory(Config.UPLOAD_FOLDER, filename)


@bp.route('/api/upload', methods=['POST'])
def upload_files():
    """
    Upload Files (PDF, DOCX, Images)
    ---
    tags:
      - Files
    consumes:
      - multipart/form-data
    parameters:
      - name: files
        in: formData
        type: file
        required: true
        description: Files to upload (PDF, DOCX, or images)
      - name: X-Session-ID
        in: header
        type: string
        required: true
        description: User session identifier
    responses:
      200:
        description: Files uploaded successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            documents:
              type: array
              items:
                type: object
                properties:
                  name:
                    type: string
                  size:
                    type: integer
                  citation:
                    type: string
            images:
              type: array
              items:
                type: object
            text:
              type: string
              description: Extracted text from documents
      400:
        description: Missing session ID or no files provided
        schema:
          type: object
          properties:
            error:
              type: string
    """
    """Handle file uploads with text extraction."""
    session_id = request.headers.get('X-Session-ID')
    if not session_id:
        return jsonify({"error": "Missing X-Session-ID header"}), 400

    session_service = get_session_service()
    file_service = get_file_service()
    session = session_service.get_session(session_id)

    if 'files' not in request.files:
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist('files')
    new_text_content = ""
    new_images = []
    uploaded_docs_metadata = []

    for file in files:
        original_filename = file.filename
        filename = secure_filename(original_filename)
        
        # Avoid collisions using uuid
        unique_name = f"{uuid.uuid4().hex[:8]}_{filename}"
        save_path = os.path.join(Config.UPLOAD_FOLDER, unique_name)
        file.save(save_path)

        # Create file URL
        base_url = request.host_url.rstrip('/')
        file_url = f"{base_url}/uploads/{unique_name}"

        # Process file based on type
        if filename.lower().endswith(('.pdf', '.txt', '.docx')):
            file_text, metadata = file_service.process_file(save_path, original_filename)
            
            # Add URL to metadata
            metadata['url'] = file_url
            uploaded_docs_metadata.append(metadata)
            
            if file_text:
                # Inject metadata into text stream for AI
                new_text_content += f"\n--- Start of Document ---\n"
                new_text_content += f"Metadata: Filename='{original_filename}', "
                new_text_content += f"Title='{metadata['title']}', Author='{metadata['author']}'\n"
                new_text_content += f"Content:\n{file_text}\n"
                new_text_content += f"--- End of Document ---\n"

        # Handle images
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            new_images.append({
                "name": original_filename,
                "url": file_url
            })

    # Update session
    session_service.update_context(session_id, new_text_content, Config.MAX_CONTEXT_CHARS)
    session_service.add_images(session_id, new_images)
    session_service.add_documents(session_id, uploaded_docs_metadata)

    return jsonify({
        "status": "success",
        "message": f"Processed {len(files)} files",
        "context_length": len(session['context']),
        "images": new_images,
        "documents": uploaded_docs_metadata,
        "session_id": session_id
    })
