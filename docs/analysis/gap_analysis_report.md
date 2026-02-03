---
type: analysis
title: Gap Analysis Report
created: 2026-02-03
tags:
  - data-quality
  - gaps
  - priorities
related:
  - "[[data_statistics]]"
  - "[[rag_gap_analysis]]"
  - "[[use_case_coverage_matrix]]"
  - "[[Phase-02-Source-Extraction]]"
---

# Gap Analysis Report

Komplexní analýza mezer v znalostní bázi pro klinické úhrady. Tento report syntetizuje výsledky z datového auditu, RAG testování a analýzy pokrytí use-cases.

---

## 1. Executive Summary

### Klíčová zjištění

1. **Dataset obsahuje 409 znalostních jednotek** bez duplicit, ale s výraznou nerovnováhou – 75% jednotek patří do domény úhrady, ostatní domény jsou podreprezentovány.

2. **Kritické mezery v konkrétních hodnotách** – Chybí 100% specifických hodnot bodu z úhradových dodatků pojišťoven, což blokuje klíčový use-case „Jaká je hodnota bodu pro mou odbornost?".

3. **Chybí 3 typy znalostních jednotek** potřebné pro plnou funkcionalitu:
   - `comparison` – pro meziroční srovnání úhrad
   - `heuristic` – pro praktické tipy z praxe
   - `example` – pro konkrétní příklady vykazování

4. **RAG testování odhalilo 4 z 10 dotazů pod prahem 0.7** – nejslabší jsou srovnávací dotazy (0.39) a dotazy na konkrétní hodnoty (0.59).

5. **Pouze 25% AI decision-support use-cases má plné pokrytí** (2 z 8), zatímco 0% produktových use-cases je plně pokryto.

---

## 2. Statistické přehledy

### 2.1 Distribuce podle domény

| Doména | Počet jednotek | Podíl | Cíl | Gap |
|--------|----------------|-------|-----|-----|
| uhrady | 307 | 75.1% | 60% | +15.1% (předimenzováno) |
| financni-rizika | 34 | 8.3% | 15% | -6.7% |
| legislativa | 32 | 7.8% | 10% | -2.2% |
| compliance | 20 | 4.9% | 10% | -5.1% |
| provoz | 16 | 3.9% | 5% | -1.1% |

**Závěr:** Dataset je silně nevyvážený. Doména `uhrady` dominuje, zatímco `compliance` a `provoz` vyžadují rozšíření.

### 2.2 Distribuce podle typu

| Typ | Počet | Podíl | Hodnocení |
|-----|-------|-------|-----------|
| rule | 294 | 71.9% | ✅ Dostatečné |
| definition | 35 | 8.6% | ✅ Dostatečné |
| risk | 30 | 7.3% | ⚠️ Rozšířit o praktická rizika |
| condition | 20 | 4.9% | ⚠️ Přidat pro specifické odbornosti |
| exception | 19 | 4.6% | ⚠️ Rozšířit pro odbornosti |
| anti_pattern | 11 | 2.7% | ⚠️ Přidat z praxe |
| comparison | 0 | 0% | ❌ **Chybí v schématu** |
| heuristic | 0 | 0% | ❌ **Chybí v schématu** |
| example | 0 | 0% | ❌ **Chybí v schématu** |

### 2.3 Distribuce podle zdroje

| Zdroj | Jednotky | Poznámka |
|-------|----------|----------|
| Úhradová vyhláška 2025 | 212 | Hlavní zdroj |
| Odůvodnění k Úhradové vyhlášce 2025 | 176 | Doplňkový zdroj |
| Úhradová vyhláška 2026 - Ambulantní specialisté | 12 | Nový zdroj |
| Metodické doporučení PMÚ 2025 | 6 | Minimální pokrytí |
| Další zdroje | 3 | Praktické příklady |

### 2.4 Kvalita obsahu

| Metrika | Hodnota |
|---------|---------|
| Průměrná délka popisu | 240 znaků |
| Rozsah délky popisu | 96–464 znaků |
| Průměrná délka titulku | 64 znaků |
| Jednotky s related_units | 24 (6%) |
| Průměrný počet tagů | 3.89 |
| Orphan reference | 0 (žádné) |

### 2.5 Výsledky RAG testování

| Kategorie | Počet dotazů | Podíl |
|-----------|--------------|-------|
| Nad prahem 0.7 | 6 | 60% |
| Pod prahem 0.7 | 4 | 40% |
| **Průměrné skóre** | **0.69** | — |

