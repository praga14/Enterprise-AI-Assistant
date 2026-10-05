from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


def extract_text(file_path: str, file_type: str) -> str:
    path = Path(file_path)

    if file_type in {"txt", "md"}:
        return path.read_text(encoding="utf-8")

    if file_type == "pdf":
        reader = PdfReader(str(path))

        text = []

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text.append(page_text)

        return "\n".join(text)

    if file_type == "docx":
        document = DocxDocument(str(path))

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(paragraphs)

    raise ValueError(f"Unsupported file type: {file_type}")