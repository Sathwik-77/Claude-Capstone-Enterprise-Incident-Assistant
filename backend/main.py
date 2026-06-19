from pathlib import Path
from document_loader import load_documents
from chunker import chunk_all_documents
from vector_store import store_chunks, search_chunks

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_PATH = str(PROJECT_ROOT / "KnowledgeBase")


def main():
    print("=" * 50)
    print("ENTERPRISE INCIDENT INVESTIGATION ASSISTANT")
    print("Phase 1: Indexing Knowledge Base")
    print("=" * 50)

    # Step 1: Load documents
    print("\n[1/3] Loading documents...")
    documents = load_documents(KNOWLEDGE_BASE_PATH)

    if not documents:
        print("No documents found in KnowledgeBase. Exiting.")
        return

    # Step 2: Chunk documents
    print("\n[2/3] Chunking documents...")
    chunks = chunk_all_documents(documents, chunk_size=500, overlap=50)

    # Step 3: Store in ChromaDB
    print("\n[3/3] Storing chunks in ChromaDB...")
    store_chunks(chunks)

    # Step 4: Quick verification search
    print("\n[Verification] Testing search...")
    results = search_chunks("failed login attempts", top_k=3)

    if results and results["documents"]:
        print("\nTop 3 results for 'failed login attempts':")
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            print(f"\n  [{i+1}] Source: {meta['file_name']} | Chunk: {meta['chunk_number']}")

            print(f"       {doc[:150]}...")
    else:
        print("No results found.")

    print("\n✅ Phase 1 complete! Knowledge base indexed successfully.")


if __name__ == "__main__":
    main()