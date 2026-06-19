import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.state import AgentState
from reliability.fallback_handler import call_claude_with_reliability
from reliability.structured_logger import start_trace, end_trace, log_error


SYSTEM_PROMPT = """You are an Incident Detection Agent specializing in cybersecurity.
Your job is to analyze security logs and identify suspicious events.

Look for:
- Failed login attempts and brute force patterns
- Unauthorized access attempts
- Privilege escalation
- New account creation with elevated permissions
- Disabled security controls (MFA, firewalls, audit logs)
- Unusual data downloads or exfiltration
- Suspicious process execution
- Ransomware indicators

Be specific and cite timestamps and usernames from the logs."""

AGENT_NAME = "Incident Agent"


def incident_agent(state: AgentState) -> AgentState:
    """
    Incident Agent: identifies suspicious events from retrieved evidence.
    """
    start = start_trace(state, AGENT_NAME)
    print(f"\n[{AGENT_NAME}] Analyzing for suspicious events...")

    chunks = state["retrieved_chunks"]
    if not chunks:
        state["findings"].append({
            "agent": AGENT_NAME,
            "findings": "No evidence retrieved to analyze."
        })
        end_trace(state, AGENT_NAME, 0)
        return state

    evidence = "\n\n".join([
        f"Source: {c['source']}\n{c['content']}" for c in chunks
    ])

    user_prompt = f"""Analyze the following security evidence and identify all suspicious incidents.

Query: {state['query']}

Evidence:
{evidence}

List each suspicious event with:
- Timestamp
- User/IP involved
- What happened
- Why it is suspicious"""

    try:
        response = call_claude_with_reliability(SYSTEM_PROMPT, user_prompt)
        state["findings"].append({
            "agent": AGENT_NAME,
            "findings": response
        })
    except Exception as e:
        log_error(AGENT_NAME, str(e))
        state["findings"].append({
            "agent": AGENT_NAME,
            "findings": f"Agent failed: {e}"
        })

    import time
    elapsed = time.time() - start
    end_trace(state, AGENT_NAME, elapsed)

    print(f"[{AGENT_NAME}] Analysis complete.")
    return state