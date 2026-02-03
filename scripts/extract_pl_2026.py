#!/usr/bin/env python3
"""
Specialized extraction for Practical Doctors (PL - 001) and PLDD (002) methodology 2026.
Extracts knowledge units from Úhradová vyhláška 2026, focused on §6 and Příloha č. 2.

Focus areas:
- Kapitační platby (capitation payments) and their rates
- Age indexes for capitation calculation
- Bonifikace (bonuses) for preventive care, vaccination, education
- Výkony (procedures) included in capitation vs. extra-capitation
- Regulační omezení (regulatory limits) for prescriptions and referrals
- Týmová praxe (team practice) conditions and payments
"""
import json
import uuid
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path("/Users/petrsovadina/Desktop/Develope/personal/klinicka-knowledge-base")
OUTPUT_DIR = BASE_DIR / "data/extracted"
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
OUTPUT_FILE = OUTPUT_DIR / "vzp_metodika_pl_2026.jsonl"

# Document metadata
DOCUMENT_METADATA = {
    "name": "Úhradová vyhláška 2026 - Praktičtí lékaři a PLDD",
    "url": "https://mzd.gov.cz/wp-content/uploads/2025/11/Uhradova_vyhlaska_2026.pdf",
    "year": 2026,
    "retrieved_at": "2026-02-03T00:00:00Z"
}


def create_unit(id_suffix, unit_type, title, description, content, specialties=None, tags=None, domain="uhrady"):
    """Create a standardized knowledge unit."""
    return {
        "id": f"ku-pl-2026-{id_suffix:03d}",
        "type": unit_type,
        "domain": domain,
        "title": title,
        "description": description,
        "version": "2026",
        "source": {
            "name": DOCUMENT_METADATA["name"],
            "url": DOCUMENT_METADATA["url"],
            "retrieved_at": DOCUMENT_METADATA["retrieved_at"]
        },
        "content": content,
        "applicability": {
            "specialties": specialties or ["001", "002"],
            "valid_from": "2026-01-01",
            "valid_to": "2026-12-31"
        },
        "related_units": [],
        "tags": tags or []
    }


