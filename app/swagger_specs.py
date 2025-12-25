"""
Swagger Documentation for WordAssistantAI API
Add this to each route file or create a central swagger spec
"""

# Example Swagger documentation for RAG routes
RAG_SEARCH_SPEC = """
Search newspapers using RAG
---
tags:
  - RAG
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - query
      properties:
        query:
          type: string
          description: Search query
          example: "Arizona 1964"
        n_results:
          type: integer
          default: 5
responses:
  200:
    description: Search results
  400:
    description: Bad request
  500:
    description: Server error
"""

RAG_GENERATE_LAYOUT_SPEC = """
Generate newspaper layout using RAG
---
tags:
  - RAG
parameters:
  - name: body
    in: body
    schema:
      type: object
      properties:
        query:
          type: string
          example: "Arizona newspaper 1964"
        n_results:
          type: integer
          default: 1
responses:
  200:
    description: Newspaper layout with 3 suggestions
    schema:
      type: object
      properties:
        newspaper:
          type: object
        suggestions:
          type: array
        summary:
          type: string
  404:
    description: No newspapers found
"""

RAG_INGEST_SPEC = """
Ingest newspapers into vector database
---
tags:
  - RAG
parameters:
  - name: body
    in: body
    schema:
      type: object
      properties:
        directory:
          type: string
          example: "./data/Newspaper"
responses:
  200:
    description: Ingestion successful
    schema:
      type: object
      properties:
        message:
          type: string
        count:
          type: integer
"""

GENERATION_SPEC = """
Generate AI report/document
---
tags:
  - Generation
security:
  - SessionID: []
parameters:
  - name: X-Session-ID
    in: header
    required: true
    type: string
  - name: body
    in: body
    required: true
    schema:
      type: object
      properties:
        topic:
          type: string
          example: "Machine Learning"
        purpose:
          type: string
        tone:
          type: string
        key_points:
          type: array
          items:
            type: string
responses:
  200:
    description: Generated content
  400:
    description: Missing session ID
"""

CHAT_SPEC = """
Stream chat responses
---
tags:
  - Chat
security:
  - SessionID: []
parameters:
  - name: X-Session-ID
    in: header
    required: true
    type: string
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - prompt
      properties:
        prompt:
          type: string
          example: "Explain quantum computing"
responses:
  200:
    description: Streaming chat response (SSE)
    content:
      text/event-stream:
        schema:
          type: string
"""

FILE_UPLOAD_SPEC = """
Upload documents or images
---
tags:
  - Files
security:
  - SessionID: []
parameters:
  - name: X-Session-ID
    in: header
    required: true
    type: string
  - name: files
    in: formData
    type: file
    required: true
    description: Files to upload
responses:
  200:
    description: Upload successful
    schema:
      type: object
      properties:
        status:
          type: string
        documents:
          type: array
        images:
          type: array
"""
