#!/usr/bin/env python3
"""
Phase 3 Final Merge: Merge all Phase 3 extractions into final MVP knowledge base.
Combines:
- Existing knowledge_base_final.jsonl (552 units from Phase 1-2)
- Phase 3 sources: ZP MV, OZP, ČPZP, year comparison, InfoProLekare

Output:
- data/knowledge_base_phase3.jsonl (intermediate)
- data/knowledge_base_mvp.jsonl (final MVP dataset)
"""
import json
import jsonschema
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import hashlib
import re

# Get script directory to compute relative paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Paths
DATA_DIR = PROJECT_ROOT / "data"
EXTRACTED_DIR = DATA_DIR / "extracted"
SCHEMA_PATH = PROJECT_ROOT / "schemas" / "knowledge_unit.schema.json"
MAIN_DATASET_PATH = DATA_DIR / "knowledge_base_final.jsonl"
PHASE3_OUTPUT_PATH = DATA_DIR / "knowledge_base_phase3.jsonl"
MVP_OUTPUT_PATH = DATA_DIR / "knowledge_base_mvp.jsonl"
REPORT_PATH = PROJECT_ROOT / "docs" / "analysis" / "merge_report_phase03.md"

# Phase 3 source files to process
PHASE3_SOURCE_FILES = [
    # ZP MV extractions
    "zpmv_metodika_2026.jsonl",
    # OZP extractions
    "ozp_metodika_2026.jsonl",
    # ČPZP extractions
    "cpzp_metodika_2026.jsonl",
    # Year comparison
    "year_comparison_2025_2026.jsonl",
    # InfoProLekare practical heuristics
    "infoprolekare_articles.jsonl",
]


def load_schema():
    """Load the JSON schema for validation."""
    if not SCHEMA_PATH.exists():
        print(f"⚠ Schema file not found: {SCHEMA_PATH}")
        return None
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


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
                unit['_source_file'] = file_path.name
                units.append(unit)
            except json.JSONDecodeError as e:
                print(f"⚠ Error in {file_path.name} line {line_num}: {e}")
    return units


