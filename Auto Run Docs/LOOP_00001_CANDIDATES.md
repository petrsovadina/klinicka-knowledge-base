# Refactoring Candidates - Loop 00001

This document tracks all refactoring candidates discovered during the investigation phase.

---

## Tactic 6: Hardcoded Path Constants - Executed 2026-02-03 12:00

### Finding 1: Hardcoded BASE_DIR in extract_as_2026.py
- **Category:** Organization
- **Location:** `scripts/extract_as_2026.py:25`
- **Current State:** Uses hardcoded absolute path that only works on one developer's machine
- **Proposed Change:** Replace with `Path(__file__).parent.parent` pattern used by other scripts
- **Code Context:**
  ```python
  # Current (problematic)
  BASE_DIR = Path("/Users/petrsovadina/Desktop/Develope/personal/klinicka-knowledge-base")
  SOURCES_DIR = BASE_DIR / "sources"
  SCHEMA_PATH = BASE_DIR / "schemas/knowledge_unit.schema.json"

  # Recommended (portable)
  SCRIPT_DIR = Path(__file__).parent
  PROJECT_ROOT = SCRIPT_DIR.parent
  SOURCES_DIR = PROJECT_ROOT / "sources"
  SCHEMA_PATH = PROJECT_ROOT / "schemas/knowledge_unit.schema.json"
  ```

### Finding 2: Hardcoded BASE_DIR in extract_pl_2026.py
- **Category:** Organization
- **Location:** `scripts/extract_pl_2026.py:20`
- **Current State:** Uses hardcoded absolute path that only works on one developer's machine
- **Proposed Change:** Replace with `Path(__file__).parent.parent` pattern used by other scripts
- **Code Context:**
  ```python
  # Current (problematic)
  BASE_DIR = Path("/Users/petrsovadina/Desktop/Develope/personal/klinicka-knowledge-base")
  OUTPUT_DIR = BASE_DIR / "data/extracted"

  # Recommended (portable)
  SCRIPT_DIR = Path(__file__).parent
  PROJECT_ROOT = SCRIPT_DIR.parent
  OUTPUT_DIR = PROJECT_ROOT / "data/extracted"
  ```

### Finding 3: Hardcoded BASE_DIR in extract_as_dodatek_2026.py
- **Category:** Organization
- **Location:** `scripts/extract_as_dodatek_2026.py:18`
- **Current State:** Uses hardcoded absolute path that only works on one developer's machine
- **Proposed Change:** Replace with `Path(__file__).parent.parent` pattern used by other scripts
- **Code Context:**
  ```python
  # Current (problematic)
  BASE_DIR = Path("/Users/petrsovadina/Desktop/Develope/personal/klinicka-knowledge-base")
  OUTPUT_DIR = BASE_DIR / "data/extracted"

  # Recommended (portable)
  SCRIPT_DIR = Path(__file__).parent
  PROJECT_ROOT = SCRIPT_DIR.parent
  OUTPUT_DIR = PROJECT_ROOT / "data/extracted"
  ```

### Tactic Summary
- **Issues Found:** 3
- **Files Affected:** 3
- **Status:** EXECUTED
- **Notes:**
  - All three files are extraction scripts that define knowledge units
  - The rest of the codebase (12+ files) already uses the correct `Path(__file__)` pattern
  - Files like `merge_phase3_final.py`, `validate_dataset.py`, `test_rag_mvp.py` demonstrate the correct approach
  - `api/rag_api.py` uses environment variables which is even better for deployment flexibility
  - Fixing these 3 files would make the codebase consistent and portable
