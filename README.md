# PDF Splitter MCP

Quick start (PowerShell on Windows):

1. Create the project and venv (run from project root):

```powershell
python -m venv .venv
# Activate (PowerShell)
.\.venv\Scripts\Activate.ps1
# If execution policy prevents script running, run as admin:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Start the server (in VSCode press F5 with the provided launch config or run):

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

4. Test the upload flow (keep server running in separate terminal):

```powershell
python test_setup.py
```

Notes:
- The project uses `data/temp` for temporary file storage. That directory is created by `app/config.py` on import.
- The MCP package is required for MCP agent functionality. If not available, you can stub out or comment the MCP-related code while developing the API endpoints.
 - The MCP package is required for MCP agent functionality. If not available, you can stub out or comment the MCP-related code while developing the API endpoints.

Dependency conflict note
------------------------

You may see an error when running `pip install -r requirements.txt` similar to:

```
ERROR: ResolutionImpossible: fastapi 0.110.0 depends on starlette<0.37.0 and >=0.36.3
but mcp 1.0.0 depends on starlette>=0.39
```

Workarounds:
- Easiest (recommended for local dev): the `mcp` line is commented out in `requirements.txt`. Run `pip install -r requirements.txt` again and continue developing the API endpoints. Install `mcp` later when you have a compatible set of packages.
- Alternative: remove the FastAPI version pin to let pip try to find a FastAPI that is compatible with `mcp` (may upgrade to a newer FastAPI which requires a newer Starlette). This can introduce other incompatibilities.
- If you have access to a specific compatible version of `mcp` (or vendor wheel), install that specific package instead.

If you want, I can try to re-run `pip install -r requirements.txt` here after commenting `mcp` so we can confirm the install succeeds.

Next steps:
- Create a virtual environment and install the requirements.
- Run the server and test the `/upload` endpoint using `test_setup.py`.
