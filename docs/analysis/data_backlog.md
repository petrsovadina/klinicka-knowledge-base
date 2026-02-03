---
type: reference
title: Data Backlog
created: 2026-02-03
tags:
  - backlog
  - priorities
  - sources
  - roadmap
related:
  - "[[gap_analysis_report]]"
  - "[[Phase-02-Source-Extraction]]"
  - "[[use_case_coverage_matrix]]"
  - "[[rag_gap_analysis]]"
---

# Data Backlog

Prioritizovaný seznam datových potřeb pro rozšíření znalostní báze klinických úhrad. Každá položka obsahuje zdroj, očekávaný počet jednotek a dopad na kvalitu RAG systému.

---

## Priority 1: Critical (Blokuje MVP)

Tyto položky musí být dokončeny pro funkční MVP. Aktuálně blokují 40% RAG testovacích dotazů.

### 1.1 Konkrétní hodnoty bodu z úhradových dodatků VZP

| Atribut | Hodnota |
|---------|---------|
| **Zdroj** | VZP Dodatek č. 1 k Rámcové smlouvě pro ambulantní specialisty 2026 |
| **URL** | https://www.vzp.cz/poskytovatele/smluvni-vztahy/uhradove-dodatky |
| **Typ jednotek** | rule (s konkrétními hodnotami) |
| **Očekávaný počet** | 50–80 jednotek |
| **Aktuální pokrytí** | 0 jednotek (0%) |
| **Dopad na RAG** | Zlepšení skóre dotazů na hodnotu bodu z 0.59 → 0.85+ |
| **Blokuje use-case** | UC-AI-004 „Jaká je hodnota bodu pro mou odbornost?" |
| **Priorita extrakce** | Ambulantní specialisté (SAS), praktici (VPL), stomatologie |

**Konkrétní data k extrakci:**
- Hodnota bodu pro jednotlivé odbornosti (603, 604, 609, 902...)
- Koeficienty bonifikací (P, K, M)
- Hodnoty pro kapitační platby

### 1.2 Důsledky překročení regulačních limitů

| Atribut | Hodnota |
|---------|---------|
| **Zdroj** | Úhradová vyhláška 2025/2026 – sekce o regulacích |
| **URL** | https://www.zakonyprolidi.cz/cs/2024-399 |
| **Typ jednotek** | risk, condition |
| **Očekávaný počet** | 15–20 jednotek |
| **Aktuální pokrytí** | 5 jednotek (25%) |
| **Dopad na RAG** | Zlepšení skóre PURO dotazů z 0.50 → 0.80+ |
| **Blokuje use-case** | UC-AI-002 „Co se stane, pokud překročím MAXÚ?" |

**Konkrétní data k extrakci:**
- Důsledky překročení PURO (srážky, regulace)
- Důsledky překročení MAXÚ
- Důsledky nesplnění degresního pásma
- Postup pojišťovny při zjištění překročení

### 1.3 Srovnávací jednotky (comparison type)

| Atribut | Hodnota |
|---------|---------|
| **Zdroj** | Porovnání Úhradová vyhláška 2025 vs 2026 |
| **Typ jednotek** | comparison (NOVÝ TYP – vyžaduje rozšíření schématu) |
| **Očekávaný počet** | 25–30 jednotek |
| **Aktuální pokrytí** | 0 jednotek (typ neexistuje) |
| **Dopad na RAG** | Zlepšení nejslabšího dotazu z 0.39 → 0.75+ |
| **Blokuje use-case** | UC-AI-005 „Jak se liší úhrady oproti minulému roku?" |

**Konkrétní data k extrakci:**
- Změny hodnoty bodu 2025 → 2026
- Změny koeficientů bonifikací
- Nové/zrušené odbornosti
- Změny v definicích PURO/MAXÚ

**Prerekvizita:** Rozšířit JSON schéma o typ `comparison`:
```json
{
  "type": "comparison",
  "comparison_data": {
    "period_from": "2025",
    "period_to": "2026",
    "parameter": "hodnota_bodu",
    "change_type": "increase|decrease|unchanged"
  }
}
```

---

## Priority 2: High (Omezuje funkcionalitu)

Tyto položky významně rozšiřují použitelnost systému pro všechny uživatele.