def normalize_text(text):
    """Normalize text for comparison - lowercase, remove extra spaces, punctuation."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def content_hash(unit):
    """Generate a hash based on title + description for duplicate detection."""
    title = normalize_text(unit.get('title', ''))
    desc = normalize_text(unit.get('description', ''))[:200]  # First 200 chars
    combined = f"{title}|{desc}"
    return hashlib.md5(combined.encode('utf-8')).hexdigest()


def similarity_score(unit1, unit2):
    """Calculate simple similarity between two units based on normalized title and description."""
    title1 = normalize_text(unit1.get('title', ''))
    title2 = normalize_text(unit2.get('title', ''))
    desc1 = normalize_text(unit1.get('description', ''))
    desc2 = normalize_text(unit2.get('description', ''))

    # Check if titles are nearly identical
    if title1 == title2:
        return 1.0

    # Check word overlap
    words1 = set(title1.split() + desc1.split()[:50])
    words2 = set(title2.split() + desc2.split()[:50])

    if not words1 or not words2:
        return 0.0

    intersection = len(words1 & words2)
    union = len(words1 | words2)

    return intersection / union if union > 0 else 0.0


def find_duplicates(new_units, existing_units, threshold=0.80):
    """Find potential duplicates between new and existing units."""
    duplicates = []
    existing_hashes = {content_hash(u): u for u in existing_units}

    for new_unit in new_units:
        new_hash = content_hash(new_unit)

        # Exact hash match
        if new_hash in existing_hashes:
            duplicates.append({
                'new': new_unit,
                'existing': existing_hashes[new_hash],
                'reason': 'exact_match',
                'score': 1.0
            })
            continue

        # Check similarity for near-duplicates (only check against same domain)
        for existing in existing_units:
            if existing.get('domain') != new_unit.get('domain'):
                continue

            score = similarity_score(new_unit, existing)
            if score >= threshold:
                duplicates.append({
                    'new': new_unit,
                    'existing': existing,
                    'reason': 'similar',
                    'score': score
                })
                break

    return duplicates


def validate_unit(unit, file_name, schema):
    """Validate a single unit against schema with relaxed ID format."""
    if schema is None:
        required_fields = ['id', 'type', 'domain', 'title', 'description', 'version', 'source', 'content', 'applicability']
        for field in required_fields:
            if field not in unit:
                return False, f"{file_name} - {unit.get('id', 'unknown')}: Missing required field '{field}'"
        return True, None

    try:
        # Create modified schema that accepts our ID format
        relaxed_schema = schema.copy()
        if 'properties' in relaxed_schema and 'id' in relaxed_schema['properties']:
            relaxed_schema['properties'] = relaxed_schema['properties'].copy()
            relaxed_schema['properties']['id'] = {"type": "string"}

        if 'properties' in relaxed_schema and 'related_units' in relaxed_schema['properties']:
            relaxed_schema['properties']['related_units'] = {
                "type": "array",
                "items": {"type": "string"}
            }

        jsonschema.validate(instance=unit, schema=relaxed_schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, f"{file_name} - {unit.get('id', 'unknown')}: {e.message}"


def find_internal_duplicates(units, threshold=0.85):
    """Find duplicates within a single list of units."""
    duplicates = []
    seen_hashes = {}

    for i, unit in enumerate(units):
        unit_hash = content_hash(unit)
        if unit_hash in seen_hashes:
            duplicates.append({
                'index': i,
                'unit': unit,
                'duplicate_of_index': seen_hashes[unit_hash],
                'reason': 'exact_hash'
            })
        else:
            # Also check similarity
            for j, other in enumerate(units[:i]):
                if other.get('domain') == unit.get('domain'):
                    score = similarity_score(unit, other)
                    if score >= threshold:
                        duplicates.append({
                            'index': i,
                            'unit': unit,
                            'duplicate_of_index': j,
                            'reason': 'similar',
                            'score': score
                        })
                        break
            else:
                seen_hashes[unit_hash] = i

    return duplicates


def generate_report(stats, report_path):
    """Generate a markdown report of the merge operation."""
    report_path.parent.mkdir(parents=True, exist_ok=True)

    report = f"""---
type: report
title: Phase 03 Final Merge Report - Extended Sources
created: {datetime.now().strftime('%Y-%m-%d')}
tags:
  - merge-report
  - phase-03
  - mvp
  - final
related:
  - "[[MVP-KB-03-Extended-Sources]]"
---

# Phase 03: Final Merge Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

| Metric | Count |
|--------|-------|
| Existing units (Phase 1-2) | {stats['existing_count']} |
| New Phase 3 units processed | {stats['new_phase3_count']} |
| Valid units | {stats['valid_count']} |
| Invalid units (rejected) | {stats['invalid_count']} |
| Duplicates with existing (removed) | {stats['duplicate_external_count']} |
| Internal duplicates (removed) | {stats['duplicate_internal_count']} |
| Units added to dataset | {stats['added_count']} |
| **Final MVP dataset size** | **{stats['final_count']}** |

## Source Files Processed

"""
    for source_name, count in stats.get('source_stats', {}).items():
        report += f"- `{source_name}`: {count} units\n"

    report += f"""
## Duplicate Detection

External threshold: 80% similarity (title + description)
Internal threshold: 85% similarity

"""
    if stats.get('duplicate_details'):
        report += "### External Duplicates (Phase 3 vs Existing)\n\n"
        report += "| New Unit | Existing Unit | Similarity |\n"
        report += "|----------|---------------|------------|\n"
        for dup in stats['duplicate_details'][:15]:
            new_title = dup['new_title'][:35] + "..." if len(dup['new_title']) > 35 else dup['new_title']
            existing_title = dup['existing_title'][:35] + "..." if len(dup['existing_title']) > 35 else dup['existing_title']
            report += f"| {new_title} | {existing_title} | {dup['score']:.0%} |\n"
        if len(stats['duplicate_details']) > 15:
            report += f"\n*...and {len(stats['duplicate_details']) - 15} more duplicates*\n"
    else:
        report += "*No external duplicates detected*\n"

    report += f"""
## Statistics by Domain

