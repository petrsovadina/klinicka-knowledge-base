#!/usr/bin/env python3
"""
Validate the knowledge base dataset for schema compliance, duplicate IDs, and orphan references.

This script performs comprehensive validation without external dependencies.
"""
import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Paths - use relative paths from script location
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
SCHEMA_PATH = PROJECT_ROOT / "schemas" / "knowledge_unit.schema.json"
DATASET_PATH = DATA_DIR / "knowledge_base_final.jsonl"
OUTPUT_PATH = PROJECT_ROOT / "docs" / "analysis" / "validation_results.json"

# ID patterns
# Standard UUID format
UUID_PATTERN = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    re.IGNORECASE
)
# Practical ID format used in the dataset:
# - ku-NNN (short form)
# - ku-NNN-slug (with slug)
# - ku-NNN-slug-YYYY (with year suffix)
# Allow Unicode letters (Czech diacritics) and underscores in slugs
PRACTICAL_ID_PATTERN = re.compile(
    r'^ku-\d{1,4}(-[\w-]+)?(-\d{4})?$',
    re.IGNORECASE | re.UNICODE
)

# Date patterns
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
DATETIME_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')

# Schema definitions (hardcoded for no-dependency validation)
REQUIRED_FIELDS = ['id', 'type', 'domain', 'title', 'description', 'version', 'source', 'content', 'applicability']
VALID_TYPES = ['rule', 'exception', 'risk', 'anti_pattern', 'condition', 'definition']
VALID_DOMAINS = ['uhrady', 'provoz', 'compliance', 'financni-rizika', 'legislativa']


def load_units(file_path):
    """Load units from JSONL file."""
    units = []
    errors = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                unit = json.loads(line)
                unit['_line_num'] = line_num
                units.append(unit)
            except json.JSONDecodeError as e:
                errors.append(f"Line {line_num}: JSON parse error - {e}")
    return units, errors


def validate_required_fields(unit):
    """Check that all required fields are present."""
    missing = []
    for field in REQUIRED_FIELDS:
        if field not in unit:
            missing.append(field)
    return missing


def validate_field_types(unit):
    """Validate field types and values."""
    errors = []

    # ID must be valid (either UUID or practical format)
    if 'id' in unit:
        id_val = unit['id']
        if not isinstance(id_val, str):
            errors.append(f"'id' must be string, got {type(id_val).__name__}")
        elif not (UUID_PATTERN.match(id_val) or PRACTICAL_ID_PATTERN.match(id_val)):
            errors.append(f"Invalid ID format: {id_val} (expected UUID or ku-NNN-slug format)")

    # Type must be valid enum
    if 'type' in unit:
        if unit['type'] not in VALID_TYPES:
            errors.append(f"Invalid 'type' value: {unit['type']} (expected one of {VALID_TYPES})")

    # Domain must be valid enum
    if 'domain' in unit:
        if unit['domain'] not in VALID_DOMAINS:
            errors.append(f"Invalid 'domain' value: {unit['domain']} (expected one of {VALID_DOMAINS})")

    # Title must be string
    if 'title' in unit and not isinstance(unit['title'], str):
        errors.append(f"'title' must be string, got {type(unit['title']).__name__}")

    # Description must be string
    if 'description' in unit and not isinstance(unit['description'], str):
        errors.append(f"'description' must be string, got {type(unit['description']).__name__}")

    # Version must be string
    if 'version' in unit and not isinstance(unit['version'], str):
        errors.append(f"'version' must be string, got {type(unit['version']).__name__}")

    # Source validation
    if 'source' in unit:
        source = unit['source']
        if not isinstance(source, dict):
            errors.append(f"'source' must be object, got {type(source).__name__}")
        else:
            for required in ['name', 'url', 'retrieved_at']:
                if required not in source:
                    errors.append(f"'source.{required}' is required")

    # Content must be object
    if 'content' in unit and not isinstance(unit['content'], dict):
        errors.append(f"'content' must be object, got {type(unit['content']).__name__}")

    # Applicability validation
    if 'applicability' in unit:
        app = unit['applicability']
        if not isinstance(app, dict):
            errors.append(f"'applicability' must be object, got {type(app).__name__}")
        else:
            if 'specialties' not in app:
                errors.append("'applicability.specialties' is required")
            elif not isinstance(app['specialties'], list):
                errors.append(f"'applicability.specialties' must be array")
            if 'valid_from' not in app:
                errors.append("'applicability.valid_from' is required")
            elif not DATE_PATTERN.match(str(app.get('valid_from', ''))):
                errors.append(f"'applicability.valid_from' must be date format (YYYY-MM-DD)")

    # Tags must be array of strings
    if 'tags' in unit:
        if not isinstance(unit['tags'], list):
            errors.append(f"'tags' must be array")
        elif not all(isinstance(t, str) for t in unit['tags']):
            errors.append(f"'tags' must be array of strings")

    # Related units must be array of valid IDs
    if 'related_units' in unit:
        if not isinstance(unit['related_units'], list):
            errors.append(f"'related_units' must be array")
        else:
            for i, ref in enumerate(unit['related_units']):
                if not isinstance(ref, str):
                    errors.append(f"'related_units[{i}]' must be string")
                elif not (UUID_PATTERN.match(ref) or PRACTICAL_ID_PATTERN.match(ref)):
                    # Allow short references too (legacy or special references)
                    if len(ref) < 2:
                        errors.append(f"'related_units[{i}]' has invalid reference: {ref}")

    return errors


