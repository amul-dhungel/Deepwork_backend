# LLM + ChromaDB Integration Guide

## 🎯 What We Built

A complete RAG (Retrieval-Augmented Generation) system that combines:
- **ChromaDB**: Vector database for semantic search
- **SentenceTransformers**: Converts text to embeddings
- **Your LLM** (Claude/Gemini/Ollama): Generates intelligent responses

---

## 📦 Installation

```bash
cd backend
pip install chromadb sentence-transformers
```

---

## 🚀 Usage

### Step 1: Ingest Newspapers (One-Time Setup)

```bash
# Start your backend
python main.py

# In another terminal, ingest newspapers
curl -X POST http://localhost:8000/api/rag/ingest \
  -H "Content-Type: application/json" \
  -d '{"directory": "./mock_responses"}'

# Response:
# {
#   "message": "Ingested 10 newspapers",
#   "count": 10
# }
```

### Step 2: Search with LLM

```bash
curl -X POST http://localhost:8000/api/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Arizona 1964 voting",
    "n_results": 5
  }'

# Response:
# {
#   "query": "Arizona 1964 voting",
#   "newspapers": [
#     {
#       "id": "newspaper_1964",
#       "json": {...},
#       "metadata": {
#         "title": "Arizona tribune.",
#         "date": "1964-10-30",
#         "state": "Arizona"
#       },
#       "similarity": 0.92
#     }
#   ],
#   "llm_summary": "Based on your search for Arizona 1964 voting news, I found 5 relevant newspapers. The most relevant is the Arizona Tribune from October 30, 1964, which contains an article titled 'GO TO The POLLS' that encourages citizens to vote in the upcoming November elections...",
#   "count": 5
# }
```

### Step 3: Get LLM Recommendation

```bash
curl -X POST http://localhost:8000/api/rag/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "I want to read about healthcare in 1964"
  }'

# Response:
# {
#   "newspaper": {...},
#   "llm_explanation": "NUMBER: 1\nREASON: The Arizona Tribune from October 30, 1964 is the best match because it contains an article titled 'Hospitals Deserve Praise' that discusses hospital services and healthcare quality...",
#   "all_options": [...]
# }
```

### Step 4: Ask Questions About a Newspaper

```bash
curl -X POST http://localhost:8000/api/rag/ask \
  -H "Content-Type: application/json" \
  -d '{
    "newspaper_json": {...},
    "question": "What articles mention voting?"
  }'

# Response:
# {
#   "question": "What articles mention voting?",
#   "answer": "The newspaper contains one article about voting: 'GO TO The POLLS' which encourages citizens to vote in the November elections. The article mentions that many people have died fighting for voting rights and urges readers to exercise their right to vote..."
# }
```

---

## 🔄 How It Works

### Architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│                                                             │
│  User types: "Arizona 1964 voting"                         │
│       ↓                                                     │
│  POST /api/rag/search                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                         BACKEND                             │
│                                                             │
│  1. NewspaperLLMRAG receives query                         │
│       ↓                                                     │
│  2. NewspaperRAG.search()                                  │
│     - Convert query to embedding                           │
│     - Search ChromaDB                                      │
│     - Return top 5 newspapers                              │
│       ↓                                                     │
│  3. Create context for LLM                                 │
│     - Extract headlines                                    │
│     - Format newspaper metadata                            │
│       ↓                                                     │
│  4. Send to LLM (Claude/Gemini/Ollama)                     │
│     Prompt: "User wants: Arizona 1964 voting               │
│              Here are relevant newspapers:                  │
│              1. Arizona Tribune (Oct 30, 1964)             │
│                 - GO TO The POLLS                          │
│              Explain which is best..."                     │
│       ↓                                                     │
│  5. LLM generates intelligent summary                      │
│       ↓                                                     │
│  6. Return newspapers + LLM summary                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│                                                             │
│  Display:                                                  │
│  - List of newspapers                                      │
│  - LLM summary explaining matches                          │
│  - "Load" button for each newspaper                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Frontend Integration

```javascript
// frontend/src/features/rag/NewspaperSearch.jsx
import React, { useState } from 'react';

const NewspaperSearch = ({ onSelectNewspaper }) => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    
    const handleSearch = async () => {
        setLoading(true);
        
        const response = await fetch('http://localhost:8000/api/rag/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, n_results: 5 })
        });
        
        const data = await response.json();
        setResults(data);
        setLoading(false);
    };
    
    return (
        <div className="newspaper-search">
            <h2>🔍 Search 600 Newspapers</h2>
            
            <input 
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., 'Arizona 1964 voting'"
            />
            <button onClick={handleSearch} disabled={loading}>
                {loading ? 'Searching...' : 'Search'}
            </button>
            
            {results && (
                <div>
                    {/* LLM Summary */}
                    <div className="llm-summary">
                        <h3>💡 AI Summary</h3>
                        <p>{results.llm_summary}</p>
                    </div>
                    
                    {/* Newspaper Results */}
                    <div className="results">
                        <h3>📰 Found {results.count} Newspapers</h3>
                        {results.newspapers.map((result, i) => (
                            <div key={i} className="result-card">
                                <h4>{result.metadata.title}</h4>
                                <p>{result.metadata.date} • {result.metadata.state}</p>
                                <p>Match: {(result.similarity * 100).toFixed(0)}%</p>
                                <button onClick={() => onSelectNewspaper(result.json)}>
                                    Load This Newspaper
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default NewspaperSearch;
```

---

## 🔑 Key Features

### 1. **Semantic Search**
- Searches by meaning, not just keywords
- "voting" finds "elections", "polls", "democracy"
- "bread" finds "food", "wheat", "baking"

### 2. **LLM Intelligence**
- Explains WHY newspapers match
- Recommends BEST newspaper
- Answers questions about content

### 3. **Scalable**
- Handles 600+ newspapers easily
- Fast vector search (<100ms)
- Persistent storage (ChromaDB)

### 4. **Flexible**
- Works with any LLM (Claude, Gemini, Ollama)
- Customizable prompts
- Multiple search modes

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/rag/search` | POST | Search with LLM summary |
| `/api/rag/recommend` | POST | Get LLM recommendation |
| `/api/rag/summarize` | POST | Generate newspaper summary |
| `/api/rag/ask` | POST | Ask questions about newspaper |
| `/api/rag/ingest` | POST | Ingest newspapers into ChromaDB |
| `/api/rag/status` | GET | Check RAG system status |

---

## 🎯 Next Steps

1. **Ingest your 600 newspapers**: `POST /api/rag/ingest`
2. **Test search**: `POST /api/rag/search`
3. **Build frontend UI**: Use NewspaperSearch component
4. **Integrate with editor**: Load selected newspaper into NewspaperRenderer

Your LLM + ChromaDB system is ready! 🚀
