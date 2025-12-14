#!/usr/bin/env python3
"""
Upload the Klinická Knowledge Base dataset to Hugging Face Hub.
"""
import json
import os
from pathlib import Path

# Instructions for manual upload
print("=" * 80)
print("HUGGING FACE DATASET UPLOAD - MANUAL INSTRUCTIONS")
print("=" * 80)
print()
print("To upload this dataset to Hugging Face, follow these steps:")
print()
print("1. Go to https://huggingface.co/new-dataset")
print("2. Create a new dataset with name: klinicka-knowledge-base")
print("3. Upload the following files:")
print("   - data/pilot_knowledge_units.jsonl")
print("   - DATASET_README.md (rename to README.md)")
print("   - schemas/knowledge_unit.schema.json")
print()
print("4. Or use the Hugging Face CLI:")
print()
print("   # Login to Hugging Face")
print("   huggingface-cli login")
print()
print("   # Create dataset repository")
print("   huggingface-cli repo create klinicka-knowledge-base --type dataset --organization petrsovadina")
print()
print("   # Upload files")
print("   huggingface-cli upload petrsovadina/klinicka-knowledge-base ./data/pilot_knowledge_units.jsonl data/")
print("   huggingface-cli upload petrsovadina/klinicka-knowledge-base ./DATASET_README.md README.md")
print("   huggingface-cli upload petrsovadina/klinicka-knowledge-base ./schemas/knowledge_unit.schema.json schemas/")
print()
print("=" * 80)
print()

# Validate dataset
print("Validating dataset...")
dataset_path = Path("/home/ubuntu/klinicka-knowledge-base/data/pilot_knowledge_units.jsonl")
if not dataset_path.exists():
    print(f"ERROR: Dataset file not found at {dataset_path}")
    exit(1)

count = 0
with open(dataset_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            count += 1
            # Basic validation
            required_fields = ['id', 'type', 'domain', 'title', 'description', 'version', 'source', 'content', 'applicability']
            for field in required_fields:
                if field not in data:
                    print(f"WARNING: Missing field '{field}' in unit {data.get('id', 'unknown')}")
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON on line {count + 1}: {e}")

print(f"✓ Dataset validated: {count} knowledge units")
print()
print("Dataset is ready for upload to Hugging Face!")
