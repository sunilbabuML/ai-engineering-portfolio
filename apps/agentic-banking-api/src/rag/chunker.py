def chunk_documents(
    documents: list[dict],
    chunk_size: int = 400,
    chunk_overlap: int = 80,
) -> list[dict]:
    """Split documents into overlapping text chunks."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if not 0 <= chunk_overlap < chunk_size:
        raise ValueError("chunk_overlap must be between 0 and chunk_size")

    chunks = []
    step = chunk_size - chunk_overlap

    for document in documents:
        content = document["content"]
        chunk_number = 0

        for start in range(0, len(content), step):
            text = content[start:start + chunk_size]

            if not text.strip():
                continue

            chunk_number += 1

            chunks.append({
                "chunk_id": f"{document['metadata']['document_id']}-CHUNK-{chunk_number:03d}",
                "content": text,
                "source": document["source"],
                "metadata": document["metadata"].copy(),
                "start_char": start,
                "end_char": min(start + chunk_size, len(content)),
            })

            if start + chunk_size >= len(content):
                break

    return chunks