def extract_pl_pldd_units():
    """Extract knowledge units for PL (001) and PLDD (002)."""
    units = []

    # ========================================
    # A) KAPITAČNÍ PLATBY - Základní sazby
    # ========================================

    # Unit 1: Základní kapitační sazba 76 Kč - plný rozsah
    units.append(create_unit(
        1, "rule",
        "Základní kapitační sazba 76 Kč pro plně dostupné ordinace",
        "Základní kapitační sazba 76 Kč náleží pracovištím PL a PLDD, která poskytují služby v rozsahu min. 30 ordinačních hodin/5 dnů, min. 1 den do 18:00 a umožňují objednání na pevný čas min. 2 dny v týdnu.",
        {
            "kapitacni_sazba": "76 Kč",
            "ordinacni_hodiny": "min. 30 hodin / 5 dnů",
            "podminky": [
                "min. 1 den v týdnu ordinace do 18:00",
                "objednávkový systém na pevnou hodinu min. 2 dny v týdnu"
            ],
            "ustanoveni": "Příloha č. 2, bod 1a)"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "kapitace", "základní_sazba", "2026"]
    ))

    # Unit 2: Kapitační sazba 69 Kč - střední rozsah
    units.append(create_unit(
        2, "rule",
        "Kapitační sazba 69 Kč pro ordinace se středním rozsahem",
        "Kapitační sazba 69 Kč náleží pracovištím PL a PLDD, která poskytují služby v rozsahu min. 25 ordinačních hodin/5 dnů, přičemž min. 1 den v týdnu mají ordinační hodiny do 18:00.",
        {
            "kapitacni_sazba": "69 Kč",
            "ordinacni_hodiny": "min. 25 hodin / 5 dnů",
            "podminky": ["min. 1 den v týdnu ordinace do 18:00"],
            "ustanoveni": "Příloha č. 2, bod 1b)"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "kapitace", "střední_sazba", "2026"]
    ))

    # Unit 3: Kapitační sazba 60 Kč pro PL - základní rozsah
    units.append(create_unit(
        3, "rule",
        "Kapitační sazba 60 Kč pro PL s omezeným rozsahem",
        "Základní kapitační sazba 60 Kč náleží pracovištím poskytovatele v odbornosti všeobecné praktické lékařství (001), která neposkytují hrazené služby v rozsahu 25-30 hodin/týden s rozšířenou dostupností.",
        {
            "kapitacni_sazba": "60 Kč",
            "odbornosti": ["001"],
            "podminky": "nesplnění podmínek pro 76 nebo 69 Kč",
            "ustanoveni": "Příloha č. 2, bod 1c)"
        },
        ["001"],
        ["praktičtí_lékaři", "kapitace", "základní_rozsah", "2026"]
    ))

    # Unit 4: Kapitační sazba 66 Kč pro PLDD - základní rozsah
    units.append(create_unit(
        4, "rule",
        "Kapitační sazba 66 Kč pro PLDD s omezeným rozsahem",
        "Základní kapitační sazba 66 Kč náleží pracovištím poskytovatele v odbornosti praktické lékařství pro děti a dorost (002), která neposkytují hrazené služby v rozsahu 25-30 hodin/týden s rozšířenou dostupností.",
        {
            "kapitacni_sazba": "66 Kč",
            "odbornosti": ["002"],
            "podminky": "nesplnění podmínek pro 76 nebo 69 Kč",
            "ustanoveni": "Příloha č. 2, bod 1d)"
        },
        ["002"],
        ["PLDD", "pediatrie", "kapitace", "základní_rozsah", "2026"]
    ))

    # ========================================
    # B) BONIFIKACE KAPITACE
    # ========================================

    # Unit 5: Bonifikace za celoživotní vzdělávání +1 Kč
    units.append(create_unit(
        5, "condition",
        "Bonifikace kapitace za celoživotní vzdělávání (+1 Kč)",
        "Kapitační sazba se navyšuje o 1,00 Kč, pokud poskytovatel do 31. ledna doloží, že min. 50% lékařů má platný doklad CVL. Doklad musí být platný po celé hodnocené období.",
        {
            "navyseni": "1.00 Kč",
            "podminka": "50% nositelů výkonů s platným dokladem CVL",
            "termin": "31. ledna hodnoceného období",
            "tolerance": "30 kalendářních dnů mezi ukončením a novým dokladem",
            "ustanoveni": "Příloha č. 2, bod 2a)"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "bonifikace", "CVL", "vzdělávání", "2026"]
    ))

    # Unit 6: Bonifikace za preventivní prohlídky dospělých +2 Kč
    units.append(create_unit(
        6, "condition",
        "Bonifikace kapitace za preventivní prohlídky dospělých (+2 Kč)",
        "Kapitační sazba se navyšuje o 2,00 Kč pro PL, pokud provedl preventivní prohlídku (výkony 01021, 01022) alespoň u 30% registrovaných pojištěnců ve věku 40-80 let. Rozhodný den je 31.12.",
        {
            "navyseni": "2.00 Kč",
            "vykony": ["01021", "01022"],
            "procento_pacientu": "30%",
            "vekova_skupina": "40-80 let",
            "rozhodny_den": "31. prosince hodnoceného období",
            "vyplaceni": "do 150 dnů po skončení hodnoceného období",
            "ustanoveni": "Příloha č. 2, bod 2b)"
        },
        ["001"],
        ["praktičtí_lékaři", "bonifikace", "prevence", "prohlídky", "2026"]
    ))

    # Unit 7: Bonifikace za preventivní prohlídky dětí +2 Kč
    units.append(create_unit(
        7, "condition",
        "Bonifikace kapitace za preventivní prohlídky dětí a dorostu (+2 Kč)",
        "Kapitační sazba se navyšuje o 2,00 Kč pro PLDD, pokud provedl preventivní prohlídku (výkony 02031, 02032) alespoň u 40% registrovaných pojištěnců ve věku 6-19 let.",
        {
            "navyseni": "2.00 Kč",
            "vykony": ["02031", "02032"],
            "procento_pacientu": "40%",
            "vekova_skupina": "6-19 let",
            "rozhodny_den": "31. prosince hodnoceného období",
            "vyplaceni": "do 150 dnů po skončení hodnoceného období",
            "ustanoveni": "Příloha č. 2, bod 2c)"
        },
        ["002"],
        ["PLDD", "pediatrie", "bonifikace", "prevence", "prohlídky", "2026"]
    ))

    # Unit 8: Bonifikace za akreditaci a školení +1 Kč
    units.append(create_unit(
        8, "condition",
        "Bonifikace kapitace za akreditaci a zajišťování školení (+1 Kč)",
        "Kapitační sazba se navyšuje o 1,00 Kč pro poskytovatele s akreditací MZ pro vzdělávací program a současně zajišťující specializační vzdělávání lékaře (školence/rezidenta).",
        {
            "navyseni": "1.00 Kč",
            "podminky": [
                "rozhodnutí MZ o udělení akreditace",
                "vzdělávací program v oboru VPL, pediatrie, dětské lékařství nebo PLDD",
                "doložení zajištění specializačního vzdělávání + potvrzení o zařazení školence"
            ],
            "ucinnost": "od prvního dne měsíce oznámení",
            "ustanoveni": "Příloha č. 2, bod 2d)"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "bonifikace", "akreditace", "školení", "2026"]
    ))

    # Unit 9: Bonifikace za screening +5 Kč pro VPL
    units.append(create_unit(
        9, "condition",
        "Bonifikace kapitace za plnění screeningových cílů pro VPL (+5 Kč)",
        "Kapitační sazba se navyšuje o 5 Kč pro pracoviště VPL splňující podmínky: 25% screening kolorektálního karcinomu, 20% očkování proti chřipce u 65+, 60% mamografický screening u žen 45-68 let.",
        {
            "navyseni": "5.00 Kč",
            "podminky_screening": [
                {"typ": "kolorektální karcinom", "procento": "25%", "vek": "45-74 let", "vykony": ["15120", "15121"], "koloskopie": ["15101", "15103", "15105", "15107"]},
                {"typ": "očkování chřipka", "procento": "20%", "vek": "od 65 let"},
                {"typ": "mamografický screening", "procento": "60%", "vek": "45-68 let (ženy)", "vykony": ["89178", "89223"]}
            ],
            "vyplaceni": "v rámci finančního vypořádání do 150 dnů",
            "ustanoveni": "Příloha č. 2, body 3a) a 4"
        },
        ["001"],
        ["praktičtí_lékaři", "bonifikace", "screening", "prevence", "2026"]
    ))

    # Unit 10: Bonifikace za screening +5 Kč pro PLDD
    units.append(create_unit(
        10, "condition",
        "Bonifikace kapitace za plnění screeningových cílů pro PLDD (+5 Kč)",
        "Kapitační sazba se navyšuje o 5 Kč pro pracoviště PLDD splňující podmínky: 90% proočkovanost, 50% screening zraku u 3letých, 50% očkování proti dalším nemocem.",
        {
            "navyseni": "5.00 Kč",
            "podminky_screening": [
                {"typ": "pravidelné očkování", "procento": "90%", "vek": "5-18 let", "obsah": "záškrt, tetanus, černý kašel, obrna, hepatitida B, Haemophilus + spalničky, příušnice, zarděnky"},
                {"typ": "screening zraku", "procento": "50%", "vek": "3 roky", "vykony": ["02036", "06512", "75171", "75022"]},
                {"typ": "dobrovolné očkování", "procento": "50%", "obsah": "pneumokoky, meningokoky, klíšťová encefalitida, hepatitida A, HPV"}
            ],
            "vyplaceni": "v rámci finančního vypořádání do 150 dnů",
            "ustanoveni": "Příloha č. 2, body 3b) a 5"
        },
        ["002"],
        ["PLDD", "pediatrie", "bonifikace", "screening", "očkování", "2026"]
    ))

    # ========================================
    # C) HODNOTY BODU PRO MIMOKAPITAČNÍ VÝKONY
    # ========================================

    # Unit 11: Hodnota bodu 1,35 Kč pro preventivní prohlídky VPL
    units.append(create_unit(
        11, "rule",
        "Hodnota bodu 1,35 Kč pro preventivní prohlídky praktických lékařů",
        "Pro výkony preventivních prohlídek č. 01021 a 01022 podle seznamu výkonů se stanoví hodnota bodu ve výši 1,35 Kč. Tyto výkony nejsou zahrnuty do kapitační platby.",
        {
            "hodnota_bodu": "1.35 Kč",
            "vykony": ["01021", "01022"],
            "typ": "preventivní prohlídky dospělých",
            "ustanoveni": "Příloha č. 2, bod 8a)"
        },
        ["001"],
        ["praktičtí_lékaři", "hodnota_bodu", "prevence", "mimokapitační", "2026"]
    ))

    # Unit 12: Hodnota bodu 1,23 Kč pro preventivní prohlídky PLDD
    units.append(create_unit(
        12, "rule",
        "Hodnota bodu 1,23 Kč pro preventivní prohlídky PLDD",
        "Pro výkony preventivních prohlídek č. 02021, 02022, 02031 a 02032 podle seznamu výkonů se stanoví hodnota bodu ve výši 1,23 Kč. Tyto výkony nejsou zahrnuty do kapitační platby.",
        {
            "hodnota_bodu": "1.23 Kč",
            "vykony": ["02021", "02022", "02031", "02032"],
            "typ": "preventivní prohlídky dětí a dorostu",
            "ustanoveni": "Příloha č. 2, bod 8a)"
        },
        ["002"],
        ["PLDD", "pediatrie", "hodnota_bodu", "prevence", "mimokapitační", "2026"]
    ))

    # Unit 13: Hodnota bodu 1,26 Kč pro diagnostické výkony
    units.append(create_unit(
        13, "rule",
        "Hodnota bodu 1,26 Kč pro diagnostické a screeningové výkony",
        "Pro výkony č. 01201, 01204, 01186, 01188, 02036, 02037, 02039, 02240, 09532, 02100, 02105, 02125, 02130, 02160, 02161, 15118, 15119, 01130, 01135, 01136, 01196, 01197 se stanoví hodnota bodu 1,26 Kč.",
        {
            "hodnota_bodu": "1.26 Kč",
            "vykony": ["01201", "01204", "01186", "01188", "02036", "02037", "02039", "02240", "09532", "02100", "02105", "02125", "02130", "02160", "02161", "15118", "15119", "01130", "01135", "01136", "01196", "01197"],
            "typ": "diagnostické a screeningové výkony",
            "ustanoveni": "Příloha č. 2, bod 8b)"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "hodnota_bodu", "diagnostika", "screening", "2026"]
    ))

    # Unit 14: Hodnota bodu 1,18 Kč pro ostatní výkony
    units.append(create_unit(
        14, "rule",
        "Hodnota bodu 1,18 Kč pro ostatní mimokapitační výkony",
        "Pro ostatní výkony nezahrnuté do kapitační platby a pro výkony za neregistrované pojištěnce se stanoví základní hodnota bodu ve výši 1,18 Kč.",
        {
            "hodnota_bodu": "1.18 Kč",
            "typ": "ostatní mimokapitační výkony + neregistrovaní pojištěnci",
            "ustanoveni": "Příloha č. 2, bod 8c)"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "hodnota_bodu", "mimokapitační", "neregistrovaní", "2026"]
    ))

    # Unit 15: Bonifikace hodnoty bodu za CVL +0,04 Kč
    units.append(create_unit(
        15, "condition",
        "Bonifikace hodnoty bodu za CVL (+0,04 Kč)",
        "Hodnota bodu pro mimokapitační výkony se navyšuje o 0,04 Kč, pokud poskytovatel do 31. ledna doloží, že min. 50% lékařů má platný doklad CVL po celé hodnocené období.",
        {
            "navyseni": "0.04 Kč",
            "podminka": "50% nositelů výkonů s platným dokladem CVL",
            "termin": "31. ledna hodnoceného období",
            "tolerance": "30 kalendářních dnů mezi doklady",
            "ustanoveni": "Příloha č. 2, bod 9"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "bonifikace", "hodnota_bodu", "CVL", "2026"]
    ))

    # Unit 16: Bonifikace hodnoty bodu za dostupnost +0,06 Kč
    units.append(create_unit(
        16, "condition",
        "Bonifikace hodnoty bodu za dostupnost a objednávkový systém (+0,06 Kč)",
        "Hodnota bodu se navyšuje o 0,06 Kč pro pracoviště poskytující služby min. 30 hodin/5 dnů, s ordinací do 18:00 min. 1 den a objednávkovým systémem umožňujícím objednání na pevný čas min. 2 dny v týdnu.",
        {
            "navyseni": "0.06 Kč",
            "podminky": [
                "min. 30 ordinačních hodin / 5 pracovních dnů",
                "min. 1 den ordinace do 18:00",
                "objednávkový systém na pevný čas min. 2 dny v týdnu"
            ],
            "ustanoveni": "Příloha č. 2, bod 10"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "bonifikace", "hodnota_bodu", "dostupnost", "2026"]
    ))

    # Unit 17: Hodnota bodu 1,26 Kč pro přepravu
    units.append(create_unit(
        17, "rule",
        "Hodnota bodu 1,26 Kč pro přepravu v návštěvní službě",
        "Pro výkony přepravy zdravotnického pracovníka v návštěvní službě se stanoví hodnota bodu ve výši 1,26 Kč.",
        {
            "hodnota_bodu": "1.26 Kč",
            "typ": "přeprava v návštěvní službě",
            "ustanoveni": "Příloha č. 2, bod 11"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "hodnota_bodu", "přeprava", "návštěvní_služba", "2026"]
    ))

    # Unit 18: Epizodní úhrada 87 Kč
    units.append(create_unit(
        18, "rule",
        "Úhrada 87 Kč za epizodu péče u dospělých pacientů",
        "Za každou vykázanou epizodu péče nebo kontakt u pacientů od 18 let v souvislosti s klinickým vyšetřením praktickým lékařem nebo PLDD se stanoví úhrada 87 Kč.",
        {
            "uhrada": "87 Kč",
            "vek": "od 18 let",
            "typ": "epizoda péče / kontakt + klinické vyšetření",
            "ustanoveni": "Příloha č. 2, bod 12"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "epizoda_péče", "úhrada", "2026"]
    ))

    # ========================================
    # D) VĚKOVÉ INDEXY PRO KAPITACI
    # ========================================

    # Unit 19: Věkové indexy
    units.append(create_unit(
        19, "definition",
        "Věkové indexy pro přepočet kapitačních plateb",
        "Věkové indexy vyjadřují poměr nákladů na pojištěnce v dané věkové skupině vůči referenční skupině 30-34 let (index 1,00). Nejvyšší index 4,35 platí pro děti 0-4 roky, nejnižší 0,90 pro věk 20-24 let.",
        {
            "indexy": {
                "0-4": 4.35, "5-9": 2.01, "10-14": 1.54, "15-19": 1.06,
                "20-24": 0.90, "25-29": 0.95, "30-34": 1.00, "35-39": 1.05,
                "40-44": 1.05, "45-49": 1.10, "50-54": 1.43, "55-59": 1.54,
                "60-64": 1.59, "65-69": 1.80, "70-74": 2.12, "75-79": 2.54,
                "80-84": 3.07, "85+": 3.60
            },
            "referencni_skupina": "30-34 let (index 1,00)",
            "ustanoveni": "Příloha č. 2, bod 13"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "věkové_indexy", "kapitace", "přepočet", "2026"]
    ))

    # ========================================
    # E) REGULAČNÍ OMEZENÍ
    # ========================================

    # Unit 20: Regulace preskripce (+20%, srážka 25%)
    units.append(create_unit(
        20, "rule",
        "Regulační omezení preskripce léků (+20%, srážka do 25%)",
        "Pokud průměrná úhrada za předepsané léky a zdravotnické prostředky (mimo inkontinenční) přepočtená na pojištěnce překročí o 20% celostátní průměr, může pojišťovna uplatnit srážku do 25% z překročení.",
        {
            "limit": "120% celostátního průměru",
            "srazka": "do 25% z překročení",
            "vylouceni": "zdravotnické prostředky pro inkontinentní",
            "zapocitavaji_se": "doplatky za nepřípustné záměny (§32 odst. 2)",
            "ustanoveni": "Příloha č. 2, část C, bod 1.1"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "regulace", "preskripce", "léky", "2026"]
    ))

    # Unit 21: Regulace inkontinenčních prostředků
    units.append(create_unit(
        21, "rule",
        "Regulační omezení zdravotnických prostředků pro inkontinentní (+20%, srážka do 25%)",
        "Pokud průměrná úhrada za inkontinenční prostředky přepočtená na pojištěnce překročí o 20% celostátní průměr, může pojišťovna uplatnit srážku do 25% z překročení.",
        {
            "limit": "120% celostátního průměru",
            "srazka": "do 25% z překročení",
            "typ": "zdravotnické prostředky pro inkontinentní",
            "ustanoveni": "Příloha č. 2, část C, bod 1.2"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "regulace", "inkontinence", "2026"]
    ))

    # Unit 22: Regulace vyžádané péče
    units.append(create_unit(
        22, "rule",
        "Regulační omezení vyžádané péče (+15%, srážka do 25%)",
        "Pokud průměrná úhrada za vyžádanou péči ve vyjmenovaných odbornostech překročí o 15% celostátní průměr, může pojišťovna uplatnit srážku do 25% z překročení. Nezahrnují se screeningové výkony.",
        {
            "limit": "115% celostátního průměru",
            "srazka": "do 25% z překročení",
            "vylouceni": [
                "výkony 01186, 01188 (paliativní péče)",
                "mamografický screening",
                "screening karcinomu děložního hrdla",
                "screening kolorektálního karcinomu",
                "screening karcinomu plic",
                "screening karcinomu prostaty",
                "screening aneurysmatu aorty",
                "vyžádaná péče v přímé vazbě na preventivní prohlídky"
            ],
            "ustanoveni": "Příloha č. 2, část C, bod 1.3"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "regulace", "vyžádaná_péče", "2026"]
    ))

    # Unit 23: Regulace vyžádané péče v odbornosti 902
    units.append(create_unit(
        23, "rule",
        "Regulační omezení vyžádané péče v odbornosti 902 (+20%, srážka do 25%)",
        "Pokud průměrná úhrada za vyžádanou péči v odbornosti 902 (fyzioterapie) překročí o 20% celostátní průměr, může pojišťovna uplatnit srážku do 25% z překročení.",
        {
            "limit": "120% celostátního průměru",
            "srazka": "do 25% z překročení",
            "odbornost": "902 (fyzioterapie)",
            "ustanoveni": "Příloha č. 2, část C, bod 1.4"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "regulace", "vyžádaná_péče", "fyzioterapie", "2026"]
    ))

    # Unit 24: Výjimka z regulací - nezbytná péče
    units.append(create_unit(
        24, "exception",
        "Výjimka z regulací pro nezbytně poskytnutou péči",
        "Regulační omezení se nepoužijí, pokud bylo nezbytné poskytnutí hrazených služeb, na jejichž základě byly překročeny průměrné úhrady.",
        {
            "podminka": "nezbytnost poskytnutí hrazených služeb",
            "typ": "výjimka z regulací",
            "ustanoveni": "Příloha č. 2, část C, bod 2"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "výjimka", "regulace", "nezbytná_péče", "2026"]
    ))

    # Unit 25: Výjimka z regulací - malí poskytovatelé
    units.append(create_unit(
        25, "exception",
        "Výjimka z regulací pro poskytovatele s 50 a méně registrovanými pojištěnci",
        "Regulační omezení se nepoužijí pro poskytovatele, který v hodnoceném období registroval 50 a méně pojištěnců dané zdravotní pojišťovny.",
        {
            "limit": "50 registrovaných pojištěnců",
            "typ": "výjimka z regulací pro malé poskytovatele",
            "ustanoveni": "Příloha č. 2, část C, bod 7"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "výjimka", "regulace", "malí_poskytovatelé", "2026"]
    ))

    # Unit 26: Maximum regulační srážky 15%
    units.append(create_unit(
        26, "rule",
        "Maximum regulační srážky 15% z celkové úhrady",
        "Zdravotní pojišťovna může uplatnit regulační srážku maximálně do výše 15% úhrady za kapitaci a výkony (snížené o ZUM a ZULP) v hodnoceném období.",
        {
            "maximum_srazky": "15%",
            "zaklad": "kapitace + výkony - ZUM - ZULP",
            "ustanoveni": "Příloha č. 2, část C, bod 8"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "regulace", "maximum_srážky", "2026"]
    ))

    # ========================================
    # F) TÝMOVÁ PRAXE
    # ========================================

    # Unit 27: Podmínky týmové praxe
    units.append(create_unit(
        27, "definition",
        "Podmínky pro uznání pracoviště týmové praxe",
        "Pracoviště týmové praxe musí splňovat: akreditaci MZ, min. 30 hodin/5 dnů, objednávkový systém, min. 1800 (VPL) resp. 1700 (PLDD) přepočtených pojištěnců, 1.0 úvazek specialisty + 0.2 úvazek dalšího lékaře.",
        {
            "podminky": {
                "ordinacni_hodiny": "min. 30 hodin / 5 dnů",
                "objednavkovy_system": "elektronický, umožňující objednání na pevný čas",
                "min_pacientu_VPL": "1800 přepočtených pojištěnců",
                "min_pacientu_PLDD": "1700 přepočtených pojištěnců",
                "personalni_obsazeni": "1.0 úvazku specialisty + 0.2 úvazku dalšího lékaře",
                "max_uvazky": "3.0 celkem, z toho max 1.0 lékař po základním kmeni"
            },
            "akreditace": "rozhodnutí MZ o udělení akreditace",
            "vybaveni_VPL": ["01441", "01443", "02230", "02250", "09127", "15119", "17129"],
            "vybaveni_PLDD": ["01441", "02036", "02220", "02230", "02250", "09125"],
            "ustanoveni": "Příloha č. 2, část D, bod 1"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "týmová_praxe", "podmínky", "2026"]
    ))

    # Unit 28: Vzorec úhrady za týmovou praxi
    units.append(create_unit(
        28, "definition",
        "Vzorec pro výpočet úhrady za týmovou praxi",
        "Měsíční úhrada za týmovou praxi = KPPokres × Úv+ × 10 400 Kč, kde Úv+ = (ÚvΣ - 1) × 10 je počet desetin úvazků nad 1.0 a KPPokres je koeficient pojištěnců v okrese.",
        {
            "vzorec": "Úhr_týmová_praxe = KPPokres × Úv+ × 10 400 Kč",
            "promenne": {
                "KPPokres": "koeficient počtu pojištěnců v okrese",
                "Úv+": "(ÚvΣ - 1) × 10 - počet desetin úvazků nad 1.0",
                "ÚvΣ": "celková výše úvazků lékařů na pracovišti"
            },
            "zakladni_castka": "10 400 Kč za 0.1 úvazku nad 1.0",
            "vyplaceni": "měsíční předběžná úhrada, vypořádání do 150 dnů",
            "ustanoveni": "Příloha č. 2, část D, body 2-3"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "týmová_praxe", "vzorec", "úhrada", "2026"]
    ))

    # ========================================
    # G) ÚHRADA ZA PODPŮRNOU PSYCHOTERAPII (PLDD)
    # ========================================

    # Unit 29: Psychoterapie PLDD
    units.append(create_unit(
        29, "rule",
        "Měsíční úhrada za podpůrnou psychoterapii u PLDD",
        "PLDD poskytující podpůrnou psychoterapii pojištěncům do 19 let má nárok na měsíční úhradu ve výši KPPokres × 5 000 Kč. Podmínkou je vykázání podpůrné psychoterapie v daném měsíci.",
        {
            "vzorec": "Úhr_psycho_PLDD = KPPokres × 5 000 Kč",
            "vekova_hranice": "do 19 let",
            "podminka": "vykázaná podpůrná psychoterapie v daném měsíci",
            "ustanoveni": "Příloha č. 2, část E"
        },
        ["002"],
        ["PLDD", "pediatrie", "psychoterapie", "úhrada", "2026"]
    ))

    # ========================================
    # H) VÝKONY ZAHRNUTÉ DO KAPITACE
    # ========================================

    # Unit 30: Kapitační výkony VPL (001)
    units.append(create_unit(
        30, "definition",
        "Seznam výkonů zahrnutých do kapitační platby pro VPL (001)",
        "Do kapitační platby v odbornosti 001 jsou zahrnuty výkony: 01023, 01024, 01025, 01030, 09215-09220, 09233, 09237, 09507, 09511, 09513, 09523, 09525, 44239, 71511, 71611.",
        {
            "vykony": {
                "01023": "Cílené vyšetření praktickým lékařem",
                "01024": "Kontrolní vyšetření praktickým lékařem",
                "01025": "Konzultace s rodinnými příslušníky",
                "01030": "Administrativní úkony",
                "09215": "Injekce I.M., S.C., I.D.",
                "09216": "Injekce do měkkých tkání",
                "09217": "I.V. injekce u dítěte do 10 let",
                "09219": "I.V. injekce u dospělého",
                "09220": "Kanylace periferní žíly + infúze",
                "09233": "Injekční okrsková anestézie",
                "09237": "Ošetření a převaz rány do 10 cm²",
                "09507": "Psychoterapie podpůrná",
                "09511": "Minimální kontakt",
                "09513": "Telefonická konzultace",
                "09523": "Edukační pohovor",
                "09525": "Rozhovor s rodinou",
                "44239": "Ošetření bércového vředu",
                "71511": "Vyjmutí cizího tělesa ze zvukovodu",
                "71611": "Vynětí cizího tělesa z nosu"
            },
            "ustanoveni": "Příloha č. 2, bod 6"
        },
        ["001"],
        ["praktičtí_lékaři", "kapitace", "výkony", "seznam", "2026"]
    ))

    # Unit 31: Kapitační výkony PLDD (002)
    units.append(create_unit(
        31, "definition",
        "Seznam výkonů zahrnutých do kapitační platby pro PLDD (002)",
        "Do kapitační platby v odbornosti 002 jsou zahrnuty výkony: 01025, 01030, 02023, 02024, 02033, 02034, 06111-06129, 09215-09221, 09233, 09235, 09237, 09253, 09507, 09511, 09513, 09523, 09525, 71511, 71611.",
        {
            "vykony": {
                "01025": "Konzultace s rodinnými příslušníky",
                "01030": "Administrativní úkony",
                "02023": "Cílené vyšetření – dítě do 6 let",
                "02024": "Kontrolní vyšetření – dítě do 6 let",
                "02033": "Cílené vyšetření – dítě nad 6 let",
                "02034": "Kontrolní vyšetření – dítě nad 6 let",
                "06111": "Komplex – vyšetření sestrou",
                "06119": "Komplex – odběr biologického materiálu",
                "06121": "Komplex – lokální ošetření",
                "06123": "Komplex – edukace, rehabilitace",
                "06125": "Komplex – klysma, cévkování, laváže",
                "06127": "Komplex – aplikace terapie",
                "06129": "Nácvik aplikace inzulínu",
                "09215": "Injekce I.M., S.C., I.D.",
                "09216": "Injekce do měkkých tkání",
                "09217": "I.V. injekce u dítěte do 10 let",
                "09219": "I.V. injekce u dospělého",
                "09220": "Kanylace periferní žíly + infúze",
                "09221": "Infúze u dítěte do 10 let",
                "09233": "Injekční okrsková anestézie",
                "09235": "Odstranění malých lézí kůže",
                "09237": "Ošetření a převaz rány do 10 cm²",
                "09253": "Uvolnění prepucia",
                "09507": "Psychoterapie podpůrná",
                "09511": "Minimální kontakt",
                "09513": "Telefonická konzultace",
                "09523": "Edukační pohovor",
                "09525": "Rozhovor s rodinou",
                "71511": "Vyjmutí cizího tělesa ze zvukovodu",
                "71611": "Vynětí cizího tělesa z nosu"
            },
            "ustanoveni": "Příloha č. 2, bod 7"
        },
        ["002"],
        ["PLDD", "pediatrie", "kapitace", "výkony", "seznam", "2026"]
    ))

    # ========================================
    # I) FINANČNÍ RIZIKA
    # ========================================

    # Unit 32: Riziko ztráty bonifikací
    units.append(create_unit(
        32, "risk",
        "Riziko ztráty bonifikací za nesplnění termínů a podmínek",
        "Nedodržení termínu 31. ledna pro doložení CVL nebo nesplnění screeningových cílů vede ke ztrátě bonifikací. Při kapitaci 76 Kč × 1500 pojištěnců = 114 000 Kč/měsíc může ztráta bonifikací činit až 18 000 Kč ročně.",
        {
            "bonifikace_v_ohrozeni": [
                {"typ": "CVL kapitace", "hodnota": "1.00 Kč/pojištěnce"},
                {"typ": "prevence", "hodnota": "2.00 Kč/pojištěnce"},
                {"typ": "screening", "hodnota": "5.00 Kč/pojištěnce"},
                {"typ": "akreditace", "hodnota": "1.00 Kč/pojištěnce"},
                {"typ": "CVL výkony", "hodnota": "0.04 Kč/bod"},
                {"typ": "dostupnost výkony", "hodnota": "0.06 Kč/bod"}
            ],
            "priklad": "1500 pojištěnců × 9 Kč ztracených bonifikací × 12 = 162 000 Kč ročně"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "riziko", "bonifikace", "termíny", "2026"],
        "financni-rizika"
    ))

    # Unit 33: Riziko regulačních srážek
    units.append(create_unit(
        33, "risk",
        "Riziko regulačních srážek za překročení nákladových limitů",
        "Překročení limitů preskripce (+20%), vyžádané péče (+15%) nebo odbornosti 902 (+20%) může vést k srážce až 25% z překročení. Maximum celkové srážky je 15% z úhrady za kapitaci a výkony.",
        {
            "rizika": [
                {"typ": "preskripce", "limit": "+20%", "srazka": "do 25%"},
                {"typ": "inkontinence", "limit": "+20%", "srazka": "do 25%"},
                {"typ": "vyžádaná péče", "limit": "+15%", "srazka": "do 25%"},
                {"typ": "odbornost 902", "limit": "+20%", "srazka": "do 25%"}
            ],
            "maximum": "15% z kapitace + výkony - ZUM - ZULP"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "riziko", "regulace", "srážky", "2026"],
        "financni-rizika"
    ))

    # Unit 34: Hodnota bodu pro seznam výkonů
    units.append(create_unit(
        34, "rule",
        "Hodnota bodu 1,00 Kč pro úhradu podle seznamu výkonů",
        "Pro hrazené služby hrazené podle seznamu výkonů (ne kombinovanou kapitačně výkonovou platbou) se stanoví hodnota bodu ve výši 1,00 Kč. Pro přepravu v návštěvní službě je hodnota 1,26 Kč.",
        {
            "hodnota_bodu": "1.00 Kč",
            "hodnota_bodu_preprava": "1.26 Kč",
            "typ": "úhrada pouze podle seznamu výkonů",
            "ustanoveni": "Příloha č. 2, část B"
        },
        ["001", "002"],
        ["praktičtí_lékaři", "PLDD", "hodnota_bodu", "seznam_výkonů", "2026"]
    ))

    return units


