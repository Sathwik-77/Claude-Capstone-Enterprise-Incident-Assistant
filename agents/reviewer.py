import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.state import AgentState
from reliability.fallback_handler import call_claude_with_reliability
from reliability.structured_logger import start_trace, end_trace, log_error

SYSTEM_PROMPT = """You are a Security Review Agent responsible for quality assurance.
Your job is to critically review the findings from other agents and identify:
- Missing evidence or gaps in analysis
- Inconsistencies between findings
- Additional context that should be investigated
- Whether the severity assessment is appropriate
- Whether root causes are sufficiently explained

Be constructive but thorough. Flag anything that needs further investigation."""

AGENT_NAME = "Reviewer Agent"


def reviewer_agent(state: AgentState) -> AgentState:
    start = start_trace(state, AGENT_NAME)
    print(f"\n[{AGENT_NAME}] Reviewing all findings...")

    all_findings = "\n\n".join([
        f"=== {f['agent']} ===\n{f['findings']}"
        for f in state["findings"]
    ])

    user_prompt = f"""Review the following security investigation findings.

Query: {state['query']}

All Findings:
{all_findings}

Provide review comments on:
1. Completeness - are there gaps or missing evidence?
2. Consistency - do the findings align with each other?
3. Severity - is the risk rating appropriate?
4. Recommendations - what additional steps are needed?"""

    try:
        response = call_claude_with_reliability(SYSTEM_PROMPT, user_prompt)
        state["review_comments"] = [response]
    except Exception as e:
        log_error(AGENT_NAME, str(e))
        state["review_comments"] = [f"Review failed: {e}"]

    elapsed = time.time() - start
    end_trace(state, AGENT_NAME, elapsed)
    print(f"[{AGENT_NAME}] Review complete.")
    return state