**Nejslabší dotazy:**
1. „Jak se liší úhrady oproti minulému roku?" – **0.39** (chybí comparison type)
2. „Co se stane, když překročím PURO?" – **0.50** (chybí důsledky)
3. „Co znamená hodnota bodu 0,94 Kč?" – **0.59** (chybí konkrétní hodnoty)
4. „Jaké mám riziko při změně IČZ?" – **0.66** (těsně pod prahem)

---

## 3. Identifikované mezery seřazené podle priority

### Priority 1: Critical (Blokuje MVP)

| ID | Kategorie | Popis | Aktuální | Cíl | Dopad |
|----|-----------|-------|----------|-----|-------|
| GAP-001 | Konkrétní hodnoty bodu | Chybí specifické hodnoty z úhradových dodatků | 0 | 100 | Blokuje UC-AI-004 |
| GAP-002 | Důsledky regulací | Chybí explicitní popis důsledků překročení PURO/MAXÚ | 5 | 20 | Blokuje UC-AI-002 |
| GAP-003 | Meziroční srovnání | Chybí comparison type pro srovnávací dotazy | 0 | 30 | Blokuje UC-AI-005 |

**Celkový dopad Priority 1:** Tyto mezery způsobují, že 40% RAG testovacích dotazů selhává.

### Priority 2: High (Omezuje funkcionalitu)

| ID | Kategorie | Popis | Aktuální | Cíl | Dopad |
|----|-----------|-------|----------|-----|-------|
| GAP-004 | Metodiky ostatních pojišťoven | Dataset obsahuje převážně VZP data | 15 | 80 | Omezená použitelnost pro pacienty jiných ZP |
| GAP-005 | Historická data | Chybí data z let 2023, 2024 pro srovnání | 0 | 50 | Nelze poskytovat časové trendy |
| GAP-006 | Praktické heuristiky | Chybí tipy a best practices z praxe | 3 | 40 | Dataset příliš formální |

### Priority 3: Medium (Zlepšuje kvalitu)

| ID | Kategorie | Popis | Aktuální | Cíl | Dopad |
|----|-----------|-------|----------|-----|-------|
| GAP-007 | Specifické odbornosti | Klíčové odbornosti zcela chybí | 0 | 30 | Psychiatrie, kardiologie, fyzioterapie |
| GAP-008 | Anti-patterny z praxe | Málo praktických anti-patternů | 11 | 30 | Vágní varování |
| GAP-009 | Příklady vykazování | Chybí konkrétní příklady | 0 | 20 | Teoretická pravidla bez příkladů |

### Priority 4: Low (Nice-to-have)

| ID | Kategorie | Popis | Dopad |
|----|-----------|-------|-------|
| GAP-010 | Granularita jednotek | Některé jednotky příliš obecné | Vágní odpovědi |
| GAP-011 | Legislativní aktualizace | Částečné pokrytí změn 2026 | Neaktuálnost |

---

## 4. Mapa chybějících zdrojů

### 4.1 VZP a úhradové dodatky (KRITICKÉ)

| Zdroj | Status | Chybějící data | Priorita |
|-------|--------|----------------|----------|
| VZP Dodatek 2026 | ❌ Chybí | Konkrétní hodnoty bodu pro všechny odbornosti | P1 |
| VZP Dodatek 2025 | ❌ Chybí | Historické hodnoty pro srovnání | P2 |
| VZP Přílohy k vyhlášce | ⚠️ Částečné | Detailní tabulky bonifikací | P1 |

### 4.2 Ostatní pojišťovny (HIGH)

| Pojišťovna | Aktuální jednotky | Cíl | Gap |
|------------|-------------------|-----|-----|
| ZP MV ČR (211) | 8 | 20 | -12 |
| OZP (207) | 3 | 20 | -17 |
| ČPZP (205) | 2 | 20 | -18 |
| VOZP (201) | 0 | 15 | -15 |
| ZP Škoda (209) | 0 | 10 | -10 |
| RBP (213) | 2 | 15 | -13 |

### 4.3 Praktické zdroje (MEDIUM)

| Zdroj | Status | Potenciál |
|-------|--------|-----------|
| InfoProLekare.cz | ⚠️ 3 jednotky | 40 praktických heuristik |
| Odborné články | ❌ Chybí | 20 příkladů z praxe |
| Zkušenosti praktiků | ❌ Chybí | 30 anti-patternů |

### 4.4 Legislativní zdroje (LOW-MEDIUM)

