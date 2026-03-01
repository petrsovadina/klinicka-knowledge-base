#!/usr/bin/env python3
"""
WikiSkripta Knowledge Base – Streamlit UI
==========================================
Spuštění:  streamlit run wikiskripta_app.py
"""

import streamlit as st
import threading
import json
import re
import time
import requests
from pathlib import Path
from datetime import datetime

# ─── Konfigurace ─────────────────────────────────────────────────────────────
API_URL       = "https://www.wikiskripta.eu/api.php"
PROGRESS_FILE = Path("wikiskripta_progress.json")
DEFAULT_OUT   = Path("wikiskripta_markdown")

st.set_page_config(
    page_title="WikiSkripta Downloader",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #1e293b;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        border-left: 4px solid #3b82f6;
        margin-bottom: 0.5rem;
    }
    .metric-card.green  { border-color: #22c55e; }
    .metric-card.red    { border-color: #ef4444; }
    .metric-card.yellow { border-color: #f59e0b; }
    .metric-label { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-value { font-size: 2rem; font-weight: 700; color: #f1f5f9; }
    .status-badge {
        display: inline-block; padding: 0.25rem 0.75rem;
        border-radius: 9999px; font-size: 0.8rem; font-weight: 600;
    }
    .badge-running  { background: #1e40af; color: #93c5fd; }
    .badge-idle     { background: #374151; color: #9ca3af; }
    .badge-done     { background: #14532d; color: #86efac; }
    .badge-error    { background: #7f1d1d; color: #fca5a5; }
    .log-box {
        background: #0f172a; border-radius: 8px; padding: 0.75rem 1rem;
        font-family: monospace; font-size: 0.78rem; color: #94a3b8;
        max-height: 200px; overflow-y: auto;
        border: 1px solid #1e293b;
    }
    .file-item {
        padding: 0.4rem 0.6rem; border-radius: 6px; cursor: pointer;
        border-left: 3px solid transparent;
    }
    .file-item:hover { background: #1e293b; border-color: #3b82f6; }
    h1.app-title { font-size: 1.8rem !important; }
</style>
""", unsafe_allow_html=True)

# ─── Stav downloadu ───────────────────────────────────────────────────────────

def read_progress() -> dict:
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"status": "idle", "total": 0, "current": 0,
            "success": 0, "errors": 0, "skipped": 0,
            "current_title": "", "log": [], "started_at": None, "finished_at": None}


def write_progress(data: dict):
    PROGRESS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def is_running() -> bool:
    p = read_progress()
    return p.get("status") == "running"

# ─── Downloader (jede v threadu) ──────────────────────────────────────────────

def sanitize_filename(title: str) -> str:
    title = title.replace("/", "_").replace("\\", "_")
    title = re.sub(r'[<>:"|?*]', "_", title)
    return title.strip(". ")[:200]


def wikitext_to_markdown(wikitext: str, title: str) -> str:
    text = wikitext
    if re.match(r'^\s*#(PŘESMĚRUJ|REDIRECT)\s*\[\[', text, re.IGNORECASE):
        target = re.search(r'\[\[([^\]]+)\]\]', text)
        return f"# {title}\n\n*Přesměrování na: {target.group(1) if target else '?'}*\n"
    text = re.sub(r'__[A-Z_]+__', '', text)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    for _ in range(3):
        text = re.sub(r'\{\{[^{}]*\}\}', '', text, flags=re.DOTALL)
    text = re.sub(r'<ref[^>]*/>', '', text)
    text = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL)
    text = re.sub(r'<references\s*/>', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = (text.replace('&nbsp;', ' ').replace('&lt;', '<')
                .replace('&gt;', '>').replace('&amp;', '&'))
    text = re.sub(r'\[\[Kategorie:[^\]]*\]\]', '', text)
    text = re.sub(r'\[\[[a-z]{2}:[^\]]*\]\]', '', text)
    text = re.sub(r'\[\[(Soubor|File|Image|Obrázek)[^\]]*\]\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\[(?:[^|\]]+\|)?([^\]]+)\]\]', r'\1', text)
    text = re.sub(r'\[https?://\S+\s+([^\]]+)\]', r'\1', text)
    text = re.sub(r'\[https?://(\S+)\]', r'\1', text)
    for lvl, hsh in [(6,'######'),(5,'#####'),(4,'####'),(3,'###'),(2,'##'),(1,'#')]:
        eq = '=' * lvl
        text = re.sub(rf'^{eq}\s*(.*?)\s*{eq}[ \t]*$', rf'{hsh} \1', text, flags=re.MULTILINE)
    text = re.sub(r"'{5}(.*?)'{5}", r'***\1***', text)
    text = re.sub(r"'{3}(.*?)'{3}", r'**\1**',   text)
    text = re.sub(r"'{2}(.*?)'{2}", r'*\1*',     text)
    text = re.sub(r'^(\*+)\s*', lambda m: '  '*(len(m.group(1))-1)+'- ', text, flags=re.MULTILINE)
    text = re.sub(r'^(#+)\s*',  lambda m: '  '*(len(m.group(1))-1)+'1. ', text, flags=re.MULTILINE)
    text = re.sub(r'^\{\|[^\n]*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\|\}[ \t]*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\|-[^\n]*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\|[+!]?\s*(?:[^|]*\|)?', '', text, flags=re.MULTILINE)
    text = re.sub(r'^!\s*(?:[^|]*\|)?', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    url_title = title.replace(' ', '_')
    header = (
        f"# {title}\n\n"
        f"> **Zdroj:** https://www.wikiskripta.eu/w/{url_title}  \n"
        f"> **Licence:** Creative Commons BY 4.0\n\n---\n\n"
    )
    return header + text.strip() + "\n"


def run_download(output_dir: Path, delay: float, max_pages: int | None):
    """Spustí stahování – voláno v samostatném threadu."""
    session = requests.Session()
    session.headers.update({"User-Agent": "WikiSkriptaDownloader/1.0 (streamlit)"})
    output_dir.mkdir(parents=True, exist_ok=True)

    prog = read_progress()
    prog.update({"status": "running", "current": 0, "success": 0,
                 "errors": 0, "skipped": 0, "log": [],
                 "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 "finished_at": None, "output_dir": str(output_dir)})
    write_progress(prog)

    # Získej seznam stránek
    titles = []
    params = {"action": "query", "list": "allpages",
              "aplimit": 50, "apnamespace": 0, "format": "json"}
    try:
        while True:
            resp = session.get(API_URL, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            titles.extend(p["title"] for p in data["query"]["allpages"])
            prog["total"] = len(titles)
            write_progress(prog)
            if "continue" not in data:
                break
            params["apcontinue"] = data["continue"]["apcontinue"]
            if max_pages and len(titles) >= max_pages:
                titles = titles[:max_pages]
                break
            time.sleep(delay)
    except Exception as e:
        prog["status"] = "error"
        prog["log"].append(f"FATAL: {e}")
        write_progress(prog)
        return

    prog["total"] = len(titles)
    write_progress(prog)

    for i, title in enumerate(titles, 1):
        # Zkontroluj, zda nebyl download zastaven
        current = read_progress()
        if current.get("status") == "stopped":
            prog["status"] = "stopped"
            prog["finished_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            write_progress(prog)
            return

        filename = output_dir / f"{sanitize_filename(title)}.md"
        prog["current"] = i
        prog["current_title"] = title

        if filename.exists():
            prog["skipped"] += 1
            write_progress(prog)
            continue

        try:
            p2 = {"action": "query", "titles": title, "prop": "revisions",
                  "rvprop": "content", "rvslots": "main", "format": "json"}
            r2 = session.get(API_URL, params=p2, timeout=30)
            r2.raise_for_status()
            page = next(iter(r2.json()["query"]["pages"].values()))
            if "missing" in page:
                prog["errors"] += 1
                write_progress(prog)
                continue
            wikitext = page["revisions"][0]["slots"]["main"]["*"]
            md = wikitext_to_markdown(wikitext, title)
            filename.write_text(md, encoding="utf-8")
            prog["success"] += 1
        except Exception as e:
            prog["errors"] += 1
            entry = f"[{i}] CHYBA: {title[:40]} – {e}"
            prog["log"] = (prog["log"] + [entry])[-50:]  # max 50 záznamů

        write_progress(prog)
        time.sleep(delay)

    prog["status"] = "done"
    prog["finished_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prog["current_title"] = "✅ Hotovo!"
    write_progress(prog)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Nastavení")
    output_dir_str = st.text_input("📁 Výstupní složka", value=str(DEFAULT_OUT))
    delay = st.slider("⏱ Pauza mezi requesty (s)", 0.1, 2.0, 0.3, 0.05,
                      help="Respektuj server – nedoporučuji pod 0.2 s")
    test_mode = st.toggle("🧪 Testovací režim", value=False)
    max_pages = None
    if test_mode:
        max_pages = st.number_input("Max stránek", min_value=5, max_value=500,
                                    value=50, step=10)

    st.divider()
    st.markdown("""
    **O projektu**
    WikiSkripta je otevřená lékařská wiki pro studenty a učitele.
    Licence: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
    Zdroj: [wikiskripta.eu](https://www.wikiskripta.eu)
    """)

# ─── Hlavní oblast ────────────────────────────────────────────────────────────
st.markdown('<h1 class="app-title">🏥 WikiSkripta Knowledge Base Downloader</h1>', unsafe_allow_html=True)
st.caption("Stahuje obsah WikiSkripta.eu do Markdown souborů pro RAG / vektorizaci")
st.divider()

prog = read_progress()
status = prog.get("status", "idle")
output_dir = Path(output_dir_str)

# Počet stažených souborů na disku
md_files = sorted(output_dir.glob("*.md")) if output_dir.exists() else []
n_files = len([f for f in md_files if f.name != "_INDEX.md"])

tab_down, tab_files, tab_help = st.tabs(["📥 Stahování", "📁 Prohlížeč souborů", "📖 Jak použít"])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 – STAHOVÁNÍ
# ════════════════════════════════════════════════════════════════════════════
with tab_down:

    # Status badge
    badge_map = {
        "idle":    ("badge-idle",    "⏸ Nečinný"),
        "running": ("badge-running", "⚡ Probíhá"),
        "done":    ("badge-done",    "✅ Dokončeno"),
        "stopped": ("badge-yellow",  "⏹ Zastaveno"),
        "error":   ("badge-error",   "❌ Chyba"),
    }
    badge_cls, badge_txt = badge_map.get(status, ("badge-idle", status))
    st.markdown(
        f'<span class="status-badge {badge_cls}">{badge_txt}</span>',
        unsafe_allow_html=True,
    )

    if prog.get("started_at"):
        st.caption(f"Zahájeno: {prog['started_at']}"
                   + (f"  |  Dokončeno: {prog['finished_at']}" if prog.get("finished_at") else ""))

    st.write("")

    # Tlačítka
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
    with col_btn1:
        start_disabled = status == "running"
        if st.button("▶️ Spustit", disabled=start_disabled, use_container_width=True, type="primary"):
            if not is_running():
                # Reset a spusť thread
                PROGRESS_FILE.unlink(missing_ok=True)
                t = threading.Thread(
                    target=run_download,
                    args=(output_dir, delay, max_pages if test_mode else None),
                    daemon=True,
                )
                t.start()
                time.sleep(0.5)
                st.rerun()

    with col_btn2:
        stop_disabled = status != "running"
        if st.button("⏹ Zastavit", disabled=stop_disabled, use_container_width=True):
            p = read_progress()
            p["status"] = "stopped"
            write_progress(p)
            st.rerun()

    st.write("")

    # Progress bar
    total   = prog.get("total", 0)
    current = prog.get("current", 0)
    pct     = (current / total) if total > 0 else 0.0

    if total > 0:
        st.progress(pct, text=f"{current:,} / {total:,} stránek  ({pct*100:.1f} %)")
    else:
        st.progress(0.0, text="Čeká na spuštění…")

    if status == "running" and prog.get("current_title"):
        st.caption(f"📄 Zpracovávám: *{prog['current_title']}*")

    st.write("")

    # Metriky
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""<div class="metric-card green">
            <div class="metric-label">Staženo</div>
            <div class="metric-value">{prog.get('success', 0):,}</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Přeskočeno</div>
            <div class="metric-value">{prog.get('skipped', 0):,}</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="metric-card red">
            <div class="metric-label">Chyby</div>
            <div class="metric-value">{prog.get('errors', 0):,}</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class="metric-card yellow">
            <div class="metric-label">Celkem na disku</div>
            <div class="metric-value">{n_files:,}</div>
        </div>""", unsafe_allow_html=True)

    # Log chyb
    log_entries = prog.get("log", [])
    if log_entries:
        st.write("")
        st.markdown("**📋 Log chyb** (posledních 50)")
        log_html = "<br>".join(log_entries[-20:])
        st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)

    # Auto-refresh při běhu
    if status == "running":
        time.sleep(1.5)
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 – PROHLÍŽEČ SOUBORŮ
# ════════════════════════════════════════════════════════════════════════════
with tab_files:
    if not output_dir.exists() or n_files == 0:
        st.info("Žádné soubory zatím nebyly staženy. Spusťte stahování na záložce 📥.")
    else:
        st.markdown(f"**Nalezeno {n_files:,} souborů** ve složce `{output_dir}/`")
        st.write("")

        col_list, col_preview = st.columns([1, 2])

        with col_list:
            search = st.text_input("🔍 Hledat článek", placeholder="např. Pneumonie")

            # Filtruj soubory
            display_files = [f for f in md_files if f.name != "_INDEX.md"]
            if search:
                display_files = [f for f in display_files
                                 if search.lower() in f.stem.lower()]

            st.caption(f"Zobrazuji {min(len(display_files), 200)} z {len(display_files)} výsledků")

            # Inicializuj výběr
            if "selected_file" not in st.session_state:
                st.session_state.selected_file = None

            for f in display_files[:200]:
                label = f.stem[:45]
                if st.button(label, key=f"file_{f.name}", use_container_width=True):
                    st.session_state.selected_file = f

        with col_preview:
            sel = st.session_state.get("selected_file")
            if sel and sel.exists():
                content = sel.read_text(encoding="utf-8")
                word_count = len(content.split())
                char_count = len(content)
                c1, c2 = st.columns(2)
                c1.metric("Slov", f"{word_count:,}")
                c2.metric("Znaků", f"{char_count:,}")
                st.divider()
                st.markdown(content[:8000] + ("\n\n*(zkráceno…)*" if len(content) > 8000 else ""))
            else:
                st.info("← Vyber článek ze seznamu vlevo")

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 – NÁPOVĚDA
# ════════════════════════════════════════════════════════════════════════════
with tab_help:
    st.markdown("""
## 🚀 Jak začít

1. **Nastav výstupní složku** v postranním panelu (nebo nech výchozí `wikiskripta_markdown/`)
2. Klikni na **▶️ Spustit** – stahování začne na pozadí
3. Sleduj průběh pomocí progress baru a metrik
4. Po dokončení přejdi na záložku **📁 Prohlížeč souborů**

## 📦 Jak vektorizovat výstup

Každý stažený soubor je čistý Markdown s metadaty (zdroj, licence). Příklad s LangChain:

```python
from langchain.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# 1. Načti dokumenty
loader = DirectoryLoader(
    "wikiskripta_markdown/",
    glob="*.md",
    loader_cls=UnstructuredMarkdownLoader,
)
docs = loader.load()

# 2. Rozděl podle nadpisů
splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[
    ("#", "title"), ("##", "section"), ("###", "subsection")
])
chunks = []
for doc in docs:
    chunks.extend(splitter.split_text(doc.page_content))

# 3. Ulož do vektorové DB
vectorstore = Chroma.from_documents(
    chunks,
    embedding=OpenAIEmbeddings(),
    persist_directory="chroma_wikiskripta",
)
print(f"Vektorizováno {len(chunks)} chunků")
```

## ⚠️ Upozornění

- Stahování ~11 500 stránek trvá přibližně **1–2 hodiny**
- Aplikaci nech běžet (nebo spusť přes terminál: `streamlit run wikiskripta_app.py`)
- Pokud stahování přerušíš, můžeš ho **obnovit** – již stažené soubory se přeskočí
- Obsah podléhá licenci **Creative Commons BY 4.0** – uveď zdroj při dalším šíření
    """)
