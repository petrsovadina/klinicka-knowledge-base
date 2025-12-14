#!/usr/bin/env python3
"""
Merge and validate all extracted knowledge units.
"""
import json
import jsonschema
from pathlib import Path
from collections import defaultdict

# Paths
DATA_DIR = Path("/home/ubuntu/klinicka-knowledge-base/data")
EXTRACTED_DIR = DATA_DIR / "extracted"
SCHEMA_PATH = Path("/home/ubuntu/klinicka-knowledge-base/schemas/knowledge_unit.schema.json")
OUTPUT_PATH = DATA_DIR / "knowledge_base_v2.jsonl"

# Load schema
with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
    schema = json.load(f)

def load_units(file_path):
    """Load units from JSONL file."""
    units = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                unit = json.loads(line)
                units.append(unit)
            except json.JSONDecodeError as e:
                print(f"⚠ Error in {file_path.name} line {line_num}: {e}")
    return units

def validate_unit(unit, file_name):
    """Validate a single unit against schema."""
    try:
        jsonschema.validate(instance=unit, schema=schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, f"{file_name} - {unit.get('id', 'unknown')}: {e.message}"

def main():
    print("="*80)
    print("MERGING AND VALIDATING KNOWLEDGE UNITS")
    print("="*80)
    print()
    
    # Load all units
    all_units = []
    file_stats = {}
    
    # Load pilot dataset
    pilot_path = DATA_DIR / "pilot_knowledge_units.jsonl"
    if pilot_path.exists():
        pilot_units = load_units(pilot_path)
        all_units.extend(pilot_units)
        file_stats['pilot'] = len(pilot_units)
        print(f"✓ Loaded {len(pilot_units)} units from pilot dataset")
    
    # Load extracted units
    for file_path in sorted(EXTRACTED_DIR.glob("*.jsonl")):
        if file_path.stat().st_size == 0:
            print(f"⊙ Skipping empty file: {file_path.name}")
            continue
        
        units = load_units(file_path)
        all_units.extend(units)
        file_stats[file_path.stem] = len(units)
        print(f"✓ Loaded {len(units)} units from {file_path.name}")
    
    print(f"\n{'='*80}")
    print(f"Total units loaded: {len(all_units)}")
    print(f"{'='*80}\n")
    
    # Validate all units
    print("Validating units...")
    valid_units = []
    errors = []
    
    for unit in all_units:
        is_valid, error = validate_unit(unit, "merged")
        if is_valid:
            valid_units.append(unit)
        else:
            errors.append(error)
    
    print(f"✓ Valid units: {len(valid_units)}")
    if errors:
        print(f"✗ Invalid units: {len(errors)}")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
    
    # Check for duplicate IDs
    print("\nChecking for duplicate IDs...")
    id_counts = defaultdict(int)
    for unit in valid_units:
        id_counts[unit['id']] += 1
    
    duplicates = {id: count for id, count in id_counts.items() if count > 1}
    if duplicates:
        print(f"⚠ Found {len(duplicates)} duplicate IDs:")
        for id, count in list(duplicates.items())[:10]:
            print(f"  - {id}: {count} occurrences")
    else:
        print("✓ No duplicate IDs found")
    
    # Statistics by domain
    print("\nStatistics by domain:")
    domain_counts = defaultdict(int)
    for unit in valid_units:
        domain_counts[unit['domain']] += 1
    
    for domain, count in sorted(domain_counts.items()):
        print(f"  - {domain}: {count} units")
    
    # Statistics by type
    print("\nStatistics by type:")
    type_counts = defaultdict(int)
    for unit in valid_units:
        type_counts[unit['type']] += 1
    
    for type_name, count in sorted(type_counts.items()):
        print(f"  - {type_name}: {count} units")
    
    # Write merged dataset
    print(f"\nWriting merged dataset to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        for unit in valid_units:
            f.write(json.dumps(unit, ensure_ascii=False) + '\n')
    
    print(f"✓ Wrote {len(valid_units)} units")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total units: {len(all_units)}")
    print(f"Valid units: {len(valid_units)}")
    print(f"Invalid units: {len(errors)}")
    print(f"Duplicate IDs: {len(duplicates)}")
    print(f"Output file: {OUTPUT_PATH}")
    print(f"File size: {OUTPUT_PATH.stat().st_size / 1024:.1f} KB")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
