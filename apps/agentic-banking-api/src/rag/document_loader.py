from pathlib import Path
import re


def extract_metadata(text: str) -> dict:
    """Extract metadata from a banking policy document."""

    title_match = re.search(r"^# (.+)$", text, re.MULTILINE)
    id_match = re.search(r"^Document ID:\s*(.+)$", text, re.MULTILINE)
    version_match = re.search(r"^Version:\s*(.+)$", text, re.MULTILINE)

    return {
        "title": title_match.group(1).strip() if title_match else "Untitled",
        "document_id": id_match.group(1).strip() if id_match else "UNKNOWN",
        "version": version_match.group(1).strip() if version_match else "UNKNOWN",
    }


def load_documents(directory: str | Path) -> list[dict]:
    """Load Markdown policy documents from a directory."""

    directory = Path(directory)

    if not directory.is_dir():
        raise FileNotFoundError(f"Knowledge base directory not found: {directory}")

    documents = []

    for file_path in sorted(directory.glob("*.md")):
        text = file_path.read_text(encoding="utf-8-sig")
        metadata = extract_metadata(text)

        documents.append({
            "source": file_path.name,
            "content": text,
            "metadata": metadata,
        })

    return documents
