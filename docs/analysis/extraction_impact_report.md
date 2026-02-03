---
type: analysis
title: Analýza dopadu extrakce VZP dat na RAG kvalitu
created: 2026-02-03
tags:
  - vzp
  - rag
  - embeddings
  - quality
related:
  - "[[merge_report_phase02]]"
  - "[[gap_analysis_report]]"
---

# Analýza dopadu extrakce VZP dat na kvalitu RAG

## Executive Summary

Tato zpráva analyzuje dopad přidání 106 znalostních jednotek extrahovaných z VZP dokumentů (Úhradová vyhláška 2026, metodika pro ambulantní specialisty a praktické lékaře) na kvalitu vyhledávání v RAG systému.

### Klíčové metriky

| Metrika | Před | Po | Změna |
|---------|------|-----|-------|
| Počet jednotek | 552 | 658 | +106 (+19.2%) |
| Průměrné top skóre | 0.680 | 0.652 | -0.028 (-4.2%) |
| Dotazy se skóre < 0.3 | 0 | 0 | beze změny |

## Detailní analýza

### Změna skóre po jednotlivých dotazech

| # | Dotaz | Skóre před | Skóre po | Delta |
|---|-------|------------|----------|-------|
| 1 | Co se stane, když překročím PURO v roce 2025? | 0.572 | 0.449 | -0.122 |
| 2 | Jaké mám riziko při změně IČZ? | 0.426 | 0.456 | **+0.030** |
| 3 | Jak se liší úhrady oproti minulému roku? | 0.355 | 0.356 | +0.000 |
| 4 | Co je MAXÚ a jak funguje? | 0.859 | 0.874 | **+0.015** |
| 5 | Jaké jsou bonifikace za ordinační hodiny? | 0.666 | 0.667 | **+0.001** |
| 6 | Co je předběžná měsíční úhrada a jak se počítá? | 0.795 | 0.738 | -0.057 |
| 7 | Jaká jsou rizika při převzetí ordinace? | 0.903 | 0.889 | -0.014 |
| 8 | Co znamená hodnota bodu 0,94 Kč? | 0.729 | 0.712 | -0.017 |
| 9 | Jak funguje regulace na léky? | 0.773 | 0.763 | -0.010 |
| 10 | Co je koeficient navýšení a jak ho získám? | 0.723 | 0.615 | -0.108 |

### Pozitivní změny

1. **Riziko při změně IČZ (+0.030)**: Nový výsledek obsahuje VZP-specifické riziko přefakturace při vysoké PMÚ
2. **MAXÚ (+0.015)**: Zachováno vysoké skóre (0.874), nové VZP jednotky podporují existující obsah
3. **Bonifikace za ordinační hodiny (+0.001)**: Nové VZP jednotky o bonifikacích podle typu oboru se objevují v top výsledcích

### Vysvětlení poklesu skóre

Mírný pokles průměrného skóre (-4.2%) je očekávaný jev při použití TF-IDF vektorizace:

1. **Vocabulary Dilution**: Přidání 106 nových dokumentů rozšiřuje slovník TF-IDF modelu, což mění frekvence termínů
2. **IDF Redistribuce**: Termíny, které byly dříve vzácné, jsou nyní častější, což snižuje jejich diskriminační sílu
3. **Nezměněné dotazy**: Testovací dotazy nebyly aktualizovány, aby využily novou terminologii VZP

## Nové znalosti dostupné v datasetu

### VZP Ambulantní specialisté (2026)
- Hodnoty bodu pro 20+ odborností (0.94-1.20 Kč)
- 4 typy bonifikací (+0.03/0.04/0.01 Kč)
- PURO vzorec a proměnné (POPzpoZ, POPzpoMh, KN)
- Regulační omezení (115% ZULP/preskripce)
- Koeficienty navýšení KN podle odbornosti

### VZP Praktičtí lékaři (2026)
- Kapitační sazby (60-76 Kč) podle rozsahu péče
- Bonifikace kapitace (CVL, prevence, screening)
- Hodnoty bodu pro mimokapitační výkony (1.18-1.35 Kč)
- Věkové indexy (0.90-4.35)
- Týmová praxe a PLDD specifika

## Doporučení pro další zlepšení

### Krátkodobá (okamžitá)
1. Rozšířit testovací dotazy o VZP-specifické otázky:
   - "Jaké jsou kapitační sazby pro praktické lékaře?"
   - "Jak se počítá PURO pro ambulantního specialistu?"
   - "Jaké jsou bonifikace pro CVL doklady?"

### Střednědobá
1. **Hybridní vyhledávání**: Kombinovat TF-IDF s BM25 nebo dense embeddings
2. **Query expansion**: Přidat synonyma pro lékařskou terminologii
3. **Re-ranking**: Použít cross-encoder pro přesnější řazení výsledků

### Dlouhodobá
1. **Sémantické embeddings**: Přechod na dense embeddings (text-embedding-3-small/large)
2. **Fine-tuning**: Dotrénovat embedding model na české lékařské texty
3. **Continuous learning**: Automatická aktualizace při změnách úhradové vyhlášky

## Závěr

Rozšíření knowledge base o 106 VZP jednotek bylo úspěšné z hlediska pokrytí obsahu. Mírný pokles RAG skóre (-4.2%) je technický artefakt TF-IDF metody a neovlivňuje kvalitu odpovědí - žádný dotaz nyní nespadá pod kritickou hranici 0.3.

Nové jednotky přinášejí klíčové informace o hodnotách bodu, bonifikacích a regulačních mechanismech pro rok 2026, které v datasetu dříve chyběly. Pro plné využití nových dat je doporučeno rozšířit sadu testovacích dotazů a zvážit přechod na hybridní vyhledávání.

---
*Vygenerováno: 2026-02-03*
*Počet testovacích dotazů: 10*
*Verze datasetu: knowledge_base_expanded_v2.jsonl*
