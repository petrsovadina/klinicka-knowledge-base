#!/usr/bin/env python3
"""
WikiSkripta Downloader
======================
Stahuje obsah WikiSkripta.eu přes MediaWiki API a ukládá jako Markdown soubory.
Vhodné pro vytvoření vektorové knowledge base pro RAG systémy.

Licence obsahu: Creative Commons BY 4.0

Použití:
    python3 wikiskripta_downloader.py              # stáhne vše
    python3 wikiskripta_downloader.py --test 50    # testovací běh (50 stránek)
    python3 wikiskripta_downloader.py --resume     # pokračuje od posledního bodu

Výstup: složka ./wikiskripta_markdown/ s .md soubory
"""

import requests
import re
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

# ── Konfigurace ─────────────────────────────────────────────────────────────
API_URL    = "https://www.wikiskripta.eu/api.php"
OUTPUT_DIR = Path("wikiskripta_markdown")
LOG_FILE   = Path("wikiskripta_download.log")
DELAY      = 0.3    # sekund mezi requesty
BATCH_SIZE = 50     # stránek na jeden seznam-request
# ────────────────────────────────────────────────────────────────────────────

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "WikiSkriptaDownloader/1.0 (educational KB; petr.sovadina9@gmail.com)"
})


# ── Pomocné funkce ───────────────────────────────────────────────────────────

def sanitize_filename(title: str) -> str:
    title = title.replace("/", "_").replace("\\", "_")
    title = re.sub(r'[<>:"|?*]', "_", title)
    return title.strip(". ")[:200]


def wikitext_to_markdown(wikitext: str, title: str) -> str:
    """Konvertuje MediaWiki markup do čistého Markdownu."""
    text = wikitext

    # Přesměrování – není co ukládat jako samostatný článek
    if re.match(r'^\s*#(PŘESMĚRUJ|REDIRECT)\s*\[\[', text, re.IGNORECASE):
        target = re.search(r'\[\[([^\]]+)\]\]', text)
        target = target.group(1) if target else "?"
        return f"# {title}\n\n*Přesměrování na: {target}*\n"

    # TOC a magic words
    text = re.sub(r'__[A-Z_]+__', '', text)

    # Komentáře <!-- ... -->
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

    # Šablony {{...}} – víceúrovňové (2 průchody)
    for _ in range(3):
        text = re.sub(r'\{\{[^{}]*\}\}', '', text, flags=re.DOTALL)

    # Reference <ref ...>...</ref> a <ref ... />
    text = re.sub(r'<ref[^>]*/>', '', text)
    text = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL)
    text = re.sub(r'<references\s*/>', '', text)

    # Ostatní HTML tagy
    text = re.sub(r'<[^>]+>', '', text)

    # HTML entity
    text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')

    # Kategorie a inter-wiki
    text = re.sub(r'\[\[Kategorie:[^\]]*\]\]', '', text)
    text = re.sub(r'\[\[[a-z]{2}:[^\]]*\]\]', '', text)

    # Soubory / obrázky
    text = re.sub(r'\[\[(Soubor|File|Image|Obrázek)[^\]]*\]\]', '', text, flags=re.IGNORECASE)

    # Interní wiki-odkazy [[Stránka|text]] → text,  [[Stránka]] → Stránka
    text = re.sub(r'\[\[(?:[^|\]]+\|)?([^\]]+)\]\]', r'\1', text)

    # Externí odkazy [URL text] → text,  [URL] → URL
    text = re.sub(r'\[https?://\S+\s+([^\]]+)\]', r'\1', text)
    text = re.sub(r'\[https?://(\S+)\]', r'\1', text)

    # Nadpisy (od největšího, aby se nepřepisovaly)
    text = re.sub(r'^======\s*(.*?)\s*======[ \t]*$', r'###### \1', text, flags=re.MULTILINE)
    text = re.sub(r'^=====\s*(.*?)\s*=====[ \t]*$',  r'##### \1',  text, flags=re.MULTILINE)
    text = re.sub(r'^====\s*(.*?)\s*====[ \t]*$',    r'#### \1',   text, flags=re.MULTILINE)
    text = re.sub(r'^===\s*(.*?)\s*===[ \t]*$',      r'### \1',    text, flags=re.MULTILINE)
    text = re.sub(r'^==\s*(.*?)\s*==[ \t]*$',        r'## \1',     text, flags=re.MULTILINE)
    text = re.sub(r'^=\s*(.*?)\s*=[ \t]*$',          r'# \1',      text, flags=re.MULTILINE)

    # Tučné / kurzíva
    text = re.sub(r"'{5}(.*?)'{5}", r'***\1***', text)
    text = re.sub(r"'{3}(.*?)'{3}", r'**\1**',   text)
    text = re.sub(r"'{2}(.*?)'{2}", r'*\1*',     text)

    # Nečíslované a číslované seznamy
    text = re.sub(r'^(\*+)\s*', lambda m: '  ' * (len(m.group(1)) - 1) + '- ', text, flags=re.MULTILINE)
    text = re.sub(r'^(#+)\s*',  lambda m: '  ' * (len(m.group(1)) - 1) + '1. ', text, flags=re.MULTILINE)

    # Tabulky – zachovat jako prostý text, odstranit wiki-syntax
    text = re.sub(r'^\{\|[^\n]*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\|\}[ \t]*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\|-[^\n]*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\|[+!]?\s*(?:[^|]*\|)?', '', text, flags=re.MULTILINE)
    text = re.sub(r'^!\s*(?:[^|]*\|)?', '', text, flags=re.MULTILINE)

    # Vícenásobné prázdné řádky → max 2
    text = re.sub(r'\n{3,}', '\n\n', text)

    header = (
        f"# {title}\n\n"
        f"> **Zdroj:** https://www.wikiskripta.eu/w/{title.replace(' ', '_')}  \n"
        f"> **Licence:** [Creative Commons BY 4.0](https://creativecommons.org/licenses/by/4.0/)\n\n"
        f"---\n\n"
    )
    return header + text.strip() + "\n"


