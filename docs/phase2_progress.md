# Fáze 2: Průběžný Status Rozšíření Datasetu

**Datum zahájení**: 14. prosince 2025  
**Cíl**: Rozšířit dataset na 100+ znalostních jednotek  
**Aktuální stav**: V procesu

---

## Dokončené Extrakce

### ✅ Metodické doporučení PMÚ 2025
- **Soubor**: `metodicke_doporuceni_pmu_2025_extracted.jsonl`
- **Počet jednotek**: 6 (ku-016 až ku-021)
- **Velikost**: 7.6 KB
- **Témata**:
  - Individuální mechanismus měsíční předběžné úhrady
  - Výchozí předpoklady pro výpočet očekávané úhrady
  - Minimální výše předběžné měsíční úhrady
  - Riziko velkých přeplatků a nedoplatků
  - Možnost úpravy výše měsíční zálohy během roku
  - Zahrnění změn do výpočtu očekávané úhrady

**Status**: ✅ Dokončeno

---

## Probíhající Extrakce

### ⏳ Úhradová vyhláška 2025
- **Soubor**: `uhradova_vyhlaska_2025.pdf`
- **Velikost**: 2.28 MB, 785,988 znaků
- **Chunků**: 138
- **Status**: Běží (od 12:37, již 15+ minut)
- **Problém**: Výstupní soubor je prázdný, proces pravděpodobně zapisuje až na konci
- **Očekávaný výstup**: 40–60 jednotek

### ⏳ Odůvodnění k úhradové vyhlášce 2025
- **Soubor**: `oduvodneni_uhradova_vyhlaska_2025.pdf`
- **Velikost**: 0.63 MB
- **Status**: Běží (od 12:46)
- **Očekávaný výstup**: 15–25 jednotek

---

## Připravené Zdroje (Staženo)

1. ✅ Úhradová vyhláška 2026 (2.45 MB) - připraveno k extrakci
2. ✅ Úhradová vyhláška 2025 (2.28 MB) - extrakce probíhá
3. ✅ Odůvodnění k úhradové vyhlášce 2025 (0.63 MB) - extrakce probíhá
4. ✅ Metodické doporučení PMÚ 2025 (0.18 MB) - dokončeno

---

## Další Kroky

### Priorita 1: Dokončit probíhající extrakce
- Počkat na dokončení úhradové vyhlášky 2025
- Počkat na dokončení odůvodnění

### Priorita 2: Extrahovat z úhradové vyhlášky 2026
- Již máme 15 jednotek z manuální extrakce
- LLM extrakce přidá další 30–40 jednotek

### Priorita 3: Stáhnout a extrahovat články z InfoProLekare.cz
- Úhradová vyhláška 2026 pro VPL a PLDD
- Úhradová vyhláška 2026 pro gynekology
- Úhradová vyhláška 2026 pro fyzioterapeuty
- Úhradová vyhláška 2026 pro domácí péče
- Povinnosti příjemce dotace
- Transformace a prodej stomatologických ordinací
- Pracujete zadarmo? Temná strana úhradové vyhlášky 2026

### Priorita 4: Stáhnout metodiky pojišťoven
- VZP: Úhradové dodatky, metodiky
- ZP MV, OZP, ČPZP, RBP: Úhradové dodatky

---

## Technické Poznámky

### Problémy a Řešení

**Problém 1**: Původní model `gpt-4o` není podporován  
**Řešení**: Změněno na `gpt-4.1-mini`  
**Status**: ✅ Vyřešeno

**Problém 2**: Velké dokumenty (138 chunků) trvají velmi dlouho  
**Možné řešení**:
- Zvýšit velikost chunků (z 8000 na 12000 znaků)
- Použít paralelní zpracování (více procesů)
- Použít rychlejší model (`gpt-4.1-nano`)

**Problém 3**: Výstupní soubor je prázdný během běhu  
**Vysvětlení**: Skript zapisuje všechny jednotky najednou na konci  
**Možné zlepšení**: Zapisovat průběžně po každém chunku

---

## Očekávaný Výstup Fáze 2

| Zdroj | Očekávaný počet jednotek | Status |
|-------|-------------------------|--------|
| Metodické doporučení PMÚ 2025 | 6 | ✅ Dokončeno |
| Úhradová vyhláška 2025 | 40–60 | ⏳ Probíhá |
| Odůvodnění k úhradové vyhlášce 2025 | 15–25 | ⏳ Probíhá |
| Úhradová vyhláška 2026 (LLM) | 30–40 | ⏳ Připraveno |
| Články InfoProLekare.cz | 30–40 | ⏳ Připraveno |
| Metodiky pojišťoven | 20–30 | ⏳ Připraveno |
| **CELKEM** | **141–201** | **⏳ V procesu** |

---

**Poslední aktualizace**: 14. prosince 2025, 12:50  
**Aktuální počet jednotek**: 21 (15 pilotních + 6 nových)  
**Cílový počet**: 100+  
**Pokrok**: 21%
