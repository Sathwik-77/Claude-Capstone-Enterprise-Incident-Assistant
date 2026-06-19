import json
import os
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_ROOT / "logs" / "agent_structured_logs.jsonl"


def _ensure_log_dir():
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def log_event(agent: str, message: str, level: str = "INFO", extra: dict = None):
    """
    Write a structured log entry to agent_structured_logs.jsonl.

    Args:
        agent: name of the agent logging the event
        message: log message
        level: INFO / WARN / ERROR
        extra: optional additional fields
    """
    _ensure_log_dir()

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "level": level,
        "message": message
    }

    if extra:
        entry.update(extra)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def start_trace(state: dict, agent_name: str) -> float:
    """
    Log agent start and return start time.

    Args:
        state: AgentState dict
        agent_name: name of the agent

    Returns:
        start time as float
    """
    import time
    start = time.time()

    log_event(
        agent=agent_name,
        message=f"{agent_name} started",
        level="INFO",
        extra={"query": state.get("query", "")}
    )

    return start


def end_trace(state: dict, agent_name: str, elapsed: float, extra: dict = None):
    """
    Log agent completion and append to execution_trace in state.

    Args:
        state: AgentState dict
        agent_name: name of the agent
        elapsed: time taken in seconds
        extra: optional additional fields
    """
    trace_entry = {
        "agent": agent_name,
        "status": "completed",
        "duration": round(elapsed, 2)
    }

    if extra:
        trace_entry.update(extra)

    state["execution_trace"].append(trace_entry)

    log_event(
        agent=agent_name,
        message=f"{agent_name} completed",
        level="INFO",
        extra={"duration": round(elapsed, 2)}
    )


def log_error(agent: str, error: str):
    """
    Log an error event.

    Args:
        agent: name of the agent
        error: error message
    """
    log_event(
        agent=agent,
        message=f"{agent} encountered an error: {error}",
        level="ERROR",
        extra={"error": error}
    )