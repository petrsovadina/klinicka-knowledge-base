#!/usr/bin/env python3
"""
Data Audit Script for Knowledge Base Analysis
Analyzes the knowledge_base_final.jsonl file and generates comprehensive statistics.
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import statistics

def load_jsonl(file_path: Path) -> list[dict]:
    """Load JSONL file into list of dictionaries."""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def analyze_dataset(data: list[dict]) -> dict:
    """Perform comprehensive analysis of the dataset."""

    # Basic counts
    total_units = len(data)

    # Domain distribution
    domain_counts = Counter(unit.get('domain', 'unknown') for unit in data)

    # Type distribution
    type_counts = Counter(unit.get('type', 'unknown') for unit in data)

    # Version/year distribution
    version_counts = Counter(unit.get('version', 'unknown') for unit in data)

    # Specialty analysis
    specialty_counts = Counter()
    specialty_coverage = defaultdict(list)
    units_with_all = 0
    for unit in data:
        applicability = unit.get('applicability', {})
        specialties = applicability.get('specialties', [])
        if specialties == ['all'] or 'all' in specialties:
            units_with_all += 1
            specialty_counts['all'] += 1
        else:
            for spec in specialties:
                specialty_counts[spec] += 1
                specialty_coverage[spec].append(unit['id'])

    # Source analysis
    source_counts = Counter()
    for unit in data:
        source = unit.get('source', {})
        source_name = source.get('name', 'unknown')
        source_counts[source_name] += 1

    # Content length analysis
    description_lengths = []
    title_lengths = []
    content_sizes = []

    for unit in data:
        description_lengths.append(len(unit.get('description', '')))
        title_lengths.append(len(unit.get('title', '')))
        content_sizes.append(len(json.dumps(unit.get('content', {}), ensure_ascii=False)))

    # Related units analysis
    related_units_counts = []
    orphan_references = []
    all_ids = {unit['id'] for unit in data}

    for unit in data:
        related = unit.get('related_units', [])
        related_units_counts.append(len(related))
        for ref in related:
            if ref not in all_ids:
                orphan_references.append({'unit_id': unit['id'], 'orphan_ref': ref})

    # Tags analysis
    all_tags = Counter()
    tags_per_unit = []
    for unit in data:
        tags = unit.get('tags', [])
        tags_per_unit.append(len(tags))
        for tag in tags:
            all_tags[tag] += 1

    # Validity period analysis
    validity_years = Counter()
    for unit in data:
        applicability = unit.get('applicability', {})
        valid_from = applicability.get('valid_from', '')
        if valid_from:
            year = valid_from.split('-')[0]
            validity_years[year] += 1

    # Compile statistics
    stats = {
        'metadata': {
            'analysis_date': datetime.now().isoformat(),
            'source_file': 'data/knowledge_base_final.jsonl'
        },
        'overview': {
            'total_units': total_units,
            'unique_ids': len(all_ids),
            'duplicates': total_units - len(all_ids)
        },
        'domain_distribution': dict(domain_counts.most_common()),
        'type_distribution': dict(type_counts.most_common()),
        'version_distribution': dict(version_counts.most_common()),
        'validity_year_distribution': dict(validity_years.most_common()),
        'specialty_coverage': {
            'total_specialty_assignments': sum(specialty_counts.values()),
            'units_with_all_specialties': units_with_all,
            'unique_specialties': len(specialty_counts),
            'specialty_distribution': dict(specialty_counts.most_common(30))
        },
        'source_distribution': dict(source_counts.most_common()),
        'content_quality': {
            'description_length': {
                'min': min(description_lengths) if description_lengths else 0,
                'max': max(description_lengths) if description_lengths else 0,
                'mean': round(statistics.mean(description_lengths), 2) if description_lengths else 0,
                'median': statistics.median(description_lengths) if description_lengths else 0
            },
            'title_length': {
                'min': min(title_lengths) if title_lengths else 0,
                'max': max(title_lengths) if title_lengths else 0,
                'mean': round(statistics.mean(title_lengths), 2) if title_lengths else 0,
                'median': statistics.median(title_lengths) if title_lengths else 0
            },
            'content_size_bytes': {
                'min': min(content_sizes) if content_sizes else 0,
                'max': max(content_sizes) if content_sizes else 0,
                'mean': round(statistics.mean(content_sizes), 2) if content_sizes else 0
            }
        },
        'relationships': {
            'total_related_references': sum(related_units_counts),
            'mean_related_per_unit': round(statistics.mean(related_units_counts), 2) if related_units_counts else 0,
            'units_with_no_relations': related_units_counts.count(0),
            'orphan_references_count': len(orphan_references),
            'orphan_references': orphan_references[:10]  # First 10 for reference
        },
        'tags': {
            'total_tag_assignments': sum(tags_per_unit),
            'unique_tags': len(all_tags),
            'mean_tags_per_unit': round(statistics.mean(tags_per_unit), 2) if tags_per_unit else 0,
            'top_30_tags': dict(all_tags.most_common(30))
        }
    }

    return stats

def main():
    # Paths
    project_root = Path(__file__).parent.parent
    data_file = project_root / 'data' / 'knowledge_base_final.jsonl'
    output_file = project_root / 'docs' / 'analysis' / 'data_statistics.json'

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Load and analyze data
    print(f"Loading data from {data_file}...")
    data = load_jsonl(data_file)
    print(f"Loaded {len(data)} knowledge units")

    print("Analyzing dataset...")
    stats = analyze_dataset(data)

    # Save results
    print(f"Saving statistics to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print("Analysis complete!")

    # Print summary
    print("\n=== SUMMARY ===")
    print(f"Total units: {stats['overview']['total_units']}")
    print(f"\nDomain distribution:")
    for domain, count in stats['domain_distribution'].items():
        print(f"  {domain}: {count}")
    print(f"\nType distribution:")
    for type_, count in stats['type_distribution'].items():
        print(f"  {type_}: {count}")
    print(f"\nVersion distribution:")
    for version, count in stats['version_distribution'].items():
        print(f"  {version}: {count}")
    print(f"\nOrphan references: {stats['relationships']['orphan_references_count']}")

if __name__ == '__main__':
    main()
