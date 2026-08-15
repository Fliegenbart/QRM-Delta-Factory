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


#: Extensions the plain-text parser handles. Markdown belongs here because the
#: entire evaluation corpus is Markdown -- and until August 2026 it was NOT
#: here, which made the harness and the product disagree about what can be
#: ingested at all: the harness uploads .md with an explicit "text/markdown"
#: content type and parsed fine, while the same file dragged into the browser
#: arrives as "application/octet-stream" and was rejected outright. The case
#: still ran and still produced a review pack -- one assembled from four
#: documents whose text was never read.
_TEXT_SUFFIXES = frozenset({".txt", ".md", ".markdown", ".text"})
_DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


class ParserRegistry:
    def __init__(self) -> None:
        self.txt_parser = TxtDocumentParser()
        self.pdf_parser = PdfDocumentParser()
        self.docx_parser = DocxPlaceholderParser()

    def for_filename(self, filename: str, mime_type: str) -> DocumentParser:
        # The suffix decides first. A client-supplied content type is a hint,
        # not evidence: browsers report "application/octet-stream" (or nothing)
        # for plenty of formats they have no entry for, and no upload should
        # fail because of what the sender guessed about its own file.
        suffix = Path(filename).suffix.lower()
        if suffix == ".pdf":
            return self.pdf_parser
        if suffix in _TEXT_SUFFIXES:
            return self.txt_parser
        if suffix == ".docx":
            return self.docx_parser

        if mime_type == "application/pdf":
            return self.pdf_parser
        if mime_type.startswith("text/"):
            return self.txt_parser
        if mime_type == _DOCX_MIME:
            return self.docx_parser
        raise ParserError(f"Unsupported file type for {filename} ({mime_type})")
