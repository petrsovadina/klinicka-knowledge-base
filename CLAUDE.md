# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Czech-language structured knowledge base for ambulatory healthcare economics, reimbursements, and operations. The system extracts knowledge units from regulatory documents (billing decrees, insurer methodologies, professional articles), stores them as JSONL, and serves them via a FastAPI RAG API with TF-IDF/SVD-based semantic search. Published to Hugging Face as `petrsovadina/klinicka-knowledge-base`.

**Language**: All data, documentation, and user-facing text is in Czech. Code comments and variable names are a mix of Czech and English.

## Commands

```bash
# Setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run API (dev)
python api/rag_api.py

# Run API (production)
uvicorn api.rag_api:app --host 0.0.0.0 --port 8000 --workers 4

# Validate dataset
python scripts/validate_dataset.py

# Generate embeddings (after adding new knowledge units)
python scripts/generate_embeddings.py --input knowledge_base_mvp.jsonl

# Run RAG test suite (25 queries, target: 80%+ with score > 0.7)
python scripts/test_rag_mvp.py

# Unit tests
python scripts/test_api_unit.py

# Load test
python scripts/test_api_load.py --concurrent 10

# Extract knowledge units from PDF
python scripts/llm_extract_v2.py <pdf_filename>

# Merge extracted units into main dataset (handles deduplication)
python scripts/merge_and_validate.py

# Docker
docker build -t klinicka-rag-api .
docker-compose up -d
```

## Architecture

### Data Pipeline

```
sources/ (PDFs, HTML) → scripts/llm_extract_v2.py → data/extracted/*.jsonl
                                                          ↓
data/knowledge_base_final.jsonl ← scripts/merge_and_validate.py (dedup + validate)
         ↓
scripts/generate_embeddings.py → data/knowledge_base_embeddings.jsonl
                                  data/tfidf_vectorizer.pkl
                                  data/svd_model.pkl
         ↓
api/rag_api.py (FastAPI) → /search (semantic), /qa (RAG with OpenAI)
```

- **Extraction** (`scripts/llm_extract_v2.py`): Uses OpenAI `gpt-4.1-nano` to extract knowledge units from PDFs. Progressive writing (flush after each chunk). Chunks at 12,000 chars.
- **Merging** (`scripts/merge_and_validate.py`): Merges extracted JSONL files into main dataset with 75% Jaccard similarity-based duplicate detection and JSON schema validation.
- **Embeddings** (`scripts/generate_embeddings.py`): TF-IDF (5000 features, bigrams) + TruncatedSVD (256 dims) with L2 normalization. Outputs: JSONL embeddings + pickled vectorizer/SVD.
- **API** (`api/rag_api.py`): FastAPI with in-memory cosine similarity search, TTL-based response cache, sliding-window rate limiter, and OpenAI `gpt-4.1-mini` for Q&A generation.

### Knowledge Unit Schema

Defined in `schemas/knowledge_unit.schema.json`. Each unit has:
- **id**: `ku-NNN-slug` format (e.g., `ku-042-riziko-nizka-puro`)
- **type**: `rule` | `exception` | `risk` | `anti_pattern` | `condition` | `definition`
- **domain**: `uhrady` | `provoz` | `compliance` | `financni-rizika` | `legislativa`
- **content**: Structured differently per type (e.g., `condition`/`consequence`/`impact` for rules, `risk`/`impact_level`/`mitigation` for risks)
- **applicability**: Medical specialty codes (e.g., `001` for general practice, `603` for gynecology) + validity dates
- **source**: Name, URL, and retrieval date of the regulatory document

### Key Data Files

- `data/knowledge_base_mvp.jsonl` — MVP dataset (669 units)
- `data/knowledge_base_final.jsonl` — Main merged dataset
- `data/knowledge_base_embeddings.jsonl` — Pre-computed embeddings
- `data/extracted/*.jsonl` — Raw extraction outputs
- `sources/metadata.json` — Source document registry with URLs, types, and download status for all 34 sources across 7 Czech health insurers

### Environment Variables

- `OPENAI_API_KEY` — Required for extraction scripts and RAG Q&A endpoint
- `DATA_DIR` — Override data directory path (default: `./data` or `/home/ubuntu/klinicka-knowledge-base/data` in some scripts)

## Important Conventions

- Data format is JSONL (one JSON object per line), not JSON arrays
- The schema formally requires UUID for `id` but the actual dataset uses `ku-NNN-slug` format — validation scripts accommodate both
- Some scripts have hardcoded absolute paths (`/home/ubuntu/...`) from the extraction server — use relative paths from `Path(__file__).parent` for new scripts
- Content structure within a knowledge unit varies by `type` field — see `CONTRIBUTING.md` for the expected structure per type
- Source metadata in `sources/metadata.json` tracks document availability; several insurer URLs return 404 and are marked with `status: "unavailable"`
