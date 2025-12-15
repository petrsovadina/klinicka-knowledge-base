# Vyhodnocení Projektu a Strategický Plán Dalšího Rozvoje

**Projekt**: Klinická Znalostní Báze – Ambulantní Zdravotní Péče v ČR  
**Datum vyhodnocení**: 14. prosince 2025  
**Verze**: 0.1.0 (Pilot)  
**Autor**: Manus AI

---

## 1. Vyhodnocení Dosavadní Práce

### 1.1 Co se podařilo

#### ✅ Infrastruktura a Základ

Vytvořili jsme robustní technickou infrastrukturu, která je připravena pro škálování. GitHub repozitář obsahuje profesionální strukturu s jasnou organizací souborů, dokumentací a standardy pro přispěvatele. Hugging Face dataset je publikovaný a přístupný pro AI komunitu. JSON schéma zajišťuje konzistenci a validovatelnost všech znalostních jednotek.

#### ✅ Datový Model

Navrhli jsme flexibilní, ale strukturovaný datový model, který pokrývá šest typů znalostních jednotek (pravidla, výjimky, rizika, anti-patterny, podmínky, definice). Model je dostatečně obecný pro různé domény (úhrady, provoz, compliance, finanční rizika, legislativa), ale zároveň dostatečně specifický pro strojové zpracování.

#### ✅ Pilotní Dataset

Extrahovali jsme 15 klíčových znalostních jednotek zaměřených na úhradovou vyhlášku 2026. Tyto jednotky pokrývají nejdůležitější změny a rizika pro ambulantní specialisty. Dataset je validovaný, propojený (related_units) a obsahuje praktické příklady výpočtů.

#### ✅ Dokumentace

Vytvořili jsme komplexní dokumentaci (README, CONTRIBUTING, model.md), která umožňuje dalším přispěvatelům rychle se zorientovat a začít přispívat. Dokumentace je psaná v češtině, což je klíčové pro cílovou skupinu (lékaři, provozovatelé ambulancí).

---

### 1.2 Co chybí a kde jsou mezery

#### ❌ Pokrytí Zdrojů

**Problém**: Pilotní dataset čerpá primárně z jednoho zdroje (InfoProLekare.cz) a jednoho roku (2026). Chybí systematické pokrytí:
- Úhradových vyhlášek z předchozích let (2025, 2024, 2023)
- Metodik jednotlivých pojišťoven (VZP, ZP MV, OZP, ČPZP, RBP)
- Legislativních dokumentů (zákon 48/1997 Sb., zákon 372/2011 Sb.)
- Praktických případových studií a anti-patternů z reálného provozu

**Dopad**: Znalostní báze není dostatečně hluboká pro produkční použití. AI model by měl omezené možnosti odpovídat na komplexní dotazy.

#### ❌ Pokrytí Odborností

**Problém**: Dataset obsahuje obecné jednotky pro "all" specialties, ale chybí specifické znalosti pro jednotlivé odbornosti (např. gynekologie, pediatrie, psychiatrie, fyzioterapie). Každá odbornost má specifické úhradové mechanismy, bonifikace a rizika.

**Dopad**: Znalostní báze není dostatečně personalizovaná pro různé typy praxí.

#### ❌ Automatizace a Škálování

**Problém**: Všechny znalostní jednotky byly extrahovány manuálně. Tento proces je časově náročný a neškálovatelný. Chybí nástroje pro:
- Poloautomatickou extrakci z PDF dokumentů (úhradové vyhlášky)
- LLM-asistovanou strukturaci textů z článků
- Validaci a deduplikaci znalostních jednotek

**Dopad**: Plnění báze bude pomalé a náchylné k chybám.

#### ❌ AI Decision-Support Vrstva

