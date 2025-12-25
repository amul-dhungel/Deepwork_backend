"""
RAG API Routes - Newspaper search with LLM
"""
from flask import Blueprint, request, jsonify
from app.rag import NewspaperRAGService

rag_bp = Blueprint('rag', __name__, url_prefix='/api/rag')

# Lazy-load RAG service to avoid downloading models at import time
_rag_service = None

def get_rag_service():
    """Lazy-load RAG service"""
    global _rag_service
    if _rag_service is None:
        _rag_service = NewspaperRAGService()
    return _rag_service

@rag_bp.route('/search', methods=['POST'])
def search_newspapers():
    """
    Search newspapers with LLM-enhanced results
    
    Request body:
    {
        "query": "Arizona 1964 voting",
        "n_results": 5
    }
    
    Response:
    {
        "query": "Arizona 1964 voting",
        "newspapers": [...],
        "llm_summary": "Based on your search...",
        "count": 5
    }
    """
    try:
        data = request.json
        query = data.get('query', '')
        n_results = data.get('n_results', 5)
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        results = get_rag_service().search_with_llm(query, n_results)
        
        return jsonify(results), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rag_bp.route('/recommend', methods=['POST'])
def recommend_newspaper():
    """
    Get LLM recommendation for best newspaper
    
    Request body:
    {
        "intent": "I want to read about civil rights in 1964"
    }
    
    Response:
    {
        "newspaper": {...},
        "llm_explanation": "This newspaper is best because...",
        "all_options": [...]
    }
    """
    try:
        data = request.json
        intent = data.get('intent', '')
        
        if not intent:
            return jsonify({"error": "Intent is required"}), 400
        
        result = get_rag_service().recommend_newspaper(intent)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rag_bp.route('/summarize', methods=['POST'])
