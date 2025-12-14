# Klinická Znalostní Báze – Ambulantní Zdravotní Péče v ČR

Strukturovaná znalostní báze a AI decision-support vrstva zaměřená na ekonomiku, úhrady a provoz ambulantní zdravotní péče v České republice.

## Cíl projektu

Nejde o další informační web ani obecného chatbota. Jde o systematické zachycení a strukturování provozního know-how, které dnes existuje roztříštěně v článcích, vyhláškách a praktických zkušenostech – a jeho zpřístupnění ve formě, se kterou může pracovat umělá inteligence.

### Proč to děláme?

1. **Aby lékaři a provozovatelé praxí rozuměli důsledkům svých rozhodnutí** – vidět rizika dopředu, pochopit ekonomické a provozní dopady, vyhnout se typickým chybám.

2. **Aby AI ve zdravotnictví pracovala s realitou, ne s teorií** – doplnit AI o znalost úhradových mechanismů, smluvních vztahů, regulačních limitů a praktických heuristik.

3. **Aby vznikl decision-support nástroj, ne zdravotnický prostředek** – vysvětlovat pravidla, upozorňovat na rizika, podporovat informované rozhodování, zůstat mimo MDR.

4. **Aby vznikla sdílená znalostní vrstva pro více produktů** – dlouhodobý strategický asset napájející klinického AI asistenta, AI audit, dokumentaci a reporting.

## Struktura repozitáře

```
klinicka-knowledge-base/
├── README.md                          # Tento soubor
├── CONTRIBUTING.md                    # Příspěvky a standardy
├── schemas/
│   └── knowledge_unit.schema.json     # JSON schéma pro validaci znalostních jednotek
├── data/
│   ├── pilot_knowledge_units.jsonl    # Pilotní dataset (15 znalostních jednotek)
│   ├── sources.json                   # Registr zdrojů
│   └── [year]/                        # Znalostní jednotky dle roku úhradové vyhlášky
│       ├── uhrady/                    # Úhradové pravidla
│       ├── provoz/                    # Provozní rozhodování
│       ├── compliance/                # Legislativa a compliance
│       └── financni-rizika/           # Finanční rizika a anti-patterny
├── docs/
│   ├── model.md                       # Popis datového modelu
│   ├── sources.md                     # Popis zdrojů a jejich aktualizace
│   └── examples.md                    # Příklady znalostních jednotek
└── scripts/
    ├── validate.py                    # Validace JSON schématu
    ├── export.py                      # Export do různých formátů
    └── update_sources.py              # Automatická aktualizace zdrojů
```

## Datový model

Znalostní jednotka je atomická, strojově zpracovatelná jednotka informace. Každá jednotka má:

- **ID**: Jedinečný identifikátor (UUID)
- **Typ**: `rule` (pravidlo), `exception` (výjimka), `risk` (riziko), `anti_pattern` (anti-pattern), `condition` (podmínka), `definition` (definice)
- **Doména**: `uhrady`, `provoz`, `compliance`, `financni-rizika`, `legislativa`
- **Obsah**: Strukturovaný dle typu (podmínka → důsledek, riziko → dopad, atd.)
- **Zdroj**: Odkaz na původní dokument s datem stažení
- **Aplikovatelnost**: Odbornosti, platnost, relevance
- **Vztahy**: Propojení s dalšími znalostními jednotkami

Viz [`schemas/knowledge_unit.schema.json`](schemas/knowledge_unit.schema.json) pro detailní specifikaci.

## Pilotní dataset

Pilotní dataset (`data/pilot_knowledge_units.jsonl`) obsahuje 15 klíčových znalostních jednotek zaměřených na:

- **Úhradové mechanismy 2026**: Hodnota bodu, PURO, MAXÚ, bonifikace, penalizace
- **Regulační omezení**: Výjimky pro vybrané odbornosti
- **Finanční rizika**: Skrytá rizika při převzetí ordinace, nízká PURO
- **Provozní rozhodování**: Checklist kupujícího, optimalizace PURO

Příklad znalostní jednotky:

```json
{
  "id": "ku-001-bod-sas-2026",
  "type": "rule",
  "domain": "uhrady",
  "title": "Jednotná hodnota bodu pro ambulantní specialisty (SAS) v roce 2026",
  "description": "Od roku 2026 platí jednotná základní hodnota bodu pro hrazené služby ambulantních specialistů ve výši 0,98 Kč.",
  "version": "2026",
  "source": {
    "name": "Úhradová vyhláška 2026 - Ambulantní specialisté",
    "url": "https://www.infoprolekare.cz/uhradova-vyhlaska-2026-pro-ambulantni-specialisty",
    "retrieved_at": "2025-12-14T00:00:00Z"
  },
  "content": {
    "condition": "Poskytovatel je ambulantní specialista (SAS) a poskytuje hrazené služby dle bodu 2 vyhlášky",
    "consequence": "Základní hodnota bodu = 0,98 Kč",
    "impact": "Zjednodušení výpočtu úhrad, jednotná sazba pro všechny SAS",
    "calculation_example": "Pokud lékař vykazuje 1000 bodů měsíčně: 1000 × 0,98 = 980 Kč"
  },
  "applicability": {
    "specialties": ["101", "102", "104", "107", ...],
    "valid_from": "2026-01-01",
    "valid_to": null
  },
  "related_units": ["ku-002-hbmin-2026", "ku-003-maxu-2026", "ku-004-bonifikace-2026"],
  "tags": ["úhrada", "bod", "SAS", "2026", "základní-sazba"]
}
```

## Zdroje

Znalostní báze čerpá z následujících zdrojů:

| Zdroj | Typ | Frekvence aktualizace |
|-------|-----|----------------------|
| [InfoProLekare.cz](https://www.infoprolekare.cz) | Praktické články | Průběžně |
| [Úhradová vyhláška MZ ČR](https://www.mzcr.cz/uredni-deska/) | Legislativa | Ročně |
| [Sbírka zákonů](https://www.zakonyprolidi.cz) | Legislativa | Průběžně |
| [VZP ČR - Metodiky](https://www.vzp.cz/poskytovatele) | Metodiky | Průběžně |
| [ZP MV ČR](https://www.zpmvcr.cz/poskytovatele) | Metodiky | Průběžně |
| [OZP](https://www.ozp.cz/poskytovatele) | Metodiky | Průběžně |
| [ČPZP](https://www.cpzp.cz/poskytovatele) | Metodiky | Průběžně |
| [RBP](https://www.rbp213.cz/poskytovatele) | Metodiky | Průběžně |

## Příspěvky

Přispívat můžete přidáním nových znalostních jednotek, opravou existujících nebo aktualizací zdrojů. Viz [`CONTRIBUTING.md`](CONTRIBUTING.md) pro detaily.

## Použití

### Validace znalostních jednotek

```bash
python3 scripts/validate.py data/pilot_knowledge_units.jsonl
```

### Export do různých formátů

```bash
python3 scripts/export.py data/pilot_knowledge_units.jsonl --format csv
python3 scripts/export.py data/pilot_knowledge_units.jsonl --format parquet
```

## Licence

Tento projekt je licencován pod [MIT License](LICENSE).

## Kontakt a feedback

Máte návrhy, chyby nebo chcete přispět? Otevřete issue nebo pull request.

---

**Poslední aktualizace**: 14. prosince 2025  
**Verze datasetu**: 0.1.0 (Pilot)  
**Počet znalostních jednotek**: 15
