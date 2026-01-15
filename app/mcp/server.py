import asyncio
from mcp.server import Server
from pathlib import Path

from app.core.config import settings
from app.services.pdf_engine import PDFEngine

# Initialize MCP Server
mcp = Server(settings.MCP_SERVER_NAME)
processor = PDFEngine(settings.TEMP_DIRECTORY)


def _sort_pages_by_number(paths: list[Path]) -> list[Path]:
    def page_index(p: Path) -> int:
        try:
            return int(p.stem.split("_p")[-1])
        except Exception:
            return 0

    return sorted(paths, key=page_index)


@mcp.call_tool()
async def split_document(file_id: str) -> str:
    """Splits a previously uploaded PDF and returns a stringified list of pages.

    Implements a "smart wait": first checks the in-memory uploads_map, then
    waits for a short time and finally falls back to scanning the temp
    directory for files created after the input file's modification time.
    """
    input_path = settings.TEMP_DIRECTORY / file_id

    # 1. Validation
    if not input_path.exists():
        return "Error: File not found. Please upload the document first."

    # Use filesystem as the source-of-truth. Attempt to find generated page
    # files that follow the naming convention '<base>_pN.pdf'. Wait briefly for
    # the processor to produce files (smart-wait).
    base_id = Path(file_id).stem.replace("input_", "")

    for _ in range(10):
        try:
            candidates = list(settings.TEMP_DIRECTORY.glob(f"{base_id}_p*.pdf"))
            if candidates:
                sorted_pages = _sort_pages_by_number(candidates)
                page_names = [p.name for p in sorted_pages]
                return str(page_names)
        except Exception:
            # ignore filesystem errors and continue waiting
            pass

        await asyncio.sleep(0.5)

    return "Error: Processing is taking longer than expected. Please try again in a moment."
