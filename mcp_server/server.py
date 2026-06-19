import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server.fastmcp import FastMCP
from backend.vector_store import search_incidents, list_logs, search_chunks
from agents.orchestrator import run_investigation

mcp = FastMCP("Enterprise Incident Investigation Assistant")


@mcp.tool()
def search_incidents_tool(query: str) -> list[dict]:
    """
    Search incident logs for relevant entries matching the query.

    Args:
        query: search term e.g. 'failed login', 'ransomware', 'privilege escalation'

    Returns:
        List of matching incident log chunks with source and content
    """
    results = search_incidents(query, top_k=5)
    return results


@mcp.tool()
def list_logs_tool() -> list[str]:
    """
    List all incident log files available in the knowledge base.

    Returns:
        List of log file names
    """
    return list_logs()


@mcp.tool()
def investigate_incident(query: str) -> dict:
    """
    Run a full multi-agent incident investigation and return the report.

    This tool runs the complete pipeline:
    Research Agent → Incident Agent → Root Cause Agent →
    Risk Agent → Reviewer Agent → Report Writer Agent

    Args:
        query: description of the incident to investigate
               e.g. 'Investigate failed login attempts and suspicious admin activity'

    Returns:
        dict with final_report and execution_trace
    """
    state = run_investigation(query)
    return {
        "final_report": state["final_report"],
        "execution_trace": state["execution_trace"]
    }


if __name__ == "__main__":
    mcp.run()