#!/usr/bin/env python3
"""
Specialized extraction for Ambulatory Specialists (AS) methodology 2026.
Extracts knowledge units from Úhradová vyhláška 2026, focused on §7 and Příloha č. 3.

Focus areas:
- Hodnoty bodu (point values) for different specialties
- Bonifikace (bonuses) and their conditions
- PURO limits and calculations
- Regulační omezení (regulatory limits)
"""
import os
import sys
import json
import subprocess
import uuid
from pathlib import Path
from datetime import datetime
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

# Paths - Updated for local environment
BASE_DIR = Path("/Users/petrsovadina/Desktop/Develope/personal/klinicka-knowledge-base")
SOURCES_DIR = BASE_DIR / "sources"
SCHEMA_PATH = BASE_DIR / "schemas/knowledge_unit.schema.json"
OUTPUT_DIR = BASE_DIR / "data/extracted"
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Document metadata
DOCUMENT_METADATA = {
    "name": "Úhradová vyhláška 2026 - Ambulantní specialisté",
    "url": "https://mzd.gov.cz/wp-content/uploads/2025/11/Uhradova_vyhlaska_2026.pdf",
    "year": 2026,
    "retrieved_at": "2026-02-03T00:00:00Z"
}

# Specialized extraction prompt for ambulatory specialists
EXTRACTION_PROMPT = """Jsi expert na české zdravotnictví a úhradové mechanismy. Extrahuj znalostní jednotky z textu Úhradové vyhlášky 2026 zaměřené na ambulantní specialisty.

TEXT:
{text}

KONTEXT: Úhradová vyhláška 2026 - Příloha č. 3 (Ambulantní specialisté)

FOKUS EXTRAKCE:
1. HODNOTY BODU - konkrétní hodnoty v Kč pro jednotlivé odbornosti
2. BONIFIKACE - navýšení hodnoty bodu za splnění podmínek (vzdělávání, ordinační hodiny, noví pacienti, objednávkový systém)
3. PURO LIMIT - vzorce pro výpočet maximální úhrady, definice proměnných
4. REGULAČNÍ OMEZENÍ - limity na předepsané léky, vyžádanou péči
5. KALKULAČNÍ VZORCE - matematické vzorce pro výpočty

Pro každou identifikovanou znalostní jednotku vytvoř JSON objekt:
{{
  "id": "{uuid_prefix}-XXX",
  "type": "rule|exception|risk|anti_pattern|condition|definition",
  "domain": "uhrady",
  "title": "Stručný název (50-150 znaků)",
  "description": "Detailní vysvětlení pravidla nebo vzorce (100-500 znaků)",
  "version": "2026",
  "source": {{"name": "Úhradová vyhláška 2026 - Ambulantní specialisté", "url": "https://mzd.gov.cz/wp-content/uploads/2025/11/Uhradova_vyhlaska_2026.pdf", "retrieved_at": "{retrieved_at}"}},
  "content": {{
    "hodnota_bodu": "X.XX Kč" (pokud relevantní),
    "odbornosti": ["XXX", "YYY"] (pokud relevantní),
    "vzorec": "matematický vzorec" (pokud relevantní),
    "podminka": "popis podmínky" (pokud relevantní),
    "navyseni": "X.XX Kč" (pokud relevantní)
  }},
  "applicability": {{"specialties": ["XXX"] nebo ["all"], "valid_from": "2026-01-01", "valid_to": "2026-12-31"}},
  "related_units": [],
  "tags": ["ambulantní_specialisté", "hodnota_bodu", "bonifikace", ...]
}}

VÝSTUP: Pouze validní JSON objekty, jeden na řádek (JSONL formát). Bez markdown bloků, bez komentářů.
Extrahuj 3-8 jednotek z tohoto textu.
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

def extract_appendix3_content(full_text):
    """Extract content specifically from Příloha č. 3 (pages related to AS)."""
    lines = full_text.split('\n')

    # Find start of Příloha č. 3
    start_idx = None
    end_idx = None

    for i, line in enumerate(lines):
        if 'Příloha č. 3' in line and 'vyhlášce' in line:
            start_idx = i
        elif start_idx and 'Příloha č. 4' in line and 'vyhlášce' in line:
            end_idx = i
            break

    if start_idx is None:
        print("Warning: Could not find Příloha č. 3, using full text")
        return full_text

    if end_idx is None:
        end_idx = min(start_idx + 2000, len(lines))  # Take about 2000 lines after start

    appendix3_text = '\n'.join(lines[start_idx:end_idx])
    print(f"Extracted Příloha č. 3: lines {start_idx} to {end_idx} ({end_idx - start_idx} lines)")
    return appendix3_text

def chunk_text(text, max_chars=10000):
    """Split text into chunks for processing."""
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

def extract_with_llm(text, chunk_id):
    """Use LLM to extract knowledge units."""
    uuid_prefix = f"ku-as-2026-{chunk_id:03d}"

    prompt = EXTRACTION_PROMPT.format(
        text=text[:8000],  # Limit text length
        uuid_prefix=uuid_prefix,
        retrieved_at=DOCUMENT_METADATA["retrieved_at"]
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use mini for cost-effectiveness
            messages=[
                {"role": "system", "content": "Jsi expert na české zdravotnictví a úhradové vyhlášky. Extrahuj strukturované znalostní jednotky. Vracíš pouze validní JSON objekty, jeden na řádek."},
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
                    # Fix common issues
                    line = line.rstrip(',')
                    unit = json.loads(line)

                    # Ensure valid UUID format
                    if not unit.get('id') or not is_valid_uuid_format(unit['id']):
                        unit['id'] = str(uuid.uuid4())

                    units.append(unit)
                except json.JSONDecodeError as e:
                    print(f"  JSON parse error: {e}")
                    continue

        return units, response.usage

    except Exception as e:
        print(f"Error calling LLM: {e}")
        return [], None

def is_valid_uuid_format(s):
    """Check if string looks like a UUID or valid ID."""
    try:
        uuid.UUID(s)
        return True
    except (ValueError, AttributeError):
        # Allow custom ID formats like ku-as-2026-001
        return s.startswith('ku-')

def process_document():
    """Process the payment decree document."""
    print(f"\n{'='*80}")
    print(f"EXTRACTION: Ambulatory Specialists Methodology 2026")
    print(f"{'='*80}\n")

    pdf_path = SOURCES_DIR / "uhradova_vyhlaska_2026.pdf"
    output_path = OUTPUT_DIR / "vzp_metodika_as_2026.jsonl"

    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)

    # Extract text from PDF
    print("Step 1: Extracting text from PDF...")
    full_text = extract_text_from_pdf(pdf_path)
    if not full_text:
        print("Error: Could not extract text from PDF")
        sys.exit(1)
    print(f"  Total text: {len(full_text):,} characters")

    # Extract Příloha č. 3 content
    print("\nStep 2: Extracting Příloha č. 3 (Ambulatory Specialists)...")
    as_text = extract_appendix3_content(full_text)
    print(f"  Relevant text: {len(as_text):,} characters")

    # Chunk the text
    print("\nStep 3: Chunking text for processing...")
    chunks = chunk_text(as_text, max_chars=8000)
    print(f"  Created {len(chunks)} chunks")

    # Process each chunk
    print("\nStep 4: Extracting knowledge units with LLM...")
    all_units = []
    total_input_tokens = 0
    total_output_tokens = 0

    with open(output_path, 'w', encoding='utf-8') as f:
        for i, chunk in enumerate(chunks, 1):
            print(f"\n  Processing chunk {i}/{len(chunks)}...")
            units, usage = extract_with_llm(chunk, i)

            if usage:
                total_input_tokens += usage.prompt_tokens
                total_output_tokens += usage.completion_tokens

            for unit in units:
                f.write(json.dumps(unit, ensure_ascii=False) + '\n')
                f.flush()
                all_units.append(unit)

            print(f"    Extracted {len(units)} units (total: {len(all_units)})")

    # Print statistics
    print(f"\n{'='*80}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*80}")
    print(f"  Total units extracted: {len(all_units)}")
    print(f"  Output file: {output_path}")
    print(f"  Input tokens: {total_input_tokens:,}")
    print(f"  Output tokens: {total_output_tokens:,}")

    # Estimate cost (GPT-4o-mini pricing)
    input_cost = total_input_tokens * 0.00015 / 1000
    output_cost = total_output_tokens * 0.0006 / 1000
    total_cost = input_cost + output_cost
    print(f"  Estimated cost: ${total_cost:.4f}")

    # Analyze extracted unit types
    type_counts = {}
    for unit in all_units:
        t = unit.get('type', 'unknown')
        type_counts[t] = type_counts.get(t, 0) + 1

    print(f"\nUnit types:")
    for t, count in sorted(type_counts.items()):
        print(f"    {t}: {count}")

    return len(all_units)

if __name__ == "__main__":
    process_document()
