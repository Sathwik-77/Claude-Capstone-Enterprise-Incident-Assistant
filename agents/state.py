from typing import TypedDict


class AgentState(TypedDict):
    query: str
    retrieved_chunks: list
    findings: list
    review_comments: list
    final_report: str
    execution_trace: list