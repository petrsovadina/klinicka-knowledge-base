#!/usr/bin/env python3
"""
MVP RAG Test Suite - Extended 25 Query Evaluation.

Tests the knowledge base with 25 realistic doctor queries covering:
- Úhrady (reimbursements)
- Provoz (operations)
- Compliance (regulatory)
- Finanční rizika (financial risks)
- Legislativa (legislation)
- Specific point values (hodnota bodu)
- Year-over-year comparisons (2025 vs 2026)

Target: 80%+ of queries should achieve score > 0.7
"""
import json
import numpy as np
import pickle
from pathlib import Path
from datetime import datetime

# Configuration
DATA_DIR = Path(__file__).parent.parent / "data"
KNOWLEDGE_FILE = DATA_DIR / "knowledge_base_mvp.jsonl"
VECTORIZER_FILE = DATA_DIR / "tfidf_vectorizer.pkl"
SVD_FILE = DATA_DIR / "svd_model.pkl"
EMBEDDINGS_FILE = DATA_DIR / "knowledge_base_embeddings.jsonl"
RESULTS_FILE = DATA_DIR / "test_results_mvp.json"

# 25 Extended Test Queries - Organized by Domain
TEST_QUERIES = [
    # === ÚHRADY (8 queries) ===
    {
        "query": "Jaká je hodnota bodu pro ambulantní specialisty v roce 2026?",
        "domain": "uhrady",
        "expected_topics": ["hodnota bodu", "0.98 Kč", "SAS"],
        "difficulty": "easy"
    },
    {
        "query": "Co je MAXÚ a jak se vypočítá maximální úhrada?",
        "domain": "uhrady",
        "expected_topics": ["MAXÚ", "koeficient", "maximální úhrada"],
        "difficulty": "medium"
    },
    {
        "query": "Jak funguje PURO a jaký je vzorec pro její výpočet?",
        "domain": "uhrady",
        "expected_topics": ["PURO", "průměrná úhrada", "unikátní pojištěnec"],
        "difficulty": "medium"
    },
    {
        "query": "Jaké jsou bonifikace za příjem nových pacientů v roce 2026?",
        "domain": "uhrady",
        "expected_topics": ["bonifikace", "+0.04", "+0.01", "noví pacienti"],
        "difficulty": "medium"
    },
    {
        "query": "Co je předběžná měsíční úhrada a jak se počítá PMÚ?",
        "domain": "uhrady",
        "expected_topics": ["PMÚ", "108%", "referenční období"],
        "difficulty": "medium"
    },
    {
        "query": "Jaké jsou podmínky pro bonifikaci za ordinační hodiny?",
        "domain": "uhrady",
        "expected_topics": ["ordinační hodiny", "bonifikace", "24 hodin", "30 hodin"],
        "difficulty": "medium"
    },
    {
        "query": "Kolik je koeficient navýšení KN podle odbornosti?",
        "domain": "uhrady",
        "expected_topics": ["koeficient navýšení", "KN", "odbornost"],
        "difficulty": "hard"
    },
    {
        "query": "Jak se hradí bílé plomby a endodoncie od roku 2026?",
        "domain": "uhrady",
        "expected_topics": ["stomatologie", "bílé plomby", "endodoncie"],
        "difficulty": "medium"
    },

    # === PROVOZ (5 queries) ===
    {
        "query": "Jaká je minimální měsíční záloha OSVČ pro zdravotní pojištění v roce 2026?",
        "domain": "provoz",
        "expected_topics": ["OSVČ", "záloha", "3306 Kč"],
        "difficulty": "easy"
    },
    {
        "query": "Co je checklist při nákupu lékařské praxe?",
        "domain": "provoz",
        "expected_topics": ["checklist", "nákup", "ordinace", "kontrola"],
        "difficulty": "medium"
    },
    {
        "query": "Jak optimalizovat PURO v ambulantní praxi?",
        "domain": "provoz",
        "expected_topics": ["PURO", "optimalizace", "strategie"],
        "difficulty": "medium"
    },
    {
        "query": "Jaké je minimální pojistné pro zaměstnavatele od roku 2026?",
        "domain": "provoz",
        "expected_topics": ["minimální pojistné", "zaměstnavatel", "3024 Kč"],
        "difficulty": "easy"
    },
    {
        "query": "Musím používat objednávkový systém pro bonifikaci?",
        "domain": "provoz",
        "expected_topics": ["objednávkový systém", "bonifikace", "podmínky"],
        "difficulty": "medium"
    },

    # === COMPLIANCE (4 queries) ===
    {
        "query": "Jaké jsou nové povinnosti elektronické komunikace se zdravotními pojišťovnami?",
        "domain": "compliance",
        "expected_topics": ["elektronická komunikace", "povinnost", "ZP"],
        "difficulty": "medium"
    },
    {
        "query": "Které odbornosti jsou vyjmuty z regulací v roce 2026?",
        "domain": "compliance",
        "expected_topics": ["výjimka", "regulace", "odbornosti"],
        "difficulty": "hard"
    },
    {
        "query": "Co se změnilo v novele zákona o zdravotním pojištění od ledna 2026?",
        "domain": "compliance",
        "expected_topics": ["novela", "zákon", "2026"],
        "difficulty": "medium"
    },
    {
        "query": "Mohu platit pojistné hotově v roce 2026?",
        "domain": "compliance",
        "expected_topics": ["bezhotovostní", "platba", "pojistné"],
        "difficulty": "easy"
    },

    # === FINANČNÍ RIZIKA (4 queries) ===
    {
        "query": "Jaká jsou rizika při převzetí ordinace s existujícím IČZ?",
        "domain": "financni-rizika",
        "expected_topics": ["riziko", "převzetí", "IČZ", "skryté"],
        "difficulty": "medium"
    },
    {
        "query": "Co je anti-pattern nízká PURO bez nových pacientů?",
        "domain": "financni-rizika",
        "expected_topics": ["anti-pattern", "PURO", "noví pacienti"],
        "difficulty": "medium"
    },
    {
        "query": "Jak funguje regulace na předepsané léky a jaké jsou limity?",
        "domain": "financni-rizika",
        "expected_topics": ["regulace", "léčiva", "115%"],
        "difficulty": "medium"
    },
    {
        "query": "Jaké jsou penalizace za nesplnění bonifikačních podmínek?",
        "domain": "financni-rizika",
        "expected_topics": ["penalizace", "koeficient", "-0.01"],
        "difficulty": "hard"
    },

    # === MEZIROČNÍ SROVNÁNÍ 2025 vs 2026 (4 queries) ===
    {
        "query": "Jak se změnila hodnota bodu pro ambulantní specialisty oproti roku 2025?",
        "domain": "uhrady",
        "expected_topics": ["hodnota bodu", "2025", "2026", "změna"],
        "difficulty": "medium",
        "comparison": True
    },
    {
        "query": "Co se změnilo v koeficientu MAXÚ oproti minulému roku?",
        "domain": "uhrady",
        "expected_topics": ["MAXÚ", "koeficient", "1.03", "1.065"],
        "difficulty": "medium",
        "comparison": True
    },
    {
        "query": "Jak se liší HBmin v roce 2026 oproti roku 2025?",
        "domain": "uhrady",
        "expected_topics": ["HBmin", "0.90", "1.03", "změna"],
        "difficulty": "medium",
        "comparison": True
    },
    {
        "query": "Změnily se nějak limity regulací na preskripci oproti roku 2025?",
        "domain": "financni-rizika",
        "expected_topics": ["regulace", "preskripce", "110%", "115%"],
        "difficulty": "hard",
        "comparison": True
    }
]


