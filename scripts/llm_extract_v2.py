#!/usr/bin/env python3
"""
LLM-assisted extraction v2 with progressive writing and optimizations.
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

# Paths
SOURCES_DIR = Path("/home/ubuntu/klinicka-knowledge-base/sources")
SCHEMA_PATH = Path("/home/ubuntu/klinicka-knowledge-base/schemas/knowledge_unit.schema.json")
OUTPUT_DIR = Path("/home/ubuntu/klinicka-knowledge-base/data/extracted")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Load JSON schema
with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
    SCHEMA = json.load(f)

# Extraction prompt template (shorter, more focused)
EXTRACTION_PROMPT = """Jsi expert na české zdravotnictví. Extrahuj znalostní jednotky z textu.

TEXT:
{text}

KONTEXT: {document_name} ({year})

ÚKOL:
Identifikuj pravidla, výjimky, rizika, anti-patterny, podmínky a definice.
Pro každou jednotku vytvoř JSON objekt s těmito poli:
- id: "ku-XXX-slug" (použij čísla od {start_id})
- type: rule|exception|risk|anti_pattern|condition|definition
- domain: uhrady|provoz|compliance|financni-rizika|legislativa
- title: Stručný název (50-150 znaků)
- description: Detailní vysvětlení (100-500 znaků)
- version: "{year}"
- source: {{"name": "{document_name}", "url": "{source_url}", "retrieved_at": "{retrieved_at}"}}
- content: Strukturovaný obsah dle typu
- applicability: {{"specialties": ["all"], "valid_from": "{year}-01-01", "valid_to": null}}
- related_units: []
- tags: [klíčová slova]

VÝSTUP: Pouze validní JSON objekty, jeden na řádek. Bez markdown bloků.
"""

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pdftotext."""
    try:
        result = subprocess.run(
            ['pdftotext', '-layout', str(pdf_path), '-'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error extracting text: {e}")
        return None

def chunk_text(text, max_chars=12000):
    """Split text into larger chunks for efficiency."""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) < max_chars:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = para + "\n\n"
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def extract_with_llm(text, document_name, year, source_url, retrieved_at, start_id):
    """Use LLM to extract knowledge units."""
    prompt = EXTRACTION_PROMPT.format(
        text=text,
        document_name=document_name,
        year=year,
        source_url=source_url,
        retrieved_at=retrieved_at,
        start_id=start_id
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",  # Faster model
            messages=[
                {"role": "system", "content": "Jsi expert na české zdravotnictví. Vracíš pouze validní JSON objekty."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=4000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse JSON Lines
        units = []
        for line in content.split('\n'):
            line = line.strip()
            if line and line.startswith('{'):
                try:
                    unit = json.loads(line)
                    units.append(unit)
                except json.JSONDecodeError:
                    continue
        
        return units
    
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return []

def process_document(pdf_path, metadata, output_path):
    """Process document with progressive writing."""
    print(f"\n{'='*80}")
    print(f"Processing: {metadata['name']}")
    print(f"{'='*80}\n")
    
    # Extract text
    print("Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return 0
    
    print(f"✓ Extracted {len(text):,} characters")
    
    # Chunk text (larger chunks = fewer API calls)
    chunks = chunk_text(text, max_chars=12000)
    print(f"✓ Split into {len(chunks)} chunks")
    
    # Open output file for progressive writing
    total_units = 0
    start_id = 22  # Continue from last ID
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, chunk in enumerate(chunks, 1):
            print(f"\nProcessing chunk {i}/{len(chunks)}...")
            units = extract_with_llm(
                text=chunk,
                document_name=metadata['name'],
                year=metadata['year'],
                source_url=metadata['url'],
                retrieved_at=metadata.get('retrieved_at', '2025-12-14T00:00:00Z'),
                start_id=start_id
            )
            
            # Write immediately
            for unit in units:
                f.write(json.dumps(unit, ensure_ascii=False) + '\n')
                f.flush()  # Force write to disk
                start_id += 1
            
            total_units += len(units)
            print(f"✓ Extracted {len(units)} units (total: {total_units})")
    
    return total_units

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 llm_extract_v2.py <pdf_filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    pdf_path = SOURCES_DIR / filename
    
    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)
    
    # Load metadata
    metadata_path = SOURCES_DIR / "metadata.json"
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata_all = json.load(f)
    
    doc_metadata = None
    for source in metadata_all['sources']:
        if source['filename'] == filename:
            doc_metadata = source
            doc_metadata['retrieved_at'] = metadata_all['downloaded_at']
            break
    
    if not doc_metadata:
        print(f"Error: Metadata not found")
        sys.exit(1)
    
    # Process
    output_filename = pdf_path.stem + "_v2_extracted.jsonl"
    output_path = OUTPUT_DIR / output_filename
    
    total = process_document(pdf_path, doc_metadata, output_path)
    
    print(f"\n{'='*80}")
    print(f"✓ EXTRACTION COMPLETE")
    print(f"Total units: {total}")
    print(f"Saved to: {output_path}")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
