import shutil
import uuid
import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool
from sse_starlette.sse import EventSourceResponse
from mcp.server.sse import SseServerTransport

from .config import settings
from .pdf_processor import PDFProcessor
from .mcp_agent import mcp

app = FastAPI(title="PDF Splitter MCP")
processor = PDFProcessor(settings.TEMP_DIRECTORY)
# Shared SSE transport for MCP endpoints
transport = SseServerTransport("/messages")

@app.post("/upload")
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    # 1. Validate
    head = await file.read(10)
    if not processor.validate_header(head):
        raise HTTPException(400, "Not a PDF")
    await file.seek(0)

    # 2. Save
    file_id = f"input_{uuid.uuid4().hex}.pdf"
    file_path = settings.TEMP_DIRECTORY / file_id
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. Process in Background (Non-blocking)
    background_tasks.add_task(process_split, file_path)

    return {"filename": file_id, "status": "processing_started"}

async def process_split(path: Path):
    await run_in_threadpool(processor.split_pdf, path)

@app.get("/pages/{filename}")
async def get_page(filename: str):
    file_path = settings.TEMP_DIRECTORY / os.path.basename(filename)
    if not file_path.exists():
        raise HTTPException(404, "Page not found")
    return FileResponse(file_path)

# --- MCP SSE Endpoints ---
@app.get("/sse")
async def handle_sse(request: Request):
    # Use the shared transport to establish an SSE connection. The transport
    # will start the EventSourceResponse itself inside the context manager.
    async with transport.connect_sse(request.scope, request.receive, request._send) as streams:
        # Use the Server API's initialization options when running the MCP server
        await mcp.run(streams[0], streams[1], mcp.create_initialization_options())
    # The response is handled by the transport; return an empty 200 response
    return {}

@app.post("/messages")
async def handle_messages(request: Request):
    # Delegate incoming POSTed client messages to the shared transport so
    # they are routed to the correct in-memory session created by `connect_sse`.
    await transport.handle_post_message(request.scope, request.receive, request._send)
