import httpx
import ast
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession


class PDFSplitterService:
    def __init__(self, service_url: str = "http://127.0.0.1:8000"):
        self.url = service_url
        self.http = httpx.AsyncClient(base_url=service_url, timeout=120.0)

    async def process_manual(self, file_path: str):
        """
        Full Workflow: 
        1. Uploads the PDF (HTTP)
        2. Asks MCP to verify/wait for split (SSE)
        3. Returns the list of page filenames
        """
        filename = file_path.split("\\")[-1]
        print(f"🚀 [Integration] Starting process for: {filename}")

        # Step 1: Upload (The "Muscle")
        try:
            with open(file_path, "rb") as f:
                # Use wait=false to let MCP handle the waiting/status
                resp = await self.http.post(
                    "/upload?wait=false",
                    files={"file": (filename, f, "application/pdf")},
                )
                resp.raise_for_status()
                data = resp.json()
                file_id = data["filename"]
                print(f"✅ [Integration] Uploaded as ID: {file_id}")
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return None

        # Step 2: Call MCP Tool (The "Brain")
        print("🧠 [Integration] Connecting to MCP to track status...")
        # Note: use trailing slash to avoid 307 redirect from the server
        async with sse_client(f"{self.url}/sse/") as (read, write):
            # Wrap streams in a ClientSession which provides high-level helpers
            session = ClientSession(read, write)
            await session.initialize()
            result = await session.call_tool(
                "split_document",
                arguments={"file_id": file_id},
            )

            tool_output = result.content[0].text

            if "Error" in tool_output:
                print(f"❌ MCP Error: {tool_output}")
                return None

            try:
                page_files = ast.literal_eval(tool_output)
                print(f"✅ [Integration] MCP confirmed {len(page_files)} pages ready.")
                return page_files
            except Exception:
                print(f"⚠️ Could not parse MCP response: {tool_output}")
                return tool_output

    async def download_page(self, page_filename: str, output_path: str):
        resp = await self.http.get(f"/pages/{page_filename}")
        if resp.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(resp.content)
            print(f"📥 Saved {page_filename} -> {output_path}")
        else:
            print(f"❌ Failed to download page: {resp.status_code}")

    async def close(self):
        await self.http.aclose()
