import httpx
from pathlib import Path
import sys
import random

# Pick a random PDF from data/examples
examples_dir = Path("data") / "examples"
if not examples_dir.exists():
    print(f"Examples directory not found at: {examples_dir!r}. Please create it and add PDF files.")
    sys.exit(1)

pdfs = list(examples_dir.glob("*.pdf"))
if not pdfs:
    print(f"No PDF files found in {examples_dir!r}. Add some example PDFs and try again.")
    sys.exit(1)

selected = random.choice(pdfs)
print(f"Selected example PDF: {selected}")

# Upload
url = "http://127.0.0.1:8000"
with open(selected, "rb") as fh:
    files = {"file": fh}
    resp = httpx.post(f"{url}/upload", files=files)

print("Upload Status:", resp.status_code)
try:
    print("Response:", resp.json())
except Exception:
    print("Response text:", resp.text)