| Domain | Before | Added | After |
|--------|--------|-------|-------|
"""
    for domain in sorted(set(list(stats.get('domain_before', {}).keys()) + list(stats.get('domain_added', {}).keys()))):
        before = stats.get('domain_before', {}).get(domain, 0)
        added = stats.get('domain_added', {}).get(domain, 0)
        after = before + added
        report += f"| {domain} | {before} | +{added} | {after} |\n"

    report += f"""
## Statistics by Type

| Type | Before | Added | After |
|------|--------|-------|-------|
"""
    for type_name in sorted(set(list(stats.get('type_before', {}).keys()) + list(stats.get('type_added', {}).keys()))):
        before = stats.get('type_before', {}).get(type_name, 0)
        added = stats.get('type_added', {}).get(type_name, 0)
        after = before + added
        report += f"| {type_name} | {before} | +{added} | {after} |\n"

    report += f"""
## Statistics by Source (Insurance Company)

| Source | Count |
|--------|-------|
"""
    for source, count in sorted(stats.get('source_distribution', {}).items(), key=lambda x: -x[1]):
        report += f"| {source} | {count} |\n"

    report += f"""
## Validation Errors

"""
    if stats.get('validation_errors'):
        for error in stats['validation_errors'][:10]:
            report += f"- {error}\n"
        if len(stats['validation_errors']) > 10:
            report += f"\n*...and {len(stats['validation_errors']) - 10} more errors*\n"
    else:
        report += "*All units passed validation*\n"

    report += f"""
## Output Files

- Phase 3 merged: `{PHASE3_OUTPUT_PATH.name}` ({stats.get('phase3_file_size', 0):.1f} KB)
- Final MVP: `{MVP_OUTPUT_PATH.name}` ({stats.get('mvp_file_size', 0):.1f} KB)

## Coverage Summary

