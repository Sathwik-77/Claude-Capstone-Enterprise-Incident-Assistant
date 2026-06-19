import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.state import AgentState
from agents.researcher import researcher_agent
from agents.incident_agent import incident_agent
from agents.root_cause_agent import root_cause_agent
from agents.risk_agent import risk_agent
from agents.reviewer import reviewer_agent
from agents.report_writer import report_writer_agent


def run_investigation(query: str) -> AgentState:
    """
    Run the full SEQUENTIAL incident investigation pipeline.

    Flow:
    Research Agent → Incident Agent → Root Cause Agent →
    Risk Agent → Reviewer Agent → Report Writer Agent
    """
    print("\n" + "=" * 60)
    print("ENTERPRISE INCIDENT INVESTIGATION ASSISTANT")
    print("Mode: Sequential")
    print("=" * 60)
    print(f"Query: {query}")
    print("=" * 60)

    state: AgentState = {
        "query": query,
        "retrieved_chunks": [],
        "findings": [],
        "review_comments": [],
        "final_report": "",
        "execution_trace": []
    }

    state = researcher_agent(state)
    state = incident_agent(state)
    state = root_cause_agent(state)
    state = risk_agent(state)
    state = reviewer_agent(state)
    state = report_writer_agent(state)

    return state


def run_investigation_parallel(query: str) -> AgentState:
    """
    Run the incident investigation pipeline with PARALLEL middle agents.

    Flow:
    Research Agent
        ↓
    ┌─────────────────────────────┐
    │ Incident Agent              │
    │ Root Cause Agent  (parallel)│
    │ Risk Agent                  │
    └─────────────────────────────┘
        ↓
    Reviewer Agent
        ↓
    Report Writer Agent
    """
    print("\n" + "=" * 60)
    print("ENTERPRISE INCIDENT INVESTIGATION ASSISTANT")
    print("Mode: Parallel")
    print("=" * 60)
    print(f"Query: {query}")
    print("=" * 60)

    state: AgentState = {
        "query": query,
        "retrieved_chunks": [],
        "findings": [],
        "review_comments": [],
        "final_report": "",
        "execution_trace": []
    }

    # Step 1: Research Agent (sequential — others depend on its output)
    state = researcher_agent(state)

    # Step 2: Run Incident, Root Cause, Risk agents in parallel
    print("\n[Orchestrator] Running Incident, Root Cause, Risk agents in parallel...")

    def run_incident(s):
        import copy
        local_state = copy.deepcopy(s)
        return incident_agent(local_state)

    def run_root_cause(s):
        import copy
        local_state = copy.deepcopy(s)
        return root_cause_agent(local_state)

    def run_risk(s):
        import copy
        local_state = copy.deepcopy(s)
        return risk_agent(local_state)

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(run_incident, state): "Incident Agent",
            executor.submit(run_root_cause, state): "Root Cause Agent",
            executor.submit(run_risk, state): "Risk Agent",
        }

        for future in as_completed(futures):
            agent_name = futures[future]
            try:
                result = future.result()
                # Merge findings and trace from each parallel agent
                state["findings"].extend(result["findings"])
                state["execution_trace"].extend(result["execution_trace"])
                print(f"[Orchestrator] {agent_name} finished.")
            except Exception as e:
                print(f"[Orchestrator] {agent_name} failed: {e}")

    # Step 3: Reviewer and Report Writer (sequential — depend on all findings)
    state = reviewer_agent(state)
    state = report_writer_agent(state)

    return state