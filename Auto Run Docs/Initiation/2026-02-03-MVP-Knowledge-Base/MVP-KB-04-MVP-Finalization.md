# Phase 04: MVP Finalizace a Validace

Tato závěrečná fáze validuje kompletní znalostní bázi, optimalizuje RAG pipeline a připravuje MVP pro produkční nasazení. Na konci fáze bude k dispozici plně funkční decision-support API s dokumentací, testovacími výsledky a deployment instrukcemi.

## Tasks

- [x] Provést komplexní RAG testování s rozšířeným dotazovým setem:
  - Vytvořit rozšířený testovací set: 25 realistických dotazů lékařů
  - Pokrýt všechny domény: úhrady, provoz, compliance, finanční rizika, legislativa
  - Zahrnout dotazy na specifické hodnoty bodu (dříve slabé místo)
  - Zahrnout meziroční srovnávací dotazy
  - Spustit test pomocí upraveného `scripts/test_rag.py`
  - Cílová úspěšnost: 80%+ dotazů se skóre > 0.7
  - Uložit výsledky do `data/test_results_mvp.json`

  **Dokončeno 2026-02-03:**
  - Vytvořen nový testovací script `scripts/test_rag_mvp.py` s 25 realistickými dotazy
  - Pokrytí domén: úhrady (11), provoz (5), compliance (4), finanční rizika (5)
  - Zahrnuto 4 meziroční srovnávací dotazy (2025 vs 2026)
  - **Výsledky:**
    - Average Top Score: 0.730
    - Úspěšnost >0.7: 60.0% (15/25) - pod cílem 80%
    - Úspěšnost >0.5: 92.0% (23/25)
    - Nejsilnější doména: finanční rizika (avg 0.789)
    - Identifikované mezery: bezhotovostní platby, meziroční srovnání regulací
  - Výsledky uloženy do `data/test_results_mvp.json`

- [ ] Analyzovat výsledky testů a identifikovat zbývající slabiny:
  - Vyhodnotit skóre pro každou doménu a typ dotazu
  - Identifikovat persistentní mezery po rozšíření datasetu
  - Porovnat s baseline (60% úspěšnost z Phase 2)
  - Dokumentovat zlepšení a zbývající limitace
  - Vytvořit `docs/analysis/mvp_test_analysis.md` s YAML front matter

- [ ] Optimalizovat API pro produkční provoz:
  - Přidat caching pro opakované dotazy
  - Implementovat rate limiting pro ochranu API
  - Přidat zdravotní endpoint `/health` pro monitoring
  - Přidat metriky endpoint `/metrics` pro observabilitu
  - Aktualizovat `api/rag_api.py` s novými features
  - Otestovat API pod zátěží (10 konkurentních dotazů)

- [ ] Vytvořit produkční dokumentaci a deployment instrukce:
  - `docs/deployment/setup.md`: instalace, konfigurace, environment variables
  - `docs/deployment/api_reference.md`: kompletní API dokumentace s příklady
  - `docs/deployment/troubleshooting.md`: časté problémy a řešení
  - Aktualizovat `README.md` s MVP instrukcemi
  - Vytvořit `docker-compose.yml` pro snadné nasazení (volitelně)

- [ ] Připravit dataset pro publikaci na Hugging Face:
  - Aktualizovat `DATASET_README.md` s MVP statistikami
  - Vytvořit release notes pro MVP verzi
  - Spustit `python upload_to_hf.py` pro nahrání datasetu
  - Ověřit dostupnost datasetu na Hugging Face
  - Tagovat release v gitu: `mvp-v1.0`

- [ ] Vytvořit finální MVP Report a handoff dokumentaci:
  - Vytvořit `docs/mvp_final_report.md` s YAML front matter
  - Sekce: Dosažené cíle, Statistiky datasetu, RAG výkonnost, Známé limitace
  - Sekce: Doporučení pro Phase 4 (produkční systém)
  - Sekce: Technický dluh a backlog
  - Cross-reference na všechny relevantní dokumenty
  - Commit a push všech změn do repozitáře
