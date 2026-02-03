#!/usr/bin/env python3
"""
Test RAG MVP with 10 real doctor questions - offline version (no API server required).
Performs TF-IDF similarity search directly on the knowledge base.
"""
import json
import numpy as np
from pathlib import Path
import pickle
import argparse
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"

# 10 reálných dotazů lékaře (same as test_rag.py)
TEST_QUESTIONS = [
    "Co se stane, když překročím PURO v roce 2025?",
    "Jaké mám riziko při změně IČZ?",
    "Jak se liší úhrady oproti minulému roku?",
    "Co je MAXÚ a jak funguje?",
    "Jaké jsou bonifikace za ordinační hodiny?",
    "Co je předběžná měsíční úhrada a jak se počítá?",
    "Jaká jsou rizika při převzetí ordinace?",
    "Co znamená hodnota bodu 0,94 Kč?",
    "Jak funguje regulace na léky?",
    "Co je koeficient navýšení a jak ho získám?",
]


def create_embedding_text(unit):
    """Create text representation for embedding (same as generate_embeddings.py)."""
    parts = [
        unit.get('type', ''),
        unit.get('domain', ''),
        unit.get('title', ''),
        unit.get('description', ''),
    ]

    if 'tags' in unit and unit['tags']:
        parts.extend(unit['tags'])

    return " ".join(parts)


def load_knowledge_base(input_file):
    """Load knowledge base from JSONL file."""
    units = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                units.append(json.loads(line))
    return units


def search_similar(query, vectorizer, svd, units, embeddings, top_k=5):
    """Search for similar knowledge units using TF-IDF similarity."""
    # Transform query
    query_tfidf = vectorizer.transform([query])
    query_embedding = svd.transform(query_tfidf)

    # Normalize
    norm = np.linalg.norm(query_embedding)
    if norm > 0:
        query_embedding = query_embedding / norm

    # Compute cosine similarity
    similarities = np.dot(embeddings, query_embedding.T).flatten()

    # Get top-k indices
    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for idx in top_indices:
        results.append({
            "id": units[idx]["id"],
            "score": float(similarities[idx]),
            "title": units[idx]["title"],
            "description": units[idx]["description"],
            "type": units[idx]["type"],
            "domain": units[idx]["domain"],
        })

    return results


def main():
    parser = argparse.ArgumentParser(description='Test RAG with 10 real doctor questions (offline)')
    parser.add_argument('--input', '-i', default='knowledge_base_expanded_v2.jsonl',
                        help='Input knowledge base JSONL file')
    parser.add_argument('--output', '-o', default='test_results_v2.json',
                        help='Output test results JSON file')
    parser.add_argument('--compare', '-c', default=None,
                        help='Compare with previous results file (e.g., test_results.json)')
    args = parser.parse_args()

    input_file = DATA_DIR / args.input
    output_file = DATA_DIR / args.output
    vectorizer_file = DATA_DIR / "tfidf_vectorizer.pkl"
    svd_file = DATA_DIR / "svd_model.pkl"

    print("="*80)
    print("RAG OFFLINE TEST - 10 REÁLNÝCH DOTAZŮ LÉKAŘE")
    print("="*80)
    print(f"Knowledge base: {input_file}")
    print()

    # Load vectorizer and SVD
    with open(vectorizer_file, 'rb') as f:
        vectorizer = pickle.load(f)
    with open(svd_file, 'rb') as f:
        svd = pickle.load(f)

    # Load knowledge base and compute embeddings
    units = load_knowledge_base(input_file)
    print(f"Loaded {len(units)} knowledge units")

    # Create embeddings for all units
    texts = [create_embedding_text(unit) for unit in units]
    tfidf_matrix = vectorizer.transform(texts)
    embeddings = svd.transform(tfidf_matrix)

    # Normalize embeddings
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1
    embeddings = embeddings / norms

    # Load previous results for comparison if specified
    previous_results = None
    if args.compare:
        compare_file = DATA_DIR / args.compare
        if compare_file.exists():
            with open(compare_file, 'r', encoding='utf-8') as f:
                prev_data = json.load(f)
                # Handle both old format (list) and new format (dict with 'results')
                if isinstance(prev_data, list):
                    previous_results = prev_data
                elif isinstance(prev_data, dict) and 'results' in prev_data:
                    previous_results = prev_data['results']
                else:
                    print(f"Warning: Unknown format in {compare_file}, skipping comparison")
            if previous_results:
                print(f"Loaded previous results from {compare_file} for comparison")

    results = []

    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n{'='*80}")
        print(f"DOTAZ {i}: {question}")
        print("="*80)

        # Search for similar units
        sources = search_similar(question, vectorizer, svd, units, embeddings, top_k=5)

        print(f"\nNALEZENÉ ZDROJE:")
        for j, source in enumerate(sources[:3], 1):
            print(f"  {j}. [{source['id']}] {source['title']} (score: {source['score']:.3f})")

        # Compare with previous if available
        if previous_results:
            prev = previous_results[i-1]
            prev_score = prev.get('top_score', 0)
            curr_score = sources[0]['score'] if sources else 0
            delta = curr_score - prev_score
            delta_str = f"+{delta:.3f}" if delta >= 0 else f"{delta:.3f}"
            print(f"\n  SROVNÁNÍ: předchozí top_score={prev_score:.3f}, nový={curr_score:.3f}, delta={delta_str}")

        # Store for analysis
        result = {
            "question": question,
            "sources": sources,
            "top_score": sources[0]["score"] if sources else 0
        }
        results.append(result)

    # Summary
    print("\n" + "="*80)
    print("SHRNUTÍ TESTU")
    print("="*80)

    avg_score = sum(r["top_score"] for r in results) / len(results)
    print(f"\nPrůměrné skóre top výsledku: {avg_score:.3f}")

    if previous_results:
        prev_avg = sum(r.get("top_score", 0) for r in previous_results) / len(previous_results)
        delta = avg_score - prev_avg
        delta_str = f"+{delta:.3f}" if delta >= 0 else f"{delta:.3f}"
        pct_change = (delta / prev_avg) * 100 if prev_avg > 0 else 0
        print(f"Předchozí průměrné skóre: {prev_avg:.3f}")
        print(f"Změna: {delta_str} ({pct_change:+.1f}%)")

    # Identify gaps (low scores)
    print("\nIDENTIFIKOVANÉ MEZERY (nízké skóre < 0.3):")
    low_score_count = 0
    for r in results:
        if r["top_score"] < 0.3:
            low_score_count += 1
            print(f"  - Nízké skóre ({r['top_score']:.3f}): {r['question']}")

    if low_score_count == 0:
        print("  Žádné dotazy s nízkým skóre!")

    # Save results with metadata
    output_data = {
        "metadata": {
            "test_date": datetime.now().isoformat(),
            "knowledge_base": str(input_file),
            "knowledge_units_count": len(units),
            "average_top_score": avg_score,
        },
        "results": results
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Výsledky uloženy do {output_file}")

    # Return summary for reporting
    return {
        "units_count": len(units),
        "avg_score": avg_score,
        "prev_avg_score": prev_avg if previous_results else None,
        "improvement_pct": pct_change if previous_results else None,
        "low_score_count": low_score_count,
    }


if __name__ == "__main__":
    main()
