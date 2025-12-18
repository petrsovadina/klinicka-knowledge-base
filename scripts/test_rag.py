#!/usr/bin/env python3
"""
Test RAG MVP with 10 real doctor questions.
"""
import requests
import json

API_URL = "http://localhost:8000"

# 10 reálných dotazů lékaře
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

def test_search(query):
    """Test search endpoint."""
    response = requests.post(
        f"{API_URL}/search",
        json={"query": query, "top_k": 3}
    )
    return response.json()

def test_qa(question):
    """Test Q&A endpoint."""
    response = requests.post(
        f"{API_URL}/qa",
        json={"question": question, "top_k": 5}
    )
    return response.json()

def main():
    print("="*80)
    print("RAG MVP TEST - 10 REÁLNÝCH DOTAZŮ LÉKAŘE")
    print("="*80)
    print()
    
    results = []
    
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n{'='*80}")
        print(f"DOTAZ {i}: {question}")
        print("="*80)
        
        # Test Q&A
        qa_result = test_qa(question)
        
        print(f"\nODPOVĚĎ:")
        print(qa_result["answer"])
        
        print(f"\nZDROJE:")
        for j, source in enumerate(qa_result["sources"][:3], 1):
            print(f"  {j}. [{source['id']}] {source['title']} (score: {source['score']:.3f})")
        
        # Store for analysis
        results.append({
            "question": question,
            "answer": qa_result["answer"],
            "sources": qa_result["sources"],
            "top_score": qa_result["sources"][0]["score"] if qa_result["sources"] else 0
        })
    
    # Summary
    print("\n" + "="*80)
    print("SHRNUTÍ TESTU")
    print("="*80)
    
    avg_score = sum(r["top_score"] for r in results) / len(results)
    print(f"\nPrůměrné skóre top výsledku: {avg_score:.3f}")
    
    # Identify gaps
    print("\nIDENTIFIKOVANÉ MEZERY:")
    for r in results:
        if r["top_score"] < 0.3:
            print(f"  - Nízké skóre ({r['top_score']:.3f}): {r['question']}")
    
    # Save results
    with open("/home/ubuntu/klinicka-knowledge-base/data/test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n✓ Výsledky uloženy do data/test_results.json")

if __name__ == "__main__":
    main()