# ── API funkce ───────────────────────────────────────────────────────────────

def get_all_page_titles(max_pages=None) -> list:
    titles = []
    params = {
        "action": "query",
        "list": "allpages",
        "aplimit": BATCH_SIZE,
        "apnamespace": 0,
        "format": "json",
    }
    print("Stahuji seznam stranck...")
    batch = 0

    while True:
        resp = SESSION.get(API_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        titles.extend(p["title"] for p in data["query"]["allpages"])
        batch += 1

        if batch % 20 == 0:
            print(f"   ... {len(titles)} nazvu")

        if "continue" not in data:
            break
        params["apcontinue"] = data["continue"]["apcontinue"]

        if max_pages and len(titles) >= max_pages:
            titles = titles[:max_pages]
            break

        time.sleep(DELAY)

    print(f"Celkem stranck: {len(titles)}\n")
    return titles


def get_page_wikitext(title: str):
    params = {
        "action": "query",
        "titles": title,
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "format": "json",
    }
    resp = SESSION.get(API_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    page = next(iter(data["query"]["pages"].values()))
    if "missing" in page:
        return None
    try:
        return page["revisions"][0]["slots"]["main"]["*"]
    except (KeyError, IndexError):
        return None


# ── Hlavní logika ────────────────────────────────────────────────────────────

def download_all(max_pages=None):
    OUTPUT_DIR.mkdir(exist_ok=True)
    errors = []

    print("=" * 60)
    print("  WikiSkripta Knowledge Base Downloader")
    print(f"  Vystupni slozka: {OUTPUT_DIR.resolve()}")
    print(f"  Zahajeno:        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if max_pages:
        print(f"  Limit:           {max_pages} stranck (testovaci rezim)")
    print("=" * 60 + "\n")

    titles = get_all_page_titles(max_pages)
    total   = len(titles)
    success = 0
    skipped = 0
    redirects = 0

    for i, title in enumerate(titles, 1):
        filename = OUTPUT_DIR / f"{sanitize_filename(title)}.md"

        # Resume podpora – přeskočit existující
        if filename.exists():
            skipped += 1
            continue

        try:
            wikitext = get_page_wikitext(title)
            if wikitext is None:
                errors.append(f"MISSING\t{title}")
                continue

            markdown = wikitext_to_markdown(wikitext, title)

            # Počítej přesměrování zvlášť
            if "*Přesměrování na:" in markdown:
                redirects += 1

            filename.write_text(markdown, encoding="utf-8")
            success += 1

            if i % 200 == 0 or i <= 3:
                pct = i / total * 100
                print(f"[{i:>5}/{total}] {pct:5.1f}%  OK: {title[:55]}")

        except Exception as e:
            errors.append(f"ERROR\t{title}\t{e}")
            print(f"  CHYBA [{i}/{total}]: {title[:40]} - {e}", file=sys.stderr)

        time.sleep(DELAY)

    # ── Souhrn ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"  Uspesne ulozeno:  {success}")
    print(f"  Presmerovani:     {redirects} (zahrnuty v uspesnych)")
    print(f"  Preskoceno:       {skipped} (uz existovaly)")
    print(f"  Chyby:            {len(errors)}")
    print(f"  Slozka:           {OUTPUT_DIR.resolve()}")
    print("=" * 60)

    if errors:
        LOG_FILE.write_text("\n".join(errors), encoding="utf-8")
        print(f"\n  Log chyb: {LOG_FILE}")

    # Index metadata
    (OUTPUT_DIR / "_INDEX.md").write_text(
        f"# WikiSkripta – Knowledge Base Index\n\n"
        f"| Atribut | Hodnota |\n"
        f"|---|---|\n"
        f"| Stazeno | {datetime.now().strftime('%Y-%m-%d %H:%M')} |\n"
        f"| Stranck celkem | {success} |\n"
        f"| Zdroj | https://www.wikiskripta.eu |\n"
        f"| Licence | Creative Commons BY 4.0 |\n"
        f"| Format | Markdown (.md) |\n\n"
        f"## Jak vektorizovat\n\n"
        f"```python\n"
        f"# Příklad s LangChain\n"
        f"from langchain.document_loaders import DirectoryLoader\n"
        f"from langchain.text_splitter import MarkdownHeaderTextSplitter\n\n"
        f"loader = DirectoryLoader('wikiskripta_markdown/', glob='*.md')\n"
        f"docs = loader.load()\n"
        f"```\n",
        encoding="utf-8",
    )
    print(f"\n  Hotovo! Spust vektorizaci ze slozky: {OUTPUT_DIR.resolve()}")


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stahuje WikiSkripta jako Markdown")
    parser.add_argument("--test", type=int, metavar="N",
                        help="Testovaci rezim: stahne jen prvnich N stranck")
    args = parser.parse_args()
    download_all(max_pages=args.test)
