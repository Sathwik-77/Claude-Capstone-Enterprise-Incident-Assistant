import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def with_fallback(fallback_func):
    """
    Decorator that calls a fallback function if the primary function fails.

    Args:
        fallback_func: function to call if primary fails

    Example:
        @with_fallback(fallback_func=rag_fallback)
        def call_claude(...):
            ...
    """
    import functools

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"[Fallback] Primary function '{func.__name__}' failed: {e}")
                print(f"[Fallback] Switching to fallback...")
                return fallback_func(*args, **kwargs)

        return wrapper
    return decorator


def rag_fallback(system_prompt: str, user_prompt: str, max_tokens: int = 1024) -> str:
    """
    RAG-based fallback when LLM call fails.
    Searches the knowledge base and returns a structured response
    based on retrieved chunks instead of calling Claude.

    Args:
        system_prompt: ignored in fallback
        user_prompt: used as search query
        max_tokens: ignored in fallback

    Returns:
        Fallback response string based on RAG results
    """
    from backend.vector_store import search_chunks

    print("[Fallback] Using RAG fallback response...")

    try:
        results = search_chunks(user_prompt[:200], top_k=3)

        if results and results["documents"] and results["documents"][0]:
            chunks = []
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i]
                chunks.append(f"[Source: {meta['file_name']}]\n{doc}")

            fallback_response = (
                "⚠️ LLM unavailable — RAG Fallback Response:\n\n"
                "Based on retrieved evidence from the knowledge base:\n\n"
                + "\n\n---\n\n".join(chunks)
            )
            return fallback_response

        return "⚠️ LLM unavailable and no relevant evidence found in knowledge base."

    except Exception as e:
        return f"⚠️ Both LLM and RAG fallback failed: {e}"


def call_claude_with_reliability(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 1024,
    max_retries: int = 3,
    timeout_seconds: float = 60.0
) -> str:
    """
    Call Claude with full reliability chain:
    Primary LLM → Retry → Timeout → Fallback to RAG

    Args:
        system_prompt: agent system prompt
        user_prompt: user query
        max_tokens: max response tokens
        max_retries: number of retries before fallback
        timeout_seconds: timeout per attempt

    Returns:
        Response string from Claude or fallback
    """
    from agents.llm_client import call_claude
    from reliability.retry_handler import retry_call
    from reliability.timeout_handler import timeout_call, TimeoutError

    for attempt in range(1, max_retries + 1):
        try:
            print(f"[Reliability] Attempt {attempt}/{max_retries}...")
            result = timeout_call(
                call_claude,
                system_prompt,
                user_prompt,
                max_tokens,
                seconds=timeout_seconds
            )
            return result

        except TimeoutError as e:
            print(f"[Reliability] Timeout on attempt {attempt}: {e}")

        except Exception as e:
            print(f"[Reliability] Error on attempt {attempt}: {e}")

    # All retries exhausted — use RAG fallback
    print("[Reliability] All retries exhausted. Using RAG fallback.")
    return rag_fallback(system_prompt, user_prompt, max_tokens)