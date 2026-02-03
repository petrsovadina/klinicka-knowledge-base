---
type: analysis
title: Use-Case Coverage Matrix
created: 2026-02-03
tags:
  - data-quality
  - coverage
  - use-cases
  - gaps
related:
  - "[[gap_analysis_report]]"
  - "[[data_statistics]]"
  - "[[rag_gap_analysis]]"
  - "[[Phase-02-Source-Extraction]]"
---

# Use-Case Coverage Matrix

Analýza pokrytí plánovaných use-cases z dokumentace `docs/roadmap_and_strategy.md` aktuálním datasetem (409 znalostních jednotek).

## Legend

| Symbol | Status | Popis |
|--------|--------|-------|
| :white_check_mark: | Plné pokrytí | Data plně podporují use-case |
| :large_orange_diamond: | Částečné pokrytí | Některá data existují, ale jsou neúplná |
| :x: | Chybí | Use-case není pokrytý v datech |

---

## 1. AI Decision-Support Use-Cases (Fáze 4)

Dotazy v přirozeném jazyce, které má AI asistent zodpovídat.

| Use-Case | Příklad dotazu | Status | Pokrytí | Poznámky |
|----------|---------------|--------|---------|----------|
| Bonifikace pro odbornost | "Jaké jsou bonifikace pro mou odbornost v roce 2026?" | :large_orange_diamond: | 75% | 22 jednotek o bonifikacích, ale chybí konkrétní hodnoty z dodatků |
| Překročení MAXÚ | "Co se stane, pokud překročím MAXÚ?" | :large_orange_diamond: | 60% | Definice MAXÚ existují, chybí explicitní důsledky |
| Optimalizace PURO | "Jak optimalizovat PURO?" | :large_orange_diamond: | 55% | 11 anti-patternů, málo praktických heuristik |
| Hodnota bodu | "Jaká je hodnota bodu pro mou odbornost?" | :x: | 0% | Chybí konkrétní hodnoty z úhradových dodatků |
| Meziroční srovnání | "Jak se liší úhrady oproti minulému roku?" | :x: | 0% | Chybí comparison type a historická data |
| Rizika při převzetí | "Jaká jsou rizika při převzetí ordinace?" | :white_check_mark: | 90% | ku-011-riziko-prevzetí-ordinace a související |
| DRG zařazení | "Jak se zařazuje výkon do DRG?" | :white_check_mark: | 85% | 39 jednotek o DRG, 27 o CZ-DRG |
| Vykazování výkonů | "Jak správně vykázat tento výkon?" | :large_orange_diamond: | 65% | 16 jednotek o vykazování, chybí konkrétní příklady |

### Shrnutí AI Decision-Support
- **Plné pokrytí:** 2/8 use-cases (25%)
- **Částečné pokrytí:** 4/8 use-cases (50%)
- **Chybí:** 2/8 use-cases (25%)

---

## 2. Pokrytí Zdrojů (Fáze 2)

| Zdroj | Status | Aktuální jednotky | Cílový počet | Gap |
|-------|--------|-------------------|--------------|-----|
| Úhradová vyhláška 2026 | :large_orange_diamond: | 12 | 40 | -28 |
| Úhradová vyhláška 2025 | :white_check_mark: | 388 | 200 | +188 |
| Úhradová vyhláška 2024 | :x: | 0 | 30 | -30 |
| Úhradová vyhláška 2023 | :x: | 0 | 20 | -20 |
| Metodiky VZP | :large_orange_diamond: | ~200 | 50 | +150 |
| Metodiky ZP MV ČR | :large_orange_diamond: | 8 | 20 | -12 |
| Metodiky OZP | :large_orange_diamond: | 3 | 20 | -17 |
| Metodiky ČPZP | :large_orange_diamond: | 2 | 20 | -18 |
| Metodiky RBP | :large_orange_diamond: | 2 | 15 | -13 |
| InfoProLekare.cz | :large_orange_diamond: | 3 | 40 | -37 |
| Zákon 48/1997 Sb. | :x: | 0 | 20 | -20 |
| Zákon 372/2011 Sb. | :x: | 0 | 10 | -10 |

### Shrnutí Pokrytí Zdrojů
- **Plné pokrytí:** 1/12 zdrojů (8%)
- **Částečné pokrytí:** 7/12 zdrojů (58%)
- **Chybí:** 4/12 zdrojů (33%)

---

## 3. Pokrytí Odborností (Cíl: 10+)

| Odbornost | Status | Jednotky | Poznámky |
|-----------|--------|----------|----------|
| all (všechny) | :white_check_mark: | 307 | Obecné jednotky |
| 603 (gynekologie-amb) | :large_orange_diamond: | 10 | Základní pokrytí |
| 604 (chirurgie-amb) | :large_orange_diamond: | 9 | Základní pokrytí |
| stomatologie | :large_orange_diamond: | 8 | Základní pokrytí |
| laboratorní diagnostika | :large_orange_diamond: | 7 | Základní pokrytí |
| 926 (rehabilitace) | :large_orange_diamond: | 7 | Základní pokrytí |
| VPL (praktici) | :large_orange_diamond: | 6 | Fragmentované pokrytí |
| PLDD (pediatři) | :large_orange_diamond: | 4 | Minimální pokrytí |
| psychiatrie | :x: | 0 | Chybí úplně |
| kardiologie | :x: | 0 | Chybí úplně |
| fyzioterapie | :x: | 0 | Chybí úplně |

