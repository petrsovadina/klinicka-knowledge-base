#!/usr/bin/env python3
"""
RAG MVP API for Klinicka Knowledge Base.
Production-ready FastAPI endpoint for semantic search and Q&A.

Features:
- Semantic search over knowledge base
- RAG-based Q&A with context retrieval
- Response caching for repeated queries
- Rate limiting for API protection
- Health and metrics endpoints for monitoring
"""
import asyncio
import hashlib
import json
import numpy as np
import os
import pickle
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI

# ============================================================================
# Configuration
# ============================================================================

# Data paths - use environment variable or default
DATA_DIR = Path(os.getenv("DATA_DIR", "/home/ubuntu/klinicka-knowledge-base/data"))
EMBEDDINGS_FILE = DATA_DIR / "knowledge_base_embeddings.jsonl"
KNOWLEDGE_FILE = DATA_DIR / "knowledge_base_final.jsonl"
VECTORIZER_FILE = DATA_DIR / "tfidf_vectorizer.pkl"
SVD_FILE = DATA_DIR / "svd_model.pkl"

# Rate limiting configuration
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))  # requests per window
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

# Cache configuration
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes default
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "1000"))  # max cached items

# ============================================================================
# Metrics Collection
# ============================================================================

@dataclass
class APIMetrics:
    """Metrics collector for API monitoring."""
    start_time: datetime = field(default_factory=datetime.now)
    total_requests: int = 0
    search_requests: int = 0
    qa_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    rate_limited_requests: int = 0
    error_count: int = 0
    total_latency_ms: float = 0.0
    request_count_for_latency: int = 0
    _lock: Lock = field(default_factory=Lock)

    def record_request(self, endpoint: str, latency_ms: float, cache_hit: bool = False):
        with self._lock:
            self.total_requests += 1
            self.total_latency_ms += latency_ms
            self.request_count_for_latency += 1

            if endpoint == "search":
                self.search_requests += 1
            elif endpoint == "qa":
                self.qa_requests += 1

            if cache_hit:
                self.cache_hits += 1
            else:
                self.cache_misses += 1

    def record_rate_limit(self):
        with self._lock:
            self.rate_limited_requests += 1

    def record_error(self):
        with self._lock:
            self.error_count += 1

    def get_metrics(self) -> dict:
        with self._lock:
            uptime_seconds = (datetime.now() - self.start_time).total_seconds()
            avg_latency = (
                self.total_latency_ms / self.request_count_for_latency
                if self.request_count_for_latency > 0 else 0
            )
            cache_hit_rate = (
                self.cache_hits / (self.cache_hits + self.cache_misses) * 100
                if (self.cache_hits + self.cache_misses) > 0 else 0
            )

            return {
                "uptime_seconds": round(uptime_seconds, 2),
                "total_requests": self.total_requests,
                "requests_per_minute": round(self.total_requests / max(uptime_seconds / 60, 1), 2),
                "search_requests": self.search_requests,
                "qa_requests": self.qa_requests,
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "cache_hit_rate_percent": round(cache_hit_rate, 2),
                "rate_limited_requests": self.rate_limited_requests,
                "error_count": self.error_count,
                "avg_latency_ms": round(avg_latency, 2)
            }

metrics = APIMetrics()

# ============================================================================
# Rate Limiter
# ============================================================================

class RateLimiter:
    """Simple sliding window rate limiter."""

    def __init__(self, max_requests: int = RATE_LIMIT_REQUESTS, window_seconds: int = RATE_LIMIT_WINDOW):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make a request."""
        now = time.time()

        with self._lock:
            # Clean old requests
            cutoff = now - self.window_seconds
            self.requests[client_id] = [
                t for t in self.requests[client_id] if t > cutoff
            ]

            # Check limit
            if len(self.requests[client_id]) >= self.max_requests:
                return False

            # Record request
            self.requests[client_id].append(now)
            return True

    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for client."""
        now = time.time()
        cutoff = now - self.window_seconds

        with self._lock:
            recent = [t for t in self.requests[client_id] if t > cutoff]
            return max(0, self.max_requests - len(recent))

rate_limiter = RateLimiter()

# ============================================================================
# Response Cache
# ============================================================================