def validate_unit(unit):
    """Validate a single unit against schema rules."""
    all_errors = []

    # Check required fields
    missing = validate_required_fields(unit)
    if missing:
        all_errors.append(f"Missing required fields: {missing}")

    # Check field types and values
    type_errors = validate_field_types(unit)
    all_errors.extend(type_errors)

    return all_errors


def check_duplicate_ids(units):
    """Check for duplicate IDs."""
    id_counts = defaultdict(list)
    for unit in units:
        if 'id' in unit:
            id_counts[unit['id']].append(unit.get('_line_num', 'unknown'))

    duplicates = {id: lines for id, lines in id_counts.items() if len(lines) > 1}
    return duplicates


def check_orphan_references(units):
    """Check for orphan related_units references."""
    valid_ids = {unit['id'] for unit in units if 'id' in unit}

    orphans = []
    for unit in units:
        related = unit.get('related_units', [])
        for ref_id in related:
            if ref_id not in valid_ids:
                orphans.append({
                    'unit_id': unit.get('id', 'unknown'),
                    'orphan_reference': ref_id,
                    'line': unit.get('_line_num', 'unknown')
                })

    return orphans


def main():
    print("=" * 80)
    print("KNOWLEDGE BASE VALIDATION")
    print("=" * 80)
    print(f"\nDataset: {DATASET_PATH}")
    print(f"Schema: {SCHEMA_PATH}")
    print()

    # Load units
    print("Loading dataset...")
    units, parse_errors = load_units(DATASET_PATH)
    total_units = len(units)
    print(f"✓ Loaded {total_units} units")
    if parse_errors:
        print(f"⚠ {len(parse_errors)} parse errors:")
        for err in parse_errors[:5]:
            print(f"  - {err}")

    # Validation results
    results = {
        'timestamp': datetime.now().isoformat(),
        'dataset_path': str(DATASET_PATH),
        'total_units': total_units,
        'checks': {}
    }

    # 1. Schema validation
    print("\n1. Validating against schema rules...")
    valid_count = 0
    invalid_units = []

    for unit in units:
        line_num = unit.get('_line_num')
        errors = validate_unit(unit)
        if errors:
            invalid_units.append({
                'id': unit.get('id', 'unknown'),
                'line': line_num,
                'errors': errors
            })
        else:
            valid_count += 1

    schema_compliance = (valid_count / total_units * 100) if total_units > 0 else 0

    results['checks']['schema_validation'] = {
        'passed': len(invalid_units) == 0,
        'valid_units': valid_count,
        'invalid_units': len(invalid_units),
        'compliance_percentage': round(schema_compliance, 2),
        'errors': invalid_units[:10]
    }

    if invalid_units:
        print(f"✗ Schema validation: {len(invalid_units)} invalid units ({schema_compliance:.1f}% compliance)")
        for err in invalid_units[:5]:
            print(f"  - {err['id']}: {err['errors'][0]}")
    else:
        print(f"✓ Schema validation: 100% compliance ({valid_count}/{total_units} units)")

    # 2. Duplicate IDs check
    print("\n2. Checking for duplicate IDs...")
    duplicates = check_duplicate_ids(units)

    results['checks']['duplicate_ids'] = {
        'passed': len(duplicates) == 0,
        'duplicate_count': len(duplicates),
        'duplicates': dict(list(duplicates.items())[:10])
    }

    if duplicates:
        print(f"✗ Found {len(duplicates)} duplicate IDs:")
        for id, lines in list(duplicates.items())[:5]:
            print(f"  - {id}: lines {lines}")
    else:
        print(f"✓ No duplicate IDs found (all {total_units} IDs are unique)")

    # 3. Orphan references check
    print("\n3. Checking for orphan related_units references...")
    orphans = check_orphan_references(units)

    results['checks']['orphan_references'] = {
        'passed': len(orphans) == 0,
        'orphan_count': len(orphans),
        'orphans': orphans[:10]
    }

    if orphans:
        print(f"✗ Found {len(orphans)} orphan references:")
        for o in orphans[:5]:
            print(f"  - Unit {o['unit_id']} references non-existent {o['orphan_reference']}")
    else:
        print(f"✓ No orphan references found")

    # 4. Additional statistics
    print("\n4. Computing additional statistics...")

    # Count units with related_units
    units_with_relations = sum(1 for u in units if u.get('related_units', []))
    unique_related_refs = set()
    for u in units:
        unique_related_refs.update(u.get('related_units', []))

    results['checks']['relationships'] = {
        'units_with_related': units_with_relations,
        'unique_references': len(unique_related_refs),
        'percentage_with_relations': round(units_with_relations / total_units * 100, 1) if total_units > 0 else 0
    }

    print(f"✓ {units_with_relations} units ({results['checks']['relationships']['percentage_with_relations']}%) have related_units")
    print(f"✓ {len(unique_related_refs)} unique related unit references")

    # Domain distribution
    domain_counts = defaultdict(int)
    for unit in units:
        domain_counts[unit.get('domain', 'unknown')] += 1

    results['checks']['domain_distribution'] = dict(domain_counts)

    # Type distribution
    type_counts = defaultdict(int)
    for unit in units:
        type_counts[unit.get('type', 'unknown')] += 1

    results['checks']['type_distribution'] = dict(type_counts)

    # Summary
    all_passed = all(
        results['checks'][check].get('passed', True)
        for check in ['schema_validation', 'duplicate_ids', 'orphan_references']
    )
    results['overall_passed'] = all_passed

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total units: {total_units}")
    print(f"Schema compliance: {schema_compliance:.1f}%")
    print(f"Duplicate IDs: {len(duplicates)}")
    print(f"Orphan references: {len(orphans)}")
    print(f"\nDomain distribution:")
    for domain, count in sorted(domain_counts.items()):
        print(f"  - {domain}: {count}")
    print(f"\nType distribution:")
    for type_name, count in sorted(type_counts.items()):
        print(f"  - {type_name}: {count}")
    print(f"\nOverall: {'✓ ALL CHECKS PASSED' if all_passed else '✗ SOME CHECKS FAILED'}")
    print("=" * 80)

    # Save results
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to: {OUTPUT_PATH}")

    return results


if __name__ == "__main__":
    main()
