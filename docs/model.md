# Datový Model – Znalostní Jednotky

## Přehled

Znalostní jednotka je atomická, strojově zpracovatelná jednotka informace o ekonomice, úhradách a provozu ambulantní zdravotní péče v ČR. Každá jednotka je strukturovaná tak, aby ji mohla zpracovávat umělá inteligence.

## Struktura znalostní jednotky

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
    "url": "https://www.infoprolekare.cz/...",
    "retrieved_at": "2025-12-14T00:00:00Z"
  },
  "content": { ... },
  "applicability": { ... },
  "related_units": [ ... ],
  "tags": [ ... ]
}
```

## Pole znalostní jednotky

### id
- **Typ**: `string` (UUID)
- **Povinné**: Ano
- **Popis**: Jedinečný identifikátor znalostní jednotky
- **Formát**: `ku-[pořadí]-[slug]`
- **Příklady**: `ku-001-bod-sas-2026`, `ku-042-riziko-nizka-puro`

### type
- **Typ**: `string` (enum)
- **Povinné**: Ano
- **Možné hodnoty**:
  - `rule` – Pravidlo (podmínka → důsledek)
  - `exception` – Výjimka (pravidlo + výjimka)
  - `risk` – Riziko (situace → potenciální dopad)
  - `anti_pattern` – Anti-pattern (chyba → sankce)
  - `condition` – Podmínka (kritérium + práh)
  - `definition` – Definice (vysvětlení termínu)

### domain
- **Typ**: `string` (enum)
- **Povinné**: Ano
- **Možné hodnoty**:
  - `uhrady` – Úhradové mechanismy, výpočty, bonifikace
  - `provoz` – Provozní rozhodování, ordinační hodiny, pacienti
  - `compliance` – Legislativa, smluvní povinnosti, regulace
  - `financni-rizika` – Finanční rizika, anti-patterny, sankce
  - `legislativa` – Zákony, vyhlášky, právní rámec

### title
- **Typ**: `string`
- **Povinné**: Ano
- **Popis**: Jasný, stručný název znalostní jednotky
- **Délka**: 50–150 znaků
- **Příklad**: "Jednotná hodnota bodu pro ambulantní specialisty (SAS) v roce 2026"

### description
- **Typ**: `string`
- **Povinné**: Ano
- **Popis**: Detailní vysvětlení znalostní jednotky
- **Délka**: 100–500 znaků
- **Příklad**: "Od roku 2026 platí jednotná základní hodnota bodu pro hrazené služby ambulantních specialistů ve výši 0,98 Kč. Toto zjednodušení nahradilo předchozí členění do čtyř kategorií (0,94 až 1,00 Kč)."

### version
- **Typ**: `string`
- **Povinné**: Ano
- **Popis**: Verze regulace nebo zdroje (obvykle rok úhradové vyhlášky)
- **Příklady**: `2026`, `2025`, `2024`

### source
- **Typ**: `object`
- **Povinné**: Ano
- **Pole**:
  - `name` (string) – Název zdroje (povinné)
  - `url` (string, URI) – URL zdroje (povinné)
  - `retrieved_at` (string, ISO 8601) – Datum stažení (povinné)

**Příklad:**
```json
"source": {
  "name": "Úhradová vyhláška 2026 - Ambulantní specialisté",
  "url": "https://www.infoprolekare.cz/uhradova-vyhlaska-2026-pro-ambulantni-specialisty",
  "retrieved_at": "2025-12-14T00:00:00Z"
}
```

### content
- **Typ**: `object`
- **Povinné**: Ano
- **Popis**: Strukturovaný obsah znalostní jednotky (liší se dle typu)

#### content pro `rule` (pravidlo)
```json
"content": {
  "condition": "Když...",
  "consequence": "Pak...",
  "impact": "Dopad je...",
  "calculation_example": "Příklad: ..."
}
```

#### content pro `exception` (výjimka)
```json
"content": {
  "exception": "Odbornosti 305, 306, ...",
  "exempted_from": ["Regulace B.3", "Regulace B.4"],
  "still_subject_to": ["Regulace B.2"],
  "change_from_previous_year": "V roce 2025..."
}
```

#### content pro `risk` (riziko)
```json
"content": {
  "risk": "Riziko je...",
  "affected_providers": "Postihuje...",
  "impact_level": "Vysoké|Střední|Nízké",
  "mitigation": "Lze se vyhnout..."
}
```

#### content pro `anti_pattern` (anti-pattern)
```json
"content": {
  "pattern": "Chyba je...",
  "consequence": "Důsledek je...",
  "why_it_happens": "Stává se, protože...",
  "impact": "Dopad: ...",
  "prevention": "Lze zabránit..."
}
```

#### content pro `condition` (podmínka)
```json
"content": {
  "condition": "Poskytovatel chce...",
  "requirement": "Musí...",
  "combined_with": "Zároveň...",
  "impact": "Dopad: ..."
}
```

#### content pro `definition` (definice)
```json
"content": {
  "term": "PURO",
  "definition": "Průměrná úhrada na unikátního pojištěnce",
  "context": "Používá se v...",
  "importance": "Klíčový ukazatel..."
}
```

### applicability
- **Typ**: `object`
- **Povinné**: Ano
- **Pole**:
  - `specialties` (array of strings) – Relevantní odbornosti (povinné)
  - `valid_from` (string, ISO 8601 date) – Počátek platnosti (povinné)
  - `valid_to` (string, ISO 8601 date, nebo null) – Konec platnosti (volitelné)

**Příklad:**
```json
"applicability": {
  "specialties": ["101", "102", "104", "107", "201", "305", "603"],
  "valid_from": "2026-01-01",
  "valid_to": null
}
```

**Speciální hodnoty:**
- `"specialties": ["all"]` – Platí pro všechny odbornosti
- `"valid_to": null` – Bez omezení do budoucna

### related_units
- **Typ**: `array of strings` (UUIDs)
- **Povinné**: Ne
- **Popis**: ID související znalostních jednotek
- **Příklad**: `["ku-002-hbmin-2026", "ku-003-maxu-2026", "ku-004-bonifikace-2026"]`

### tags
- **Typ**: `array of strings`
- **Povinné**: Ne
- **Popis**: Klíčová slova pro vyhledávání a kategorizaci
- **Příklad**: `["úhrada", "bod", "SAS", "2026", "základní-sazba"]`

## Typy znalostních jednotek – Detaily

### Rule (Pravidlo)

Pravidlo je znalostní jednotka, která popisuje vztah mezi podmínkou a důsledkem.

**Struktura:**
- Podmínka (když...)
- Důsledek (pak...)
- Dopad (co to znamená)
- Příklad (jak se to počítá)

**Příklad:**
```json
{
  "id": "ku-001-bod-sas-2026",
  "type": "rule",
  "title": "Jednotná hodnota bodu pro ambulantní specialisty (SAS) v roce 2026",
  "content": {
    "condition": "Poskytovatel je ambulantní specialista (SAS) a poskytuje hrazené služby dle bodu 2 vyhlášky",
    "consequence": "Základní hodnota bodu = 0,98 Kč",
    "impact": "Zjednodušení výpočtu úhrad, jednotná sazba pro všechny SAS",
    "calculation_example": "Pokud lékař vykazuje 1000 bodů měsíčně: 1000 × 0,98 = 980 Kč"
  }
}
```

### Exception (Výjimka)

Výjimka popisuje situaci, kdy se obecné pravidlo neuplatňuje.

**Struktura:**
- Výjimka (co je vyjmuto)
- Vyjmuto z (která pravidla se neuplatňují)
- Stále podléhá (která pravidla se stále uplatňují)
- Změna (jak se to změnilo)

**Příklad:**
```json
{
  "id": "ku-008-vyjimky-regulace-2026",
  "type": "exception",
  "title": "Výjimky z regulací pro vybrané odbornosti v roce 2026",
  "content": {
    "exception": "Odbornosti 305, 306, 308, 309, 350, 355, 360, 370, 920, 922, 935",
    "exempted_from": ["Regulace B.3 (předpisy)", "Regulace B.4 (vykazování)"],
    "still_subject_to": ["Regulace B.2 (výkony)"],
    "change_from_2025": "V roce 2025 byly tyto odbornosti vyjmuty ze všech regulací B.2, B.3, B.4. V roce 2026 jsou vyjmuty pouze z B.3 a B.4."
  }
}
```

### Risk (Riziko)

Riziko popisuje potenciální negativní dopad určité situace.

**Struktura:**
- Riziko (co se může stát)
- Postihuje (koho)
- Úroveň dopadu (vysoké/střední/nízké)
- Zmírnění (jak se vyhnout)

**Příklad:**
```json
{
  "id": "ku-009-riziko-nizka-hbmin",
  "type": "risk",
  "title": "Riziko nižší úhrady v důsledku snížené HBmin v roce 2026",
  "content": {
    "risk": "Snížená HBmin (0,90 Kč) → nižší PURO → nižší úhrada",
    "affected_providers": "Poskytovatelé s nízkými nebo průměrnými výkony",
    "impact_level": "Vysoké (může znamenat 5-15% snížení úhrad)",
    "mitigation": "Zvýšit počet výkonů, zvýšit počet nových pacientů, splňovat bonifikační podmínky"
  }
}
```

### Anti-pattern (Anti-pattern)

Anti-pattern popisuje typickou chybu nebo špatné chování a jeho důsledky.

**Struktura:**
- Chyba (co se dělá špatně)
- Důsledek (co se stane)
- Proč se to stává (příčiny)
- Dopad (jaké jsou následky)
- Prevence (jak se tomu vyhnout)

**Příklad:**
```json
{
  "id": "ku-010-anti-pattern-nizka-puro",
  "type": "anti_pattern",
  "title": "Anti-pattern: Ordinace s nízkou PURO a bez nových pacientů",
  "content": {
    "pattern": "Nízká PURO + Bez nových pacientů",
    "consequence": "Nižší úhrada, bez bonifikace, postupné snižování příjmů",
    "why_it_happens": "Lékaři se zaměřují na stávající pacienty, neinvestují do rozvoje",
    "impact": "Může vést až k 20-30% snížení příjmů oproti konkurenci",
    "prevention": "Aktivní marketing, přijetí nových pacientů, zvýšení PURO, splnění bonifikačních podmínek"
  }
}
```

### Condition (Podmínka)

Podmínka popisuje kritérium nebo práh, který musí být splněn.

**Struktura:**
- Podmínka (co se vyžaduje)
- Požadavek (co přesně)
- Kombinace (co dalšího)
- Dopad (jaký je důsledek)

**Příklad:**
```json
{
  "id": "ku-005-ordinacni-hodiny-2026",
  "type": "condition",
  "title": "Ordinační hodiny jako podmínka pro vyšší bonifikaci v roce 2026",
  "content": {
    "condition": "Poskytovatel chce získat vyšší bonifikaci (+0,04 Kč/bod)",
    "requirement": "Musí splnit minimální počet ordinačních hodin (dle konkrétní odbornosti)",
    "combined_with": "Zároveň musí ošetřit ≥10% nových pojištěnců (15% u operačních oborů)",
    "impact": "Poskytovatelé bez dostatečných ordinačních hodin nemohou získat vyšší bonus"
  }
}
```

### Definition (Definice)

Definice vysvětluje důležitý termín nebo koncept.

**Struktura:**
- Termín (co se definuje)
- Definice (vysvětlení)
- Kontext (kde se používá)
- Důležitost (proč je důležité)

## Validace

Všechny znalostní jednotky musí splňovat JSON schéma v [`schemas/knowledge_unit.schema.json`](../schemas/knowledge_unit.schema.json).

Validaci lze provést:

```bash
python3 scripts/validate.py data/pilot_knowledge_units.jsonl
```

## Příklady

Příklady znalostních jednotek naleznete v:
- `data/pilot_knowledge_units.jsonl` – Pilotní dataset
- `docs/examples.md` – Detailní příklady

## Verze

- **v1.0** (14.12.2025) – Iniciální verze datového modelu