class ResponseCache:
    """TTL-based response cache for search and QA results."""

    def __init__(self, ttl_seconds: int = CACHE_TTL, max_size: int = CACHE_MAX_SIZE):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self.cache: Dict[str, tuple] = {}  # key -> (value, timestamp)
        self._lock = Lock()

    def _hash_key(self, query: str, top_k: int, endpoint: str) -> str:
        """Generate cache key from query parameters."""
        key_str = f"{endpoint}:{query.lower().strip()}:{top_k}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, query: str, top_k: int, endpoint: str) -> Optional[dict]:
        """Get cached response if valid."""
        key = self._hash_key(query, top_k, endpoint)
        now = time.time()

        with self._lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if now - timestamp < self.ttl_seconds:
                    return value
                # Expired - remove
                del self.cache[key]
        return None

    def set(self, query: str, top_k: int, endpoint: str, value: dict):
        """Cache a response."""
        key = self._hash_key(query, top_k, endpoint)
        now = time.time()

        with self._lock:
            # Evict oldest if at capacity
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
                del self.cache[oldest_key]

            self.cache[key] = (value, now)

    def clear(self):
        """Clear all cached items."""
        with self._lock:
            self.cache.clear()

    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)

response_cache = ResponseCache()

# ============================================================================
# Data Loading
# ============================================================================

knowledge_units: Dict[str, dict] = {}
embeddings: Dict[str, np.ndarray] = {}
embedding_ids: List[str] = []
embedding_matrix: Optional[np.ndarray] = None
vectorizer = None
svd = None
data_loaded = False

def load_data():
    """Load knowledge base data at startup."""
    global knowledge_units, embeddings, embedding_ids, embedding_matrix, vectorizer, svd, data_loaded

    if data_loaded:
        return True

    try:
        # Check if data files exist
        if not KNOWLEDGE_FILE.exists():
            print(f"Warning: Knowledge file not found at {KNOWLEDGE_FILE}")
            return False

        # Load knowledge units
        with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                unit = json.loads(line.strip())
                knowledge_units[unit['id']] = unit

        # Load embeddings if available
        if EMBEDDINGS_FILE.exists():
            emb_list = []
            with open(EMBEDDINGS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line.strip())
                    embedding_ids.append(data['id'])
                    emb_list.append(data['embedding'])

            embedding_matrix = np.array(emb_list)

        # Load vectorizer and SVD if available
        if VECTORIZER_FILE.exists() and SVD_FILE.exists():
            with open(VECTORIZER_FILE, 'rb') as f:
                vectorizer = pickle.load(f)
            with open(SVD_FILE, 'rb') as f:
                svd = pickle.load(f)

        data_loaded = True
        print(f"Loaded {len(knowledge_units)} knowledge units")
        print(f"Loaded {len(embedding_ids)} embeddings")
        return True

    except Exception as e:
        print(f"Error loading data: {e}")
        return False

# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Klinicka Knowledge Base RAG API",
    description="Production-ready API for semantic search and Q&A over Czech medical practice knowledge base",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Request/Response Models
# ============================================================================

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
    cached: bool = False

class QARequest(BaseModel):
    question: str
    top_k: int = 5

class QAResponse(BaseModel):
    question: str
    answer: str
    sources: List[SearchResult]
    cached: bool = False

class HealthResponse(BaseModel):
    status: str
    version: str
    knowledge_units: int
    embeddings: int
    data_loaded: bool
    timestamp: str

class MetricsResponse(BaseModel):
    uptime_seconds: float
    total_requests: int
    requests_per_minute: float
    search_requests: int
    qa_requests: int
    cache_hits: int
    cache_misses: int
    cache_hit_rate_percent: float
    rate_limited_requests: int
    error_count: int
    avg_latency_ms: float
    cache_size: int

# ============================================================================
# Startup Event
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize data on startup."""
    load_data()

# ============================================================================
# Middleware for Rate Limiting
# ============================================================================

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to all endpoints except health and metrics."""
    # Skip rate limiting for health/metrics endpoints
    if request.url.path in ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)

    # Get client identifier (IP address or API key if implemented)
    client_id = request.client.host if request.client else "unknown"

    if not rate_limiter.is_allowed(client_id):
        metrics.record_rate_limit()
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "detail": f"Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds",
                "retry_after_seconds": RATE_LIMIT_WINDOW
            },
            headers={"Retry-After": str(RATE_LIMIT_WINDOW)}
        )

    # Add rate limit headers
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(rate_limiter.get_remaining(client_id))
    response.headers["X-RateLimit-Window"] = str(RATE_LIMIT_WINDOW)

    return response