**Problém**: Znalostní báze existuje jako statický dataset, ale chybí AI vrstva, která by:
- Odpovídala na dotazy lékařů v přirozeném jazyce
- Kombinovala více znalostních jednotek pro komplexní analýzy
- Vysvětlovala důsledky rozhodnutí s odkazy na zdroje
- Upozorňovala na rizika a anti-patterny

**Dopad**: Znalostní báze je zatím pouze "sklad dat", ne funkční decision-support nástroj.

#### ❌ Verzování a Aktualizace

**Problém**: Chybí mechanismus pro:
- Sledování změn v legislativě a úhradových vyhláškách
- Automatické upozornění na zastaralé znalostní jednotky
- Verzování znalostní báze (např. snapshot pro každý rok)

**Dopad**: Znalostní báze může rychle zastaralá a poskytovat neaktuální informace.

---

## 2. Strategický Plán Dalšího Rozvoje

### Fáze 2: Rozšíření Datasetu (Měsíc 1–2)

**Cíl**: Rozšířit dataset na **100–150 znalostních jednotek** pokrývajících klíčové oblasti.

#### Kroky:

1. **Systematická extrakce z úhradových vyhlášek**
   - Stáhnout úhradové vyhlášky 2023, 2024, 2025, 2026 (PDF)
   - Extrahovat klíčové změny, pravidla a výjimky
   - Strukturovat do znalostních jednotek
   - **Výstup**: 30–40 jednotek

2. **Analýza metodik pojišťoven**
   - VZP: Metodiky pro ambulantní specialisty, VPL, fyzioterapeuty
   - ZP MV, OZP, ČPZP, RBP: Specifické dodatky a podmínky
   - **Výstup**: 20–30 jednotek

3. **Extrakce praktických článků z InfoProLekare.cz**
   - Rizika při převzetí ordinace
   - Optimalizace PURO
   - Finanční anti-patterny
   - Compliance a sankce
   - **Výstup**: 30–40 jednotek

4. **Legislativní rámec**
   - Zákon 48/1997 Sb. (veřejné zdravotní pojištění)
   - Zákon 372/2011 Sb. (zdravotní služby)
   - Relevantní vyhlášky a nařízení
   - **Výstup**: 20–30 jednotek

#### Metriky úspěchu:
- ✅ 100+ znalostních jednotek
- ✅ Pokrytí všech 5 domén (úhrady, provoz, compliance, finanční rizika, legislativa)
- ✅ Pokrytí alespoň 10 odborností

---

### Fáze 3: Automatizace a Nástroje (Měsíc 2–3)

**Cíl**: Vyvinout nástroje pro poloautomatickou extrakci a validaci znalostních jednotek.

#### Kroky:

1. **LLM-asistovaná extrakce**
   - Vyvinout prompt pro GPT-4 / Claude, který:
     - Přečte text z PDF/článku
     - Identifikuje pravidla, výjimky, rizika
     - Strukturuje do JSON formátu dle schématu
   - Manuální review a validace výstupu
   - **Výstup**: Python skript `extract_knowledge.py`

2. **Validační nástroje**
   - Rozšířit `validate.py` o:
     - Kontrolu duplicit (podobné tituly, stejné podmínky)
     - Kontrolu propojení (related_units existují)
     - Kontrolu zdrojů (URL jsou dostupné)
   - **Výstup**: Robustní validační pipeline

3. **Monitoring změn ve zdrojích**
   - Skript pro periodické stahování úhradových vyhlášek
   - Detekce změn v metodikách pojišťoven
   - Automatické upozornění na nové dokumenty
   - **Výstup**: Python skript `monitor_sources.py`

4. **Export a transformace**
   - Export do CSV, Parquet, SQLite
   - Generování embeddings pro RAG
   - Export do formátu pro fine-tuning LLM
   - **Výstup**: Python skript `export.py`

#### Metriky úspěchu:
- ✅ Extrakce 1 znalostní jednotky trvá <5 minut (místo 15–20 minut)
- ✅ Validace detekuje 90%+ chyb
- ✅ Monitoring běží automaticky 1× týdně