### Shrnutí Pokrytí Odborností
- **Unikátních odborností v datasetu:** 102
- **Odborností s 5+ jednotkami:** 9
- **Zcela chybějící klíčové odbornosti:** psychiatrie, kardiologie, fyzioterapie

---

## 4. Pokrytí Domén (Cíl: 5/5)

| Doména | Status | Jednotky | % z celku | Cíl | Gap |
|--------|--------|----------|-----------|-----|-----|
| uhrady | :white_check_mark: | 307 | 75.1% | 60% | +15% |
| financni-rizika | :large_orange_diamond: | 34 | 8.3% | 15% | -7% |
| legislativa | :large_orange_diamond: | 32 | 7.8% | 10% | -2% |
| compliance | :large_orange_diamond: | 20 | 4.9% | 10% | -5% |
| provoz | :x: | 16 | 3.9% | 5% | -1% |

### Shrnutí Pokrytí Domén
- **Plné pokrytí:** 1/5 domén (úhrady dominují dataset)
- **Částečné pokrytí:** 3/5 domén
- **Nedostatečné pokrytí:** 1/5 domén (provoz)
- **Nerovnoměrnost:** 75% jednotek v jedné doméně

---

## 5. Pokrytí Typů Znalostních Jednotek

| Typ | Status | Jednotky | % z celku | Hodnocení |
|-----|--------|----------|-----------|-----------|
| rule | :white_check_mark: | 294 | 71.9% | Dostatečné |
| definition | :white_check_mark: | 35 | 8.6% | Dostatečné |
| risk | :large_orange_diamond: | 30 | 7.3% | Rozšířit o praktická rizika |
| condition | :large_orange_diamond: | 20 | 4.9% | Přidat pro specifické odbornosti |
| exception | :large_orange_diamond: | 19 | 4.6% | Rozšířit pro odbornosti |
| anti_pattern | :large_orange_diamond: | 11 | 2.7% | Přidat z praxe |
| comparison | :x: | 0 | 0% | **Chybí typ v schématu** |
| heuristic | :x: | 0 | 0% | **Chybí typ v schématu** |
| example | :x: | 0 | 0% | **Chybí typ v schématu** |

### Shrnutí Pokrytí Typů
- **Plné pokrytí:** 2/9 typů (22%)
- **Částečné pokrytí:** 4/9 typů (44%)
- **Chybí:** 3/9 typů (33%) - vyžaduje rozšíření schématu

---

## 6. Produktové Use-Cases (Fáze 5)

| Produkt | Use-Case | Status | Poznámky |
|---------|----------|--------|----------|
| AI Asistent | Dotazy o bonifikacích | :large_orange_diamond: | Částečná data |
| AI Asistent | Výpočet úhrad | :large_orange_diamond: | Chybí konkrétní hodnoty |
| AI Asistent | Rizikové analýzy | :large_orange_diamond: | 30 risk jednotek, málo praktických |
| Audit modul | Ekonomická analýza | :x: | Chybí benchmarky a metriky |
| Audit modul | Identifikace anti-patternů | :large_orange_diamond: | Pouze 11 anti-patternů |
| Audit modul | Doporučení optimalizace | :x: | Chybí heuristiky |
| Reporting | Srovnání s průměrem | :x: | Chybí agregovaná data |
| Reporting | Predikce příjmů | :x: | Chybí historická data |

### Shrnutí Produktových Use-Cases
- **Plné pokrytí:** 0/8 use-cases (0%)
- **Částečné pokrytí:** 4/8 use-cases (50%)
- **Chybí:** 4/8 use-cases (50%)

---

## 7. Prioritizovaný Seznam Nepokrytých Use-Cases

### Priority 1 - Critical (Blokuje MVP)
1. **Konkrétní hodnoty bodu** - 0/100 jednotek
2. **Důsledky regulací** - 5/20 jednotek
3. **Meziroční srovnání** - 0/30 jednotek (chybí typ)

### Priority 2 - High (Omezuje funkcionalitu)
4. **Metodiky ostatních pojišťoven** - 15/80 jednotek
5. **Praktické heuristiky** - 3/40 jednotek
6. **Historická data 2023-2024** - 0/50 jednotek

### Priority 3 - Medium (Zlepšuje kvalitu)
7. **Specifické odbornosti** - fragmentované pokrytí
8. **Anti-patterny z praxe** - 11/30 jednotek
9. **Příklady vykazování** - 0/20 jednotek

### Priority 4 - Low (Nice-to-have)
10. **Legislativní aktualizace 2026** - částečné
11. **Optimalizace granularity** - revize existujících

---

## 8. Doporučení pro Phase 02

Na základě této analýzy doporučujeme v Phase 02 prioritizovat:

1. **Extrakce hodnot bodu z VZP dodatků** - kritický gap
2. **Přidání comparison typu do schématu** - umožní meziroční srovnání
3. **Dokumentace důsledků regulací** - PURO, MAXÚ
4. **Rozšíření o další pojišťovny** - ZP MV ČR, OZP, ČPZP

Viz [[Phase-02-Source-Extraction]] pro detailní plán extrakce.

---

*Generováno: 2026-02-03*
*Zdroj: Automatická analýza datasetu vs. roadmap_and_strategy.md*
