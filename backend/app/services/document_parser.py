from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Protocol

from pypdf import PdfReader


class ParserError(Exception):
    pass


@dataclass(frozen=True)
class ParsedPage:
    page_number: int
    text: str
    extraction_confidence: float


@dataclass(frozen=True)
class ParsedDocument:
    pages: list[ParsedPage]
    parser_version: str
    error: str | None = None


class DocumentParser(Protocol):
    parser_version: str

    def parse(self, *, filename: str, content: bytes) -> ParsedDocument:
        ...


class OcrProvider(Protocol):
    def extract_text(self, *, filename: str, content: bytes) -> ParsedDocument:
        ...


class TxtDocumentParser:
    parser_version = "txt-parser-v0.1"

    def parse(self, *, filename: str, content: bytes) -> ParsedDocument:
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("utf-8", errors="replace")
        return ParsedDocument(
            pages=[ParsedPage(page_number=1, text=text, extraction_confidence=1.0)],
            parser_version=self.parser_version,
        )


class PdfDocumentParser:
    parser_version = "pdf-parser-pypdf-v0.1"

    def parse(self, *, filename: str, content: bytes) -> ParsedDocument:
        try:
            reader = PdfReader(BytesIO(content))
            pages = [
                ParsedPage(
                    page_number=index + 1,
                    text=page.extract_text() or "",
                    extraction_confidence=0.9,
                )
                for index, page in enumerate(reader.pages)
            ]
            return ParsedDocument(pages=pages, parser_version=self.parser_version)
        except Exception as exc:  # pypdf raises several concrete parser exceptions.
            raise ParserError(f"PDF parser failed for {filename}: {exc}") from exc


class DocxPlaceholderParser:
    parser_version = "docx-placeholder-parser-v0.1"

    def parse(self, *, filename: str, content: bytes) -> ParsedDocument:
        return ParsedDocument(
            pages=[ParsedPage(page_number=1, text="", extraction_confidence=0.0)],
            parser_version=self.parser_version,
            error="DOCX text extraction is not implemented in this iteration.",
        )


class ParserRegistry:
    def __init__(self) -> None:
        self.txt_parser = TxtDocumentParser()
        self.pdf_parser = PdfDocumentParser()
        self.docx_parser = DocxPlaceholderParser()

    def for_filename(self, filename: str, mime_type: str) -> DocumentParser:
        suffix = Path(filename).suffix.lower()
        if suffix == ".pdf" or mime_type == "application/pdf":
            return self.pdf_parser
        if suffix == ".txt" or mime_type.startswith("text/"):
            return self.txt_parser
        if (
            suffix == ".docx"
            or mime_type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            return self.docx_parser
        raise ParserError(f"Unsupported file type for {filename} ({mime_type})")
