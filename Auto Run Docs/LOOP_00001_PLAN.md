# Refactoring Plan - Loop 00001

## Summary
- **Total Candidates:** 3
- **PENDING (auto-implement):** 0
- **IMPLEMENTED:** 1
- **PENDING - MANUAL REVIEW:** 0
- **WON'T DO:** 0
- **Remaining to evaluate:** 2

## Status Matrix

| # | Candidate | Risk | Benefit | Status |
|---|-----------|------|---------|--------|
| 1 | Hardcoded BASE_DIR in extract_as_2026.py | LOW | HIGH | IMPLEMENTED |

## Detailed Evaluations

### 1. Hardcoded BASE_DIR in extract_as_2026.py
- **Location:** `scripts/extract_as_2026.py:25-29`
- **Category:** Organization (Portability)
- **Risk:** LOW
- **Benefit:** HIGH
- **Status:** IMPLEMENTED

#### Risk Rationale
- **Internal-only change:** The path constants are only used within this single file
- **No API changes:** No exported functions or interfaces are affected
- **Single file:** Only `extract_as_2026.py` needs modification
- **Easy to verify:** Can be tested by running the script from different directories
- **No side effects:** Just changes how paths are computed, not what they point to
- **Pattern already exists:** 12+ other files in the codebase use `Path(__file__).parent` successfully

#### Benefit Rationale
- **Portability:** Currently fails on any machine except the original developer's
- **Team collaboration:** Blocks other developers from running the script
- **CI/CD compatibility:** Would break in any automated testing or deployment pipeline
- **Consistency:** Aligns with the established pattern in the rest of the codebase
- **Best practice:** Using `__file__` for relative paths is Python standard practice

#### Refactoring Approach
Replace lines 24-29:
```python
# Current (problematic)
BASE_DIR = Path("/Users/petrsovadina/Desktop/Develope/personal/klinicka-knowledge-base")
SOURCES_DIR = BASE_DIR / "sources"
SCHEMA_PATH = BASE_DIR / "schemas/knowledge_unit.schema.json"
OUTPUT_DIR = BASE_DIR / "data/extracted"
```

With:
```python
# Portable (recommended)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SOURCES_DIR = PROJECT_ROOT / "sources"
SCHEMA_PATH = PROJECT_ROOT / "schemas/knowledge_unit.schema.json"
OUTPUT_DIR = PROJECT_ROOT / "data/extracted"
```

This follows the exact pattern used in `scripts/validate_dataset.py`, `scripts/download_sources.py`, and other scripts in this project.
