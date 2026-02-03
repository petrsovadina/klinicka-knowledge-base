#!/usr/bin/env python3
"""
Load test script for Klinicka Knowledge Base RAG API.
Tests API under concurrent load with 10 simultaneous queries.
"""
import asyncio
import aiohttp
import time
import json
import argparse
from dataclasses import dataclass
from typing import List, Optional

# Default configuration
DEFAULT_BASE_URL = "http://localhost:8000"
CONCURRENT_REQUESTS = 10

# Test queries covering different domains
TEST_QUERIES = [
    # Úhrady domain
    "Jaká je hodnota bodu pro VZP v roce 2026?",
    "Jak se počítá PURO u praktického lékaře?",
    "Co je to bonifikace kvality?",

    # Provoz domain
    "Jaké jsou požadavky na personální zajištění ambulance?",
    "Jak správně vést zdravotnickou dokumentaci?",

    # Compliance domain
    "Jaké jsou podmínky pro registraci u zdravotní pojišťovny?",
    "Co kontroluje revizní lékař?",

    # Finanční rizika domain
    "Jaké jsou sankce za nesprávné vykazování?",
    "Jak minimalizovat riziko regresu?",

    # Legislativa domain
    "Co říká zákon 372/2011 Sb. o ordinačních hodinách?",
]


@dataclass
class RequestResult:
    """Result of a single API request."""
    query: str
    success: bool
    status_code: int
    latency_ms: float
    cached: bool
    error: Optional[str] = None


