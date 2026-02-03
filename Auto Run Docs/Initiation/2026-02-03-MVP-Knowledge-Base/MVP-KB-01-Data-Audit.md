# Phase 01: Data Audit & Gap Analysis

Tato fáze provede hloubkovou analýzu stávajících 409 znalostních jednotek a vytvoří strukturovaný report identifikující kritické mezery v datech. Na konci fáze vznikne funkční audit report v Markdown formátu s vizualizací pokrytí a prioritizovaným seznamem chybějících oblastí – viditelný výstup demonstrující hodnotu projektu.

## Tasks

- [x] Načíst a analyzovat aktuální dataset z `data/knowledge_base_final.jsonl`:
  - Spočítat distribuci jednotek podle domény (uhrady, provoz, compliance, financni-rizika, legislativa)
  - Spočítat distribuci podle typu (rule, exception, risk, anti_pattern, condition, definition)
  - Identifikovat pokrytí podle odborností (ambulantní specialisté, praktici, stomatologie, atd.)
  - Analyzovat pokrytí podle roku platnosti (2024, 2025, 2026)
  - Vytvořit statistiky délky obsahu a kvality popisů
  - Uložit raw statistiky do `docs/analysis/data_statistics.json`

  **Completed 2026-02-03:** Created `scripts/data_audit.py` to analyze the dataset. Key findings:
  - **409 knowledge units** (100% unique IDs, no duplicates)
  - **Domain distribution:** uhrady (307), financni-rizika (34), legislativa (32), compliance (20), provoz (16)
  - **Type distribution:** rule (294), definition (35), risk (30), condition (20), exception (19), anti_pattern (11)
  - **Version:** 96% from 2025, only 4% from 2026
  - **Validity:** 344 units valid from 2025, 65 from 2026
  - **Specialty coverage:** 307 units apply to "all", 102 unique specialties referenced
  - **Content quality:** Avg description 240 chars (range 96-464), avg title 64 chars
  - **Relationships:** Only 24 units have related_units (94% have none), no orphan references
  - Statistics saved to `docs/analysis/data_statistics.json`

- [x] Analyzovat výsledky RAG testu z `data/test_results.json`:
  - Extrahovat dotazy se skóre < 0.7 (identifikované mezery)
  - Mapovat slabé odpovědi na chybějící typy znalostí
  - Analyzovat chybějící témata zmíněná v `docs/rag_mvp_analysis.md`
  - Vytvořit seznam témat s nedostatečným pokrytím
  - Uložit analýzu do `docs/analysis/rag_gap_analysis.json`

  **Completed 2026-02-03:** Analyzed 10 RAG test queries from `data/test_results.json`. Key findings:
  - **4 queries below 0.7 threshold:** PURO consequences (0.50), year-over-year comparison (0.39), specific point values (0.59), IČZ change risks (0.66)
  - **Critical gaps identified:** Missing specific point values from insurance supplements, missing comparison-type units, incomplete consequence descriptions
  - **7 gap categories prioritized:** GAP-001 to GAP-007 covering concrete values, comparisons, other insurers' methodologies, historical data, practical heuristics
  - **Missing knowledge types:** comparison, heuristic, example (not present in current schema)
  - **Recommendations:** Immediate focus on VZP supplement extraction, creating comparison units, and documenting regulation consequences
  - Analysis saved to `docs/analysis/rag_gap_analysis.json`

- [ ] Porovnat aktuální pokrytí s cílovými use-cases z dokumentace:
  - Načíst plánované use-cases z `docs/roadmap_and_strategy.md`
  - Vyhodnotit pokrytí pro každý use-case (plné/částečné/chybí)
  - Identifikovat use-cases bez podpory v datech
  - Vytvořit matici pokrytí use-case vs. dostupná data

- [ ] Vytvořit strukturovaný Gap Analysis Report v `docs/analysis/gap_analysis_report.md`:
  - YAML front matter: type: analysis, title: Gap Analysis Report, created: YYYY-MM-DD, tags: [data-quality, gaps, priorities]
  - Sekce 1: Executive Summary (3-5 klíčových zjištění)
  - Sekce 2: Statistické přehledy s tabulkami
  - Sekce 3: Identifikované mezery seřazené podle priority
  - Sekce 4: Mapa chybějících zdrojů (VZP dodatky, pojišťovny, praktické články)
  - Sekce 5: Doporučení pro Phase 02 (konkrétní akce)
  - Použít wiki-links `[[Phase-02-Source-Extraction]]` pro cross-reference

- [ ] Spustit validaci datasetu a ověřit integritu:
  - Spustit `python scripts/merge_and_validate.py` s aktuálním datasetem
  - Ověřit 100% schema compliance
  - Zkontrolovat duplicitní ID
  - Zkontrolovat orphan related_units odkazy
  - Přidat výsledky validace do reportu

- [ ] Vytvořit prioritizovaný backlog datových potřeb v `docs/analysis/data_backlog.md`:
  - YAML front matter: type: reference, title: Data Backlog, created: YYYY-MM-DD, tags: [backlog, priorities, sources]
  - Priority 1 (Critical): Konkrétní hodnoty bodu z úhradových dodatků VZP
  - Priority 2 (High): Metodiky ostatních pojišťoven (ZP MV, OZP, ČPZP)
  - Priority 3 (Medium): Srovnávací jednotky (comparison type)
  - Priority 4 (Low): Praktické heuristiky z InfoProLekare.cz
  - Každá položka: zdroj, očekávaný počet jednotek, dopad na RAG kvalitu
  - Cross-reference: `[[gap_analysis_report]]`, `[[Phase-02-Source-Extraction]]`
