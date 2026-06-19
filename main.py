import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.orchestrator import run_investigation, run_investigation_parallel


def print_results(state, mode):
    print("\n" + "=" * 60)
    print(f"FINAL REPORT ({mode})")
    print("=" * 60)
    print(state["final_report"])

    print("\n" + "=" * 60)
    print(f"EXECUTION TRACE ({mode})")
    print("=" * 60)
    for trace in state["execution_trace"]:
        duration = trace.get("duration", "N/A")
        print(f"  {trace['agent']:<25} {trace['status']:<12} {duration}s")

    total = sum(t.get("duration", 0) for t in state["execution_trace"])
    print(f"\n  Total time: {round(total, 2)}s")


def main():
    query = "Investigate failed login attempts and suspicious admin activity"

    # Choose mode: change to run_investigation for sequential
    print("\nRunning PARALLEL mode...")
    state = run_investigation_parallel(query)
    print_results(state, "PARALLEL")


if __name__ == "__main__":
    main()