def summarize_newspaper():
    """
    Generate LLM summary of a newspaper
    
    Request body:
    {
        "newspaper_json": {...}
    }
    
    Response:
    {
        "summary": "This newspaper from 1964..."
    }
    """
    try:
        data = request.json
        newspaper_json = data.get('newspaper_json', {})
        
        if not newspaper_json:
            return jsonify({"error": "Newspaper JSON is required"}), 400
        
        summary = get_rag_service().generate_newspaper_summary(newspaper_json)
        
        return jsonify({"summary": summary}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rag_bp.route('/ask', methods=['POST'])
def ask_about_newspaper():
    """
    Ask LLM a question about a specific newspaper
    
    Request body:
    {
        "newspaper_json": {...},
        "question": "What articles mention voting?"
    }
    
    Response:
    {
        "question": "What articles mention voting?",
        "answer": "The newspaper contains..."
    }
    """
    try:
        data = request.json
        newspaper_json = data.get('newspaper_json', {})
        question = data.get('question', '')
        
        if not newspaper_json or not question:
            return jsonify({"error": "Both newspaper_json and question are required"}), 400
        
        answer = get_rag_service().answer_question_about_newspaper(newspaper_json, question)
        
        return jsonify({
            "question": question,
            "answer": answer
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rag_bp.route('/ingest', methods=['POST'])
def ingest_newspapers():
    """
    Ingest all newspapers from directory into ChromaDB
    
    Request body:
    {
        "directory": "./mock_responses"  # optional
    }
    
    Response:
    {
        "message": "Ingested 10 newspapers",
        "count": 10
    }
    """
    try:
        data = request.json or {}
        directory = data.get('directory', './mock_responses')
        
        count = get_rag_service().ingest_from_directory(directory)
        
        return jsonify({
            "message": f"Ingested {count} newspapers",
            "count": count
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rag_bp.route('/status', methods=['GET'])
def get_status():
    """
    Get RAG system status
    
    Response:
    {
        "status": "ready",
        "newspaper_count": 10,
        "model": "all-MiniLM-L6-v2"
    }
    """
    try:
        status = get_rag_service().get_status()
        return jsonify(status), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@rag_bp.route('/generate_layout', methods=['POST'])
def generate_newspaper_layout():
    """
    Generate newspaper layout using RAG
    
    Request body:
    {
        "query": "Arizona 1964 newspaper",
        "n_results": 1
    }
    
    Response:
    {
        "newspaper": {...},  # Full newspaper JSON
        "summary": "LLM-generated context",
        "query": "Arizona 1964 newspaper"
    }
    """
    try:
        data = request.json or {}
        query = data.get('query', '')
        n_results = data.get('n_results', 1)
        
        print(f"\n{'='*60}")
        print(f"📰 NEWSPAPER LAYOUT REQUEST")
        print(f"{'='*60}")
        print(f"Query: '{query}'")
        print(f"N Results: {n_results}")
        
        if not query:
            # If no query, get a random newspaper
            query = "newspaper 1964"
            print(f"⚠️  Empty query, using default: '{query}'")
        
        # Use RAG to search for newspapers
        rag_service = get_rag_service()
        
        # Check if database is empty and auto-ingest if needed
        status = rag_service.get_status()
        print(f"📊 Database status: {status.get('newspaper_count', 0)} newspapers")
        
        if status.get('newspaper_count', 0) == 0:
            print("📦 Database empty, auto-ingesting newspapers...")
            # Try both directories
            try:
                count = rag_service.ingest_from_directory('./data/Newspaper')
                print(f"✅ Ingested {count} newspapers from data/Newspaper")
            except:
                count = rag_service.ingest_from_directory('./mock_responses')
                print(f"✅ Ingested {count} newspapers from mock_responses")
        
        
        # Search for newspapers (get 4 results: 1 main + 3 suggestions)
        print(f"\n🔍 Searching for: '{query}'")
        results = rag_service.search_with_llm(query, n_results=4)
        
        print(f"\n📋 Search Results:")
        print(f"   Found: {len(results.get('newspapers', []))} newspapers")
        
        if results.get('newspapers'):
            for i, np in enumerate(results['newspapers'][:4]):  # Show all 4
                meta = np.get('metadata', {})
                print(f"   {i+1}. {meta.get('title', 'Unknown')} - {meta.get('date', 'Unknown')}")
                print(f"      Similarity: {np.get('similarity', 0):.4f}")
                print(f"      Articles: {meta.get('article_count', 0)}")
        
        if not results.get('newspapers') or len(results['newspapers']) == 0:
            print("❌ No newspapers found!")
            return jsonify({
                "error": "No newspapers found matching your query"
            }), 404
        
        # Get the best match (main result)
        best_newspaper = results['newspapers'][0]
        best_meta = best_newspaper.get('metadata', {})
        
        print(f"\n✅ Selected Best Match:")
        print(f"   Title: {best_meta.get('title', 'Unknown')}")
        print(f"   Date: {best_meta.get('date', 'Unknown')}")
        print(f"   ID: {best_newspaper.get('id', 'Unknown')}")
        print(f"   Similarity Score: {best_newspaper.get('similarity', 0):.4f}")
        
        # Get the full JSON
        newspaper_json = best_newspaper.get('json', {})
        print(f"\n📄 Newspaper JSON:")
        print(f"   Has 'lccn': {('lccn' in newspaper_json)}")
        print(f"   Has 'edition': {('edition' in newspaper_json)}")
        print(f"   Has 'full articles': {('full articles' in newspaper_json)}")
        print(f"   Has 'bboxes': {('bboxes' in newspaper_json)}")
        print(f"   Article count: {len(newspaper_json.get('full articles', []))}")
        print(f"   Bbox count: {len(newspaper_json.get('bboxes', []))}")
        
        # Prepare alternative suggestions (next 3 results)
        suggestions = []
        for i, np in enumerate(results['newspapers'][1:4]):  # Get next 3
            suggestions.append({
                "id": np.get('id', f'suggestion_{i}'),
                "title": np.get('metadata', {}).get('title', 'Unknown'),
                "date": np.get('metadata', {}).get('date', 'Unknown'),
                "similarity": np.get('similarity', 0),
                "article_count": np.get('metadata', {}).get('article_count', 0),
                "newspaper_json": np.get('json', {})
            })
        
        print(f"\n💡 Returning {len(suggestions)} alternative suggestions")
        print(f"{'='*60}\n")
        
        # Return formatted response with suggestions
        return jsonify({
            "newspaper": newspaper_json,  # Main result
            "summary": results.get('llm_summary', ''),
            "query": query,
            "total_found": len(results['newspapers']),
            "selected_id": best_newspaper.get('id', 'Unknown'),
            "similarity": best_newspaper.get('similarity', 0),
            "suggestions": suggestions  # 3 alternative layouts
        }), 200
    
    except Exception as e:
        print(f"❌ Error generating newspaper layout: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": str(e)
        }), 500

