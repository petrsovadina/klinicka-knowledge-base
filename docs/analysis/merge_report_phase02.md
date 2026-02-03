---
type: report
title: Phase 02 Merge Report - VZP Source Extraction
created: 2026-02-03
tags:
  - merge-report
  - phase-02
  - vzp-sources
related:
  - "[[MVP-KB-02-Source-Extraction]]"
---

# Phase 02: Merge Report

Generated: 2026-02-03 02:41:52

## Summary

| Metric | Count |
|--------|-------|
| Total units before merge | 552 |
| New VZP units processed | 106 |
| Valid units | 106 |
| Invalid units (rejected) | 0 |
| Duplicates detected | 0 |
| Units added to dataset | 106 |
| **Final dataset size** | **658** |

## Source Files Processed

- `vzp_metodika_as_2026.jsonl`: 32 units
- `vzp_dodatek_as_2026.jsonl`: 40 units
- `vzp_metodika_pl_2026.jsonl`: 34 units

## Duplicate Detection

Threshold: 75% similarity (title + description)

*No duplicates detected*

## Statistics by Domain

| Domain | Before | Added | After |
|--------|--------|-------|-------|
| compliance | 26 | +0 | 26 |
| financni-rizika | 85 | +7 | 92 |
| legislativa | 58 | +0 | 58 |
| provoz | 45 | +0 | 45 |
| uhrady | 338 | +99 | 437 |

## Statistics by Type

| Type | Before | Added | After |
|------|--------|-------|-------|
| anti_pattern | 14 | +0 | 14 |
| condition | 30 | +14 | 44 |
| definition | 41 | +11 | 52 |
| exception | 27 | +8 | 35 |
| risk | 39 | +7 | 46 |
| rule | 401 | +66 | 467 |

## Validation Errors

*All units passed validation*

## Output

- Output file: `knowledge_base_expanded_v2.jsonl`
- File size: 694.1 KB
