# Klinická Znalostní Báze – Ambulantní Zdravotní Péče v ČR

[![Dataset](https://img.shields.io/badge/Hugging%20Face-Dataset-yellow)](https://huggingface.co/datasets/petrsovadina/klinicka-knowledge-base)
[![Version](https://img.shields.io/badge/version-1.0.0--MVP-blue)]()
[![Knowledge Units](https://img.shields.io/badge/knowledge%20units-669-green)]()
[![License](https://img.shields.io/badge/license-MIT-lightgrey)]()

Strukturovaná znalostní báze a AI decision-support vrstva zaměřená na ekonomiku, úhrady a provoz ambulantní zdravotní péče v České republice.

## MVP Status (2026)

| Metrika | Hodnota | Status |
|---------|---------|--------|
| **Knowledge Units** | 669 | ✅ |
| **Domény** | 5 (úhrady, provoz, compliance, fin. rizika, legislativa) | ✅ |
| **RAG Skóre (průměr)** | 0.730 | ✅ |
| **API Verze** | 1.0.0 | ✅ |

## Rychlý start

### 1. Instalace

```bash
git clone https://github.com/petrsovadina/klinicka-knowledge-base.git
cd klinicka-knowledge-base

python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

### 2. Konfigurace

```bash
# Vytvořte .env soubor
cat > .env << EOF
DATA_DIR=$(pwd)/data
OPENAI_API_KEY=sk-your-api-key-here
EOF
```

### 3. Spuštění API

```bash
# Vývojový režim
python api/rag_api.py

# Produkční režim
uvicorn api.rag_api:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Ověření

```bash
# Health check
curl http://localhost:8000/health

# Test vyhledávání
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "hodnota bodu 2026", "top_k": 3}'
```

## Cíl projektu

Nejde o další informační web ani obecného chatbota. Jde o systematické zachycení a strukturování provozního know-how, které dnes existuje roztříštěně v článcích, vyhláškách a praktických zkušenostech – a jeho zpřístupnění ve formě, se kterou může pracovat umělá inteligence.

### Proč to děláme?

1. **Aby lékaři a provozovatelé praxí rozuměli důsledkům svých rozhodnutí** – vidět rizika dopředu, pochopit ekonomické a provozní dopady, vyhnout se typickým chybám.

2. **Aby AI ve zdravotnictví pracovala s realitou, ne s teorií** – doplnit AI o znalost úhradových mechanismů, smluvních vztahů, regulačních limitů a praktických heuristik.

3. **Aby vznikl decision-support nástroj, ne zdravotnický prostředek** – vysvětlovat pravidla, upozorňovat na rizika, podporovat informované rozhodování, zůstat mimo MDR.

4. **Aby vznikla sdílená znalostní vrstva pro více produktů** – dlouhodobý strategický asset napájející klinického AI asistenta, AI audit, dokumentaci a reporting.

## API Endpointy

| Endpoint | Metoda | Popis |
|----------|--------|-------|
| `/health` | GET | Health check pro monitoring |
| `/metrics` | GET | Provozní metriky |
| `/search` | POST | Sémantické vyhledávání |
| `/qa` | POST | Otázka a odpověď (RAG) |
| `/unit/{id}` | GET | Detail znalostní jednotky |
| `/docs` | GET | Swagger dokumentace |

### Příklad: Vyhledávání

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "bonifikace za nové pacienty 2026",
    "top_k": 5
  }'
```

### Příklad: Q&A

```bash
curl -X POST http://localhost:8000/qa \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Jaké jsou bonifikace za příjem nových pacientů v roce 2026?",
    "top_k": 5
  }'
```

## Struktura repozitáře

```
klinicka-knowledge-base/
├── README.md                          # Tento soubor
├── CONTRIBUTING.md                    # Příspěvky a standardy
├── api/
│   └── rag_api.py                     # FastAPI RAG endpoint
├── schemas/
│   └── knowledge_unit.schema.json     # JSON schéma pro validaci
├── data/
│   ├── knowledge_base_mvp.jsonl       # MVP dataset (669 jednotek)
│   ├── knowledge_base_embeddings.jsonl # Embeddings
│   ├── tfidf_vectorizer.pkl           # TF-IDF model
│   └── svd_model.pkl                  # SVD model
├── docs/
│   ├── deployment/
│   │   ├── setup.md                   # Instalace a konfigurace
│   │   ├── api_reference.md           # Kompletní API dokumentace
│   │   └── troubleshooting.md         # Řešení problémů
│   └── analysis/
│       └── mvp_test_analysis.md       # Analýza MVP testování
└── scripts/
    ├── generate_embeddings.py         # Generování embeddings
    ├── test_rag_mvp.py               # MVP testování RAG
    ├── test_api_unit.py              # Unit testy API
    └── test_api_load.py              # Zátěžové testy
```

## Datový model

Znalostní jednotka je atomická, strojově zpracovatelná jednotka informace:

- **ID**: Jedinečný identifikátor (UUID)
- **Typ**: `rule`, `exception`, `risk`, `anti_pattern`, `condition`, `definition`, `comparison`
- **Doména**: `uhrady`, `provoz`, `compliance`, `financni-rizika`, `legislativa`
- **Obsah**: Strukturovaný dle typu (podmínka → důsledek, riziko → dopad)
- **Zdroj**: Odkaz na původní dokument s datem stažení
- **Aplikovatelnost**: Odbornosti, platnost, relevance
- **Vztahy**: Propojení s dalšími znalostními jednotkami

Viz [`schemas/knowledge_unit.schema.json`](schemas/knowledge_unit.schema.json) pro detailní specifikaci.

## Pokryté domény

| Doména | Knowledge Units | Příklady |
|--------|-----------------|----------|
| **Úhrady** | 280+ | Hodnota bodu, PURO, MAXÚ, bonifikace |
| **Provoz** | 150+ | Ordinační hodiny, smlouvy, personál |
| **Compliance** | 100+ | Legislativa, regulace, elektronická komunikace |
| **Finanční rizika** | 80+ | Převzetí praxe, regulační rizika |
| **Legislativa** | 60+ | Novely zákonů, vyhlášky |

## Zdroje dat

| Zdroj | Typ | Pokrytí |
|-------|-----|---------|
| [InfoProLekare.cz](https://www.infoprolekare.cz) | Praktické články | ✅ Kompletní |
| [Úhradová vyhláška 2026](https://www.mzcr.cz) | Legislativa | ✅ Kompletní |
| [VZP ČR](https://www.vzp.cz/poskytovatele) | Metodiky | ✅ Částečně |
| [ZP MV ČR](https://www.zpmvcr.cz) | Metodiky | ✅ Částečně |
| [OZP](https://www.ozp.cz) | Metodiky | ✅ Částečně |
| [ČPZP](https://www.cpzp.cz) | Metodiky | ✅ Částečně |

## Dokumentace

- [Instalace a konfigurace](docs/deployment/setup.md)
- [API Reference](docs/deployment/api_reference.md)
- [Troubleshooting](docs/deployment/troubleshooting.md)
- [MVP Test Analýza](docs/analysis/mvp_test_analysis.md)

## Docker nasazení

```bash
# Sestavení
docker build -t klinicka-rag-api .

# Spuštění
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -v $(pwd)/data:/app/data \
  klinicka-rag-api
```

Nebo pomocí Docker Compose:

```bash
docker-compose up -d
```

## Testování

```bash
# Unit testy API
python scripts/test_api_unit.py

# RAG testování (25 dotazů)
python scripts/test_rag_mvp.py

# Zátěžový test
python scripts/test_api_load.py --concurrent 10
```

## Příspěvky

Přispívat můžete přidáním nových znalostních jednotek, opravou existujících nebo aktualizací zdrojů. Viz [`CONTRIBUTING.md`](CONTRIBUTING.md) pro detaily.

## Licence

Tento projekt je licencován pod [MIT License](LICENSE).

## Kontakt a feedback

Máte návrhy, chyby nebo chcete přispět? Otevřete issue nebo pull request na [GitHub](https://github.com/petrsovadina/klinicka-knowledge-base/issues).

---

**Poslední aktualizace**: 3. února 2026
**Verze datasetu**: 1.0.0-MVP
**Počet znalostních jednotek**: 669
