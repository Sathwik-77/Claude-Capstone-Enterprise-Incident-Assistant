import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.state import AgentState
from reliability.fallback_handler import call_claude_with_reliability
from reliability.structured_logger import start_trace, end_trace, log_error

SYSTEM_PROMPT = """You are a Risk Assessment Agent specializing in cybersecurity.
Your job is to evaluate the severity and business impact of security incidents.

Use the following severity levels:
- Critical: Immediate threat to business operations, data breach confirmed, ransomware active
- High: Significant security control bypassed, privilege escalation, data exfiltration suspected
- Medium: Multiple failed attempts, policy violations, unauthorized access attempts
- Low: Single policy violation, minor anomaly, no confirmed impact

Consider:
- Confidentiality impact (data exposed)
- Integrity impact (data modified)
- Availability impact (systems disrupted)
- Regulatory implications (GDPR, ISO 27001)
- Business continuity risk"""

AGENT_NAME = "Risk Agent"


def risk_agent(state: AgentState) -> AgentState:
    start = start_trace(state, AGENT_NAME)
    print(f"\n[{AGENT_NAME}] Evaluating risk and severity...")

    incident_findings = next(
        (f["findings"] for f in state["findings"] if f["agent"] == "Incident Agent"),
        "No incident findings available."
    )
    root_cause_findings = next(
        (f["findings"] for f in state["findings"] if f["agent"] == "Root Cause Agent"),
        "No root cause findings available."
    )

    user_prompt = f"""Evaluate the risk and severity of the following security incidents.

Query: {state['query']}

Incident Findings:
{incident_findings}

Root Cause Findings:
{root_cause_findings}

Provide:
- Overall severity rating (Critical/High/Medium/Low)
- CIA impact assessment (Confidentiality, Integrity, Availability)
- Business impact summary
- Regulatory implications
- Recommended immediate actions"""

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
    print(f"[{AGENT_NAME}] Assessment complete.")
    return state