---
type: reference
title: Instalace a konfigurace MVP RAG API
created: 2026-02-03
tags:
  - deployment
  - setup
  - configuration
  - installation
related:
  - "[[api_reference]]"
  - "[[troubleshooting]]"
  - "[[mvp_test_analysis]]"
---

# Instalace a konfigurace MVP RAG API

Kompletní průvodce instalací, konfigurací a spuštěním MVP znalostní báze pro ambulantní zdravotní péči.

---

## Obsah

1. [Požadavky](#1-požadavky)
2. [Instalace](#2-instalace)
3. [Konfigurace](#3-konfigurace)
4. [Příprava dat](#4-příprava-dat)
5. [Spuštění API](#5-spuštění-api)
6. [Verifikace](#6-verifikace)
7. [Produkční nasazení](#7-produkční-nasazení)

---

## 1. Požadavky

### Systémové požadavky

| Komponenta | Minimum | Doporučeno |
|------------|---------|------------|
| **Python** | 3.10+ | 3.11+ |
| **RAM** | 2 GB | 4 GB |
| **Disk** | 500 MB | 1 GB |
| **CPU** | 2 cores | 4 cores |

### Software

- Python 3.10 nebo novější
- pip (správce balíčků)
- Git
- OpenAI API klíč (pro Q&A endpoint)

### Podporované platformy

- Linux (Ubuntu 20.04+, Debian 11+)
- macOS (11.0+)
- Windows 10/11 (s WSL2 doporučeno)

---

## 2. Instalace

### 2.1 Klonování repozitáře

```bash
git clone https://github.com/petrsovadina/klinicka-knowledge-base.git
cd klinicka-knowledge-base
```

### 2.2 Vytvoření virtuálního prostředí

```bash
# Vytvoření virtuálního prostředí
python3 -m venv .venv

# Aktivace (Linux/macOS)
source .venv/bin/activate

# Aktivace (Windows)
.venv\Scripts\activate
```

### 2.3 Instalace závislostí

```bash
pip install -r requirements.txt
```

#### Hlavní závislosti

| Balíček | Verze | Účel |
|---------|-------|------|
| `fastapi` | 0.104+ | Web framework |
| `uvicorn` | 0.24+ | ASGI server |
| `numpy` | 1.24+ | Vektorové operace |
| `scikit-learn` | 1.3+ | TF-IDF, SVD modely |
| `openai` | 1.0+ | GPT API pro Q&A |
| `pydantic` | 2.0+ | Validace dat |

### 2.4 Instalace pro vývoj (volitelná)

```bash
pip install -r requirements-dev.txt
```

---

## 3. Konfigurace

### 3.1 Environment variables

Vytvořte soubor `.env` v kořenovém adresáři:

```bash
# Cesta k datovým souborům
DATA_DIR=/path/to/klinicka-knowledge-base/data

# OpenAI API klíč (vyžadován pro /qa endpoint)
OPENAI_API_KEY=sk-your-api-key-here

# Rate limiting
RATE_LIMIT_REQUESTS=60    # Maximální počet požadavků za okno
RATE_LIMIT_WINDOW=60      # Délka okna v sekundách

# Cache
CACHE_TTL=300             # Doba platnosti cache v sekundách (5 min)
CACHE_MAX_SIZE=1000       # Maximální počet cachovaných položek
```

### 3.2 Popis konfiguračních proměnných

| Proměnná | Výchozí | Popis |
|----------|---------|-------|
| `DATA_DIR` | `/home/ubuntu/klinicka-knowledge-base/data` | Cesta k adresáři s daty |
| `OPENAI_API_KEY` | - | API klíč pro OpenAI (povinné pro Q&A) |
| `RATE_LIMIT_REQUESTS` | 60 | Max požadavků na klienta za okno |
| `RATE_LIMIT_WINDOW` | 60 | Délka rate limit okna (sekundy) |
| `CACHE_TTL` | 300 | Platnost cache (sekundy) |
| `CACHE_MAX_SIZE` | 1000 | Max položek v cache |

### 3.3 Konfigurace pro produkci

Pro produkční prostředí doporučujeme:

```bash
# Přísnější rate limiting
RATE_LIMIT_REQUESTS=30
RATE_LIMIT_WINDOW=60

# Delší cache pro stabilnější dotazy
CACHE_TTL=600

# Větší cache pro více uživatelů
CACHE_MAX_SIZE=5000
```

---

## 4. Příprava dat

### 4.1 Struktura datových souborů

```
data/
├── knowledge_base_mvp.jsonl        # Znalostní báze (669 jednotek)
├── knowledge_base_embeddings.jsonl  # Embeddings pro vyhledávání
├── tfidf_vectorizer.pkl            # TF-IDF model
└── svd_model.pkl                   # SVD model pro dimenzionalitu
```

### 4.2 Verifikace dat

```bash
# Kontrola počtu znalostních jednotek
wc -l data/knowledge_base_mvp.jsonl
# Očekávaný výstup: 669

# Kontrola validace JSON
python scripts/validate_dataset.py data/knowledge_base_mvp.jsonl
```

### 4.3 Generování embeddings (pokud chybí)

```bash
python scripts/generate_embeddings.py
```

Tento script:
1. Načte znalostní jednotky z `knowledge_base_mvp.jsonl`
2. Vytvoří TF-IDF vektorizér
3. Aplikuje SVD pro redukci dimenzí
4. Uloží embeddings a modely

---

## 5. Spuštění API

### 5.1 Vývojový režim

```bash
# Přímé spuštění
python api/rag_api.py

# Nebo přes uvicorn s hot-reload
uvicorn api.rag_api:app --reload --port 8000
```

### 5.2 Produkční režim

```bash
uvicorn api.rag_api:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --no-access-log \
  --limit-concurrency 100
```

### 5.3 Spuštění pomocí Docker

```bash
# Sestavení image
docker build -t klinicka-rag-api .

# Spuštění kontejneru
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -v $(pwd)/data:/app/data \
  --name klinicka-api \
  klinicka-rag-api
```

---

## 6. Verifikace

### 6.1 Health check

```bash
curl http://localhost:8000/health
```

Očekávaná odpověď:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "knowledge_units": 669,
  "embeddings": 669,
  "data_loaded": true,
  "timestamp": "2026-02-03T10:00:00.000000"
}
```

### 6.2 Test vyhledávání

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "hodnota bodu 2026", "top_k": 3}'
```

### 6.3 Test Q&A

```bash
curl -X POST http://localhost:8000/qa \
  -H "Content-Type: application/json" \
  -d '{"question": "Jaká je hodnota bodu pro ambulantní specialisty v roce 2026?", "top_k": 5}'
```

### 6.4 Spuštění unit testů

```bash
python scripts/test_api_unit.py
```

### 6.5 Zátěžový test

```bash
python scripts/test_api_load.py --concurrent 10 --requests 100
```

---

## 7. Produkční nasazení

### 7.1 Systemd služba (Linux)

Vytvořte `/etc/systemd/system/klinicka-api.service`:

```ini
[Unit]
Description=Klinicka Knowledge Base RAG API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/klinicka-knowledge-base
Environment="PATH=/opt/klinicka-knowledge-base/.venv/bin"
Environment="DATA_DIR=/opt/klinicka-knowledge-base/data"
Environment="OPENAI_API_KEY=sk-your-key"
ExecStart=/opt/klinicka-knowledge-base/.venv/bin/uvicorn api.rag_api:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Aktivace:
```bash
sudo systemctl daemon-reload
sudo systemctl enable klinicka-api
sudo systemctl start klinicka-api
```

### 7.2 Nginx reverse proxy

```nginx
server {
    listen 80;
    server_name api.klinicka.cz;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint pro load balancer
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_connect_timeout 5s;
        proxy_read_timeout 5s;
    }
}
```

### 7.3 Monitoring

Doporučené metriky pro monitoring:

| Metrika | Endpoint | Alert threshold |
|---------|----------|-----------------|
| Health status | `/health` | `status != "healthy"` |
| Request rate | `/metrics` | `requests_per_minute > 100` |
| Error rate | `/metrics` | `error_count / total_requests > 0.05` |
| Latency | `/metrics` | `avg_latency_ms > 2000` |
| Cache hit rate | `/metrics` | `cache_hit_rate_percent < 30` |

---

## Další kroky

- [[api_reference]] - Kompletní API dokumentace
- [[troubleshooting]] - Řešení častých problémů
- [[mvp_test_analysis]] - Analýza výkonnosti RAG

---

*Vytvořeno: 2026-02-03*
*Verze dokumentu: 1.0*
*API verze: 1.0.0*
