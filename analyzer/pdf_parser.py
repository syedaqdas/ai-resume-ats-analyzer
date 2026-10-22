"""
PDF Parsing module for AI Resume ATS Analyzer.
Provides robust text extraction with fallback strategies and error diagnostics.
"""

import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Union

import pdfplumber
import pypdf


@dataclass
class PDFParseResult:
    """Holds the result of a PDF parsing operation."""
    text: str = ""
    num_pages: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_valid: bool = False
    is_scanned_image: bool = False
    error_message: Optional[str] = None


# Maximum allowable PDF size in bytes (15 MB)
MAX_FILE_BYTES = 15 * 1024 * 1024
# Maximum pages to extract for a resume document
MAX_RESUME_PAGES = 50


def extract_text_from_pdf(pdf_source: Union[str, Path, io.BytesIO, bytes, Any]) -> PDFParseResult:
    """
    Extracts text and metadata from a PDF file using pdfplumber with pypdf fallback.
    Safely handles corrupt files, password protection, empty documents, and scanned PDFs.

    Args:
        pdf_source: Path to PDF file, bytes, or file-like object (e.g. UploadedFile).

    Returns:
        PDFParseResult with extracted text, page count, and status flags.
    """
    # Normalize input into bytes stream if needed
    stream: io.BytesIO
    if isinstance(pdf_source, (str, Path)):
        path = Path(pdf_source)
        if not path.exists():
            return PDFParseResult(
                error_message=f"File not found: {path}",
                is_valid=False
            )
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                return PDFParseResult(
                    error_message=f"File size exceeds maximum limit of {MAX_FILE_BYTES // (1024 * 1024)}MB.",
                    is_valid=False
                )
            with open(path, "rb") as f:
                stream = io.BytesIO(f.read())
        except Exception as e:
            return PDFParseResult(
                error_message=f"Failed to read file from disk: {str(e)}",
                is_valid=False
            )
    elif isinstance(pdf_source, bytes):
        if len(pdf_source) > MAX_FILE_BYTES:
            return PDFParseResult(
                error_message=f"File size exceeds maximum limit of {MAX_FILE_BYTES // (1024 * 1024)}MB.",
                is_valid=False
            )
        stream = io.BytesIO(pdf_source)
    elif hasattr(pdf_source, "read"):
        # Handle Streamlit UploadedFile or io.BytesIO
        try:
            content = pdf_source.read()
            if hasattr(pdf_source, "seek"):
                pdf_source.seek(0)
            if len(content) > MAX_FILE_BYTES:
                return PDFParseResult(
                    error_message=f"File size exceeds maximum limit of {MAX_FILE_BYTES // (1024 * 1024)}MB.",
                    is_valid=False
                )
            stream = io.BytesIO(content)
        except Exception as e:
            return PDFParseResult(
                error_message=f"Failed to read file stream: {str(e)}",
                is_valid=False
            )
    else:
        return PDFParseResult(
            error_message="Invalid input type provided for PDF extraction.",
            is_valid=False
        )

    # Validate header magic bytes (%PDF)
    stream.seek(0)
    magic = stream.read(5)
    stream.seek(0)
    if not magic.startswith(b"%PDF"):
        return PDFParseResult(
            error_message="Invalid file format: File does not appear to be a valid PDF document.",
            is_valid=False
        )

    extracted_text = ""
    num_pages = 0
    metadata: Dict[str, Any] = {}
    used_engine = "none"

    # Primary Engine: pdfplumber
    try:
        with pdfplumber.open(stream) as pdf:
            num_pages = len(pdf.pages)
            if pdf.metadata:
                metadata = {str(k): str(v) for k, v in pdf.metadata.items()}
            page_texts = []
            for page_idx, page in enumerate(pdf.pages):
                if page_idx >= MAX_RESUME_PAGES:
                    break
                t = page.extract_text()
                if t:
                    page_texts.append(t)
            extracted_text = "\n\n".join(page_texts).strip()
            used_engine = "pdfplumber"
    except Exception as e_plumber:
        # Fallback Engine: pypdf
        try:
            stream.seek(0)
            reader = pypdf.PdfReader(stream)
            num_pages = len(reader.pages)
            if reader.metadata:
                metadata = {str(k): str(v) for k, v in reader.metadata.items()}
            page_texts = []
            for page_idx, p in enumerate(reader.pages):
                if page_idx >= MAX_RESUME_PAGES:
                    break
                t = p.extract_text()
                if t:
                    page_texts.append(t)
            extracted_text = "\n\n".join(page_texts).strip()
            used_engine = "pypdf"
        except pypdf.errors.FileNotDecryptedError:
            return PDFParseResult(
                error_message="PDF is password-protected or encrypted. Please remove encryption and re-upload.",
                is_valid=False
            )
        except Exception as e_pypdf:
            return PDFParseResult(
                error_message=f"Failed to parse PDF document: {str(e_pypdf)}",
                is_valid=False
            )

    # Check for empty or scanned image document
    if not extracted_text:
        # Check if fallback pypdf might have text if pdfplumber extracted nothing
        if used_engine == "pdfplumber":
            try:
                stream.seek(0)
                reader = pypdf.PdfReader(stream)
                page_texts = [p.extract_text() for p in reader.pages if p.extract_text()]
                extracted_text = "\n\n".join(page_texts).strip()
            except Exception:
                pass

    if not extracted_text:
        return PDFParseResult(
            text="",
            num_pages=num_pages,
            metadata=metadata,
            is_valid=False,
            is_scanned_image=True,
            error_message="No selectable text could be extracted. The document may be a scanned image or empty. Please upload a text-based PDF."
        )

    return PDFParseResult(
        text=extracted_text,
        num_pages=num_pages,
        metadata=metadata,
        is_valid=True,
        is_scanned_image=False,
        error_message=None
    )
