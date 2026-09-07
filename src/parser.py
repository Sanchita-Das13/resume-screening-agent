from pathlib import Path

import fitz
from docx import Document


def extract_pdf(path):
    """Extract text from a PDF file."""

    text = ""

    document = fitz.open(path)

    for page in document:
        text += page.get_text()

    document.close()

    return text


def extract_docx(path):
    """Extract text from a DOCX file."""

    document = Document(path)

    text = "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
    )

    return text


def extract_txt(path):
    """Extract text from a TXT file."""

    return Path(path).read_text(
        encoding="utf-8",
        errors="ignore"
    )


def extract_resume_text(path):
    """
    Extract resume text based on file extension.

    Supported formats:
    - PDF
    - DOCX
    - TXT
    """

    extension = Path(path).suffix.lower()

    if extension == ".pdf":
        return extract_pdf(path)

    elif extension == ".docx":
        return extract_docx(path)

    elif extension == ".txt":
        return extract_txt(path)

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )