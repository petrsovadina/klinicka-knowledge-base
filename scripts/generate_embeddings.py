#!/usr/bin/env python3
"""
Generate embeddings for knowledge units using sklearn TF-IDF.
Simple but effective for MVP.
"""
import json
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import pickle

# Paths
DATA_DIR = Path("/home/ubuntu/klinicka-knowledge-base/data")
INPUT_FILE = DATA_DIR / "knowledge_base_final.jsonl"
OUTPUT_FILE = DATA_DIR / "knowledge_base_embeddings.jsonl"
VECTORIZER_FILE = DATA_DIR / "tfidf_vectorizer.pkl"
SVD_FILE = DATA_DIR / "svd_model.pkl"

# Embedding dimension
EMBEDDING_DIM = 256

def create_embedding_text(unit):
    """Create text representation for embedding."""
    parts = [
        unit['type'],
        unit['domain'],
        unit['title'],
        unit['description'],
    ]
    
    if 'tags' in unit and unit['tags']:
        parts.extend(unit['tags'])
    
    return " ".join(parts)

def main():
    print("="*80)
    print("GENERATING EMBEDDINGS (TF-IDF + SVD)")
    print("="*80)
    print()
    
    # Load knowledge units
    units = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                units.append(json.loads(line))
    
    print(f"Loaded {len(units)} knowledge units")
    
    # Create texts
    texts = [create_embedding_text(unit) for unit in units]
    
    # TF-IDF vectorization
    print("Creating TF-IDF vectors...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95
    )
    tfidf_matrix = vectorizer.fit_transform(texts)
    print(f"✓ TF-IDF matrix: {tfidf_matrix.shape}")
    
    # Dimensionality reduction with SVD
    print(f"Reducing to {EMBEDDING_DIM} dimensions...")
    svd = TruncatedSVD(n_components=min(EMBEDDING_DIM, tfidf_matrix.shape[1] - 1))
    embeddings = svd.fit_transform(tfidf_matrix)
    print(f"✓ Embeddings: {embeddings.shape}")
    
    # Normalize embeddings
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1
    embeddings = embeddings / norms
    
    # Save vectorizer and SVD for later use
    with open(VECTORIZER_FILE, 'wb') as f:
        pickle.dump(vectorizer, f)
    with open(SVD_FILE, 'wb') as f:
        pickle.dump(svd, f)
    print(f"✓ Saved vectorizer and SVD model")
    
    # Save embeddings
    print(f"Saving embeddings to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for i, unit in enumerate(units):
            result = {
                "id": unit["id"],
                "embedding": embeddings[i].tolist(),
                "metadata": {
                    "type": unit["type"],
                    "domain": unit["domain"],
                    "title": unit["title"],
                    "version": unit.get("version", "unknown")
                }
            }
            f.write(json.dumps(result, ensure_ascii=False) + '\n')
    
    print(f"✓ Saved {len(units)} embeddings")
    
    # Summary
    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total embeddings: {len(units)}")
    print(f"Embedding dimension: {embeddings.shape[1]}")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
    print("="*80)

if __name__ == "__main__":
    main()
