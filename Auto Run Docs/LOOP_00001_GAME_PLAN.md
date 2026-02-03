# Refactoring Game Plan

## Codebase Profile
- **Total Files:** ~20 Python files (excluding .venv)
- **Total LOC:** ~6,300 lines of Python code
- **Largest Files:**
  1. `scripts/extract_pl_2026.py` - 769 LOC
  2. `scripts/extract_as_dodatek_2026.py` - 677 LOC
  3. `api/rag_api.py` - 637 LOC
  4. `scripts/merge_phase3_final.py` - 577 LOC
  5. `scripts/merge_and_validate.py` - 445 LOC
  6. `scripts/test_rag_mvp.py` - 433 LOC
  7. `scripts/validate_dataset.py` - 364 LOC
  8. `scripts/test_api_load.py` - 304 LOC
  9. `scripts/test_api_unit.py` - 280 LOC
  10. `scripts/extract_as_2026.py` - 276 LOC

- **Key Directories:**
  - `scripts/` - Extraction, validation, testing, and merge scripts
  - `api/` - FastAPI RAG API implementation
  - `data/` - Knowledge base JSONL files and extracted data
  - `docs/` - Documentation and analysis reports
  - `schemas/` - JSON schema definitions

- **Existing Patterns:**
  - Knowledge unit creation functions (`create_unit`, `create_knowledge_unit`)
  - JSONL file loading patterns (`load_units`)
  - Validation functions (`validate_unit`, `validate_required_fields`)
  - Content hash/similarity functions for duplicate detection
  - TF-IDF + SVD embedding pipeline in RAG API
  - Report generation with markdown output
  - Consistent use of Path objects for file handling

## Investigation Tactics

Each tactic is a specific, actionable search pattern for finding refactoring opportunities.

### Tactic 1: Large Extraction Scripts with Repetitive Unit Creation
- **Target:** Repetitive `create_unit()` calls with similar structure in extraction scripts
- **Search Pattern:** Look for files with 500+ LOC containing multiple `units.append(create_unit(...)` patterns
- **Files to Check:**
  - `scripts/extract_pl_2026.py` (769 LOC - ~30+ unit creation calls)
  - `scripts/extract_as_dodatek_2026.py` (677 LOC - ~40+ unit creation calls)
  - `scripts/extract_as_2026.py` (276 LOC)
- **Why It Matters:** The extraction scripts are essentially data definition files with hardcoded knowledge units. While the structure is consistent, the repetitive `create_unit()` calls could benefit from:
  - Data-driven approach (YAML/JSON configuration files)
  - Shared base class or factory pattern for unit creation
  - Template-based generation

### Tactic 2: Duplicated Load/Validate Functions Across Scripts
- **Target:** Nearly identical `load_units()`, `validate_unit()`, and `load_schema()` functions appearing in multiple files
- **Search Pattern:** `grep -l "def load_units\|def validate_unit\|def load_schema" scripts/*.py`
- **Files to Check:**
  - `scripts/merge_phase3_final.py`
  - `scripts/merge_and_validate.py`
  - `scripts/validate_dataset.py`
- **Why It Matters:** These utilities are duplicated with minor variations. Extracting to a shared `utils/` module would:
  - Reduce code duplication by ~100-150 LOC
  - Ensure consistent validation behavior
  - Make maintenance easier

### Tactic 3: Duplicate Detection Logic
- **Target:** Similar `content_hash()`, `normalize_text()`, and `similarity_score()` functions
- **Search Pattern:** `grep -l "def content_hash\|def normalize_text\|def similarity_score" scripts/*.py`
- **Files to Check:**
  - `scripts/merge_phase3_final.py`
  - `scripts/merge_and_validate.py`
- **Why It Matters:** Duplicate detection algorithms are nearly identical in both merge scripts. A shared deduplication module would ensure consistent behavior.

### Tactic 4: Report Generation Patterns
- **Target:** Similar markdown report generation functions
- **Search Pattern:** `def generate_report` pattern
- **Files to Check:**
  - `scripts/merge_phase3_final.py` - `generate_report()`
  - `scripts/merge_and_validate.py` - `generate_report()`
