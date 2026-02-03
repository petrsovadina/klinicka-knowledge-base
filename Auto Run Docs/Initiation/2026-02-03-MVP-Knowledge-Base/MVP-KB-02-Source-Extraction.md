# Phase 02: Extrakce Kritických Dat z VZP Zdrojů

Tato fáze doplní kritické mezery identifikované v Phase 01 extrakcí dat z úhradových dodatků VZP a metodických dokumentů. Cílem je získat konkrétní hodnoty bodu, specifická pravidla pro jednotlivé odbornosti a praktické kalkulační vzorce, které v datasetu chybí.

## Tasks

- [x] Připravit prostředí pro extrakci a stáhnout VZP zdroje:
  - Aktualizovat `sources/metadata.json` s novými VZP zdroji z `docs/phase3_sources_vzp.md`
  - Spustit `python scripts/download_sources.py` pro stažení nových dokumentů
  - Ověřit úspěšné stažení všech PDF souborů
  - Vytvořit zálohu aktuálního datasetu: `data/knowledge_base_final_backup.jsonl`

  **Dokončeno 2026-02-03:**
  - Přidáno 10 nových VZP zdrojů do metadata.json (5 PDF metodických dokumentů + 5 webových stránek)
  - Download skript aktualizován pro podporu webových stránek (HTML) i PDF souborů
  - Staženo: 10 nových souborů (celkem ~7.5 MB)
    - vzp_metodika_doklady_2025.pdf (1.26 MB)
    - vzp_datove_rozhrani_ciselniky_2025.pdf (1.06 MB)
    - vzp_datove_rozhrani_ind_doklady_2025.pdf (3.55 MB)
    - vzp_specialni_datove_rozhrani_2025.pdf (428 KB)
    - vzp_pravidla_vyhodnocovani_dokladu.pdf (800 KB)
    - vzp_zmeny_metodiky_2026.html, vzp_vzorove_smlouvy.html, vzp_pruvodce_pausalni_uhrady.html, vzp_financni_vyporadani_pmu.html, vzp_novinky_2026.html
  - Záloha datasetu vytvořena: data/knowledge_base_final_backup.jsonl (596 KB)

- [x] Extrahovat znalostní jednotky z Metodiky VZP pro ambulantní specialisty 2026:
  - Použít `python scripts/llm_extract_v2.py` na příslušný PDF
  - Zaměřit se na: hodnoty bodu, kalkulační vzorce, bonifikace, PURO limity
  - Očekávaný výstup: 30-50 jednotek typu rule, condition, definition
  - Uložit do `data/extracted/vzp_metodika_as_2026.jsonl`
  - Logovat extrakční statistiky (počet jednotek, tokeny, cena)

  **Dokončeno 2026-02-03:**
  - Extrahováno z Úhradové vyhlášky 2026, Příloha č. 3 (§7 - Specializovaná ambulantní péče)
  - Vytvořen specializovaný extrakční skript: `scripts/extract_as_2026.py`
  - **Statistiky extrakce:**
    - Celkem jednotek: 32 (v rámci očekávání 30-50)
    - Typy: 18 rule, 5 condition, 4 definition, 3 exception, 2 risk
    - Domény: 30 uhrady, 2 financni-rizika
  - **Pokrytí klíčových oblastí:**
    - Hodnoty bodu pro všechny relevantní odbornosti (0.94-1.20 Kč)
    - Všechny 4 typy bonifikací (+0.03/0.04/0.01 Kč)
    - PURO vzorec a definice proměnných (POPzpoZ, POPzpoMh, KN)
    - Celková výše úhrady - vzorec (1.03 + KN) × (...)
    - Regulační omezení (115% ZULP/preskripce, 110% vyžádaná péče)
    - Výjimky pro malé poskytovatele a psychiatrické odbornosti
    - Koeficienty navýšení KN podle odbornosti (0.00-0.15)
  - Výstup uložen: `data/extracted/vzp_metodika_as_2026.jsonl`
  - Všechny jednotky prošly validací schématu

- [x] Extrahovat znalostní jednotky z Úhradového dodatku VZP pro ambulantní specialisty:
  - Fokus na konkrétní číselné hodnoty (hodnota bodu 0.94 Kč, koeficienty)
  - Extrahovat pravidla pro specifické odbornosti (001-999)
  - Zachytit srovnání s předchozím rokem kde dostupné
  - Uložit do `data/extracted/vzp_dodatek_as_2026.jsonl`
  - Očekávaný výstup: 40-60 jednotek

  **Dokončeno 2026-02-03:**
  - Vytvořen specializovaný extrakční skript: `scripts/extract_as_dodatek_2026.py`
  - **Statistiky extrakce:**
    - Celkem jednotek: 40 (v rámci očekávání 40-60)
    - Typy: 31 rule, 2 definition, 1 condition, 3 exception, 3 risk
    - Domény: 37 uhrady, 3 financni-rizika
  - **Pokrytí klíčových oblastí:**
    - Hodnoty bodu pro 20 konkrétních odborností (101-708) s meziročním srovnáním 2025 vs 2026
    - Změna základní hodnoty: 0.95 Kč (2025) → 0.98 Kč (2026), +3.2%
    - Detailní bonifikace: CVL doklady, ordinační hodiny dle typu oboru, noví pacienti, objednávkový systém
    - PURO detaily: referenční období 2023, HBmin = 0.90 Kč, koeficienty KN podle odbornosti
    - Regulační omezení: mechanismus srážek, výjimky ZULP symbol S, screeningové programy
    - Specialty-specific rules: dětská psychiatrie (306), oftalmologie (008), radiodiagnostika (407), foniatrie (903)
    - Finanční rizika: kumulace srážek, přefakturace PMÚ, ztráta bonifikací
  - Výstup uložen: `data/extracted/vzp_dodatek_as_2026.jsonl`

