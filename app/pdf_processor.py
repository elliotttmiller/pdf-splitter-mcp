import uuid
from pathlib import Path
from pypdf import PdfReader, PdfWriter

class PDFProcessor:
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir

    def validate_header(self, file_head: bytes) -> bool:
        return file_head.startswith(b'%PDF-')

    def split_pdf(self, input_path: Path):
        """CPU-bound task"""
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
