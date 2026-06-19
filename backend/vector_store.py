import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VECTOR_DB_PATH = str(PROJECT_ROOT / "vector_db")
COLLECTION_NAME = "incident_knowledge_base"


def get_client():
    """Get a persistent ChromaDB client."""
    return chromadb.PersistentClient(path=VECTOR_DB_PATH)


def get_collection():
    """Get or create the ChromaDB collection with default embedding function."""
    client = get_client()
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn
    )
    return collection


def store_chunks(chunks: list[dict]):
    """
    Store all chunks into ChromaDB.

    Args:
        chunks: list of chunk dicts from chunker.py
    """
    collection = get_collection()

    documents = []
    metadatas = []
    ids = []

    for i, chunk in enumerate(chunks):
        documents.append(chunk["content"])
        metadatas.append({
            "file_name": chunk["file_name"],
            "file_type": chunk["file_type"],
            "chunk_number": chunk["chunk_number"]
        })
        ids.append(f"{chunk['file_name']}_chunk_{chunk['chunk_number']}_{i}")

    collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print(f"Stored {len(chunks)} chunks into ChromaDB collection: {COLLECTION_NAME}")


def search_chunks(question: str, top_k: int = 5) -> dict:
    """
    Search the ChromaDB collection for relevant chunks.

    Args:
        question: search query string
        top_k: number of results to return

    Returns:
        ChromaDB query result dict
    """
    collection = get_collection()

    results = collection.query(
        query_texts=[question],
        n_results=top_k
    )

    return results


def search_incidents(query: str, top_k: int = 5) -> list[dict]:
    """
    Search specifically for incident log entries.

    Args:
        query: search query string
        top_k: number of results to return

    Returns:
        list of relevant incident chunks
    """
    collection = get_collection()

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where={"file_type": "txt"}
    )

    output = []
    if results and results["documents"]:
        for i, doc in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i]
            output.append({
                "source": metadata["file_name"],
                "chunk": metadata["chunk_number"],
                "content": doc
            })

    return output


def list_logs() -> list[str]:
    """
    List all incident log files stored in the vector DB.

    Returns:
        list of unique log file names
    """
    collection = get_collection()
    results = collection.get(where={"file_type": "txt"})

    if not results or not results["metadatas"]:
        return []

    file_names = list({m["file_name"] for m in results["metadatas"]})
    return sorted(file_names)