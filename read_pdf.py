from pathlib import Path
from pypdf import PdfReader

folder = Path(".")

for pdf_file in folder.glob("*.pdf"):
    print(f"\n{'='*60}")
    print(f"Reading: {pdf_file.name}")
    print(f"{'='*60}")

    reader = PdfReader(pdf_file)

    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    print(text[:1000])  # Print only the first 1000 characters