#!/usr/bin/env python3
"""
Upload the Klinická Knowledge Base MVP dataset to Hugging Face Hub.

Version: 1.0.0-MVP
Date: 2026-02-03
"""
import json
import os
from pathlib import Path

# Configuration
DATASET_FILE = "data/knowledge_base_mvp.jsonl"
EMBEDDINGS_FILE = "data/knowledge_base_embeddings.jsonl"
SCHEMA_FILE = "schemas/knowledge_unit.schema.json"
README_FILE = "DATASET_README.md"
HF_REPO = "petrsovadina/klinicka-knowledge-base"

def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.absolute()

def validate_dataset(dataset_path: Path) -> tuple[bool, int]:
    """Validate the dataset file and return (is_valid, count)."""
    if not dataset_path.exists():
        print(f"ERROR: Dataset file not found at {dataset_path}")
        return False, 0

    count = 0
    errors = []
    required_fields = ['id', 'type', 'domain', 'title', 'description', 'version', 'source', 'content', 'applicability']

    with open(dataset_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line)
                count += 1
                for field in required_fields:
                    if field not in data:
                        errors.append(f"Line {line_num}: Missing field '{field}' in unit {data.get('id', 'unknown')}")
            except json.JSONDecodeError as e:
                errors.append(f"Line {line_num}: Invalid JSON: {e}")

    if errors:
        print("Validation warnings:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")

    return len(errors) == 0, count

def print_instructions(project_root: Path):
    """Print upload instructions."""
    print("=" * 80)
    print("HUGGING FACE DATASET UPLOAD - MVP VERSION 1.0.0")
    print("=" * 80)
    print()
    print("Option 1: Manual Upload via Web Interface")
    print("-" * 40)
    print("1. Go to https://huggingface.co/datasets/petrsovadina/klinicka-knowledge-base")
    print("2. Click 'Files' tab, then 'Add file' -> 'Upload files'")
    print("3. Upload the following files:")
    print(f"   - {DATASET_FILE}")
    print(f"   - {EMBEDDINGS_FILE}")
    print(f"   - {SCHEMA_FILE}")
    print(f"   - {README_FILE}")
    print()
    print("Option 2: Using Hugging Face CLI")
    print("-" * 40)
    print()
    print("# 1. Install huggingface_hub if not installed")
    print("pip install huggingface_hub")
    print()
    print("# 2. Login to Hugging Face")
    print("huggingface-cli login")
    print()
    print("# 3. Upload files")
    print(f"cd {project_root}")
    print()
    print(f"huggingface-cli upload {HF_REPO} {DATASET_FILE} data/knowledge_base_mvp.jsonl --repo-type dataset")
    print(f"huggingface-cli upload {HF_REPO} {EMBEDDINGS_FILE} data/knowledge_base_embeddings.jsonl --repo-type dataset")
    print(f"huggingface-cli upload {HF_REPO} {SCHEMA_FILE} schemas/knowledge_unit.schema.json --repo-type dataset")
    print(f"huggingface-cli upload {HF_REPO} {README_FILE} README.md --repo-type dataset")
    print()
    print("Option 3: Using Python SDK")
    print("-" * 40)
    print("""
from huggingface_hub import HfApi, login

# Login (will prompt for token)
login()

api = HfApi()

# Upload files
api.upload_file(
    path_or_fileobj="data/knowledge_base_mvp.jsonl",
    path_in_repo="data/knowledge_base_mvp.jsonl",
    repo_id="petrsovadina/klinicka-knowledge-base",
    repo_type="dataset"
)

api.upload_file(
    path_or_fileobj="DATASET_README.md",
    path_in_repo="README.md",
    repo_id="petrsovadina/klinicka-knowledge-base",
    repo_type="dataset"
)
""")
    print("=" * 80)
    print()

def main():
    project_root = get_project_root()
    dataset_path = project_root / DATASET_FILE

    print("Klinická Knowledge Base - Upload Script")
    print(f"Project root: {project_root}")
    print()

    # Validate dataset
    print("Validating dataset...")
    is_valid, count = validate_dataset(dataset_path)

    if not is_valid:
        print("Dataset validation failed. Please fix errors before uploading.")
        return 1

    print(f"✓ Dataset validated: {count} knowledge units")
    print()

    # Check for embeddings file
    embeddings_path = project_root / EMBEDDINGS_FILE
    if embeddings_path.exists():
        print(f"✓ Embeddings file found: {EMBEDDINGS_FILE}")
    else:
        print(f"⚠ Embeddings file not found: {EMBEDDINGS_FILE}")
        print("  Run `python scripts/generate_embeddings.py` to generate embeddings")
    print()

    # Print upload instructions
    print_instructions(project_root)

    print("Dataset is ready for upload to Hugging Face!")
    print(f"Repository: https://huggingface.co/datasets/{HF_REPO}")

    return 0

if __name__ == "__main__":
    exit(main())
