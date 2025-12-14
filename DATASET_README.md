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
size_categories:
- n<1K
---

# Klinická Znalostní Báze – Ambulantní Zdravotní Péče v ČR

## Dataset Summary

Strukturovaná znalostní báze zaměřená na ekonomiku, úhrady a provoz ambulantní zdravotní péče v České republice. Dataset obsahuje atomické znalostní jednotky (pravidla, výjimky, rizika, anti-patterny) extrahované z úhradových vyhlášek, metodik pojišťoven a praktických článků.

**Účel**: Poskytnout AI decision-support vrstvu, která pomáhá lékařům a provozovatelům ambulancí rozumět ekonomickým, úhradovým a provozním důsledkům jejich rozhodnutí.

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
- **type** (string): Typ jednotky (`rule`, `exception`, `risk`, `anti_pattern`, `condition`, `definition`)
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

Pilotní verze obsahuje 15 znalostních jednotek bez rozdělení na train/test/validation.

## Dataset Creation

### Source Data

- **InfoProLekare.cz**: Praktické články o úhradách a provozu
- **Úhradová vyhláška MZ ČR**: Oficiální legislativa
- **Metodiky pojišťoven**: VZP, ZP MV, OZP, ČPZP, RBP

### Annotation Process

Znalostní jednotky byly manuálně extrahovány a strukturovány podle JSON schématu. Každá jednotka byla validována a propojená s souvisejícími jednotkami.

## Considerations for Using the Data

### Social Impact

Dataset pomáhá lékařům a provozovatelům ambulancí:
- Rozumět ekonomickým dopadům rozhodnutí
- Vyhnout se typickým chybám
- Optimalizovat provoz praxe

### Discussion of Biases

Dataset je zaměřen na českou ambulantní péči a nemusí být aplikovatelný na jiné země nebo segmenty zdravotnictví.

### Other Known Limitations

- Pilotní verze obsahuje pouze 15 jednotek
- Zaměřeno primárně na úhradovou vyhlášku 2026
- Vyžaduje průběžnou aktualizaci

## Additional Information

### Dataset Curators

Manus AI

### Licensing Information

MIT License

### Citation Information

```
@misc{klinicka-knowledge-base-2025,
  title={Klinická Znalostní Báze – Ambulantní Zdravotní Péče v ČR},
  author={Manus AI},
  year={2025},
  url={https://github.com/petrsovadina/klinicka-knowledge-base}
}
```

### Contributions

Přispívat můžete na [GitHub repozitáři](https://github.com/petrsovadina/klinicka-knowledge-base).
