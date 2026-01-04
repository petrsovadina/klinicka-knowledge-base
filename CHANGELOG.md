# Changelog - Klinická Knowledge Base

## Verze 0.3.0 - Pokrok Fáze 3 (ZP MV ČR)

**Datum:** 2026-01-03

### Nové funkce a obsah

*   **Rozšíření datové báze:** Celkový počet validovaných znalostních jednotek se zvýšil na **456**.
*   **Nové zdroje:**
    *   Úhradové ujednání VZP ČR pro rok 2026 (Dodatek č. 5).
    *   Zdravotně pojistný plán ZP MV ČR pro rok 2026.
*   **Nové jednotky:** Extrahováno 47 nových jednotek z dokumentu ZP MV ČR, zaměřených na specifika úhrad a provozu u této pojišťovny.

### Vylepšení a opravy

*   **Stabilizace extrakčního skriptu:** Opravena chyba v llm_extract_v2.py týkající se manipulace s cestami k souborům, což umožňuje spolehlivou extrakci z PDF i textových souborů.
*   **Oprava duplicitních ID:** Automaticky opraveno 7 duplicitních ID, které vznikly při slučování extrahovaných dat.
*   **Bezpečnostní oprava:** Odstraněn hardcoded Hugging Face token z upload skriptů, aby bylo zajištěno dodržení pravidel GitHub Push Protection.
*   **Publikace:** Úspěšně publikováno na GitHub a aktualizován dataset na Hugging Face.

---

## Verze 0.2.0 - Dokončení Fáze 2 (VZP)

**Datum:** 2025-12-28

### Nové funkce a obsah

*   **Rozšíření datové báze:** Celkový počet validovaných znalostních jednotek se zvýšil na **409**.
*   **Nové zdroje:**
    *   VZP Metodika pro pořizování a předávání dokladů.
    *   VZP Číselníky.
    *   Agregovaná úhrada pro gynekology.
*   **Publikace:** První publikace datasetu na GitHub (petrsovadina/klinicka-knowledge-base) a Hugging Face.

### Vylepšení a opravy

*   **Validace domén:** Opravena chyba v doméně "uhrazeni" na "uhrady".
*   **Extrakční pipeline:** Optimalizace LLM-assisted extrakce pro gpt-4.1-nano.

---

# Changelog

## [phase2_core_2025] - 2025-12-14

### Dataset Freeze: Fáze 2

**Verze**: `phase2_core_2025`  
**Datum**: 14. prosince 2025  
**Soubor**: `data/knowledge_base_final.jsonl`

### Statistiky

- **Celkem jednotek**: 423
- **Validních jednotek**: 409 (96.7%)
- **Velikost**: 448.5 KB

### Pokrytí

**Domény:**
- Úhrady: 307 (75%)
- Finanční rizika: 34 (8%)
- Legislativa: 32 (8%)
- Compliance: 20 (5%)
- Provoz: 16 (4%)

**Typy:**
- Pravidla: 294 (72%)
- Definice: 35 (9%)
- Rizika: 30 (7%)
- Podmínky: 20 (5%)
- Výjimky: 19 (5%)
- Anti-patterny: 11 (3%)

### Zdroje

1. Úhradová vyhláška 2026 (pilotní dataset) - 15 jednotek
2. Metodické doporučení PMÚ 2025 - 6 jednotek
3. Odůvodnění k úhradové vyhlášce 2025 - 183 jednotek
4. Úhradová vyhláška 2025 (v2 extrakce) - 219 jednotek

### Známá Omezení

- **Pokrytí pojišťoven**: Pouze VZP a obecné zdroje (MZ ČR)
- **Pokrytí odborností**: Primárně ambulantní specialisté, chybí specifika pro VPL, stomatologii
- **Časové pokrytí**: Primárně 2025-2026, chybí historická data
- **Nevalidní jednotky**: 14 (3.3%) - chybějící source pole
- **Testování**: Není provedeno testování s reálnými dotazy

### Technologie

- **Extrakce**: `llm_extract_v2.py` (gpt-4.1-nano)
- **Validace**: `merge_and_validate.py` (jsonschema)
- **Náklady**: ~$1.75 (celá Fáze 2)

---

## [phase1_pilot] - 2025-12-14

### Pilotní Dataset

**Verze**: `phase1_pilot`  
**Datum**: 14. prosince 2025  
**Soubor**: `data/pilot_knowledge_units.jsonl`

### Statistiky

- **Celkem jednotek**: 15
- **Validních jednotek**: 15 (100%)

### Zdroje

1. Úhradová vyhláška 2026 (manuální extrakce)
2. InfoProLekare.cz články (manuální extrakce)

---

**Status**: ✅ Dataset zmrazen pro produkční použití
