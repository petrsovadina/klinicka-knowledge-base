---
type: reference
title: Troubleshooting - Řešení častých problémů
created: 2026-02-03
tags:
  - troubleshooting
  - debugging
  - errors
  - deployment
related:
  - "[[setup]]"
  - "[[api_reference]]"
  - "[[mvp_test_analysis]]"
---

# Troubleshooting - Řešení častých problémů

Průvodce řešením běžných problémů při instalaci, konfiguraci a provozu MVP RAG API.

---

## Obsah

1. [Problémy při instalaci](#1-problémy-při-instalaci)
2. [Problémy při spuštění](#2-problémy-při-spuštění)
3. [Runtime chyby](#3-runtime-chyby)
4. [Problémy s výkonem](#4-problémy-s-výkonem)
5. [Síťové problémy](#5-síťové-problémy)
6. [Diagnostické nástroje](#6-diagnostické-nástroje)

---

## 1. Problémy při instalaci

### 1.1 Chyba: `pip install` selhává

**Symptom:**
```
error: subprocess-exited-with-error
× Building wheel for scikit-learn failed
```

**Příčina:** Chybí build dependencies nebo nekompatibilní verze Pythonu.

**Řešení:**

```bash
# Ubuntu/Debian
sudo apt-get install python3-dev build-essential

# macOS
xcode-select --install

# Poté znovu instalace
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

---

### 1.2 Chyba: Python verze nekompatibilní

**Symptom:**
```
ERROR: Package 'fastapi' requires a different Python: 3.8.0 not in '>=3.10'
```

**Řešení:**

```bash
# Kontrola verze
python3 --version

# Instalace Python 3.11 (Ubuntu)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv

# Vytvoření venv s konkrétní verzí
python3.11 -m venv .venv
source .venv/bin/activate
```

---

### 1.3 Chyba: numpy build selhává na Apple Silicon

**Symptom:**
```
RuntimeError: NumPy cannot be built with BLAS acceleration
```

**Řešení:**

```bash
# Instalace Homebrew dependencies
brew install openblas

# Export cest
export OPENBLAS=$(brew --prefix openblas)
export CFLAGS="-falign-functions=8 ${CFLAGS}"

pip install numpy --no-cache-dir
```

---

## 2. Problémy při spuštění

### 2.1 Chyba: Data soubory nenalezeny

**Symptom:**
```
Warning: Knowledge file not found at /home/ubuntu/klinicka-knowledge-base/data/knowledge_base_final.jsonl
```

**Příčina:** Nesprávně nastavená cesta `DATA_DIR`.

**Řešení:**

```bash
# Kontrola existence souborů
ls -la data/

# Nastavení správné cesty
export DATA_DIR=$(pwd)/data

# Nebo v .env souboru
echo "DATA_DIR=$(pwd)/data" >> .env
```

---

### 2.2 Chyba: Port již používán

**Symptom:**
```
ERROR: [Errno 98] Address already in use
```

**Řešení:**

```bash
# Najít proces na portu 8000
lsof -i :8000

# Ukončit proces
kill -9 <PID>

# Nebo použít jiný port
uvicorn api.rag_api:app --port 8001
```

---

### 2.3 Chyba: ModuleNotFoundError

**Symptom:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Příčina:** Virtuální prostředí není aktivované.

**Řešení:**

```bash
# Aktivace venv
source .venv/bin/activate

# Ověření
which python
# Mělo by zobrazit: /path/to/.venv/bin/python
```

---

### 2.4 Chyba: Embeddings model nenačten

**Symptom:**
```json
{
  "detail": "Embedding models not loaded"
}
```

**Příčina:** Chybí soubory `tfidf_vectorizer.pkl` nebo `svd_model.pkl`.

**Řešení:**

```bash
# Kontrola souborů
ls -la data/*.pkl

# Pokud chybí, vygenerovat znovu
python scripts/generate_embeddings.py
```

---

## 3. Runtime chyby

### 3.1 Chyba: OpenAI API rate limit

**Symptom:**
```json
{
  "detail": "QA error: Rate limit exceeded"
}
```

**Řešení:**

1. Zkontrolujte stav OpenAI API klíče
2. Implementujte exponential backoff
3. Snižte počet Q&A požadavků

```bash
# Test API klíče
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

---

### 3.2 Chyba: Vysoká latence odpovědí

**Symptom:** Odpovědi trvají déle než 5 sekund.

**Diagnostika:**

```bash
# Kontrola metrik
curl http://localhost:8000/metrics | jq '.avg_latency_ms'
```

**Možné příčiny a řešení:**

| Příčina | Řešení |
|---------|--------|
| Velký `top_k` | Snížit na 3-5 |
| Cold start | První dotaz po startu je vždy pomalejší |
| Nedostatek RAM | Zvýšit RAM nebo snížit workers |
| Pomalé OpenAI API | Q&A endpoint závisí na externím API |

---

### 3.3 Chyba: Memory error

**Symptom:**
```
MemoryError: Unable to allocate array
```

**Řešení:**

```bash
# Kontrola paměti
free -h

# Snížení počtu workers
uvicorn api.rag_api:app --workers 2

# Nebo zvýšení swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

### 3.4 Chyba: 429 Too Many Requests

**Symptom:**
```json
{
  "error": "Rate limit exceeded",
  "detail": "Maximum 60 requests per 60 seconds"
}
```

**Řešení pro klienty:**

```python
import time

def request_with_retry(url, data, max_retries=3):
    for attempt in range(max_retries):
        response = requests.post(url, json=data)
        if response.status_code == 429:
            retry_after = response.headers.get('Retry-After', 60)
            time.sleep(int(retry_after))
            continue
        return response
    raise Exception("Max retries exceeded")
```

**Řešení pro administrátory:**

```bash
# Zvýšení limitu
export RATE_LIMIT_REQUESTS=120
```

---

## 4. Problémy s výkonem

### 4.1 Nízká cache hit rate

**Symptom:** `cache_hit_rate_percent` pod 20%.

**Diagnostika:**

```bash
curl http://localhost:8000/metrics | jq '{
  cache_hits: .cache_hits,
  cache_misses: .cache_misses,
  cache_hit_rate_percent: .cache_hit_rate_percent
}'
```

**Řešení:**

1. Zvýšit TTL cache:
   ```bash
   export CACHE_TTL=600  # 10 minut
   ```

2. Zvýšit velikost cache:
   ```bash
   export CACHE_MAX_SIZE=5000
   ```

3. Normalizovat dotazy na klientské straně (lowercase, trim whitespace)

---

### 4.2 Vysoká chybovost

**Symptom:** `error_count` roste rychle.

**Diagnostika:**

```bash
# Kontrola logů
journalctl -u klinicka-api -f

# Nebo Docker logs
docker logs -f klinicka-api
```

**Časté příčiny:**

| Chyba | Řešení |
|-------|--------|
| OpenAI API nedostupné | Kontrola API klíče a statusu |
| Malformované JSON | Validace na klientské straně |
| Interní chyby | Kontrola logů pro stacktrace |

---

### 4.3 API reaguje pomalu

**Checklist optimalizace:**

1. **Zkontrolujte workers:**
   ```bash
   uvicorn api.rag_api:app --workers 4
   ```

2. **Povolte keep-alive:**
   ```bash
   uvicorn api.rag_api:app --timeout-keep-alive 30
   ```

3. **Zvažte gunicorn:**
   ```bash
   gunicorn api.rag_api:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

---

## 5. Síťové problémy

### 5.1 CORS chyby

**Symptom:**
```
Access to fetch at 'http://localhost:8000' from origin 'http://example.com' has been blocked by CORS policy
```

**Řešení:**

Upravte `api/rag_api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com", "https://app.example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 5.2 Timeout při reverse proxy

**Symptom:** Nginx vrací `504 Gateway Timeout`.

**Řešení v nginx.conf:**

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_connect_timeout 300s;
    proxy_read_timeout 300s;
    proxy_send_timeout 300s;
}
```

---

### 5.3 SSL/TLS problémy

**Symptom:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Řešení:**

```bash
# Aktualizace certifikátů (Ubuntu)
sudo apt-get update && sudo apt-get install ca-certificates

# macOS
/Applications/Python\ 3.11/Install\ Certificates.command
```

---

## 6. Diagnostické nástroje

### 6.1 Health check script

```bash
#!/bin/bash
# health_check.sh

API_URL="${1:-http://localhost:8000}"

echo "=== Health Check ==="
curl -s "$API_URL/health" | jq '.'

echo -e "\n=== Metrics ==="
curl -s "$API_URL/metrics" | jq '{
  uptime: .uptime_seconds,
  requests: .total_requests,
  errors: .error_count,
  latency_ms: .avg_latency_ms,
  cache_hit_rate: .cache_hit_rate_percent
}'

echo -e "\n=== Test Search ==="
curl -s -X POST "$API_URL/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "top_k": 1}' | jq '.results[0].score'
```

### 6.2 Load test script

```bash
#!/bin/bash
# load_test.sh

API_URL="${1:-http://localhost:8000}"
CONCURRENT="${2:-10}"
TOTAL="${3:-100}"

echo "Running load test: $CONCURRENT concurrent, $TOTAL total requests"

seq 1 $TOTAL | xargs -P $CONCURRENT -I {} \
  curl -s -X POST "$API_URL/search" \
    -H "Content-Type: application/json" \
    -d '{"query": "hodnota bodu 2026", "top_k": 3}' \
    -o /dev/null -w "%{http_code} %{time_total}s\n"
```

### 6.3 Log analýza

```bash
# Počet chyb za posledních 24 hodin
journalctl -u klinicka-api --since "24 hours ago" | grep -c "ERROR"

# Nejčastější chyby
journalctl -u klinicka-api --since "24 hours ago" | grep "ERROR" | sort | uniq -c | sort -rn | head -10
```

### 6.4 Memory profiling

```bash
# Kontrola memory usage
ps aux | grep uvicorn

# Detailní memory info
python -c "
import sys
import psutil
p = psutil.Process()
print(f'Memory: {p.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

---

## Kontakt a eskalace

Pokud problém přetrvává:

1. Zkontrolujte [GitHub Issues](https://github.com/petrsovadina/klinicka-knowledge-base/issues)
2. Vytvořte nový issue s:
   - Popisem problému
   - Error logem
   - Kroky k reprodukci
   - Verzí API (`GET /health`)

---

*Vytvořeno: 2026-02-03*
*Verze dokumentu: 1.0*