- **Why It Matters:** Report generation code has similar structure with f-strings building markdown. A report template system would reduce duplication and allow consistent formatting.

### Tactic 5: Test File Redundancy
- **Target:** Overlapping test functionality between test files
- **Search Pattern:** Multiple test files with similar setup/teardown and knowledge base loading
- **Files to Check:**
  - `scripts/test_rag_mvp.py` (433 LOC)
  - `scripts/test_rag_offline.py` (233 LOC)
  - `scripts/test_rag.py` (92 LOC)
  - `scripts/test_api_unit.py` (280 LOC)
  - `scripts/test_api_load.py` (304 LOC)
- **Why It Matters:** Multiple test files share:
  - Knowledge base loading code
  - Embedding creation functions
  - Similar test case structures
  A shared test utilities module and pytest fixtures would reduce duplication.

### Tactic 6: Hardcoded Path Constants
- **Target:** Repeated absolute path definitions across multiple files
- **Search Pattern:** `BASE_DIR = Path(` or hardcoded paths like `/Users/petrsovadina/`
- **Files to Check:**
  - `scripts/extract_pl_2026.py` - hardcoded BASE_DIR
  - `scripts/extract_as_dodatek_2026.py` - hardcoded BASE_DIR
  - `api/rag_api.py` - uses environment variables (good pattern)
- **Why It Matters:** Several extraction scripts have hardcoded absolute paths. These should use relative paths from `__file__` or environment variables for portability.

### Tactic 7: Missing Type Hints
- **Target:** Functions without type annotations
- **Search Pattern:** Functions with `def function_name(` without `->` return type annotations
- **Files to Check:** All Python files, particularly:
  - `scripts/extract_*.py`
  - `scripts/merge_*.py`
- **Why It Matters:** Adding type hints improves code clarity, enables better IDE support, and catches errors early with tools like mypy.

### Tactic 8: Long Functions in API
- **Target:** Functions over 50 lines that could be decomposed
- **Search Pattern:** Look for functions with multiple responsibilities
- **Files to Check:**
  - `api/rag_api.py` - `qa_endpoint()` combines search, context building, and LLM call
- **Why It Matters:** The QA endpoint does multiple things - search, context construction, prompt building, and LLM calling. Separating these concerns would improve testability and maintainability.

### Tactic 9: Inconsistent Error Handling
- **Target:** Mix of exception handling patterns
- **Search Pattern:** `except Exception` vs specific exception handling
- **Files to Check:**
  - `api/rag_api.py`
  - `scripts/merge_*.py`
- **Why It Matters:** Some files catch generic `Exception`, while others have specific handling. Consistent error handling improves debugging and reliability.

### Tactic 10: Dead/Commented Code
- **Target:** Unused imports, commented-out code blocks, unused functions
- **Search Pattern:**
  - `# ` followed by code-like patterns
  - Imports not used in file
- **Files to Check:** All Python files
- **Why It Matters:** Dead code adds cognitive load and can confuse developers. Removing it improves maintainability.

## Priority Order

1. **High Impact, Lower Effort:**
   - Tactic 6: Fix hardcoded paths (quick win for portability)
   - Tactic 2: Extract shared utilities (reduces ~150 LOC duplication)
   - Tactic 3: Shared deduplication module

2. **High Impact, Higher Effort:**
   - Tactic 1: Data-driven extraction (significant refactor but major win)
   - Tactic 5: Test utilities consolidation

3. **Medium Impact:**
   - Tactic 4: Report generation templates
   - Tactic 7: Add type hints
   - Tactic 8: Decompose long functions

4. **Lower Priority:**
   - Tactic 9: Standardize error handling
   - Tactic 10: Clean up dead code

## Notes

- The codebase is relatively small (~6,300 LOC) and well-organized
- Most scripts follow consistent patterns, which is good
- The main duplication is between merge/validation scripts
- Extraction scripts are data-heavy by design (knowledge unit definitions)
- The API is well-structured with clear separation of concerns