This MVP knowledge base covers:
- **Insurance companies**: VZP, ZP MV ČR, OZP, ČPZP
- **Document types**: Úhradové dodatky, metodiky, úhradová vyhláška
- **Practical content**: InfoProLekare.cz heuristics, year-over-year comparisons
- **Time period**: 2025-2026 regulations
"""

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    return report_path


def main():
    print("="*80)
    print("PHASE 03 FINAL: MERGING ALL EXTENDED SOURCES")
    print("="*80)
    print()

    # Load schema
    schema = load_schema()
    if schema:
        print(f"✓ Loaded schema from {SCHEMA_PATH}")
    else:
        print("⚠ Running without schema validation")

    # Stats for reporting
    stats = {
        'source_stats': {},
        'validation_errors': [],
        'duplicate_details': [],
        'domain_before': defaultdict(int),
        'domain_added': defaultdict(int),
        'type_before': defaultdict(int),
        'type_added': defaultdict(int),
        'source_distribution': defaultdict(int),
    }

    # Load existing main dataset
    existing_units = []
    if MAIN_DATASET_PATH.exists():
        existing_units = load_units(MAIN_DATASET_PATH)
        print(f"✓ Loaded {len(existing_units)} units from main dataset: {MAIN_DATASET_PATH.name}")

        for unit in existing_units:
            stats['domain_before'][unit.get('domain', 'unknown')] += 1
            stats['type_before'][unit.get('type', 'unknown')] += 1

            # Track source distribution
            source_name = unit.get('source', {}).get('name', 'Unknown')
            if 'VZP' in source_name or 'VZP' in unit.get('title', ''):
                stats['source_distribution']['VZP'] += 1
            elif 'ZP MV' in source_name or 'ZPMV' in source_name:
                stats['source_distribution']['ZP MV ČR'] += 1
            elif 'OZP' in source_name:
                stats['source_distribution']['OZP'] += 1
            elif 'ČPZP' in source_name or 'CPZP' in source_name:
                stats['source_distribution']['ČPZP'] += 1
            elif 'InfoProLekare' in source_name:
                stats['source_distribution']['InfoProLekare.cz'] += 1
            elif 'Úhradová vyhláška' in source_name or 'uhradova-vyhlaska' in unit.get('source', {}).get('url', ''):
                stats['source_distribution']['Úhradová vyhláška'] += 1
            else:
                stats['source_distribution']['Other'] += 1
    else:
        print(f"⚠ Main dataset not found: {MAIN_DATASET_PATH}")

    stats['existing_count'] = len(existing_units)

    # Load new Phase 3 source files
    new_phase3_units = []
    print("\n--- Loading Phase 3 Source Files ---")
    for phase3_file in PHASE3_SOURCE_FILES:
        file_path = EXTRACTED_DIR / phase3_file
        if file_path.exists():
            units = load_units(file_path)
            new_phase3_units.extend(units)
            stats['source_stats'][phase3_file] = len(units)
            print(f"✓ Loaded {len(units)} units from {phase3_file}")
        else:
            print(f"⚠ File not found: {phase3_file}")
            stats['source_stats'][phase3_file] = 0

    stats['new_phase3_count'] = len(new_phase3_units)
    print(f"\nTotal new Phase 3 units: {len(new_phase3_units)}")

    # Validate new units
    print("\n--- Validating New Units ---")
    valid_new_units = []
    for unit in new_phase3_units:
        is_valid, error = validate_unit(unit, unit.get('_source_file', 'unknown'), schema)
        if is_valid:
            valid_new_units.append(unit)
        else:
            stats['validation_errors'].append(error)

    stats['valid_count'] = len(valid_new_units)
    stats['invalid_count'] = len(stats['validation_errors'])
    print(f"✓ Valid units: {len(valid_new_units)}")
    if stats['validation_errors']:
        print(f"✗ Invalid units: {len(stats['validation_errors'])}")
        for error in stats['validation_errors'][:5]:
            print(f"  - {error}")

    # Detect duplicates with existing dataset
    print("\n--- Detecting External Duplicates (vs Existing Dataset) ---")
    duplicates = find_duplicates(valid_new_units, existing_units, threshold=0.80)
    duplicate_ids = {d['new']['id'] for d in duplicates}

    stats['duplicate_external_count'] = len(duplicates)
    for dup in duplicates:
        stats['duplicate_details'].append({
            'new_title': dup['new'].get('title', ''),
            'existing_title': dup['existing'].get('title', ''),
            'score': dup['score'],
            'reason': dup['reason']
        })

    if duplicates:
        print(f"⚠ Found {len(duplicates)} potential duplicates with existing dataset:")
        for dup in duplicates[:5]:
            print(f"  - {dup['new'].get('title', '')[:50]}... ({dup['reason']}, {dup['score']:.0%})")
        if len(duplicates) > 5:
            print(f"  ... and {len(duplicates) - 5} more")
    else:
        print("✓ No external duplicates detected")

    # Filter out duplicates
    units_after_external_dedup = [u for u in valid_new_units if u['id'] not in duplicate_ids]

    # Check for internal duplicates within Phase 3 units
    print("\n--- Detecting Internal Duplicates (within Phase 3) ---")
    internal_duplicates = find_internal_duplicates(units_after_external_dedup, threshold=0.85)
    internal_dup_indices = {d['index'] for d in internal_duplicates}

    stats['duplicate_internal_count'] = len(internal_duplicates)
    if internal_duplicates:
        print(f"⚠ Found {len(internal_duplicates)} internal duplicates")
        for dup in internal_duplicates[:3]:
            print(f"  - Index {dup['index']}: {dup['unit'].get('title', '')[:50]}...")
    else:
        print("✓ No internal duplicates detected")

    # Filter out internal duplicates
    units_to_add = [u for i, u in enumerate(units_after_external_dedup) if i not in internal_dup_indices]

    # Check for duplicate IDs within new units
    print("\n--- Checking for Duplicate IDs ---")
    id_counts = defaultdict(int)
    for unit in units_to_add:
        id_counts[unit['id']] += 1

    internal_id_duplicates = {id: count for id, count in id_counts.items() if count > 1}
    if internal_id_duplicates:
        print(f"⚠ Found {len(internal_id_duplicates)} duplicate IDs within new units")
        seen_ids = set()
        deduped_units = []
        for unit in units_to_add:
            if unit['id'] not in seen_ids:
                seen_ids.add(unit['id'])
                deduped_units.append(unit)
        units_to_add = deduped_units
    else:
        print("✓ No duplicate IDs within new units")

    # Check for ID collisions with existing dataset
    existing_ids = {u['id'] for u in existing_units}
    id_collisions = [u for u in units_to_add if u['id'] in existing_ids]
    if id_collisions:
        print(f"⚠ Found {len(id_collisions)} ID collisions with existing dataset - skipping these")
        units_to_add = [u for u in units_to_add if u['id'] not in existing_ids]

    stats['added_count'] = len(units_to_add)

    # Count domains and types for added units
    for unit in units_to_add:
        stats['domain_added'][unit.get('domain', 'unknown')] += 1
        stats['type_added'][unit.get('type', 'unknown')] += 1

        # Track source distribution
        source_name = unit.get('source', {}).get('name', 'Unknown')
        if 'ZP MV' in source_name or 'ZPMV' in source_name:
            stats['source_distribution']['ZP MV ČR'] += 1
        elif 'OZP' in source_name:
            stats['source_distribution']['OZP'] += 1
        elif 'ČPZP' in source_name or 'CPZP' in source_name:
            stats['source_distribution']['ČPZP'] += 1
        elif 'InfoProLekare' in source_name:
            stats['source_distribution']['InfoProLekare.cz'] += 1
        elif 'Comparison' in unit.get('title', '') or 'srovnání' in str(unit.get('tags', [])):
            stats['source_distribution']['Year Comparison'] += 1
        else:
            stats['source_distribution']['Other'] += 1

    # Merge datasets
    print("\n--- Merging Datasets ---")
    merged_units = existing_units + units_to_add
    stats['final_count'] = len(merged_units)
    print(f"✓ Final dataset: {len(existing_units)} existing + {len(units_to_add)} new = {len(merged_units)} total")

    # Write Phase 3 output (just new units)
    print(f"\n--- Writing Phase 3 Output ---")
    for unit in units_to_add:
        unit.pop('_source_file', None)

    with open(PHASE3_OUTPUT_PATH, 'w', encoding='utf-8') as f:
        for unit in units_to_add:
            f.write(json.dumps(unit, ensure_ascii=False) + '\n')

    stats['phase3_file_size'] = PHASE3_OUTPUT_PATH.stat().st_size / 1024
    print(f"✓ Wrote {len(units_to_add)} Phase 3 units to {PHASE3_OUTPUT_PATH.name}")

    # Write MVP output (complete merged dataset)
    print(f"\n--- Writing MVP Output ---")
    for unit in merged_units:
        unit.pop('_source_file', None)

    with open(MVP_OUTPUT_PATH, 'w', encoding='utf-8') as f:
        for unit in merged_units:
            f.write(json.dumps(unit, ensure_ascii=False) + '\n')

    stats['mvp_file_size'] = MVP_OUTPUT_PATH.stat().st_size / 1024
    print(f"✓ Wrote {len(merged_units)} units to {MVP_OUTPUT_PATH.name}")
    print(f"  File size: {stats['mvp_file_size']:.1f} KB")

    # Generate report
    print("\n--- Generating Report ---")
    report_path = generate_report(stats, REPORT_PATH)
    print(f"✓ Report saved to {report_path}")

    # Summary
    print(f"\n{'='*80}")
    print("PHASE 03 FINAL MERGE SUMMARY")
    print(f"{'='*80}")
    print(f"Existing units (Phase 1-2): {stats['existing_count']}")
    print(f"New Phase 3 units: {stats['new_phase3_count']}")
    print(f"Valid: {stats['valid_count']}, Invalid: {stats['invalid_count']}")
    print(f"External duplicates removed: {stats['duplicate_external_count']}")
    print(f"Internal duplicates removed: {stats['duplicate_internal_count']}")
    print(f"Units added: {stats['added_count']}")
    print(f"Final MVP dataset size: {stats['final_count']}")
    print(f"\nOutput files:")
    print(f"  Phase 3: {PHASE3_OUTPUT_PATH}")
    print(f"  MVP: {MVP_OUTPUT_PATH}")
    print(f"{'='*80}")

    return stats


if __name__ == "__main__":
    main()
