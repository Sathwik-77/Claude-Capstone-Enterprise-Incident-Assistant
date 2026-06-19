def chunk_document(document: dict, chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """
    Split a document into overlapping chunks.

    Args:
        document: dict with keys file_name, content, file_type
        chunk_size: number of characters per chunk
        overlap: number of characters to overlap between chunks

    Returns:
        list of chunk dicts with keys: file_name, file_type, chunk_number, content
    """
    content = document["content"]
    file_name = document["file_name"]
    file_type = document["file_type"]

    chunks = []
    start = 0
    chunk_number = 0

    while start < len(content):
        end = start + chunk_size
        chunk_text = content[start:end]

        if chunk_text.strip():
            chunks.append({
                "file_name": file_name,
                "file_type": file_type,
                "chunk_number": chunk_number,
                "content": chunk_text.strip()
            })
            chunk_number += 1

        start += chunk_size - overlap

    return chunks


def chunk_all_documents(documents: list[dict], chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """
    Chunk all loaded documents.

    Args:
        documents: list of document dicts from document_loader
        chunk_size: characters per chunk
        overlap: overlap between chunks

    Returns:
        flat list of all chunks across all documents
    """
    all_chunks = []

    for document in documents:
        chunks = chunk_document(document, chunk_size, overlap)
        all_chunks.extend(chunks)
        print(f"Chunked: {document['file_name']} → {len(chunks)} chunks")

    print(f"\nTotal chunks created: {len(all_chunks)}")
    return all_chunks