async def make_search_request(
    session: aiohttp.ClientSession,
    base_url: str,
    query: str
) -> RequestResult:
    """Make a single search request to the API."""
    start_time = time.time()

    try:
        async with session.post(
            f"{base_url}/search",
            json={"query": query, "top_k": 5},
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            latency_ms = (time.time() - start_time) * 1000

            if response.status == 200:
                data = await response.json()
                return RequestResult(
                    query=query,
                    success=True,
                    status_code=response.status,
                    latency_ms=latency_ms,
                    cached=data.get("cached", False)
                )
            elif response.status == 429:
                return RequestResult(
                    query=query,
                    success=False,
                    status_code=response.status,
                    latency_ms=latency_ms,
                    cached=False,
                    error="Rate limited"
                )
            else:
                error_text = await response.text()
                return RequestResult(
                    query=query,
                    success=False,
                    status_code=response.status,
                    latency_ms=latency_ms,
                    cached=False,
                    error=error_text[:200]
                )

    except asyncio.TimeoutError:
        return RequestResult(
            query=query,
            success=False,
            status_code=0,
            latency_ms=(time.time() - start_time) * 1000,
            cached=False,
            error="Timeout"
        )
    except Exception as e:
        return RequestResult(
            query=query,
            success=False,
            status_code=0,
            latency_ms=(time.time() - start_time) * 1000,
            cached=False,
            error=str(e)[:200]
        )


async def run_concurrent_load_test(
    base_url: str,
    num_concurrent: int = CONCURRENT_REQUESTS
) -> List[RequestResult]:
    """Run concurrent load test with specified number of requests."""
    queries = TEST_QUERIES[:num_concurrent]

    # Pad with repeated queries if needed
    while len(queries) < num_concurrent:
        queries.extend(TEST_QUERIES[:num_concurrent - len(queries)])

    async with aiohttp.ClientSession() as session:
        tasks = [
            make_search_request(session, base_url, query)
            for query in queries[:num_concurrent]
        ]
        results = await asyncio.gather(*tasks)

    return results


async def check_health(base_url: str) -> bool:
    """Check if API is healthy."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{base_url}/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Health check: {data['status']}")
                    print(f"  Knowledge units: {data['knowledge_units']}")
                    print(f"  Embeddings: {data['embeddings']}")
                    return data['status'] == 'healthy'
                return False
    except Exception as e:
        print(f"Health check failed: {e}")
        return False


async def get_metrics(base_url: str) -> Optional[dict]:
    """Get API metrics."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{base_url}/metrics",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None
    except Exception as e:
        print(f"Metrics fetch failed: {e}")
        return None


def print_results(results: List[RequestResult], phase: str):
    """Print test results summary."""
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    cached = [r for r in successful if r.cached]

    print(f"\n{'='*60}")
    print(f"{phase} Results")
    print(f"{'='*60}")
    print(f"Total requests: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"Cache hits: {len(cached)}")

    if successful:
        latencies = [r.latency_ms for r in successful]
        print(f"\nLatency (successful requests):")
        print(f"  Min: {min(latencies):.2f} ms")
        print(f"  Max: {max(latencies):.2f} ms")
        print(f"  Avg: {sum(latencies)/len(latencies):.2f} ms")

    if failed:
        print(f"\nFailed requests:")
        for r in failed[:5]:  # Show first 5 failures
            print(f"  - {r.query[:40]}... : {r.error}")

    return len(successful), len(failed)


async def main():
    parser = argparse.ArgumentParser(description="Load test for RAG API")
    parser.add_argument(
        "--url",
        default=DEFAULT_BASE_URL,
        help=f"Base URL of the API (default: {DEFAULT_BASE_URL})"
    )
    parser.add_argument(
        "--concurrent",
        type=int,
        default=CONCURRENT_REQUESTS,
        help=f"Number of concurrent requests (default: {CONCURRENT_REQUESTS})"
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=2,
        help="Number of test rounds (default: 2, for testing cache)"
    )
    args = parser.parse_args()

    print(f"Klinicka Knowledge Base RAG API - Load Test")
    print(f"{'='*60}")
    print(f"Target: {args.url}")
    print(f"Concurrent requests: {args.concurrent}")
    print(f"Test rounds: {args.rounds}")

    # Health check
    print(f"\n{'='*60}")
    print("Health Check")
    print(f"{'='*60}")
    healthy = await check_health(args.url)

    if not healthy:
        print("\nAPI is not healthy. Continuing with tests anyway...")

    # Get initial metrics
    initial_metrics = await get_metrics(args.url)

    all_results = []
    total_success = 0
    total_failed = 0

    # Run multiple rounds to test caching
    for round_num in range(1, args.rounds + 1):
        print(f"\n{'='*60}")
        print(f"Round {round_num}: Running {args.concurrent} concurrent requests")
        print(f"{'='*60}")

        start_time = time.time()
        results = await run_concurrent_load_test(args.url, args.concurrent)
        elapsed = time.time() - start_time

        success, failed = print_results(results, f"Round {round_num}")
        total_success += success
        total_failed += failed
        all_results.extend(results)

        print(f"\nTotal elapsed time: {elapsed:.2f}s")
        print(f"Requests per second: {len(results)/elapsed:.2f}")

        # Small delay between rounds
        if round_num < args.rounds:
            await asyncio.sleep(0.5)

    # Get final metrics
    final_metrics = await get_metrics(args.url)

    if final_metrics:
        print(f"\n{'='*60}")
        print("API Metrics After Test")
        print(f"{'='*60}")
        print(f"Total requests: {final_metrics['total_requests']}")
        print(f"Cache hit rate: {final_metrics['cache_hit_rate_percent']:.1f}%")
        print(f"Avg latency: {final_metrics['avg_latency_ms']:.2f} ms")
        print(f"Rate limited: {final_metrics['rate_limited_requests']}")
        print(f"Errors: {final_metrics['error_count']}")

    # Final summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"Total requests across all rounds: {len(all_results)}")
    print(f"Total successful: {total_success}")
    print(f"Total failed: {total_failed}")
    print(f"Success rate: {total_success/len(all_results)*100:.1f}%")

    # Determine pass/fail
    success_rate = total_success / len(all_results) * 100

    if success_rate >= 90:
        print(f"\n✓ LOAD TEST PASSED (Success rate: {success_rate:.1f}%)")
        return 0
    else:
        print(f"\n✗ LOAD TEST FAILED (Success rate: {success_rate:.1f}%)")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
