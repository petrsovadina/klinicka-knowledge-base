# Phase 03: Rozšíření o Další Pojišťovny a Praktické Zdroje

Tato fáze rozšíří znalostní bázi o metodiky dalších zdravotních pojišťoven (ZP MV, OZP, ČPZP, RBP) a praktické heuristiky z InfoProLekare.cz. Cílem je dosáhnout komplexního pokrytí českého zdravotního pojištění a doplnit praktické know-how, které lékaři potřebují v každodenní praxi.

## Tasks

- [x] Připravit a stáhnout zdroje ostatních zdravotních pojišťoven:
  - Aktualizovat `sources/metadata.json` s odkazy na ZP MV, OZP, ČPZP, RBP
  - Přidat zdroje z `docs/phase3_sources_other.md`
  - Stáhnout úhradové dodatky a metodiky pro rok 2026
  - Ověřit dostupnost a formát všech dokumentů
  - Vytvořit seznam zdrojů seřazený podle priority (podíl na trhu)

  **Completed 2026-02-03:**
  - Added 17 new Phase 3 sources to `sources/metadata.json` (34 total sources)
  - Successfully downloaded 10 new files (27 total available, 7 unavailable)
  - Downloaded sources: ZP MV ČR (2), OZP (2), InfoProLekare.cz (6)
  - Unavailable (404): ČPZP, RBP contracts page, VoZP, ZPŠ, 3 InfoProLekare articles
  - Created priority list by market share: VZP (59%), ČPZP (12%), ZP MV (10.5%), OZP (6.5%), VoZP (6%), RBP (4%), ZPŠ (1.2%)
  - Added metadata summary: 13 PDFs, 14 HTML files; 27 available for extraction

- [x] Extrahovat znalostní jednotky ze ZP MV (Zdravotní pojišťovna Ministerstva vnitra):
  - Fokus na specifické odlišnosti od VZP
  - Zachytit bonifikační programy a limity
  - Identifikovat pravidla pro speciální skupiny pojištěnců
  - Uložit do `data/extracted/zpmv_metodika_2026.jsonl`
  - Očekávaný výstup: 20-30 jednotek

  **Completed 2026-02-03:**
  - Extracted 30 knowledge units from ZP MV ČR Dodatek AS/2025 (7-page PDF)
  - Covered payment rules by specialty: 4 tiers (1.00/0.98/0.96/0.94 Kč)
  - Documented 7 bonification programs (+0.01 to +0.06 Kč):
    - CŽV (continuous education): +0.03 Kč
    - Extended hours (30h/week): +0.04 Kč
    - Extra hours (35h/week): +0.02 Kč
    - New patients (basic/extended): +0.01/+0.03 Kč
    - Appointment system: +0.01 Kč
    - Psychiatry specials: +0.06 Kč
  - Captured MAXÚ formula with coefficient matrices
  - Documented 3 regulation limits (ZUM/ZULP 115%, prescriptions 110%, induced care 110%)
  - Identified exceptions for psychiatry/CDZ (305, 306, 308, 309, 350, 355, 360, 370, 922)
  - Included risk unit for bonification loss penalties
  - All 30 units validated against schema (100% compliance)

- [ ] Extrahovat znalostní jednotky z OZP a ČPZP:
  - Zpracovat OZP (Oborová zdravotní pojišťovna) metodiky
  - Zpracovat ČPZP (Česká průmyslová zdravotní pojišťovna)
  - Zaměřit se na unikátní pravidla a odchylky od standardu
  - Uložit do `data/extracted/ozp_metodika_2026.jsonl` a `data/extracted/cpzp_metodika_2026.jsonl`
  - Očekávaný výstup: 15-25 jednotek za každou pojišťovnu

- [ ] Vytvořit srovnávací jednotky (comparison type) pro meziroční změny:
  - Porovnat pravidla 2025 vs 2026 z existujících dat
  - Vytvořit nový typ jednotky "comparison" nebo použít "rule" s tagy
  - Zachytit: co se změnilo, dopad na praxi, rizika přechodného období
  - Uložit do `data/extracted/year_comparison_2025_2026.jsonl`
  - Očekávaný výstup: 15-20 srovnávacích jednotek

- [ ] Extrahovat praktické heuristiky z InfoProLekare.cz článků:
  - Identifikovat 10 nejrelevantnějších článků o úhradách a provozu praxe
  - Extrahovat praktická doporučení, tipy, varování
  - Zaměřit se na anti-patterny a rizika z reálné praxe
  - Uložit do `data/extracted/infoprolekare_articles.jsonl`
  - Očekávaný výstup: 25-40 jednotek typu anti_pattern, risk, rule

- [ ] Finální sloučení, validace a regenerace embeddings:
  - Sloučit všechny nové extrakce do `data/knowledge_base_phase3.jsonl`
  - Spustit kompletní validaci proti schema
  - Odstranit duplicity pomocí title + content similarity check
  - Regenerovat embeddings pro celý rozšířený dataset
  - Vytvořit finální statistiky: celkový počet jednotek, pokrytí, distribuce
  - Uložit finální dataset do `data/knowledge_base_mvp.jsonl`