### 2.1 Metodiky ZP MV ČR (kód 211)

| Atribut | Hodnota |
|---------|---------|
| **Zdroj** | Zdravotní pojišťovna Ministerstva vnitra ČR – metodické pokyny |
| **URL** | https://www.zpmvcr.cz/poskytovatele |
| **Typ jednotek** | rule, condition, exception |
| **Očekávaný počet** | 20–25 jednotek |
| **Aktuální pokrytí** | 8 jednotek (32%) |
| **Dopad na RAG** | Rozšíření pokrytí o 2. největší pojišťovnu (~10% pojištěnců) |

**Specifika ZP MV ČR k extrakci:**
- Odlišné bonifikační koeficienty
- Specifická pravidla pro ambulantní specialisty
- Úhradové dodatky pro 2026

### 2.2 Metodiky OZP (kód 207)

| Atribut | Hodnota |
|---------|---------|
| **Zdroj** | Oborová zdravotní pojišťovna – úhradové dodatky |
| **URL** | https://www.ozp.cz/poskytovatele |
| **Typ jednotek** | rule, condition |
| **Očekávaný počet** | 20 jednotek |
| **Aktuální pokrytí** | 3 jednotky (15%) |
| **Dopad na RAG** | Rozšíření pokrytí o 3. největší pojišťovnu |

### 2.3 Metodiky ČPZP (kód 205)

| Atribut | Hodnota |
|---------|---------|
| **Zdroj** | Česká průmyslová zdravotní pojišťovna – smluvní dokumenty |
| **URL** | https://www.cpzp.cz/poskytovatele |
| **Typ jednotek** | rule, condition |
| **Očekávaný počet** | 20 jednotek |
| **Aktuální pokrytí** | 2 jednotky (10%) |
| **Dopad na RAG** | Rozšíření pokrytí o další významnou pojišťovnu |

### 2.4 Historická data pro srovnání (2024)

| Atribut | Hodnota |
|---------|---------|
| **Zdroj** | Úhradová vyhláška 2024 (č. 423/2023 Sb.) |
| **URL** | https://www.zakonyprolidi.cz/cs/2023-423 |
| **Typ jednotek** | rule, comparison |
| **Očekávaný počet** | 30–40 jednotek |
| **Aktuální pokrytí** | 0 jednotek |
| **Dopad na RAG** | Umožní komplexní meziroční srovnání |

---

## Priority 3: Medium (Zlepšuje kvalitu)

Tyto položky zlepšují kvalitu odpovědí a uživatelskou zkušenost.

### 3.1 Praktické heuristiky z InfoProLekare.cz

| Atribut | Hodnota |
|---------|---------|
| **Zdroj** | InfoProLekare.cz – odborné články |
| **URL** | https://www.infoprolekare.cz |
| **Typ jednotek** | heuristic (NOVÝ TYP) |
| **Očekávaný počet** | 30–40 jednotek |
| **Aktuální pokrytí** | 3 jednotky (7%) |
| **Dopad na RAG** | Dataset bude obsahovat praktické tipy vedle formálních pravidel |

**Typy heuristik k extrakci:**
- Optimalizace ordinačních hodin pro maximalizaci úhrad
- Praktické tipy pro správné vykazování
- Best practices od zkušených ordinací
- Časté chyby a jejich řešení

**Prerekvizita:** Rozšířit JSON schéma o typ `heuristic`:
```json
{
  "type": "heuristic",
  "practical_tip": "string",
  "source_experience": "string",
  "applicability": ["array of specialties"]
}
```

### 3.2 Specifické odbornosti (psychiatrie, kardiologie, fyzioterapie)

| Atribut | Hodnota |
|---------|---------|
| **Zdroj** | Úhradová vyhláška 2025/2026 – přílohy pro specifické odbornosti |
| **Typ jednotek** | rule, condition, exception |
| **Očekávaný počet** | 25–30 jednotek |
| **Aktuální pokrytí** | 0 jednotek pro tyto odbornosti |
| **Dopad na RAG** | Pokrytí klíčových odborností, které zcela chybí |

**Odbornosti k prioritnímu zpracování:**
- 305 – Psychiatrie
- 107 – Kardiologie
- 902 – Fyzioterapie
- 809 – Radiologie a zobrazovací metody

