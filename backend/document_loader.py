import os
from pathlib import Path


def load_documents(knowledge_base_path: str) -> list[dict]:
    """
    Load all documents from the KnowledgeBase directory.
    Supports .pdf and .txt files.
    Returns a list of dicts with keys: file_name, content, file_type
    """
    documents = []
    kb_path = Path(knowledge_base_path)

    if not kb_path.exists():
        raise FileNotFoundError(f"KnowledgeBase path not found: {kb_path}")

    for file in kb_path.iterdir():
        if file.is_file():
            if file.suffix.lower() == ".pdf":
                content = _load_pdf(file)
                file_type = "pdf"
            elif file.suffix.lower() == ".txt":
                content = _load_txt(file)
                file_type = "txt"
            else:
                continue

            if content:
                documents.append({
                    "file_name": file.name,
                    "content": content,
                    "file_type": file_type
                })
                print(f"Loaded: {file.name} ({file_type})")

    print(f"\nTotal documents loaded: {len(documents)}")
    return documents


def _load_pdf(file_path: Path) -> str:
    """Extract text from a PDF file using pypdf."""
    try:
        import pypdf
        reader = pypdf.PdfReader(str(file_path))
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error loading PDF {file_path.name}: {e}")
        return ""


def _load_txt(file_path: Path) -> str:
    """Read a plain text file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error loading TXT {file_path.name}: {e}")
        return ""
