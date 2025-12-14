# Příspěvky do Klinické Znalostní Báze

Děkujeme za zájem o přispívání do tohoto projektu! Tato příručka vám pomůže pochopit, jak správně přispívat.

## Typy příspěvků

### 1. Nové znalostní jednotky

Přidejte nové znalostní jednotky zaměřené na ekonomiku, úhrady a provoz ambulantní péče.

**Postup:**
1. Vytvořte nový JSON objekt dle schématu v [`schemas/knowledge_unit.schema.json`](schemas/knowledge_unit.schema.json)
2. Přidejte do příslušného souboru v `data/[year]/[domain]/`
3. Zajistěte validaci: `python3 scripts/validate.py`
4. Otevřete pull request s popisem

**Příklad:**
```json
{
  "id": "ku-XXX-popis",
  "type": "rule|exception|risk|anti_pattern|condition|definition",
  "domain": "uhrady|provoz|compliance|financni-rizika|legislativa",
  "title": "Jasný a stručný název",
  "description": "Detailní popis znalostní jednotky",
  "version": "2026",
  "source": {
    "name": "Název zdroje",
    "url": "https://...",
    "retrieved_at": "2025-12-14T00:00:00Z"
  },
  "content": {
    "condition": "...",
    "consequence": "...",
    "impact": "..."
  },
  "applicability": {
    "specialties": ["001", "002", "..."],
    "valid_from": "2026-01-01",
    "valid_to": null
  },
  "related_units": ["ku-XXX", "ku-YYY"],
  "tags": ["tag1", "tag2"]
}
```

### 2. Opravy a vylepšení

Opravujte chyby, nejasnosti nebo doplňujte chybějící informace v existujících jednotkách.

**Postup:**
1. Identifikujte problém
2. Proveďte opravu
3. Zajistěte validaci
4. Otevřete pull request s vysvětlením

### 3. Aktualizace zdrojů

Aktualizujte informace z měnících se zdrojů (úhradové vyhlášky, metodiky pojišťoven).

**Postup:**
1. Ověřte změnu v původním zdroji
2. Aktualizujte příslušné znalostní jednotky
3. Změňte `version` a `retrieved_at`
4. Otevřete pull request

## Standardy a konvence

### Pojmenování ID

```
ku-[pořadí]-[slug]
```

Příklady:
- `ku-001-bod-sas-2026`
- `ku-015-kategorie-pece-do-15-let`
- `ku-042-riziko-nizka-puro`

### Domény

- **uhrady**: Úhradové mechanismy, výpočty, bonifikace, penalizace
- **provoz**: Provozní rozhodování, ordinační hodiny, pacienti
- **compliance**: Legislativa, smluvní povinnosti, regulace
- **financni-rizika**: Finanční rizika, anti-patterny, sankce
- **legislativa**: Zákony, vyhlášky, právní rámec

### Typy znalostních jednotek

- **rule**: Pravidlo (podmínka → důsledek)
- **exception**: Výjimka (pravidlo + výjimka)
- **risk**: Riziko (situace → potenciální dopad)
- **anti_pattern**: Anti-pattern (chyba → sankce/problém)
- **condition**: Podmínka (kritérium + práh)
- **definition**: Definice (vysvětlení termínu)

### Struktura obsahu

Obsah se liší dle typu:

**Rule:**
```json
"content": {
  "condition": "Když...",
  "consequence": "Pak...",
  "impact": "Dopad je...",
  "calculation_example": "Příklad: ..."
}
```

**Risk:**
```json
"content": {
  "risk": "Riziko je...",
  "affected_providers": "Postihuje...",
  "impact_level": "Vysoké|Střední|Nízké",
  "mitigation": "Lze se vyhnout..."
}
```

**Anti-pattern:**
```json
"content": {
  "pattern": "Chyba je...",
  "consequence": "Důsledek je...",
  "why_it_happens": "Stává se, protože...",
  "impact": "Dopad: ...",
  "prevention": "Lze zabránit..."
}
```

### Odbornosti

Používejte oficiální kódy dle MZ ČR:

| Kód | Obor |
|-----|------|
| 001 | Všeobecné praktické lékařství |
| 002 | Praktické lékařství pro děti a dorost |
| 101 | Vnitřní lékařství |
| 305 | Psychiatrie |
| 603 | Gynekologie a porodnictví |
| 706 | Urologie |
| 902 | Fyzioterapeut |

Viz `data/specialties.json` pro úplný seznam.

## Validace

Před odesláním pull requestu zajistěte validaci:

```bash
# Validace jednoho souboru
python3 scripts/validate.py data/pilot_knowledge_units.jsonl

# Validace všech souborů
python3 scripts/validate.py data/
```

## Pull Request Proces

1. **Fork** repozitáře
2. **Vytvořte branch**: `git checkout -b feature/nove-jednotky`
3. **Proveďte změny** a validujte
4. **Commit**: `git commit -m "Přidáno: 5 nových znalostních jednotek o PURO"`
5. **Push**: `git push origin feature/nove-jednotky`
6. **Pull Request**: Otevřete PR s jasným popisem

### Popis PR

```markdown
## Popis
Přidávám 5 nových znalostních jednotek zaměřených na PURO a optimalizaci ordinace.

## Typ
- [ ] Nové jednotky
- [ ] Oprava chyby
- [ ] Aktualizace zdroje

## Kontrola
- [ ] Validace prošla bez chyb
- [ ] Všechny jednotky mají zdroj
- [ ] Jsou propojeny související jednotky
- [ ] Popis je jasný a bez chyb

## Zdroje
- Úhradová vyhláška 2026
- InfoProLekare.cz (14.12.2025)
```

## Otázky a Diskuse

Máte otázky? Otevřete diskusi v sekci "Discussions" nebo kontaktujte maintainery.

## Kodex chování

Prosím, buďte respektfulní a konstruktivní. Cílem je vytvořit užitečný zdroj pro všechny.

---

Děkujeme za přispívání! 🙏
