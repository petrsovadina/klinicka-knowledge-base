#!/usr/bin/env python3
import json
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path("/home/ubuntu/klinicka-knowledge-base/data")
INPUT_PATH = DATA_DIR / "knowledge_base_v2.jsonl"
OUTPUT_PATH = DATA_DIR / "knowledge_base_v3.jsonl"

def fix_duplicates():
    print("="*80)
    print("FIXING DUPLICATE IDs")
    print("="*80)
    
    units = []
    id_map = defaultdict(list)
    
    # Load units
    with open(INPUT_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            unit = json.loads(line)
            units.append(unit)
            id_map[unit['id']].append(unit)

    # Identify and fix duplicates
    fixed_units = []
    fixed_count = 0
    
    for unit in units:
        unit_id = unit['id']
        if len(id_map[unit_id]) > 1:
            # Only fix the duplicates, keep the first one as is
            if id_map[unit_id][0] is unit:
                fixed_units.append(unit)
            else:
                # Append a suffix to the duplicate ID
                new_id = f"{unit_id}-dup-{fixed_count}"
                unit['id'] = new_id
                fixed_units.append(unit)
                fixed_count += 1
        else:
            fixed_units.append(unit)

    # Write fixed units
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        for unit in fixed_units:
            f.write(json.dumps(unit, ensure_ascii=False) + '\n')
            
    print(f"Total units loaded: {len(units)}")
    print(f"Total duplicates fixed: {fixed_count}")
    print(f"Output file: {OUTPUT_PATH}")
    print("="*80)

if __name__ == "__main__":
    fix_duplicates()
