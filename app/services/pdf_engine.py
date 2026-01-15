import uuid
from pathlib import Path
from pypdf import PdfReader, PdfWriter


class PDFEngine:
    """Pure PDF processing logic.

    This class is intentionally independent from FastAPI or MCP. It takes an
    input Path and returns generated page filenames. This makes it easy to
    unit test and to run in worker processes.
    """

    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir

    def validate_header(self, file_head: bytes) -> bool:
        return file_head.startswith(b"%PDF-")

    def split(self, input_path: Path):
        """Split input PDF into per-page PDF files and return list of filenames.

        Returns (page_files, page_count)
        """
        try:
            reader = PdfReader(str(input_path))
            page_files = []
            base_id = uuid.uuid4().hex[:8]

            for i, page in enumerate(reader.pages):
                writer = PdfWriter()
                writer.add_page(page)
                filename = f"{base_id}_p{i+1}.pdf"
                output_path = self.temp_dir / filename
                with open(output_path, "wb") as f:
                    writer.write(f)
                page_files.append(filename)

            return page_files, len(reader.pages)
        except Exception as e:
            raise RuntimeError(f"PDF Error: {str(e)}")