---

### Fáze 4: AI Decision-Support Vrstva (Měsíc 3–4)

**Cíl**: Postavit AI vrstvu, která umožní interaktivní práci se znalostní bází.

#### Kroky:

1. **RAG Pipeline**
   - Vygenerovat embeddings pro všechny znalostní jednotky (OpenAI, Cohere)
   - Uložit do vector database (Pinecone, Weaviate, Qdrant)
   - Implementovat semantic search
   - **Výstup**: RAG pipeline v Pythonu

2. **Q&A API**
   - FastAPI endpoint pro dotazy v přirozeném jazyce
   - Kombinace RAG + LLM (GPT-4, Claude) pro generování odpovědí
   - Citace zdrojů (odkazy na znalostní jednotky)
   - **Výstup**: REST API

3. **Vysvětlovací vrstva**
   - Pro každou odpověď:
     - Zobrazit použité znalostní jednotky
     - Vysvětlit logiku rozhodování
     - Upozornit na rizika a výjimky
   - **Výstup**: Strukturovaný response s metadaty

4. **Testování a validace**
   - Vytvořit testovací sadu 50 dotazů
   - Evaluace přesnosti odpovědí (manuální review)
   - Iterativní zlepšování promptů
   - **Výstup**: Test suite

#### Metriky úspěchu:
- ✅ API odpovídá na 90%+ dotazů relevantně
- ✅ Průměrná latence <3 sekundy
- ✅ Všechny odpovědi mají citace zdrojů

---

### Fáze 5: Produktizace a Integrace (Měsíc 4–6)

**Cíl**: Integrovat znalostní bázi do produktů Czech MedAI.

#### Kroky:

1. **Integrace do klinického AI asistenta**
   - Rozšířit asistenta o ekonomickou a provozní vrstvu
   - Umožnit lékařům klást dotazy typu:
     - "Jaké jsou bonifikace pro mou odbornost v roce 2026?"
     - "Co se stane, pokud překročím MAXÚ?"
     - "Jak optimalizovat PURO?"
   - **Výstup**: Rozšířený AI asistent

2. **AI Audit ambulantních praxí**
   - Automatická analýza ekonomické situace ordinace
   - Identifikace rizik a anti-patternů
   - Doporučení pro optimalizaci
   - **Výstup**: Audit modul

3. **Management Reporting**
   - Generování reportů pro majitele ordinací
   - Srovnání s průměrem v oboru a regionu
   - Predikce vývoje příjmů
   - **Výstup**: Reporting modul

4. **Dokumentace a školení**
   - Uživatelská příručka pro lékaře
   - Video tutoriály
   - Webináře a semináře
   - **Výstup**: Vzdělávací materiály

#### Metriky úspěchu:
- ✅ 100+ aktivních uživatelů
- ✅ 90%+ spokojenost uživatelů
- ✅ Prokázaná hodnota (úspora času, zvýšení příjmů)

---

## 3. Prioritizace a Roadmap

### Priorita 1 (Měsíc 1): Rozšíření datasetu na 100+ jednotek
- **Proč**: Bez dostatečného pokrytí nemá smysl stavět AI vrstvu
- **Jak**: Manuální extrakce + LLM asistence
- **Kdo**: 1–2 lidé (domain expert + AI engineer)

### Priorita 2 (Měsíc 2): Automatizace extrakce
- **Proč**: Škálování manuálního procesu není udržitelné
- **Jak**: LLM-asistovaná extrakce + validační nástroje
- **Kdo**: 1 AI engineer

### Priorita 3 (Měsíc 3): RAG Pipeline a Q&A API
- **Proč**: Umožní interaktivní práci se znalostní bází
- **Jak**: RAG + LLM + FastAPI
- **Kdo**: 1 AI engineer + 1 backend developer

