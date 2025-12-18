#!/usr/bin/env python3
"""
RAG MVP API for Klinicka Knowledge Base.
Simple FastAPI endpoint for semantic search and Q&A.
"""
import json
import numpy as np
import pickle
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

# Initialize
app = FastAPI(title="Klinicka Knowledge Base RAG API", version="0.1.0")
client = OpenAI()

# Paths
DATA_DIR = Path("/home/ubuntu/klinicka-knowledge-base/data")
EMBEDDINGS_FILE = DATA_DIR / "knowledge_base_embeddings.jsonl"
KNOWLEDGE_FILE = DATA_DIR / "knowledge_base_final.jsonl"
VECTORIZER_FILE = DATA_DIR / "tfidf_vectorizer.pkl"
SVD_FILE = DATA_DIR / "svd_model.pkl"

# Load data at startup
knowledge_units = {}
embeddings = {}
embedding_ids = []
embedding_matrix = None
vectorizer = None
svd = None

def load_data():
    global knowledge_units, embeddings, embedding_ids, embedding_matrix, vectorizer, svd
    
    # Load knowledge units
    with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            unit = json.loads(line.strip())
            knowledge_units[unit['id']] = unit
    
    # Load embeddings
    emb_list = []
    with open(EMBEDDINGS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            embedding_ids.append(data['id'])
            emb_list.append(data['embedding'])
    
    embedding_matrix = np.array(emb_list)
    
    # Load vectorizer and SVD
    with open(VECTORIZER_FILE, 'rb') as f:
        vectorizer = pickle.load(f)
    with open(SVD_FILE, 'rb') as f:
        svd = pickle.load(f)
    
    print(f"Loaded {len(knowledge_units)} knowledge units")
    print(f"Loaded {len(embedding_ids)} embeddings")

# Load on startup
load_data()

# Request/Response models
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchResult(BaseModel):
    id: str
    score: float
    title: str
    description: str
    type: str
    domain: str

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]

class QARequest(BaseModel):
    question: str
    top_k: int = 5

class QAResponse(BaseModel):
    question: str
    answer: str
    sources: List[SearchResult]

def embed_query(query: str) -> np.ndarray:
    """Embed a query using the same TF-IDF + SVD pipeline."""
    tfidf = vectorizer.transform([query])
    embedding = svd.transform(tfidf)
    # Normalize
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    return embedding[0]

def search(query: str, top_k: int = 5) -> List[dict]:
    """Search for relevant knowledge units."""
    query_embedding = embed_query(query)
    
    # Cosine similarity (embeddings are normalized)
    scores = embedding_matrix @ query_embedding
    
    # Get top-k
    top_indices = np.argsort(scores)[::-1][:top_k]
    
    results = []
    for idx in top_indices:
        unit_id = embedding_ids[idx]
        unit = knowledge_units[unit_id]
        results.append({
            "id": unit_id,
            "score": float(scores[idx]),
            "title": unit["title"],
            "description": unit["description"],
            "type": unit["type"],
            "domain": unit["domain"]
        })
    
    return results

@app.get("/")
def root():
    return {"status": "ok", "units": len(knowledge_units), "version": "0.1.0"}

@app.post("/search", response_model=SearchResponse)
def search_endpoint(request: SearchRequest):
    """Semantic search over knowledge base."""
    results = search(request.query, request.top_k)
    return SearchResponse(query=request.query, results=results)

@app.post("/qa", response_model=QAResponse)
def qa_endpoint(request: QARequest):
    """Question answering with RAG."""
    # Search for relevant context
    search_results = search(request.question, request.top_k)
    
    # Build context
    context_parts = []
    for r in search_results:
        unit = knowledge_units[r["id"]]
        context_parts.append(f"[{r['id']}] {unit['title']}: {unit['description']}")
    
    context = "\n\n".join(context_parts)
    
    # Generate answer
    prompt = f"""Jsi AI asistent pro lékaře v České republice. Odpovídej na základě poskytnutého kontextu.

KONTEXT:
{context}

OTÁZKA: {request.question}

INSTRUKCE:
- Odpověz stručně a věcně
- Cituj zdroje pomocí [ID]
- Pokud kontext neobsahuje odpověď, řekni to
- Nenavrhuj konkrétní vykazování, pouze vysvětluj pravidla

ODPOVĚĎ:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"Chyba při generování odpovědi: {str(e)}"
    
    return QAResponse(
        question=request.question,
        answer=answer,
        sources=search_results
    )

@app.get("/unit/{unit_id}")
def get_unit(unit_id: str):
    """Get a specific knowledge unit."""
    if unit_id not in knowledge_units:
        raise HTTPException(status_code=404, detail="Unit not found")
    return knowledge_units[unit_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
