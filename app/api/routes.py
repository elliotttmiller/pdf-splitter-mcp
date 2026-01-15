from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool
import shutil
import uuid
import os
from pathlib import Path

from app.core.config import settings
from app.services.pdf_engine import PDFEngine

router = APIRouter()
processor = PDFEngine(settings.TEMP_DIRECTORY)


@router.get("/health")
async def health():
    return {"status": "ok", "service": settings.PROJECT_NAME, "version": settings.VERSION}


@router.post("/upload")
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    wait: bool = False,
):
    head = await file.read(10)
    if not processor.validate_header(head):
        raise HTTPException(400, "Not a PDF")
    await file.seek(0)

    file_id = f"input_{uuid.uuid4().hex}.pdf"
    file_path = settings.TEMP_DIRECTORY / file_id

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if wait:
        page_files, page_count = await process_split(file_id, file_path)
        background_tasks.add_task(cleanup_temp_files, days=7)
        return {
            "filename": file_id,
            "status": "completed",
            "pages": page_files,
            "page_count": page_count,
        }
    else:
        background_tasks.add_task(process_split, file_id, file_path)
        background_tasks.add_task(cleanup_temp_files, days=7)
        return {"filename": file_id, "status": "processing_started"}


async def process_split(file_id: str, path: Path):
    page_files, page_count = await run_in_threadpool(processor.split, path)
    # We intentionally do not keep in-memory mapping here. The filesystem
    # is the source-of-truth: callers can list pages by globbing the
    # TEMP_DIRECTORY for the generated page files.
    return page_files, page_count


@router.get("/pages/{filename}")
async def get_page(filename: str):
    file_path = settings.TEMP_DIRECTORY / os.path.basename(filename)
    if not file_path.exists():
        raise HTTPException(404, "Page not found")
    return FileResponse(file_path)


@router.get("/uploads/{file_id}/pages")
async def get_upload_pages(file_id: str):
    # Look up generated page files based on the input file id. We expect
    # per-page files to be named like '<base>_p1.pdf'. Use filesystem as state.
    base_id = Path(file_id).stem.replace("input_", "")
    matches = sorted(settings.TEMP_DIRECTORY.glob(f"{base_id}_p*.pdf"), key=lambda p: int(p.stem.split("_p")[-1]) if "_p" in p.stem else 0)
    if matches:
        page_names = [p.name for p in matches]
        return {"filename": file_id, "pages": page_names, "page_count": len(page_names)}

    input_path = settings.TEMP_DIRECTORY / file_id
    if input_path.exists():
        raise HTTPException(status_code=202, detail="Processing")

    raise HTTPException(404, "Upload not found")


def cleanup_temp_files(days: int = 7):
    import time

    cutoff = time.time() - (days * 86400)
    for p in settings.TEMP_DIRECTORY.iterdir():
        try:
            if p.is_file() and p.stat().st_mtime < cutoff:
                p.unlink()
        except Exception:
            continue
