import fitz
import json
from pathlib import Path


def pdf_to_text(pdf_path):
    """Open one PDF and return all its text as one big string."""
    doc = fitz.open(pdf_path)
    pages = []

    for page in doc:
        pages.append(page.get_text())

    return "\n".join(pages)


def make_chunks(text, source_name, size=500, overlap=80):
    """Split text into overlapping chunks."""

    words = text.split()
    chunks = []

    start = 0

    while start < len(words):

        piece = words[start:start + size]

        chunks.append({
            "text": " ".join(piece),
            "source": source_name
        })

        start += size - overlap

    return chunks


all_chunks = []

for pdf_file in Path("data").glob("*.pdf"):

    print(f"Reading {pdf_file.name}...")

    text = pdf_to_text(pdf_file)

    chunks = make_chunks(text, pdf_file.name)

    all_chunks.extend(chunks)

    print(f"Created {len(chunks)} chunks")


with open("chunks.json", "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, ensure_ascii=False, indent=2)

print()
print(f"Done! Saved {len(all_chunks)} chunks to chunks.json")