def main():
    """Main function to run extraction."""
    print(f"\n{'='*80}")
    print("EXTRACTION: Praktičtí lékaři (001) a PLDD (002) Methodology 2026")
    print(f"{'='*80}\n")

    # Extract units
    print("Step 1: Extracting knowledge units...")
    units = extract_pl_pldd_units()
    print(f"  Total units: {len(units)}")

    # Count by type
    type_counts = {}
    domain_counts = {}
    for unit in units:
        t = unit.get("type", "unknown")
        d = unit.get("domain", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
        domain_counts[d] = domain_counts.get(d, 0) + 1

    print(f"\nStep 2: Unit type distribution:")
    for t, count in sorted(type_counts.items()):
        print(f"    {t}: {count}")

    print(f"\nStep 3: Domain distribution:")
    for d, count in sorted(domain_counts.items()):
        print(f"    {d}: {count}")

    # Write to JSONL
    print(f"\nStep 4: Writing to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for unit in units:
            f.write(json.dumps(unit, ensure_ascii=False) + '\n')

    print(f"\n{'='*80}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*80}")
    print(f"  Total units extracted: {len(units)}")
    print(f"  Output file: {OUTPUT_FILE}")
    print(f"  Expected: 25-40 units (actual: {len(units)})")

    # Validate expected count
    if 25 <= len(units) <= 40:
        print("  ✓ Within expected range")
    else:
        print(f"  ⚠ Outside expected range (25-40)")

    return len(units)


if __name__ == "__main__":
    main()