def load_knowledge_base():
    """Load knowledge units from JSONL."""
    knowledge_units = {}
    with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            unit = json.loads(line.strip())
            knowledge_units[unit['id']] = unit
    return knowledge_units


def load_embeddings():
    """Load embeddings and models."""
    # Load vectorizer and SVD
    with open(VECTORIZER_FILE, 'rb') as f:
        vectorizer = pickle.load(f)
    with open(SVD_FILE, 'rb') as f:
        svd = pickle.load(f)

    # Load embeddings
    embedding_ids = []
    emb_list = []
    with open(EMBEDDINGS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            embedding_ids.append(data['id'])
            emb_list.append(data['embedding'])

    embedding_matrix = np.array(emb_list)

    return vectorizer, svd, embedding_ids, embedding_matrix


def embed_query(query: str, vectorizer, svd) -> np.ndarray:
    """Embed a query using the TF-IDF + SVD pipeline."""
    tfidf = vectorizer.transform([query])
    embedding = svd.transform(tfidf)
    # Normalize
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    return embedding[0]


def search(query: str, vectorizer, svd, embedding_ids, embedding_matrix, knowledge_units, top_k: int = 5):
    """Search for relevant knowledge units."""
    query_embedding = embed_query(query, vectorizer, svd)

    # Cosine similarity (embeddings are normalized)
    scores = embedding_matrix @ query_embedding

    # Get top-k
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        unit_id = embedding_ids[idx]
        if unit_id in knowledge_units:
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


def evaluate_result(result, test_query):
    """Evaluate a search result against expected topics."""
    top_score = result[0]["score"] if result else 0

    # Check if any expected topics are found in the top results
    combined_text = " ".join([
        r["title"].lower() + " " + r["description"].lower()
        for r in result[:3]
    ])

    topics_found = 0
    for topic in test_query.get("expected_topics", []):
        if topic.lower() in combined_text:
            topics_found += 1

    topic_coverage = topics_found / len(test_query.get("expected_topics", [1])) if test_query.get("expected_topics") else 0

    return {
        "top_score": top_score,
        "topic_coverage": topic_coverage,
        "topics_found": topics_found,
        "topics_expected": len(test_query.get("expected_topics", []))
    }


def run_tests():
    """Run all tests and generate results."""
    print("=" * 80)
    print("MVP RAG TEST SUITE - 25 EXTENDED QUERIES")
    print("=" * 80)
    print()

    # Load data
    print("Loading knowledge base...")
    knowledge_units = load_knowledge_base()
    print(f"  Loaded {len(knowledge_units)} knowledge units")

    print("Loading embeddings and models...")
    vectorizer, svd, embedding_ids, embedding_matrix = load_embeddings()
    print(f"  Loaded {len(embedding_ids)} embeddings")
    print()

    # Run tests
    results = []
    domain_scores = {}

    for i, test_query in enumerate(TEST_QUERIES, 1):
        print(f"\n{'─' * 80}")
        print(f"QUERY {i:02d}: {test_query['query']}")
        print(f"Domain: {test_query['domain']} | Difficulty: {test_query.get('difficulty', 'medium')}")
        if test_query.get('comparison'):
            print("(Year-over-year comparison query)")
        print("─" * 80)

        # Search
        search_results = search(
            test_query['query'],
            vectorizer, svd, embedding_ids, embedding_matrix, knowledge_units,
            top_k=5
        )

        # Evaluate
        evaluation = evaluate_result(search_results, test_query)

        # Display results
        print(f"\nTop Score: {evaluation['top_score']:.3f}")
        print(f"Topic Coverage: {evaluation['topics_found']}/{evaluation['topics_expected']} ({evaluation['topic_coverage']*100:.0f}%)")

        print("\nTop 3 Results:")
        for j, r in enumerate(search_results[:3], 1):
            print(f"  {j}. [{r['id']}] {r['title'][:60]}...")
            print(f"     Score: {r['score']:.3f} | Domain: {r['domain']}")

        # Track domain performance
        domain = test_query['domain']
        if domain not in domain_scores:
            domain_scores[domain] = []
        domain_scores[domain].append(evaluation['top_score'])

        # Store result
        results.append({
            "query": test_query['query'],
            "domain": test_query['domain'],
            "difficulty": test_query.get('difficulty', 'medium'),
            "is_comparison": test_query.get('comparison', False),
            "top_score": evaluation['top_score'],
            "topic_coverage": evaluation['topic_coverage'],
            "sources": search_results[:5]
        })

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    # Overall metrics
    all_scores = [r['top_score'] for r in results]
    avg_score = np.mean(all_scores)
    above_07 = sum(1 for s in all_scores if s > 0.7)
    above_05 = sum(1 for s in all_scores if s > 0.5)
    success_rate = above_07 / len(all_scores) * 100

    print(f"\nOVERALL METRICS:")
    print(f"  Total Queries: {len(results)}")
    print(f"  Average Top Score: {avg_score:.3f}")
    print(f"  Queries with Score > 0.7: {above_07}/{len(results)} ({success_rate:.1f}%)")
    print(f"  Queries with Score > 0.5: {above_05}/{len(results)} ({above_05/len(results)*100:.1f}%)")
    print(f"\n  TARGET: 80%+ with score > 0.7")
    print(f"  STATUS: {'✓ PASSED' if success_rate >= 80 else '✗ FAILED'}")

    # Domain breakdown
    print(f"\nDOMAIN BREAKDOWN:")
    for domain, scores in sorted(domain_scores.items()):
        domain_avg = np.mean(scores)
        domain_above_07 = sum(1 for s in scores if s > 0.7)
        print(f"  {domain}: avg={domain_avg:.3f}, >0.7={domain_above_07}/{len(scores)}")

    # Comparison queries
    comparison_results = [r for r in results if r.get('is_comparison')]
    if comparison_results:
        comparison_avg = np.mean([r['top_score'] for r in comparison_results])
        print(f"\nYEAR-OVER-YEAR COMPARISONS:")
        print(f"  Queries: {len(comparison_results)}")
        print(f"  Average Score: {comparison_avg:.3f}")

    # Identified gaps (low scores)
    print(f"\nIDENTIFIED GAPS (Score < 0.5):")
    gaps = [r for r in results if r['top_score'] < 0.5]
    if gaps:
        for r in gaps:
            print(f"  - [{r['domain']}] {r['query'][:50]}... (score: {r['top_score']:.3f})")
    else:
        print("  None - all queries scored above 0.5")

    # Save results
    output = {
        "metadata": {
            "test_date": datetime.now().isoformat(),
            "knowledge_base": str(KNOWLEDGE_FILE),
            "knowledge_units_count": len(knowledge_units),
            "total_queries": len(results),
            "average_top_score": avg_score,
            "success_rate_07": success_rate,
            "target_met": success_rate >= 80
        },
        "domain_summary": {
            domain: {
                "count": len(scores),
                "average": float(np.mean(scores)),
                "above_07": sum(1 for s in scores if s > 0.7)
            }
            for domain, scores in domain_scores.items()
        },
        "results": results
    }

    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Results saved to {RESULTS_FILE}")

    return output


if __name__ == "__main__":
    run_tests()
