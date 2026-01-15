"""Service layer package - pure business logic, no HTTP or MCP dependencies."""

from .pdf_engine import PDFEngine

__all__ = ["PDFEngine"]
