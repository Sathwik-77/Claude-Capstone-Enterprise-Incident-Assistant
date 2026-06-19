import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.state import AgentState
from reliability.fallback_handler import call_claude_with_reliability
from reliability.structured_logger import start_trace, end_trace, log_error

SYSTEM_PROMPT = """You are a Security Report Writer specializing in incident investigation reports.
Your job is to produce a clear, professional, and structured incident investigation report.

The report must include:
1. Executive Summary
2. Evidence Retrieved
3. Incident Findings
4. Root Cause Analysis
5. Risk Assessment
6. Review Comments
7. Recommendations

Use clear headings and professional language suitable for both technical and non-technical audiences."""

AGENT_NAME = "Report Writer Agent"


def report_writer_agent(state: AgentState) -> AgentState:
    start = start_trace(state, AGENT_NAME)
    print(f"\n[{AGENT_NAME}] Generating final report...")

    findings_text = "\n\n".join([
        f"=== {f['agent']} ===\n{f['findings']}"
        for f in state["findings"]
    ])

    review_text = "\n".join(state["review_comments"]) if state["review_comments"] else "No review comments."
    sources = list({c["source"] for c in state["retrieved_chunks"]})

    user_prompt = f"""Generate a comprehensive incident investigation report based on the following.

User Query: {state['query']}

Evidence Sources:
{chr(10).join(f'- {s}' for s in sources)}

Agent Findings:
{findings_text}

Review Comments:
{review_text}

Write a professional incident investigation report with all required sections."""

    try:
        response = call_claude_with_reliability(SYSTEM_PROMPT, user_prompt, max_tokens=2048)
        state["final_report"] = response
    except Exception as e:
        log_error(AGENT_NAME, str(e))
        state["final_report"] = f"Report generation failed: {e}"

    elapsed = time.time() - start
    end_trace(state, AGENT_NAME, elapsed)
    print(f"[{AGENT_NAME}] Report generated.")
    return state