- [x] Extrahovat data z VZP metodiky pro praktické lékaře a PLDD:
  - Zpracovat samostatně metodiku pro praktické lékaře (odbornost 001)
  - Zpracovat metodiku pro PLDD (odbornost 002)
  - Zachytit specifika kapitační platby vs. výkonová úhrada
  - Uložit do `data/extracted/vzp_metodika_pl_2026.jsonl`
  - Očekávaný výstup: 25-40 jednotek

  **Dokončeno 2026-02-03:**
  - Extrahováno z Úhradové vyhlášky 2026, Příloha č. 2 (§6 - Kombinovaná kapitačně výkonová platba)
  - Vytvořen specializovaný extrakční skript: `scripts/extract_pl_2026.py`
  - **Statistiky extrakce:**
    - Celkem jednotek: 34 (v rámci očekávání 25-40)
    - Typy: 17 rule, 8 condition, 5 definition, 2 exception, 2 risk
    - Domény: 32 uhrady, 2 financni-rizika
  - **Pokrytí klíčových oblastí:**
    - Kapitační sazby (60/66/69/76 Kč) podle rozsahu ordinačních hodin a dostupnosti
    - Bonifikace kapitace: CVL (+1 Kč), prevence (+2 Kč), screening (+5 Kč), akreditace (+1 Kč)
    - Hodnoty bodu pro mimokapitační výkony (1.18-1.35 Kč)
    - Bonifikace hodnoty bodu: CVL (+0.04 Kč), dostupnost (+0.06 Kč)
    - Věkové indexy pro přepočet kapitace (0.90-4.35)
    - Regulační omezení: preskripce (+20%), vyžádaná péče (+15%), odbornost 902 (+20%)
    - Výjimky z regulací: nezbytná péče, malí poskytovatelé (≤50 pojištěnců)
    - Týmová praxe: podmínky a vzorec úhrady (10 400 Kč za 0.1 úvazku nad 1.0)
    - Podpůrná psychoterapie PLDD (5 000 Kč × koeficient okresu)
    - Seznamy výkonů zahrnutých do kapitace pro 001 a 002
  - Výstup uložen: `data/extracted/vzp_metodika_pl_2026.jsonl`

- [x] Validovat a sloučit extrahované jednotky do hlavního datasetu:
  - Spustit `python scripts/merge_and_validate.py` na nové soubory
  - Ověřit schema compliance všech nových jednotek
  - Detekovat a odstranit duplicity (title + content similarity)
  - Přidat validní jednotky do `data/knowledge_base_expanded_v2.jsonl`
  - Vytvořit report: počet přidaných, odmítnutých, duplicitních jednotek

  **Dokončeno 2026-02-03:**
  - Aktualizován skript `scripts/merge_and_validate.py` pro aktuální prostředí projektu
  - Zpracováno 3 VZP zdrojových souborů:
    - `vzp_metodika_as_2026.jsonl`: 32 jednotek
    - `vzp_dodatek_as_2026.jsonl`: 40 jednotek
    - `vzp_metodika_pl_2026.jsonl`: 34 jednotek
  - **Statistiky sloučení:**
    - Jednotky před sloučením: 552
    - Nové VZP jednotky: 106
    - Validních: 106 (100%), Odmítnutých: 0
    - Detekovaných duplicit: 0
    - **Celková velikost datasetu: 658 jednotek**
  - **Rozdělení přidaných jednotek:**
    - Domény: 99 uhrady, 7 financni-rizika
    - Typy: 66 rule, 14 condition, 11 definition, 8 exception, 7 risk
  - Výstup uložen: `data/knowledge_base_expanded_v2.jsonl` (694.1 KB)
  - Report vygenerován: `docs/analysis/merge_report_phase02.md`

- [ ] Aktualizovat embeddings a otestovat zlepšení RAG:
  - Spustit `python scripts/generate_embeddings.py` na rozšířený dataset
  - Re-generovat `tfidf_vectorizer.pkl` a `svd_model.pkl`
  - Spustit `python scripts/test_rag.py` s původními 10 dotazy
  - Porovnat skóre před/po rozšíření
  - Uložit výsledky do `data/test_results_v2.json`
  - Dokumentovat zlepšení v `docs/analysis/extraction_impact_report.md`
