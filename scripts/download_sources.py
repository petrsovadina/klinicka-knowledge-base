#!/usr/bin/env python3
"""
Download source documents for Phase 2 knowledge extraction.
"""
import os
import requests
from pathlib import Path
from datetime import datetime

# Create sources directory
SOURCES_DIR = Path("/home/ubuntu/klinicka-knowledge-base/sources")
SOURCES_DIR.mkdir(exist_ok=True)

# Source documents to download
SOURCES = [
    {
        "name": "Úhradová vyhláška 2026",
        "url": "https://mzd.gov.cz/wp-content/uploads/2025/11/Uhradova_vyhlaska_2026.pdf",
        "filename": "uhradova_vyhlaska_2026.pdf",
        "year": 2026,
        "type": "decree"
    },
    {
        "name": "Úhradová vyhláška 2025",
        "url": "https://mzd.gov.cz/wp-content/uploads/2024/11/Uhradova-vyhlaska-2025.pdf",
        "filename": "uhradova_vyhlaska_2025.pdf",
        "year": 2025,
        "type": "decree"
    },
    {
        "name": "Odůvodnění k Úhradové vyhlášce 2025",
        "url": "https://www.lkcr.cz/doc/cms_library/uv-mz-zduvodneni-102013.pdf",
        "filename": "oduvodneni_uhradova_vyhlaska_2025.pdf",
        "year": 2025,
        "type": "explanation"
    },
    {
        "name": "Metodické doporučení PMÚ 2025",
        "url": "https://mzd.gov.cz/wp-content/uploads/2024/11/Metodicke-doporuceni-ke-stanoveni-predbezne-mesicni-uhrady-v-segmentu-ambulantnich-specialistu-v-roce-2025.pdf",
        "filename": "metodicke_doporuceni_pmu_2025.pdf",
        "year": 2025,
        "type": "methodology"
    }
]

def download_file(url, filepath):
    """Download a file from URL to filepath."""
    try:
        print(f"Downloading: {url}")
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
        print(f"✓ Downloaded: {filepath.name} ({file_size:.2f} MB)")
        return True
    except Exception as e:
        print(f"✗ Error downloading {url}: {e}")
        return False

def main():
    print("=" * 80)
    print("DOWNLOADING SOURCE DOCUMENTS FOR PHASE 2")
    print("=" * 80)
    print()
    
    downloaded = 0
    failed = 0
    skipped = 0
    
    for source in SOURCES:
        filepath = SOURCES_DIR / source["filename"]
        
        # Skip if already exists
        if filepath.exists():
            file_size = os.path.getsize(filepath) / (1024 * 1024)
            print(f"⊙ Already exists: {source['name']} ({file_size:.2f} MB)")
            skipped += 1
            continue
        
        # Download
        if download_file(source["url"], filepath):
            downloaded += 1
        else:
            failed += 1
    
    print()
    print("=" * 80)
    print(f"SUMMARY: {downloaded} downloaded, {skipped} skipped, {failed} failed")
    print("=" * 80)
    
    # Create metadata file
    metadata_path = SOURCES_DIR / "metadata.json"
    import json
    metadata = {
        "downloaded_at": datetime.now().isoformat(),
        "sources": SOURCES,
        "stats": {
            "downloaded": downloaded,
            "skipped": skipped,
            "failed": failed
        }
    }
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"✓ Metadata saved to: {metadata_path}")

if __name__ == "__main__":
    main()
