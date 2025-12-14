# Fáze 3: Detailní Implementační Plán

**Datum plánování**: 14. prosince 2025  
**Verze**: 1.0  
**Status**: ✅ Připraveno k implementaci

---

## 1. Cíle Fáze 3

- **Primární cíl**: Rozšířit znalostní bázi na **700–850 jednotek**.
- **Sekundární cíl**: Pokrýt metodiky všech 7 hlavních zdravotních pojišťoven a klíčové odborné články.
- **Technologický cíl**: Optimalizovat a paralelizovat extrakční pipeline pro maximální efektivitu.

---

## 2. Implementační Kroky (8 týdnů)

### Týden 1: Příprava a VZP (Část 1)

1.  **Aktualizace skriptů**:
    -   `download_sources.py`: Přidat URL pro všechny zdroje Fáze 3.
    -   `llm_extract_v2.py`: Zlepšit logování a chybové hlášky.
    -   `merge_and_validate.py`: Přidat automatickou opravu duplicitních ID.
2.  **Stažení zdrojů**: Spustit `download_sources.py` pro stažení všech PDF a uložení URL článků.
3.  **Extrakce (VZP)**:
    -   Spustit paralelní extrakci pro:
        -   `metodika-porizovani-dokladu-vzp.pdf`
        -   `pravidla-vyhodnocovani-dokladu-vzp.pdf`
        -   `pruvodce-financovanim-pausalne-hrazenych-vzp.pdf`

### Týden 2: VZP (Část 2) a Validace

1.  **Extrakce (VZP)**:
    -   Spustit extrakci pro vzorové smlouvy a další dokumenty VZP.
2.  **Průběžná validace**:
    -   Spustit `merge_and_validate.py` pro ověření výsledků z týdne 1.
    -   Analyzovat chyby a upravit extrakční prompt, pokud je to nutné.

### Týden 3: InfoProLekare.cz (Část 1)

1.  **Extrakce z webu**:
    -   Vytvořit skript `extract_from_web.py`, který:
        -   Načte URL ze seznamu.
        -   Použije `browser_navigate` pro získání textového obsahu.
        -   Zavolá `llm_extract_v2.py` pro extrakci.
2.  **Extrakce (Články)**:
    -   Spustit paralelní extrakci pro:
        -   `prehled-uhradovych-dodatku-2025.html`
        -   `temna-strana-uhradove-vyhlasky-2026.html`
        -   `uhradova-vyhlaska-2026-vpl-pldd.html`

### Týden 4: InfoProLekare.cz (Část 2) a Validace

1.  **Extrakce (Články)**:
    -   Spustit extrakci pro zbývající články z InfoProLekare.cz.
2.  **Průběžná validace**:
    -   Sloučit a validovat všechny dosud extrahované jednotky.
    -   Zkontrolovat pokrytí témat a odborností.

### Týden 5: ZP MV ČR a OZP

1.  **Extrakce (ZP MV)**:
    -   Spustit extrakci pro `dodatek-as-2025-zpmv.pdf`.
2.  **Extrakce (OZP)**:
    -   Spustit extrakci pro metodiky a informace z webu OZP.

### Týden 6: Ostatní Pojišťovny a Validace

1.  **Extrakce (Ostatní)**:
    -   Spustit extrakci pro zdroje ČPZP, RBP, VoZP, ZPŠ.
2.  **Průběžná validace**:
    -   Sloučit a validovat všechny dosud extrahované jednotky.

### Týden 7: Doplňkové Zdroje

1.  **Extrakce (Doplňky)**:
    -   Zpracovat zbývající datová rozhraní VZP.
    -   Zpracovat legislativní texty (zákony 48/1997, 372/2011).

### Týden 8: Finální Validace a Publikace

1.  **Finální sloučení a validace**:
    -   Spustit `merge_and_validate.py` na kompletním datasetu.
    -   Manuálně opravit zbývající chyby.
2.  **Deduplikace**:
    -   Vytvořit skript pro sémantickou deduplikaci (např. pomocí embeddings).
3.  **Generování statistik**:
    -   Vytvořit finální report s detailními statistikami pokrytí.
4.  **Publikace**:
    -   Commitnout finální dataset na GitHub.
    -   Nahrát finální dataset na Hugging Face.

---

## 3. Technologický Stack

-   **Jazyk**: Python 3.11
-   **LLM**: `gpt-4.1-nano` (OpenAI API)
-   **Knihovny**: `openai`, `jsonschema`, `beautifulsoup4` (pro extrakci z webu)
-   **Nástroje**: `pdftotext`, `git`, `huggingface_hub`
-   **Prostředí**: Manus Sandbox

---

## 4. Očekávané Výstupy

-   **Finální dataset**: `knowledge_base_v3.jsonl` (700–850 jednotek)
-   **GitHub repozitář**: Aktualizovaný s novými daty a skripty.
-   **Hugging Face dataset**: Aktualizovaný s novou verzí datasetu.
-   **Finální report Fáze 3**: Detailní shrnutí výsledků, statistik a poznatků.

---

## 5. Klíčové Metriky Úspěchu

-   **Počet jednotek**: > 700
-   **Validita**: > 98%
-   **Pokrytí pojišťoven**: 100% (všech 7)
-   **Pokrytí odborností**: > 15
-   **Dodržení časového plánu**: Dokončení do 8 týdnů.

---

**Status**: ✅ Tento plán je připraven k okamžité implementaci.
