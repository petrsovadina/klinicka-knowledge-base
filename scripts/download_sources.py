#!/usr/bin/env python3
"""
Download source documents for knowledge extraction.
Reads sources from metadata.json and downloads PDFs and webpages.
"""
import os
import json
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import re

# Determine project root relative to script location
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SOURCES_DIR = PROJECT_ROOT / "sources"
SOURCES_DIR.mkdir(exist_ok=True)


def download_file(url: str, filepath: Path, is_webpage: bool = False) -> bool:
    """Download a file or webpage from URL to filepath."""
    try:
        print(f"Downloading: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=60, stream=True, headers=headers)
        response.raise_for_status()

        if is_webpage:
            # Save HTML content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
        else:
            # Save binary content (PDF)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

        file_size = os.path.getsize(filepath) / 1024  # KB
        size_str = f"{file_size:.2f} KB" if file_size < 1024 else f"{file_size/1024:.2f} MB"
        print(f"✓ Downloaded: {filepath.name} ({size_str})")
        return True
    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP Error downloading {url}: {e}")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"✗ Connection Error downloading {url}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error downloading {url}: {e}")
        return False


def load_sources_from_metadata() -> list:
    """Load source definitions from metadata.json."""
    metadata_path = SOURCES_DIR / "metadata.json"
    if not metadata_path.exists():
        print(f"✗ Metadata file not found: {metadata_path}")
        return []

    with open(metadata_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data.get("sources", [])


def main():
    print("=" * 80)
    print("DOWNLOADING SOURCE DOCUMENTS")
    print(f"Sources directory: {SOURCES_DIR}")
    print("=" * 80)
    print()

    sources = load_sources_from_metadata()
    if not sources:
        print("No sources found in metadata.json")
        return

    print(f"Found {len(sources)} sources in metadata.json")
    print()

    downloaded = 0
    failed = 0
    skipped = 0

    for source in sources:
        filename = source.get("filename")
        url = source.get("url")
        name = source.get("name", filename)
        fmt = source.get("format", "pdf")

        if not filename or not url:
            print(f"⚠ Skipping invalid source (missing filename or url): {name}")
            continue

        filepath = SOURCES_DIR / filename
        is_webpage = fmt == "webpage" or filename.endswith('.html')

        # Skip if already exists and has content
        if filepath.exists():
            file_size = os.path.getsize(filepath)
            if file_size > 0:
                size_kb = file_size / 1024
                size_str = f"{size_kb:.2f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
                print(f"⊙ Already exists: {name} ({size_str})")
                skipped += 1
                continue

        # Download
        if download_file(url, filepath, is_webpage=is_webpage):
            downloaded += 1
        else:
            failed += 1

    print()
    print("=" * 80)
    print(f"SUMMARY: {downloaded} downloaded, {skipped} skipped, {failed} failed")
    print("=" * 80)

    # Update stats in metadata
    metadata_path = SOURCES_DIR / "metadata.json"
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    metadata["stats"] = {
        "downloaded": downloaded,
        "skipped": skipped,
        "failed": failed,
        "last_run": datetime.now().isoformat()
    }

    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"✓ Stats updated in: {metadata_path}")


if __name__ == "__main__":
    main()
