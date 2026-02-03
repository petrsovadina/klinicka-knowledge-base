---
type: report
title: Phase 03 Final Merge Report - Extended Sources
created: 2026-02-03
tags:
  - merge-report
  - phase-03
  - mvp
  - final
related:
  - "[[MVP-KB-03-Extended-Sources]]"
---

# Phase 03: Final Merge Report

Generated: 2026-02-03 04:10:53

## Summary

| Metric | Count |
|--------|-------|
| Existing units (Phase 1-2) | 552 |
| New Phase 3 units processed | 117 |
| Valid units | 117 |
| Invalid units (rejected) | 0 |
| Duplicates with existing (removed) | 0 |
| Internal duplicates (removed) | 0 |
| Units added to dataset | 117 |
| **Final MVP dataset size** | **669** |

## Source Files Processed

- `zpmv_metodika_2026.jsonl`: 30 units
- `ozp_metodika_2026.jsonl`: 16 units
- `cpzp_metodika_2026.jsonl`: 15 units
- `year_comparison_2025_2026.jsonl`: 16 units
- `infoprolekare_articles.jsonl`: 40 units

## Duplicate Detection

External threshold: 80% similarity (title + description)
Internal threshold: 85% similarity

*No external duplicates detected*

## Statistics by Domain

| Domain | Before | Added | After |
|--------|--------|-------|-------|
| compliance | 26 | +3 | 29 |
| financni-rizika | 85 | +7 | 92 |
| legislativa | 58 | +3 | 61 |
| provoz | 45 | +6 | 51 |
| uhrady | 338 | +98 | 436 |

## Statistics by Type

| Type | Before | Added | After |
|------|--------|-------|-------|
| anti_pattern | 14 | +5 | 19 |
| condition | 30 | +0 | 30 |
| definition | 41 | +3 | 44 |
| exception | 27 | +5 | 32 |
| risk | 39 | +11 | 50 |
| rule | 401 | +93 | 494 |

## Statistics by Source (Insurance Company)

| Source | Count |
|--------|-------|
| Other | 259 |
| Úhradová vyhláška | 224 |
| ZP MV ČR | 78 |
| InfoProLekare.cz | 62 |
| OZP | 25 |
| Year Comparison | 11 |
| ČPZP | 10 |

## Validation Errors

*All units passed validation*

## Output Files

- Phase 3 merged: `knowledge_base_phase3.jsonl` (139.3 KB)
- Final MVP: `knowledge_base_mvp.jsonl` (721.4 KB)

## Coverage Summary

This MVP knowledge base covers:
- **Insurance companies**: VZP, ZP MV ČR, OZP, ČPZP
- **Document types**: Úhradové dodatky, metodiky, úhradová vyhláška
- **Practical content**: InfoProLekare.cz heuristics, year-over-year comparisons
- **Time period**: 2025-2026 regulations
