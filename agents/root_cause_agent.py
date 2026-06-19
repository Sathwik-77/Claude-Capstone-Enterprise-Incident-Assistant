import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.state import AgentState
from reliability.fallback_handler import call_claude_with_reliability
from reliability.structured_logger import start_trace, end_trace, log_error

SYSTEM_PROMPT = """You are a Root Cause Analysis Agent specializing in cybersecurity investigations.
Your job is to determine the underlying causes of security incidents.

Consider possible root causes such as:
- Brute-force or credential stuffing attacks
- Compromised credentials
- Insider threat or malicious insider activity
- Misconfiguration of security controls
- Malware or ransomware infection
- Social engineering or phishing
- Lack of security controls (no MFA, weak password policy)
- Insufficient monitoring and alerting

Be analytical and explain your reasoning based on the evidence."""

AGENT_NAME = "Root Cause Agent"


def root_cause_agent(state: AgentState) -> AgentState:
    start = start_trace(state, AGENT_NAME)
    print(f"\n[{AGENT_NAME}] Determining root causes...")

    incident_findings = next(
        (f["findings"] for f in state["findings"] if f["agent"] == "Incident Agent"),
        "No incident findings available."
    )

    chunks = state["retrieved_chunks"]
    evidence = "\n\n".join([
        f"Source: {c['source']}\n{c['content']}" for c in chunks
    ])

    user_prompt = f"""Based on the incident findings and evidence below, determine the root causes.

Query: {state['query']}

Incident Findings:
{incident_findings}

Supporting Evidence:
{evidence}

For each root cause provide:
- Root cause description
- Supporting evidence
- Likelihood (High/Medium/Low)"""

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

    elapsed = time.time() - start
    end_trace(state, AGENT_NAME, elapsed)
    print(f"[{AGENT_NAME}] Analysis complete.")
    return state