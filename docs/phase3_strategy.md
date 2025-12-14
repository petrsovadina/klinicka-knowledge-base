# Fáze 3: Extrakční Strategie a Prioritizace

**Datum plánování**: 14. prosince 2025  
**Status**: Připraveno k implementaci

---

## Cíle Fáze 3

1.  **Rozšířit znalostní bázi** o 300–460 nových jednotek.
2.  **Pokrýt metodiky** všech 7 hlavních zdravotních pojišťoven.
3.  **Zpracovat odborné články** z praktických zdrojů (InfoProLekare.cz).
4.  **Zvýšit pokrytí** specifických odborností a rizikových oblastí.
5.  **Vytvořit robustní a diverzifikovaný dataset** pro AI decision-support.

---

## Extrakční Strategie

### 1. Metodika Extrakce

-   **Nástroj**: `llm_extract_v2.py` (optimalizovaná verze)
-   **Model**: `gpt-4.1-nano` (rychlý, efektivní)
-   **Velikost chunků**: 12,000 znaků
-   **Průběžný zápis**: Ano
-   **Paralelizace**: Spouštět více extrakcí současně pro zrychlení.

### 2. Zpracování Zdrojů

-   **PDF dokumenty**: Stáhnout a zpracovat pomocí `pdftotext`.
-   **Webové články**: Použít `browser_navigate` a extrahovat textový obsah.
-   **Metadata**: Pro každý zdroj vytvořit metadata (název, URL, rok, typ).

### 3. Validace a Sloučení

-   **Nástroj**: `merge_and_validate.py`
-   **Proces**:
    1.  Sloučit všechny extrahované soubory.
    2.  Validovat proti JSON schématu.
    3.  Detekovat a opravit duplicitní ID.
    4.  Opravit běžné chyby (např. špatné domény).
    5.  Vygenerovat statistiky pokrytí.

---

## Prioritizace a Časový Plán (8 týdnů)

### Týden 1–2: VZP Metodiky a Úhradové Dodatky

-   **Cíl**: 115–170 jednotek
-   **Priorita**: Velmi vysoká
-   **Zdroje**:
    1.  Metodika pro pořizování a předávání dokladů (VZP)
    2.  Pravidla pro vyhodnocování dokladů (VZP)
    3.  Průvodce financováním paušálně hrazených poskytovatelů (VZP)
    4.  Vzorové typové smlouvy (VZP)
    5.  Finanční vypořádání předběžných úhrad (VZP)

### Týden 3–4: Odborné Články (InfoProLekare.cz)

-   **Cíl**: 110–165 jednotek
-   **Priorita**: Vysoká
-   **Zdroje**:
    1.  Přehled úhradových dodatků 2025 (všechny pojišťovny)
    2.  Pracujete zadarmo? Temná strana úhradové vyhlášky 2026
    3.  Úhradová vyhláška 2026 pro VPL a PLDD
    4.  Úhradová vyhláška 2026 pro gynekology
    5.  Bonifikace za ordinační hodiny 2025 (VZP)

### Týden 5–6: Metodiky Ostatních Pojišťoven

-   **Cíl**: 75–125 jednotek
-   **Priorita**: Střední
-   **Zdroje**:
    1.  Dodatek AS/2025 (ZP MV ČR)
    2.  Úhradové dodatky 2025 (ZP MV ČR)
    3.  Ambulantní specialisté - Aktuální informace (OZP)
    4.  Úhradové dodatky (ČPZP, RBP, VoZP, ZPŠ)

### Týden 7–8: Doplňkové Zdroje a Finalizace

-   **Cíl**: Flexibilní (dle potřeby)
-   **Priorita**: Nízká
-   **Zdroje**:
    1.  Zbývající datová rozhraní VZP
    2.  Zbývající články z InfoProLekare.cz (stomatologie, dotace)
    3.  Legislativní rámec (zákony 48/1997, 372/2011)
    4.  Kompletní validace, deduplikace a finální publikace.

---

## Očekávané Výsledky Fáze 3

| Metrika | Cíl |
|---|---|
| **Celkový počet jednotek** | 700–850 (409 + 300–460) |
| **Pokrytí pojišťoven** | 7/7 (VZP, ZP MV, OZP, ČPZP, RBP, VoZP, ZPŠ) |
| **Pokrytí odborností** | 15+ (VPL, PLDD, GYN, KAR, LOG, FYZ, STO, ...) |
| **Pokrytí témat** | Úhrady, regulace, bonifikace, smlouvy, rizika, anti-patterny |
| **Validita** | 98%+ |

---

## Rizika a Mitigace

### Riziko 1: Nízká kvalita extrakce z některých zdrojů
-   **Mitigace**: Upravit prompt pro specifické dokumenty, provést manuální review a opravy.

### Riziko 2: Změny v URL adresách nebo struktuře webů
-   **Mitigace**: Pravidelně aktualizovat skripty pro stahování, mít záložní kopie dokumentů.

### Riziko 3: Časová náročnost extrakce
-   **Mitigace**: Paralelizovat extrakce, využít rychlejší model `gpt-4.1-nano`, optimalizovat chunky.

---

**Status**: ✅ Připraveno k implementaci