### Priorita 4 (Měsíc 4–6): Integrace do produktů
- **Proč**: Reálná hodnota pro uživatele
- **Jak**: Integrace do existujících produktů Czech MedAI
- **Kdo**: Product team + AI team

---

## 4. Technologický Stack

### Aktuální Stack
- **Storage**: GitHub (Git), Hugging Face (dataset)
- **Format**: JSON Lines, JSON Schema
- **Validation**: Python (custom scripts)

### Doporučený Stack pro Fázi 3–4

| Komponenta | Technologie | Důvod |
|------------|-------------|-------|
| **Vector DB** | Pinecone / Qdrant | Snadná integrace, škálovatelnost |
| **Embeddings** | OpenAI text-embedding-3-large | Vysoká kvalita, česká podpora |
| **LLM** | GPT-4o / Claude 3.5 Sonnet | Nejlepší reasoning pro češtinu |
| **API Framework** | FastAPI | Rychlost, async, automatická dokumentace |
| **Monitoring** | Langfuse / LangSmith | Sledování LLM calls, debugging |
| **Deployment** | Docker + Kubernetes | Škálovatelnost, reliability |

---

## 5. Rizika a Mitigace

### Riziko 1: Zastaralost dat
**Popis**: Úhradové vyhlášky se mění ročně, metodiky průběžně.  
**Mitigace**: Automatický monitoring zdrojů, verzování datasetu, jasné označení platnosti.

### Riziko 2: Kvalita extrakce
**Popis**: LLM může chybně interpretovat složité legislativní texty.  
**Mitigace**: Manuální review všech extrakcí, validační nástroje, iterativní zlepšování promptů.

### Riziko 3: Právní odpovědnost
**Popis**: Chybné informace mohou vést k finančním ztrátám uživatelů.  
**Mitigace**: Jasné disclaimer, že jde o decision-support (ne právní poradenství), citace zdrojů, doporučení konzultace s expertem.

### Riziko 4: Škálovatelnost
**Popis**: Ruční extrakce neškáluje, API může být přetížené.  
**Mitigace**: Automatizace extrakce (Fáze 3), caching, rate limiting, horizontální škálování.

---

## 6. Klíčové Metriky Úspěchu

### Metriky Datasetu
- **Počet znalostních jednotek**: 100+ (Fáze 2), 500+ (Fáze 5)
- **Pokrytí odborností**: 10+ odborností
- **Pokrytí let**: 2023–2026
- **Validační úspěšnost**: 95%+ jednotek bez chyb

### Metriky AI Vrstvy
- **Relevance odpovědí**: 90%+ dotazů relevantně zodpovězeno
- **Latence**: <3 sekundy průměrně
- **Citace zdrojů**: 100% odpovědí s odkazy

### Metriky Produktu
- **Aktivní uživatelé**: 100+ (Fáze 5)
- **Spokojenost**: 4.5/5 (NPS 50+)
- **Prokázaná hodnota**: Úspora času, zvýšení příjmů

---

## 7. Závěr a Doporučení

Projekt má **obrovský potenciál** stát se klíčovým nástrojem pro lékaře a provozovatelé ambulancí v ČR. Pilotní fáze prokázala technickou proveditelnost a správný směr.

### Klíčová doporučení:

1. **Prioritizovat rozšíření datasetu** – bez dostatečného pokrytí nemá smysl stavět AI vrstvu
2. **Investovat do automatizace** – manuální extrakce není udržitelná
3. **Začít s RAG pipeline co nejdříve** – umožní testovat hodnotu pro uživatele
4. **Iterovat s uživateli** – pravidelný feedback od lékařů je kritický
5. **Verzovat a aktualizovat** – znalostní báze musí být vždy aktuální

**Další krok**: Začít s Fází 2 (rozšíření datasetu) a paralelně připravit LLM-asistovanou extrakci.

---

**Autor**: Manus AI  
**Datum**: 14. prosince 2025  
**Verze dokumentu**: 1.0
