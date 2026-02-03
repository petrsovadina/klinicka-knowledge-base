---
type: reference
title: Kompletní API Reference - MVP RAG API
created: 2026-02-03
tags:
  - api
  - reference
  - endpoints
  - documentation
related:
  - "[[setup]]"
  - "[[troubleshooting]]"
  - "[[mvp_test_analysis]]"
---

# Kompletní API Reference - MVP RAG API

Dokumentace všech endpointů RAG API pro Klinickou znalostní bázi.

---

## Obsah

1. [Přehled](#1-přehled)
2. [Autentizace a limity](#2-autentizace-a-limity)
3. [Endpointy](#3-endpointy)
4. [Chybové odpovědi](#4-chybové-odpovědi)
5. [Příklady použití](#5-příklady-použití)

---

## 1. Přehled

### Base URL

```
http://localhost:8000
```

Produkce:
```
https://api.klinicka.cz
```

### Podporované formáty

- **Request body**: `application/json`
- **Response**: `application/json`

### Verze API

Aktuální verze: `1.0.0`

### OpenAPI dokumentace

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

---

## 2. Autentizace a limity

### Rate limiting

API využívá sliding window rate limiting:

| Parametr | Výchozí hodnota |
|----------|-----------------|
| Limit | 60 požadavků |
| Okno | 60 sekund |

#### Rate limit headers

Každá odpověď obsahuje:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Window: 60
```

#### Překročení limitu

Při překročení limitu vrací API status `429 Too Many Requests`:

```json
{
  "error": "Rate limit exceeded",
  "detail": "Maximum 60 requests per 60 seconds",
  "retry_after_seconds": 60
}
```

### Endpointy bez rate limitingu

- `/health`
- `/metrics`
- `/docs`
- `/redoc`
- `/openapi.json`

---

## 3. Endpointy

### 3.1 Root

```
GET /
```

Základní informace o API.

#### Response

```json
{
  "status": "ok",
  "name": "Klinicka Knowledge Base RAG API",
  "version": "1.0.0",
  "units": 669,
  "endpoints": {
    "search": "/search",
    "qa": "/qa",
    "health": "/health",
    "metrics": "/metrics",
    "docs": "/docs"
  }
}
```

---

### 3.2 Search

```
POST /search
```

Sémantické vyhledávání nad znalostní bází.

#### Request body

| Pole | Typ | Povinné | Default | Popis |
|------|-----|---------|---------|-------|
| `query` | string | Ano | - | Dotaz pro vyhledávání |
| `top_k` | integer | Ne | 5 | Počet vrácených výsledků (1-20) |

```json
{
  "query": "hodnota bodu pro ambulantní specialisty 2026",
  "top_k": 5
}
```

#### Response

```json
{
  "query": "hodnota bodu pro ambulantní specialisty 2026",
  "results": [
    {
      "id": "ku-001-bod-sas-2026",
      "score": 0.808,
      "title": "Jednotná hodnota bodu pro ambulantní specialisty (SAS) v roce 2026",
      "description": "Od roku 2026 platí jednotná základní hodnota bodu pro hrazené služby ambulantních specialistů ve výši 0,98 Kč.",
      "type": "rule",
      "domain": "uhrady"
    },
    {
      "id": "ku-002-hbmin-2026",
      "score": 0.754,
      "title": "Snížení minimální hodnoty bodu (HBmin) pro výpočet PURO v roce 2026",
      "description": "Minimální hodnota bodu pro výpočet PURO byla snížena z 1,03 Kč na 0,90 Kč.",
      "type": "rule",
      "domain": "uhrady"
    }
  ],
  "cached": false
}
```

#### Response fields

| Pole | Typ | Popis |
|------|-----|-------|
| `query` | string | Původní dotaz |
| `results` | array | Pole výsledků seřazené podle relevance |
| `results[].id` | string | Unikátní ID znalostní jednotky |
| `results[].score` | float | Skóre relevance (0.0 - 1.0) |
| `results[].title` | string | Název znalostní jednotky |
| `results[].description` | string | Popis znalostní jednotky |
| `results[].type` | string | Typ: `rule`, `exception`, `risk`, `anti_pattern`, `condition`, `definition`, `comparison` |
| `results[].domain` | string | Doména: `uhrady`, `provoz`, `compliance`, `financni-rizika`, `legislativa` |
| `cached` | boolean | Zda byla odpověď načtena z cache |

---

### 3.3 Question & Answer

```
POST /qa
```

Otázka s vygenerovanou odpovědí pomocí RAG (Retrieval-Augmented Generation).

#### Request body

| Pole | Typ | Povinné | Default | Popis |
|------|-----|---------|---------|-------|
| `question` | string | Ano | - | Otázka v češtině |
| `top_k` | integer | Ne | 5 | Počet kontextových zdrojů |

```json
{
  "question": "Jaké jsou bonifikace za příjem nových pacientů v roce 2026?",
  "top_k": 5
}
```

#### Response

```json
{
  "question": "Jaké jsou bonifikace za příjem nových pacientů v roce 2026?",
  "answer": "V roce 2026 jsou zavedeny dvě úrovně bonifikace za příjem nových pacientů:\n\n1. **Vyšší bonifikace (+0,04 Kč/bod)**: Poskytovatel musí splnit podmínku ordinačních hodin a ošetřit ≥10% nových pojištěnců (15% u operačních oborů) [ku-004-bonifikace-2026].\n\n2. **Nižší bonifikace (+0,01 Kč/bod)**: Stačí ošetřit ≥5% nových pojištěnců (10% u operačních oborů), bez požadavku na ordinační hodiny [ku-004-bonifikace-2026].\n\nPříklad: Lékař s 1000 body a vyšší bonifikací získá: (1000 × 0,98) + (1000 × 0,04) = 1020 Kč.",
  "sources": [
    {
      "id": "ku-004-bonifikace-2026",
      "score": 0.900,
      "title": "Nová odstupňovaná bonifikace za příjem nových pacientů v roce 2026",
      "description": "V roce 2026 byla zavedena nová, odstupňovaná bonifikace za příjem nových pacientů.",
      "type": "rule",
      "domain": "uhrady"
    }
  ],
  "cached": false
}
```

#### Response fields

| Pole | Typ | Popis |
|------|-----|-------|
| `question` | string | Původní otázka |
| `answer` | string | Vygenerovaná odpověď s citacemi [ID] |
| `sources` | array | Zdroje použité pro odpověď |
| `cached` | boolean | Zda byla odpověď načtena z cache |

---

### 3.4 Health Check

```
GET /health
```

Kontrola stavu služby pro monitoring a load balancery.

#### Response

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "knowledge_units": 669,
  "embeddings": 669,
  "data_loaded": true,
  "timestamp": "2026-02-03T10:30:00.123456"
}
```

#### Status values

| Status | Popis |
|--------|-------|
| `healthy` | Všechna data načtena, API připraveno |
| `degraded` | Data nenačtena, API funkční s omezeními |

---

### 3.5 Metrics

```
GET /metrics
```

Provozní metriky pro observabilitu a monitoring dashboardy.

#### Response

```json
{
  "uptime_seconds": 3600.5,
  "total_requests": 1250,
  "requests_per_minute": 20.83,
  "search_requests": 800,
  "qa_requests": 450,
  "cache_hits": 375,
  "cache_misses": 875,
  "cache_hit_rate_percent": 30.0,
  "rate_limited_requests": 5,
  "error_count": 2,
  "avg_latency_ms": 125.5,
  "cache_size": 250
}
```

#### Metrics fields

| Metrika | Typ | Popis |
|---------|-----|-------|
| `uptime_seconds` | float | Doba běhu API v sekundách |
| `total_requests` | int | Celkový počet požadavků |
| `requests_per_minute` | float | Průměrný počet požadavků za minutu |
| `search_requests` | int | Počet /search požadavků |
| `qa_requests` | int | Počet /qa požadavků |
| `cache_hits` | int | Počet cache hitů |
| `cache_misses` | int | Počet cache missů |
| `cache_hit_rate_percent` | float | Procento cache hitů |
| `rate_limited_requests` | int | Počet odmítnutých požadavků kvůli rate limitingu |
| `error_count` | int | Počet chyb |
| `avg_latency_ms` | float | Průměrná latence v ms |
| `cache_size` | int | Aktuální počet položek v cache |

---

### 3.6 Get Unit

```
GET /unit/{unit_id}
```

Získání konkrétní znalostní jednotky podle ID.

#### Path parameters

| Parametr | Typ | Popis |
|----------|-----|-------|
| `unit_id` | string | ID znalostní jednotky (např. `ku-001-bod-sas-2026`) |

#### Response

```json
{
  "id": "ku-001-bod-sas-2026",
  "type": "rule",
  "domain": "uhrady",
  "title": "Jednotná hodnota bodu pro ambulantní specialisty (SAS) v roce 2026",
  "description": "Od roku 2026 platí jednotná základní hodnota bodu...",
  "version": "2026",
  "source": {
    "name": "Úhradová vyhláška 2026 - Ambulantní specialisté",
    "url": "https://www.infoprolekare.cz/uhradova-vyhlaska-2026-pro-ambulantni-specialisty",
    "retrieved_at": "2025-12-14T00:00:00Z"
  },
  "content": {
    "condition": "Poskytovatel je ambulantní specialista (SAS)...",
    "consequence": "Základní hodnota bodu = 0,98 Kč",
    "impact": "Zjednodušení výpočtu úhrad..."
  },
  "applicability": {
    "specialties": ["101", "102", "104"],
    "valid_from": "2026-01-01",
    "valid_to": null
  },
  "related_units": ["ku-002-hbmin-2026", "ku-003-maxu-2026"],
  "tags": ["úhrada", "bod", "SAS", "2026"]
}
```

---

### 3.7 Clear Cache

```
POST /cache/clear
```

Vymazání response cache (admin endpoint).

#### Response

```json
{
  "status": "ok",
  "message": "Cache cleared"
}
```

---

## 4. Chybové odpovědi

### HTTP Status kódy

| Kód | Význam |
|-----|--------|
| `200` | Úspěch |
| `404` | Jednotka nenalezena |
| `429` | Rate limit překročen |
| `500` | Interní chyba serveru |
| `503` | Služba nedostupná (data nenačtena) |

### Formát chyby

```json
{
  "detail": "Popis chyby"
}
```

### Příklady chyb

#### 404 - Unit not found

```json
{
  "detail": "Unit not found"
}
```

#### 429 - Rate limit exceeded

```json
{
  "error": "Rate limit exceeded",
  "detail": "Maximum 60 requests per 60 seconds",
  "retry_after_seconds": 60
}
```

#### 503 - Service unavailable

```json
{
  "detail": "Embeddings not loaded"
}
```

---

## 5. Příklady použití

### 5.1 cURL

#### Search

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "bonifikace za nové pacienty",
    "top_k": 3
  }'
```

#### Q&A

```bash
curl -X POST http://localhost:8000/qa \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Jaká je penalizace za nesplnění bonifikačních podmínek?",
    "top_k": 5
  }'
```

### 5.2 Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Search
response = requests.post(
    f"{BASE_URL}/search",
    json={"query": "PURO výpočet", "top_k": 5}
)
results = response.json()

for r in results["results"]:
    print(f"{r['score']:.3f} - {r['title']}")

# Q&A
response = requests.post(
    f"{BASE_URL}/qa",
    json={"question": "Jak se počítá PURO?", "top_k": 5}
)
answer = response.json()
print(answer["answer"])
```

### 5.3 JavaScript (fetch)

```javascript
const BASE_URL = 'http://localhost:8000';

// Search
async function search(query, topK = 5) {
  const response = await fetch(`${BASE_URL}/search`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({query, top_k: topK})
  });
  return response.json();
}

// Q&A
async function askQuestion(question, topK = 5) {
  const response = await fetch(`${BASE_URL}/qa`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({question, top_k: topK})
  });
  return response.json();
}

// Usage
const results = await search('hodnota bodu 2026');
const answer = await askQuestion('Jaká je hodnota bodu pro AS?');
```

### 5.4 Polling metrik

```bash
#!/bin/bash
while true; do
  curl -s http://localhost:8000/metrics | jq '.requests_per_minute, .error_count, .avg_latency_ms'
  sleep 60
done
```

---

## Další kroky

- [[setup]] - Instalace a konfigurace
- [[troubleshooting]] - Řešení častých problémů
- [[mvp_test_analysis]] - Analýza výkonnosti RAG

---

*Vytvořeno: 2026-02-03*
*Verze dokumentu: 1.0*
*API verze: 1.0.0*
