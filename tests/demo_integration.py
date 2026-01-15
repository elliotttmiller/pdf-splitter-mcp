from pathlib import Path
import asyncio


async def run_demo():
    # local import to avoid module-level side-effects and satisfy linters
    from integrations.pdf_service_client import PDFSplitterService

    service = PDFSplitterService("http://127.0.0.1:8000")
    try:
        pdf = Path("data") / "examples" / "Middleton Full w Options & Alt Elev - Base Plan - 2024 (1).pdf"
        if not pdf.exists():
            print("Demo PDF not found:", pdf)
            return

        pages = await service.process_manual(str(pdf))
        if pages:
            print("First 3 pages:", pages[:3])
            # download first page as a quick check
            await service.download_page(pages[0], f"downloaded_{pages[0]}")
    finally:
        await service.close()


if __name__ == '__main__':
    # Ensure repo root is on sys.path when running this script directly
    import sys

    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    asyncio.run(run_demo())
