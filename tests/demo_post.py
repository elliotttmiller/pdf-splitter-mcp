import time
import httpx
from pathlib import Path

URL = "http://127.0.0.1:8000/upload?wait=true"
PDF = Path("data") / "examples" / "Middleton Full w Options & Alt Elev - Base Plan - 2024 (1).pdf"

if not PDF.exists():
    print(f"Demo PDF not found: {PDF}")
    raise SystemExit(1)

client = httpx.Client(timeout=120.0)

for attempt in range(10):
    try:
        with open(PDF, "rb") as f:
            files = {"file": (PDF.name, f, "application/pdf")}
            print(f"Posting {PDF} to {URL} (attempt {attempt+1})...")
            resp = client.post(URL, files=files)
        print("Status code:", resp.status_code)
        try:
            print("JSON response:", resp.json())
        except Exception:
            print("Text response:", resp.text)
        break
    except httpx.ConnectError as e:
        print("Connection failed, retrying...", e)
        time.sleep(0.5)
else:
    print("Failed to connect to the server after retries")