### 3.3 Anti-patterny z praxe

| Atribut | Hodnota |
|---------|---------|
| **Zdroj** | Odborné články, kontrolní zprávy pojišťoven, case studies |
| **Typ jednotek** | anti_pattern |
| **Očekávaný počet** | 15–20 jednotek |
| **Aktuální pokrytí** | 11 jednotek (55%) |
| **Dopad na RAG** | Lepší prevence chyb ve vykazování |

**Kategorie anti-patternů k doplnění:**
- Chybné vykazování kombinací výkonů
- Typické chyby při DRG zařazení
- Časté důvody zamítnutí úhrad
- Rizikové vzorce chování detekované pojišťovnami

---

## Priority 4: Low (Nice-to-have)

Položky pro dlouhodobé zlepšení, bez urgence.

### 4.1 Příklady vykazování (example type)

| Atribut | Hodnota |
|---------|---------|
| **Zdroj** | Metodické materiály, vzorové doklady |
| **Typ jednotek** | example (NOVÝ TYP) |
| **Očekávaný počet** | 15–20 jednotek |
| **Aktuální pokrytí** | 0 jednotek (typ neexistuje) |
| **Dopad na RAG** | Konkrétní příklady místo abstraktních pravidel |

### 4.2 Legislativní aktualizace 2026

| Atribut | Hodnota |
|---------|---------|
| **Zdroj** | Zákon 48/1997 Sb., novely 2025–2026 |
| **Typ jednotek** | rule, definition |
| **Očekávaný počet** | 15–20 jednotek |
| **Aktuální pokrytí** | částečné |
| **Dopad na RAG** | Aktuálnost legislativního rámce |

### 4.3 Další pojišťovny (VOZP, ZP Škoda, RBP)

| Pojišťovna | Kód | Očekávaný počet | Aktuální |
|------------|-----|-----------------|----------|
| VOZP | 201 | 15 jednotek | 0 |
| ZP Škoda | 209 | 10 jednotek | 0 |
| RBP | 213 | 15 jednotek | 2 |

---

## Souhrn backlogu

### Celkové očekávané rozšíření datasetu

| Priorita | Položky | Očekávané jednotky | Aktuální stav |
|----------|---------|--------------------| --------------|
| P1 Critical | 3 | 90–130 | 5 (4%) |
| P2 High | 4 | 90–105 | 13 (12%) |
| P3 Medium | 3 | 70–90 | 14 (16%) |
| P4 Low | 3 | 40–55 | 2 (4%) |
| **Celkem** | **13** | **290–380** | **34 (10%)** |

### Očekávaný stav po implementaci

| Metrika | Aktuální | Po backlogu |
|---------|----------|-------------|
| Celkem jednotek | 552 | ~900 |
| Pokrytí pojišťoven | 1 plně, 4 částečně | 4+ plně |
| Typy jednotek | 6 | 9 (+ comparison, heuristic, example) |
| RAG dotazy nad 0.7 | 60% | 90%+ |
| Use-cases plně pokryté | 25% | 75%+ |

### Změny schématu potřebné pro backlog

Pro plnou implementaci backlogu je nutné rozšířit JSON schéma:

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
      "comparison",    // P1 - meziroční srovnání
      "heuristic",     // P3 - praktické tipy
      "example"        // P4 - konkrétní příklady
    ]
  }
}
```

---

## Tracking pokroku

Tento backlog bude aktualizován po každé fázi extrakce.

| Fáze | Očekávané dokončení | Položky | Status |
|------|---------------------|---------|--------|
| Phase 02 | Týden 1–2 | P1.1, P1.2, P1.3 | ⏳ Čeká |
| Phase 03 | Týden 3–4 | P2.1, P2.2, P2.3, P2.4 | ⏳ Čeká |
| Phase 04 | Měsíc 2 | P3.1, P3.2, P3.3 | ⏳ Čeká |
| Phase 05 | Měsíc 3 | P4.1, P4.2, P4.3 | ⏳ Čeká |

---

*Vytvořeno: 2026-02-03*
*Autor: Benjamin (Maestro AI Agent)*
*Zdroje: [[gap_analysis_report]], [[rag_gap_analysis]], [[use_case_coverage_matrix]]*
