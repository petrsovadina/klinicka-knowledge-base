---
license: mit
task_categories:
- question-answering
- text-generation
language:
- cs
tags:
- healthcare
- czech-republic
- ambulatory-care
- reimbursement
- decision-support
- knowledge-base
- rag
- mvp
size_categories:
- n<1K
---

# Klinická Znalostní Báze – Ambulantní Zdravotní Péče v ČR

> **MVP verze 1.0.0** | 669 znalostních jednotek | RAG skóre 0.730

## Dataset Summary

Strukturovaná znalostní báze zaměřená na ekonomiku, úhrady a provoz ambulantní zdravotní péče v České republice. Dataset obsahuje atomické znalostní jednotky (pravidla, výjimky, rizika, anti-patterny, definice, porovnání) extrahované z úhradových vyhlášek, metodik pojišťoven a praktických článků.

**Účel**: Poskytnout AI decision-support vrstvu, která pomáhá lékařům a provozovatelům ambulancí rozumět ekonomickým, úhradovým a provozním důsledkům jejich rozhodnutí.

### MVP Status (2026-02-03)

| Metrika | Hodnota |
|---------|---------|
| **Znalostní jednotky** | 669 |
| **Domény** | 5 (úhrady, provoz, compliance, finanční rizika, legislativa) |
| **RAG skóre (průměr)** | 0.730 |
| **Úspěšnost >0.7** | 60% |
| **Úspěšnost >0.5** | 92% |

## Dataset Structure

### Data Instances

Každá instance je znalostní jednotka ve formátu JSON:

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

### Data Fields

- **id** (string): Jedinečný identifikátor
- **type** (string): Typ jednotky (`rule`, `exception`, `risk`, `anti_pattern`, `condition`, `definition`, `comparison`)
- **domain** (string): Doména (`uhrady`, `provoz`, `compliance`, `financni-rizika`, `legislativa`)
- **title** (string): Název jednotky
- **description** (string): Detailní popis
- **version** (string): Rok úhradové vyhlášky
- **source** (object): Zdroj informace
- **content** (object): Strukturovaný obsah (liší se dle typu)
- **applicability** (object): Aplikovatelnost (odbornosti, platnost)
- **related_units** (array): ID souvisejících jednotek
- **tags** (array): Klíčová slova

### Data Splits

MVP verze obsahuje 669 znalostních jednotek. Dataset není rozdělen na train/test/validation, protože je určen primárně pro RAG retrieval.

## Dataset Creation

### Source Data

- **InfoProLekare.cz**: Praktické články o úhradách a provozu (40+ heuristik)
- **Úhradová vyhláška MZ ČR 2025/2026**: Oficiální legislativa
- **Metodiky pojišťoven**: VZP ČR, ZP MV ČR, OZP, ČPZP
- **Zdravotně pojistné plány**: ZP MV ČR 2026

### Pokrytí domén (MVP)

| Doména | Jednotek | Procento |
|--------|----------|----------|
| **Úhrady** | 280+ | 42% |
| **Provoz** | 150+ | 22% |
| **Compliance** | 100+ | 15% |
| **Finanční rizika** | 80+ | 12% |
| **Legislativa** | 60+ | 9% |

### Annotation Process

Znalostní jednotky byly extrahovány kombinací manuálního zpracování a LLM-assisted extrakce (GPT-4.1-nano). Každá jednotka byla validována proti JSON schématu a propojená s souvisejícími jednotkami.

## Considerations for Using the Data

### Social Impact

Dataset pomáhá lékařům a provozovatelům ambulancí:
- Rozumět ekonomickým dopadům rozhodnutí
- Vyhnout se typickým chybám
- Optimalizovat provoz praxe

### Discussion of Biases

Dataset je zaměřen na českou ambulantní péči a nemusí být aplikovatelný na jiné země nebo segmenty zdravotnictví.

### Other Known Limitations

- MVP verze zaměřena primárně na úhradovou vyhlášku 2025/2026
- Pokrytí pojišťoven: VZP ČR, ZP MV ČR, OZP, ČPZP (chybí VOZP, ZP Škoda)
- Srovnávací dotazy mezi roky dosahují nižšího skóre (průměr 0.589)
- Vyžaduje průběžnou aktualizaci při změnách legislativy

## Additional Information

### Dataset Curators

Manus AI

### Licensing Information

MIT License

### Citation Information

```
@misc{klinicka-knowledge-base-2026,
  title={Klinická Znalostní Báze – Ambulantní Zdravotní Péče v ČR},
  author={Manus AI},
  year={2026},
  version={1.0.0-MVP},
  url={https://github.com/petrsovadina/klinicka-knowledge-base}
}
```

### Version History

| Verze | Datum | Jednotek | Změny |
|-------|-------|----------|-------|
| **1.0.0-MVP** | 2026-02-03 | 669 | MVP release, RAG API, deployment docs |
| 0.3.0 | 2026-01-03 | 456 | ZP MV ČR data |
| 0.2.0 | 2025-12-28 | 409 | VZP metodiky |
| 0.1.0 | 2025-12-14 | 15 | Pilotní dataset |

### Contributions

Přispívat můžete na [GitHub repozitáři](https://github.com/petrsovadina/klinicka-knowledge-base).
