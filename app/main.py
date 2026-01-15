from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from mcp.server.sse import SseServerTransport

# --- NEW IMPORTS ---
from app.core.config import settings
from app.core.logging import setup_logging
from app.api import routes
from app.mcp.server import mcp
# -------------------

# 1. Setup Logging first
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)


@app.get("/health")
async def root_health():
    return {"status": "ok", "service": settings.PROJECT_NAME, "version": settings.VERSION}

# 2. Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Mount Routes
app.include_router(routes.router)

# 4. Mount MCP (SSE)
@app.get("/sse")
async def handle_sse(request: Request):
    transport = SseServerTransport("/messages")
    async with mcp.connect_sse(request.scope, request.receive, request._send) as streams:
        await mcp.run(streams[0], streams[1], transport)
    return EventSourceResponse(transport.incoming_messages())

@app.post("/messages")
async def handle_messages(request: Request):
    await mcp.handle_post_message(request.scope, request.receive, request._send)
