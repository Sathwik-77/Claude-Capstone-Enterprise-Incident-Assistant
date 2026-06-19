import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.state import AgentState
from backend.vector_store import search_chunks
from reliability.structured_logger import start_trace, end_trace, log_error

AGENT_NAME = "Research Agent"


def researcher_agent(state: AgentState) -> AgentState:
    """
    Research Agent: retrieves relevant evidence from the knowledge base.
    """
    start = start_trace(state, AGENT_NAME)
    print(f"\n[{AGENT_NAME}] Retrieving evidence...")

    try:
        query = state["query"]
        results = search_chunks(query, top_k=5)

        chunks = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                chunks.append({
                    "source": metadata["file_name"],
                    "chunk": metadata["chunk_number"],
                    "content": doc
                })

        state["retrieved_chunks"] = chunks
        elapsed = time.time() - start
        end_trace(state, AGENT_NAME, elapsed, extra={"chunks_retrieved": len(chunks)})
        print(f"[{AGENT_NAME}] Retrieved {len(chunks)} chunks.")

    except Exception as e:
        log_error(AGENT_NAME, str(e))
        state["retrieved_chunks"] = []
        elapsed = time.time() - start
        end_trace(state, AGENT_NAME, elapsed)

    return state