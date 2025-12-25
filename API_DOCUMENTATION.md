# WordAssistantAI API Documentation

## Overview
Complete Swagger/OpenAPI documentation for all WordAssistantAI backend APIs.

## Access Swagger UI
Once the backend is running, access the interactive API documentation at:
**http://localhost:8000/api/docs**

## API Endpoints

### Health & Status
- `GET /api/health` - Health check endpoint
- `GET /api/models/status` - Get AI model status

### File Management
- `POST /api/upload` - Upload documents/images
- `GET /api/files/{session_id}` - Get uploaded files for session

### AI Generation
- `POST /api/generate` - Generate AI reports/documents
- `POST /api/generate/academic_report` - Stream academic report generation
- `POST /api/summarize` - Summarize documents
- `POST /api/refine` - Refine existing content

### Chat
- `POST /api/stream_chat` - Stream chat responses
- `POST /api/chat` - Non-streaming chat

### RAG (Retrieval-Augmented Generation)
- `POST /api/rag/ingest` - Ingest newspapers into vector database
- `POST /api/rag/search` - Search newspapers
- `POST /api/rag/generate_layout` - Generate newspaper layout (returns 1 main + 3 suggestions)
- `POST /api/rag/summarize` - Summarize newspaper
- `POST /api/rag/ask` - Ask questions about newspaper
- `GET /api/rag/status` - Get RAG system status

### Mock/Testing
- `GET /api/mock/stream_report` - Test streaming with mock data

## Authentication
All endpoints require `X-Session-ID` header for session management.

## Response Formats
- JSON for standard responses
- Server-Sent Events (SSE) for streaming endpoints

## Error Codes
- 200: Success
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

## Installation
```bash
pip install flasgger
```

## Usage
The Swagger UI provides:
- Interactive API testing
- Request/response examples
- Schema definitions
- Authentication testing

## Quick Start
1. Install dependencies: `pip install -r requirements.txt`
2. Run backend: `python main.py`
3. Open browser: `http://localhost:8000/api/docs`
4. Test APIs interactively!
