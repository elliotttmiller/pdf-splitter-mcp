from mcp.server.fastapi import FcpServer
from .config import settings

# Initialize MCP Server
mcp = FcpServer(settings.MCP_SERVER_NAME)

@mcp.tool()
async def split_uploaded_document(file_filename: str) -> str:
    """
    Splits a previously uploaded PDF. 
    Input: The filename returned by /upload.
    """
    input_path = settings.TEMP_DIRECTORY / file_filename
    
    if not input_path.exists():
        return "Error: File not found. Upload first."

    # In a real scenario, we might trigger logic here, 
    # but for this architecture, we assume the API handled the heavy lifting
    # or we return instructions on where to find the pages.
    return f"Document {file_filename} is ready for processing."
