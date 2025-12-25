# RAG Module

Clean, modular implementation of Retrieval-Augmented Generation for newspaper search.

## 📁 Structure

```
app/rag/
├── __init__.py          # Module exports
├── vector_store.py      # ChromaDB vector database operations
├── llm_service.py       # LLM integration for analysis
└── rag_service.py       # Main RAG orchestration
```

## 🎯 Components

### 1. **VectorStore** (`vector_store.py`)
Handles all ChromaDB operations:
- Create embeddings with SentenceTransformers
- Store newspapers in vector database
- Perform semantic search
- Manage database lifecycle

```python
from app.rag import NewspaperVectorStore

vector_store = NewspaperVectorStore()
vector_store.add_newspaper(newspaper_json, "newspaper_1964")
results = vector_store.search("Arizona 1964 voting", n_results=5)
```

### 2. **LLMService** (`llm_service.py`)
Handles all LLM operations:
- Generate search summaries
- Recommend best newspapers
- Summarize newspaper content
- Answer questions about newspapers

```python
from app.rag import NewspaperLLMService

llm_service = NewspaperLLMService()
summary = llm_service.generate_search_summary(query, newspapers)
recommendation = llm_service.recommend_best_newspaper(intent, newspapers)
```

### 3. **RAGService** (`rag_service.py`)
Main orchestrator that combines vector search + LLM:
- Search with LLM summaries
- Get recommendations
- Ingest newspapers
- System status

```python
from app.rag import NewspaperRAGService

rag = NewspaperRAGService()
result = rag.search_with_llm("Arizona 1964 voting")
# Returns: {newspapers: [...], llm_summary: "..."}
```

## 🚀 Usage

### Import the main service:

```python
from app.rag import NewspaperRAGService

# Initialize
rag = NewspaperRAGService()

# Ingest newspapers
rag.ingest_from_directory("./mock_responses")

# Search with LLM
result = rag.search_with_llm("Arizona 1964 voting", n_results=5)

# Get recommendation
recommendation = rag.recommend_newspaper("I want to read about healthcare")

# Summarize a newspaper
summary = rag.summarize_newspaper(newspaper_json)

# Ask a question
answer = rag.answer_question(newspaper_json, "What articles mention voting?")
```

## 🔧 Configuration

### Vector Store
- **Model**: `all-MiniLM-L6-v2` (384 dimensions)
- **Database**: ChromaDB with cosine similarity
- **Storage**: `./chroma_db` (persistent)

### LLM Service
- Uses existing `AIService` from `app/services/ai_service.py`
- Supports Claude, Gemini, Ollama

## 📊 API Integration

The RAG module is exposed via Flask routes in `app/routes/rag_routes.py`:

- `POST /api/rag/search` - Search with LLM
- `POST /api/rag/recommend` - Get recommendation
- `POST /api/rag/summarize` - Summarize newspaper
- `POST /api/rag/ask` - Ask questions
- `POST /api/rag/ingest` - Ingest newspapers
- `GET /api/rag/status` - System status

## 🎯 Benefits of This Structure

### ✅ Separation of Concerns
- `vector_store.py` - Only ChromaDB operations
- `llm_service.py` - Only LLM operations
- `rag_service.py` - Orchestration only

### ✅ Easy Testing
Each component can be tested independently:
```python
# Test vector store only
vector_store = NewspaperVectorStore()
assert vector_store.get_count() == 0

# Test LLM service only
llm_service = NewspaperLLMService()
summary = llm_service.summarize_newspaper(test_newspaper)
```

### ✅ Easy to Extend
Want to add a new feature? Just extend the appropriate service:
```python
# Add to vector_store.py
def search_by_date_range(self, start_date, end_date):
    ...

# Add to llm_service.py
def compare_newspapers(self, newspaper1, newspaper2):
    ...
```

### ✅ Clean Imports
```python
# Before (messy)
from app.services.newspaper_rag import NewspaperRAG
from app.services.llm_rag import NewspaperLLMRAG

# After (clean)
from app.rag import NewspaperRAGService
```

## 🔄 Migration from Old Structure

Old files (can be deleted):
- `app/services/newspaper_rag.py` ❌
- `app/services/llm_rag.py` ❌

New files (use these):
- `app/rag/vector_store.py` ✅
- `app/rag/llm_service.py` ✅
- `app/rag/rag_service.py` ✅

## 📝 Example: Full Workflow

```python
from app.rag import NewspaperRAGService

# Initialize
rag = NewspaperRAGService()

# 1. Ingest newspapers (one-time)
count = rag.ingest_from_directory("./mock_responses")
print(f"Ingested {count} newspapers")

# 2. Search with LLM
result = rag.search_with_llm("Arizona 1964 voting", n_results=5)
print(f"LLM Summary: {result['llm_summary']}")
print(f"Found {result['count']} newspapers")

# 3. Get best recommendation
recommendation = rag.recommend_newspaper("I want to read about civil rights")
best_newspaper = recommendation['newspaper']
print(f"Recommended: {best_newspaper['metadata']['title']}")
print(f"Explanation: {recommendation['explanation']}")

# 4. Ask a question
answer = rag.answer_question(
    best_newspaper['json'],
    "What articles mention voting rights?"
)
print(f"Answer: {answer}")
```

## 🎉 Result

Clean, modular, testable RAG system that's easy to understand and extend!
