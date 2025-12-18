# RAG MVP: Analýza Mezer a Doporučení

**Datum analýzy**: 14. prosince 2025  
**Verze datasetu**: `phase2_core_2025` (409 jednotek)

---

## 1. Shrnutí Výsledků Testu

Provedli jsme testování RAG MVP s 10 reálnými dotazy lékařů. Cílem bylo ověřit schopnost AI smysluplně odpovídat na základě existující znalostní báze.

### Klíčové Metriky

-   **Průměrné skóre top výsledku**: 0.691
-   **Počet dotazů s top skóre > 0.7**: 6/10 (60%)
-   **Počet dotazů s top skóre < 0.5**: 1/10 (10%)
-   **Počet dotazů bez přímé odpovědi**: 1/10 (10%)

### Celkové Hodnocení

-   ✅ **Velmi dobrá relevance**: Pro 6 z 10 dotazů AI našla vysoce relevantní znalostní jednotky (skóre > 0.7) a poskytla přesnou, citovanou odpověď.
-   ✅ **Dobrá schopnost syntézy**: AI dokázala zkombinovat informace z více zdrojů do koherentní odpovědi (viz dotaz na rizika při převzetí ordinace).
-   ✅ **Bezpečnost**: AI se držela instrukcí a nenavrhovala konkrétní vykazování, pouze vysvětlovala pravidla.
-   ⚠️ **Problémy s granularitou**: U obecných dotazů (např. rozdíly v úhradách) AI našla relevantní jednotky, ale odpověď byla příliš obecná.
-   ❌ **Slepá místa**: U dotazu na hodnotu bodu 0,94 Kč AI správně identifikovala, že odpověď v kontextu není, což odhalilo mezeru v datech.

---

## 2. Detailní Analýza Dotazů

| Dotaz | Top Skóre | Kvalita Odpovědi | Analýza a Doporučení |
|---|---|---|---|
| **Co se stane, když překročím PURO v roce 2025?** | 0.814 | ✅ Výborná | Přímá odpověď, správně cituje regulaci. **Není třeba akce.** |
| **Jaké mám riziko při změně IČZ?** | 0.927 | ✅ Výborná | Perfektní syntéza z více jednotek, jasně vysvětluje rizika. **Není třeba akce.** |
| **Jak se liší úhrady oproti minulému roku?** | 0.538 | ⚠️ Průměrná | AI našla obecné informace o změnách, ale chybí konkrétní srovnání. **Doporučení**: Vytvořit srovnávací jednotky (např. `comparison` type). |
| **Co je MAXÚ a jak funguje?** | 0.816 | ✅ Výborná | Přímá a přesná definice. **Není třeba akce.** |
| **Jaké jsou bonifikace za ordinační hodiny?** | 0.791 | ✅ Výborná | Přesná odpověď, cituje správné pravidlo. **Není třeba akce.** |
| **Co je předběžná měsíční úhrada?** | 0.713 | ✅ Výborná | Jasná definice a vysvětlení. **Není třeba akce.** |
| **Jaká jsou rizika při převzetí ordinace?** | 0.927 | ✅ Výborná | Znovu skvělá syntéza, pokrývá více aspektů. **Není třeba akce.** |
| **Co znamená hodnota bodu 0,94 Kč?** | 0.590 | ❌ Nedostatečná | AI správně identifikovala, že odpověď nezná. **Doporučení**: Přidat data z úhradových dodatků, kde jsou tyto hodnoty specifikovány. |
| **Jak funguje regulace na léky?** | 0.711 | ✅ Výborná | Přesné vysvětlení zmírnění regulace. **Není třeba akce.** |
| **Co je koeficient navýšení a jak ho získám?** | 0.728 | ✅ Výborná | Přesná definice a podmínky. **Není třeba akce.** |

---

## 3. Identifikované Mezery a Jejich Priorita

### 1. Chybějící Specifické Hodnoty (Priorita: Vysoká)

-   **Problém**: AI nezná konkrétní hodnoty bodu nebo koeficienty, které jsou uvedeny v úhradových dodatcích jednotlivých pojišťoven (např. hodnota bodu 0,94 Kč).
-   **Dopad**: Omezuje praktickou použitelnost pro lékaře, kteří potřebují znát přesná čísla.
-   **Řešení**: **Zpracovat úhradové dodatky všech 7 pojišťoven** (jak je plánováno ve Fázi 3). Zaměřit se na extrakci konkrétních číselných hodnot.

### 2. Nedostatečná Srovnávací Analýza (Priorita: Střední)

-   **Problém**: AI nedokáže dobře odpovídat na srovnávací dotazy (např. "Jak se liší úhrady oproti minulému roku?").
-   **Dopad**: Uživatel nedostane komplexní přehled, pouze útržky informací.
-   **Řešení**:
    1.  **Vytvořit nový typ znalostní jednotky**: `comparison`, která bude explicitně srovnávat dva nebo více parametrů (např. úhrady 2025 vs. 2026).
    2.  **Zpracovat historická data**: Přidat data z úhradových vyhlášek 2023 a 2024 pro umožnění meziročního srovnání.

### 3. Obecnost Některých Jednotek (Priorita: Nízká)

-   **Problém**: Některé znalostní jednotky jsou příliš obecné a neposkytují dostatek detailů.
-   **Dopad**: Odpovědi mohou být vágní.
-   **Řešení**: Během další extrakce se zaměřit na **vyšší granularitu** a rozdělovat komplexní pravidla na menší, specifičtější jednotky.

---

## 4. Doporučení pro Další Kroky

**1. Okamžitě pokračovat s Fází 3 (Rozšíření Datasetu)**

-   Testování potvrdilo, že **největší hodnotu nyní přinese rozšíření datasetu**, nikoliv optimalizace RAG pipeline.
-   **Priorita #1**: Zpracovat **úhradové dodatky všech 7 pojišťoven**. Tím se vyřeší největší slepé místo (konkrétní hodnoty).
-   **Priorita #2**: Zpracovat **odborné články z InfoProLekare.cz**. Tím se přidá praktický kontext a pokryjí se další rizika a anti-patterny.

**2. Vytvořit Srovnávací Jednotky (`comparison`)

-   Během extrakce aktivně vyhledávat a vytvářet jednotky, které srovnávají parametry mezi různými obdobími nebo pojišťovnami.

**3. Iterativně Testovat

-   Po každém významnějším rozšíření datasetu (např. po zpracování VZP) znovu spustit test s 10 dotazy a sledovat zlepšení.

---

## Závěr

RAG MVP je **životaschopný a funkční**. Znalostní báze již nyní poskytuje hodnotné odpovědi na většinu dotazů. Testování jasně ukázalo, že **strategie rozšíření datasetu je správná** a přinese největší užitek. Není třeba se zdržovat optimalizací RAG, klíčem k úspěchu je nyní **systematická a kvalitní extrakce dalších dat**.

**Další krok**: Zahájit implementaci Fáze 3 dle schváleného plánu, s prioritou na úhradové dodatky pojišťoven.