# ============================================================================
# Core Functions
# ============================================================================

def embed_query(query: str) -> np.ndarray:
    """Embed a query using TF-IDF + SVD pipeline."""
    if vectorizer is None or svd is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Embedding models not loaded"
        )

    tfidf = vectorizer.transform([query])
    embedding = svd.transform(tfidf)
    # Normalize
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    return embedding[0]

def search(query: str, top_k: int = 5) -> List[dict]:
    """Search for relevant knowledge units."""
    if embedding_matrix is None or len(embedding_ids) == 0:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Embeddings not loaded"
        )

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

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
def root():
    """Root endpoint with basic API info."""
    return {
        "status": "ok",
        "name": "Klinicka Knowledge Base RAG API",
        "version": "1.0.0",
        "units": len(knowledge_units),
        "endpoints": {
            "search": "/search",
            "qa": "/qa",
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthResponse)
def health_endpoint():
    """
    Health check endpoint for monitoring and load balancers.

    Returns service health status including:
    - Data loading status
    - Number of loaded knowledge units
    - Number of loaded embeddings
    """
    return HealthResponse(
        status="healthy" if data_loaded else "degraded",
        version="1.0.0",
        knowledge_units=len(knowledge_units),
        embeddings=len(embedding_ids),
        data_loaded=data_loaded,
        timestamp=datetime.now().isoformat()
    )

@app.get("/metrics", response_model=MetricsResponse)
def metrics_endpoint():
    """
    Metrics endpoint for observability and monitoring dashboards.

    Returns operational metrics including:
    - Request counts by endpoint
    - Cache hit rates
    - Rate limiting statistics
    - Average latency
    """
    m = metrics.get_metrics()
    return MetricsResponse(
        **m,
        cache_size=response_cache.size()
    )

@app.post("/search", response_model=SearchResponse)
def search_endpoint(request: SearchRequest):
    """
    Semantic search over knowledge base.

    Returns top-k most relevant knowledge units for the given query.
    Results are cached for improved performance on repeated queries.
    """
    start_time = time.time()

    # Check cache
    cached = response_cache.get(request.query, request.top_k, "search")
    if cached:
        latency = (time.time() - start_time) * 1000
        metrics.record_request("search", latency, cache_hit=True)
        return SearchResponse(**cached, cached=True)

    try:
        results = search(request.query, request.top_k)
        response_data = {"query": request.query, "results": results}

        # Cache response
        response_cache.set(request.query, request.top_k, "search", response_data)

        latency = (time.time() - start_time) * 1000
        metrics.record_request("search", latency, cache_hit=False)

        return SearchResponse(**response_data, cached=False)

    except Exception as e:
        metrics.record_error()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )

@app.post("/qa", response_model=QAResponse)
def qa_endpoint(request: QARequest):
    """
    Question answering with RAG (Retrieval-Augmented Generation).

    Retrieves relevant context from knowledge base and generates
    an answer using GPT-4.1-mini. Results are cached for improved
    performance on repeated questions.
    """
    start_time = time.time()

    # Check cache
    cached = response_cache.get(request.question, request.top_k, "qa")
    if cached:
        latency = (time.time() - start_time) * 1000
        metrics.record_request("qa", latency, cache_hit=True)
        return QAResponse(**cached, cached=True)

    try:
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

        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        answer = response.choices[0].message.content.strip()

        response_data = {
            "question": request.question,
            "answer": answer,
            "sources": search_results
        }

        # Cache response
        response_cache.set(request.question, request.top_k, "qa", response_data)

        latency = (time.time() - start_time) * 1000
        metrics.record_request("qa", latency, cache_hit=False)

        return QAResponse(**response_data, cached=False)

    except Exception as e:
        metrics.record_error()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"QA error: {str(e)}"
        )

@app.get("/unit/{unit_id}")
def get_unit(unit_id: str):
    """Get a specific knowledge unit by ID."""
    if unit_id not in knowledge_units:
        raise HTTPException(status_code=404, detail="Unit not found")
    return knowledge_units[unit_id]

@app.post("/cache/clear")
def clear_cache():
    """Clear the response cache. Admin endpoint."""
    response_cache.clear()
    return {"status": "ok", "message": "Cache cleared"}

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
