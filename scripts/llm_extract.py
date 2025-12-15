#!/usr/bin/env python3
"""
LLM-assisted extraction of knowledge units from source documents.
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from openai import OpenAI

# Initialize OpenAI client (API key from environment)
client = OpenAI()

# Paths
SOURCES_DIR = Path("/home/ubuntu/klinicka-knowledge-base/sources")
SCHEMA_PATH = Path("/home/ubuntu/klinicka-knowledge-base/schemas/knowledge_unit.schema.json")
OUTPUT_DIR = Path("/home/ubuntu/klinicka-knowledge-base/data/extracted")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Load JSON schema
with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
    SCHEMA = json.load(f)

# Extraction prompt template
EXTRACTION_PROMPT = """Jsi expert na české zdravotnictví a úhradové mechanismy ambulantní péče. Tvým úkolem je extrahovat znalostní jednotky z následujícího textu.

TEXT Z DOKUMENTU:
{text}

KONTEXT:
- Dokument: {document_name}
- Rok: {year}
- Zdroj: {source_url}

ÚKOL:
1. Pečlivě přečti text a identifikuj všechna:
   - Pravidla (rule): podmínka → důsledek
   - Výjimky (exception): situace, kdy se pravidlo neuplatňuje
   - Rizika (risk): potenciální negativní dopady
   - Anti-patterny (anti_pattern): typické chyby a jejich důsledky
   - Podmínky (condition): kritéria, která musí být splněna
   - Definice (definition): vysvětlení důležitých termínů

2. Pro každou znalostní jednotku vytvoř JSON objekt s těmito poli:
   - id: ve formátu "ku-XXX-slug" (použij další volné číslo od 016)
   - type: rule|exception|risk|anti_pattern|condition|definition
   - domain: uhrady|provoz|compliance|financni-rizika|legislativa
   - title: Jasný, stručný název (50-150 znaků)
   - description: Detailní vysvětlení (100-500 znaků)
   - version: "{year}"
   - source: {{
       "name": "{document_name}",
       "url": "{source_url}",
       "retrieved_at": "{retrieved_at}"
     }}
   - content: Strukturovaný obsah dle typu (viz příklady níže)
   - applicability: {{
       "specialties": ["all" nebo konkrétní kódy],
       "valid_from": "{year}-01-01",
       "valid_to": null
     }}
   - related_units: [] (můžeš nechat prázdné, propojíme později)
   - tags: [relevantní klíčová slova]

3. PŘÍKLADY STRUKTURY CONTENT:

Pro type="rule":
{{
  "condition": "Když...",
  "consequence": "Pak...",
  "impact": "Dopad je...",
  "calculation_example": "Příklad výpočtu..."
}}

Pro type="exception":
{{
  "exception": "Co je vyjmuto...",
  "exempted_from": ["Seznam pravidel"],
  "still_subject_to": ["Seznam pravidel"],
  "change_from_previous_year": "Změna oproti..."
}}

Pro type="risk":
{{
  "risk": "Riziko je...",
  "affected_providers": "Postihuje...",
  "impact_level": "Vysoké|Střední|Nízké",
  "mitigation": "Lze se vyhnout..."
}}

DŮLEŽITÉ PRAVIDLA:
- Extrahuj POUZE faktické informace z textu, nevymýšlej
- Každá jednotka musí být atomická (jedna myšlenka)
- Používej profesionální, přesný jazyk
- Uvádej konkrétní čísla, procenta, částky
- Pokud text neobsahuje relevantní znalosti, vrať prázdný seznam

VÝSTUP:
Vrať pouze validní JSON objekty, jeden na řádek (JSON Lines formát).
Nezačínej ani nekončíš markdown blokem (```json), pouze čisté JSON objekty.
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
        print(f"Error extracting text from {pdf_path}: {e}")
        return None

def chunk_text(text, max_chars=8000):
    """Split text into chunks for LLM processing."""
    # Simple chunking by paragraphs
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

def extract_with_llm(text, document_name, year, source_url, retrieved_at):
    """Use LLM to extract knowledge units from text."""
    prompt = EXTRACTION_PROMPT.format(
        text=text,
        document_name=document_name,
        year=year,
        source_url=source_url,
        retrieved_at=retrieved_at
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Jsi expert na české zdravotnictví a strukturování znalostí. Vracíš pouze validní JSON objekty."},
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
                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to parse JSON line: {e}")
                    continue
        
        return units
    
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return []

def process_document(pdf_path, metadata):
    """Process a single document and extract knowledge units."""
    print(f"\n{'='*80}")
    print(f"Processing: {metadata['name']}")
    print(f"{'='*80}\n")
    
    # Extract text
    print("Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("✗ Failed to extract text")
        return []
    
    text_length = len(text)
    print(f"✓ Extracted {text_length:,} characters")
    
    # Chunk text
    chunks = chunk_text(text, max_chars=8000)
    print(f"✓ Split into {len(chunks)} chunks")
    
    # Extract from each chunk
    all_units = []
    for i, chunk in enumerate(chunks, 1):
        print(f"\nProcessing chunk {i}/{len(chunks)}...")
        units = extract_with_llm(
            text=chunk,
            document_name=metadata['name'],
            year=metadata['year'],
            source_url=metadata['url'],
            retrieved_at=metadata.get('retrieved_at', '2025-12-14T00:00:00Z')
        )
        print(f"✓ Extracted {len(units)} knowledge units from chunk {i}")
        all_units.extend(units)
    
    return all_units

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 llm_extract.py <pdf_filename>")
        print("\nAvailable documents:")
        metadata_path = SOURCES_DIR / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                for source in metadata['sources']:
                    print(f"  - {source['filename']}: {source['name']}")
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
    
    # Find document metadata
    doc_metadata = None
    for source in metadata_all['sources']:
        if source['filename'] == filename:
            doc_metadata = source
            doc_metadata['retrieved_at'] = metadata_all['downloaded_at']
            break
    
    if not doc_metadata:
        print(f"Error: Metadata not found for {filename}")
        sys.exit(1)
    
    # Process document
    units = process_document(pdf_path, doc_metadata)
    
    # Save results
    output_filename = pdf_path.stem + "_extracted.jsonl"
    output_path = OUTPUT_DIR / output_filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for unit in units:
            f.write(json.dumps(unit, ensure_ascii=False) + '\n')
    
    print(f"\n{'='*80}")
    print(f"✓ EXTRACTION COMPLETE")
    print(f"Total units extracted: {len(units)}")
    print(f"Saved to: {output_path}")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