| Zákon | Status | Relevantní sekce |
|-------|--------|------------------|
| 48/1997 Sb. | ❌ Chybí | Veřejné zdravotní pojištění |
| 372/2011 Sb. | ❌ Chybí | Zdravotní služby |
| Úhradová vyhláška 2024 | ❌ Chybí | Pro meziroční srovnání |
| Úhradová vyhláška 2023 | ❌ Chybí | Pro historická data |

---

## 5. Doporučení pro [[Phase-02-Source-Extraction]]

### 5.1 Immediate Actions (Týden 1-2)

1. **Extrahovat konkrétní hodnoty bodu z VZP dodatků 2026**
   - Zdroj: Úhradové dodatky VZP pro ambulantní specialisty
   - Očekávaný výstup: ~50 jednotek s konkrétními hodnotami
   - Dopad: Řeší GAP-001, zlepší RAG skóre dotazů na hodnoty bodu

2. **Vytvořit znalostní jednotky typu `comparison`**
   - Akce: Rozšířit JSON schéma o nový typ
   - Vytvořit 10-15 jednotek porovnávajících 2025 vs 2026
   - Dopad: Řeší GAP-003, zlepší nejslabší RAG dotaz (0.39)

3. **Doplnit důsledky překročení regulačních limitů**
   - Zdroj: Úhradová vyhláška, sekce o regulacích
   - Očekávaný výstup: 15 jednotek o důsledcích PURO, MAXÚ
   - Dopad: Řeší GAP-002, zlepší RAG skóre (0.50 → 0.75+)

### 5.2 Short-term (Týden 3-4)

4. **Zpracovat metodiky ZP MV ČR a OZP**
   - Zdroj: Veřejně dostupné metodické pokyny
   - Očekávaný výstup: 30-40 jednotek
   - Dopad: Částečně řeší GAP-004

5. **Přidat praktické heuristiky z InfoProLekare.cz**
   - Akce: Rozšířit schéma o typ `heuristic`
   - Očekávaný výstup: 20 praktických tipů
   - Dopad: Částečně řeší GAP-006

6. **Rozšířit pokrytí anti-patternů**
   - Zdroj: Odborné články, zkušenosti z praxe
   - Očekávaný výstup: 15 nových anti-patternů
   - Dopad: Řeší GAP-008

### 5.3 Medium-term (Měsíc 2)

7. **Přidat historická data 2024**
   - Zdroj: Úhradová vyhláška 2024
   - Očekávaný výstup: 30 jednotek pro srovnání
   - Dopad: Částečně řeší GAP-005

8. **Doplnit specifické odbornosti**
   - Focus: psychiatrie, kardiologie, fyzioterapie
   - Očekávaný výstup: 30 jednotek pro chybějící odbornosti
   - Dopad: Řeší GAP-007

9. **Vytvořit příklady vykazování**
   - Akce: Rozšířit schéma o typ `example`
   - Očekávaný výstup: 20 konkrétních příkladů
   - Dopad: Řeší GAP-009

### 5.4 Změny schématu

Pro plnou implementaci doporučení je nutné rozšířit JSON schéma o následující typy:

```json
{
  "type": {
    "enum": [
      "rule",
      "definition",
      "risk",
      "condition",
      "exception",
      "anti_pattern",
      "comparison",    // NOVÝ: meziroční srovnání
      "heuristic",     // NOVÝ: praktické tipy
      "example"        // NOVÝ: konkrétní příklady
    ]
  }
}
```

---

## 6. Očekávaný dopad po implementaci

### 6.1 RAG Quality Improvement

| Metrika | Aktuální | Po Phase 02 |
|---------|----------|-------------|
| Dotazy nad 0.7 | 60% | 85%+ |
| Průměrné skóre | 0.69 | 0.80+ |
| Nejslabší dotaz | 0.39 | 0.65+ |

### 6.2 Use-Case Coverage

| Kategorie | Aktuální | Po Phase 02 |
|-----------|----------|-------------|
| AI Decision-Support plné pokrytí | 25% | 75% |
| Produktové use-cases plné pokrytí | 0% | 50% |

### 6.3 Dataset Growth

| Metrika | Aktuální | Po Phase 02 |
|---------|----------|-------------|
| Celkem jednotek | 409 | ~600 |
| Nové typy | 0 | 3 |
| Pokrytí pojišťoven | 1 | 4+ |

---

*Generováno: 2026-02-03*
*Autor: Benjamin (Maestro AI Agent)*
*Zdroje: [[data_statistics]], [[rag_gap_analysis]], [[use_case_coverage_matrix]]*
