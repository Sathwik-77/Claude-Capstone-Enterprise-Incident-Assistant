import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import json
import plotly.graph_objects as go
from agents.orchestrator import run_investigation, run_investigation_parallel

st.set_page_config(
    page_title="Incident Investigation",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* App background */
.stApp { background-color: #F8F9FA; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #EBEBEB !important;
}
[data-testid="stSidebar"] section { padding: 1.5rem 1rem !important; }
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label { color: #6B7280 !important; font-size: 0.78rem !important; }

/* Sidebar sample buttons */
[data-testid="stSidebar"] .stButton button {
    background: #FFFFFF !important;
    border: 1px solid #EBEBEB !important;
    color: #374151 !important;
    font-size: 0.75rem !important;
    border-radius: 6px !important;
    text-align: left !important;
    padding: 7px 10px !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.15s, background 0.15s !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #F3F4F6 !important;
    border-color: #D1D5DB !important;
    color: #111827 !important;
}

/* Remove default Streamlit header padding */
.block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }

/* Textarea */
.stTextArea textarea {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 8px !important;
    color: #111827 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    line-height: 1.55 !important;
    resize: none !important;
}
.stTextArea textarea:focus {
    border-color: #38BDF8 !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.12) !important;
}
.stTextArea label {
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    color: #9CA3AF !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}

/* Primary run button */
.stButton [kind="primary"] {
    background: #38BDF8 !important;
    border: 1px solid #38BDF8 !important;
    border-radius: 7px !important;
    color: #0C4A6E !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    padding: 9px 22px !important;
    transition: opacity 0.15s !important;
}
.stButton [kind="primary"]:hover { opacity: 0.85 !important; }

/* Metric cards */
[data-testid="metric-container"] {
    background: #FFFFFF !important;
    border: 1px solid #F3F4F6 !important;
    border-radius: 10px !important;
    padding: 14px 18px !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: #9CA3AF !important;
    font-size: 0.7rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #0EA5E9 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1.4rem !important;
    font-weight: 600 !important;
}

/* Alerts / severity banners */
.stAlert {
    border-radius: 8px !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    border-width: 1px !important;
}

/* Expanders */
[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid #F3F4F6 !important;
    border-radius: 8px !important;
    margin-bottom: 6px !important;
}
[data-testid="stExpander"] summary {
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: #374151 !important;
    padding: 10px 14px !important;
}
[data-testid="stExpander"] .stMarkdown {
    font-size: 0.83rem !important;
    color: #4B5563 !important;
    line-height: 1.65 !important;
    padding: 4px 4px 8px !important;
}

/* Dividers */
hr { border-color: #F3F4F6 !important; margin: 18px 0 !important; }

/* Spinner */
.stSpinner > div { border-top-color: #38BDF8 !important; }

/* Radio */
.stRadio label { font-size: 0.8rem !important; color: #374151 !important; }

/* Checkbox */
.stCheckbox label { font-size: 0.76rem !important; color: #6B7280 !important; }

/* Success toast */
.stSuccess {
    background: #F0FDF4 !important;
    border: 1px solid #BBF7D0 !important;
    color: #166534 !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
}

/* Subheader */
h3 {
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    color: #111827 !important;
    letter-spacing: -0.01em !important;
}

/* Trace text */
.stText, pre {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.73rem !important;
    background: #F9FAFB !important;
    color: #6B7280 !important;
    border-radius: 4px;
}

/* Sidebar section labels */
.sidebar-label {
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #D1D5DB;
    margin: 18px 0 8px;
    padding-bottom: 5px;
    border-bottom: 1px solid #F3F4F6;
}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:#FFFFFF;border:1px solid #F3F4F6;border-radius:12px;padding:22px 28px;margin-bottom:20px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
  <div>
    <div style="font-size:1.15rem;font-weight:600;color:#111827;letter-spacing:-0.02em;margin-bottom:3px;">
      🛡️ Incident Investigation
    </div>
    <div style="font-size:0.76rem;color:#9CA3AF;">
      Multi-agent analysis pipeline · Powered by Claude
    </div>
  </div>
  <div style="display:inline-flex;align-items:center;gap:6px;background:#F0FDF4;border:1px solid #BBF7D0;border-radius:99px;padding:5px 12px;font-size:0.72rem;font-weight:500;color:#166534;">
    <span style="width:6px;height:6px;border-radius:50%;background:#22C55E;display:inline-block;"></span>
    System ready
  </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-label">Execution mode</div>', unsafe_allow_html=True)
    mode = st.radio(
        "",
        ["Sequential", "Parallel"],
        index=1,
        help="Parallel runs Incident, Root Cause and Risk agents at the same time"
    )

    st.markdown('<div class="sidebar-label">Sample queries</div>', unsafe_allow_html=True)
    queries = [
        "Failed login attempts & suspicious admin activity",
        "Ransomware indicators & data exfiltration",
        "Privilege escalation & unauthorized accounts",
        "Insider activity & data theft",
    ]
    for q in queries:
        if st.button(q, use_container_width=True):
            st.session_state["query"] = q

    st.markdown('<div class="sidebar-label">Logs</div>', unsafe_allow_html=True)
    log_file = PROJECT_ROOT / "logs" / "agent_structured_logs.jsonl"
    if log_file.exists():
        with open(log_file) as f:
            lines = f.readlines()
        if st.checkbox("Show last 20 entries"):
            for line in lines[-20:]:
                try:
                    e = json.loads(line)
                    icon = {"INFO": "●", "WARN": "▲", "ERROR": "✕"}.get(e.get("level","INFO"), "●")
                    st.text(f"{icon} [{e['agent']}] {e['message']}")
                except Exception:
                    pass
    else:
        st.caption("No log file found.")

# ── Query input ────────────────────────────────────────────────────────────────
query = st.text_area(
    "// Query",
    value=st.session_state.get("query", "Investigate failed login attempts and suspicious admin activity"),
    height=85,
)

c1, c2 = st.columns([1, 7])
with c1:
    run_btn = st.button("▶  Run", type="primary", use_container_width=True)
with c2:
    st.markdown(
        f'<div style="padding-top:10px;font-size:0.72rem;color:#9CA3AF;">'
        f'Mode: <strong style="color:#374151;">{mode}</strong></div>',
        unsafe_allow_html=True
    )

# ── Investigation ──────────────────────────────────────────────────────────────
if run_btn and query:
    with st.spinner("Running pipeline…"):
        if mode == "Parallel":
            state = run_investigation_parallel(query)
        else:
            state = run_investigation(query)

    st.success("Investigation complete.")
    st.divider()

    # ── Metrics ───────────────────────────────────────────────────────────────
    trace = state["execution_trace"]
    seen = {}
    for t in trace:
        seen[t["agent"]] = t
    unique_trace = list(seen.values())

    durations  = [t.get("duration", 0) for t in unique_trace]
    total_time = round(sum(durations), 2)

    m_cols = st.columns(4)
    m_cols[0].metric("Total time", f"{total_time}s")
    m_cols[1].metric("Agents run", len(unique_trace))
    m_cols[2].metric("Mode", mode)
    completed = sum(1 for t in unique_trace if t["status"] == "completed")
    m_cols[3].metric("Completed", f"{completed}/{len(unique_trace)}")

    st.divider()

    # ── Timeline chart ────────────────────────────────────────────────────────
    st.subheader("Agent timeline")

    agent_names = [t["agent"] for t in unique_trace]
    max_d = max(durations) if durations else 1

    fig = go.Figure(go.Bar(
        x=durations,
        y=agent_names,
        orientation="h",
        marker=dict(
            color="#38BDF8",
            opacity=0.75,
            line=dict(width=0),
        ),
        text=[f"{d}s" for d in durations],
        textposition="outside",
        textfont=dict(family="Inter", size=11, color="#9CA3AF"),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", size=11, color="#6B7280"),
        xaxis=dict(
            showgrid=True,
            gridcolor="#F3F4F6",
            zeroline=False,
            showline=False,
            title="",
            ticksuffix="s",
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            gridcolor="rgba(0,0,0,0)",
            tickfont=dict(size=11, color="#374151"),
        ),
        height=max(220, len(unique_trace) * 44),
        margin=dict(l=0, r=60, t=10, b=10),
        bargap=0.45,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Severity ──────────────────────────────────────────────────────────────
    st.subheader("Threat level")
    risk_findings = next(
        (f["findings"] for f in state["findings"] if f["agent"] == "Risk Agent"), ""
    )
    if "critical" in risk_findings.lower():
        st.error("Critical — Immediate containment required")
    elif "high" in risk_findings.lower():
        st.warning("High — Escalate to the incident response team")
    elif "medium" in risk_findings.lower():
        st.info("Medium — Monitor and investigate further")
    else:
        st.success("Low — No immediate action required")

    st.divider()

    # ── Report ────────────────────────────────────────────────────────────────
    st.subheader("Incident report")
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid #F3F4F6;border-radius:10px;'
        f'padding:22px 26px;line-height:1.75;color:#374151;font-size:0.87rem;">'
        f'{state["final_report"]}</div>',
        unsafe_allow_html=True
    )

    st.divider()

    # ── Agent findings ────────────────────────────────────────────────────────
    st.subheader("Agent findings")
    for finding in state["findings"]:
        with st.expander(finding["agent"]):
            st.markdown(finding["findings"])

    if state["review_comments"]:
        with st.expander("Reviewer comments"):
            for comment in state["review_comments"]:
                st.markdown(comment)

    st.divider()

    # ── Execution trace ───────────────────────────────────────────────────────
    st.subheader("Execution trace")

    rows_html = ""
    for t in unique_trace:
        ok = t["status"] == "completed"
        icon  = "✓" if ok else "✗"
        color = "#22C55E" if ok else "#EF4444"
        rows_html += (
            f'<div style="display:flex;align-items:center;gap:14px;padding:9px 0;'
            f'border-bottom:1px solid #F9FAFB;">'
            f'<span style="color:{color};font-size:12px;font-family:JetBrains Mono,monospace;'
            f'font-weight:600;min-width:12px;">{icon}</span>'
            f'<span style="flex:1;font-size:0.8rem;color:#374151;">{t["agent"]}</span>'
            f'<span style="font-size:0.75rem;color:#9CA3AF;">{t["status"]}</span>'
            f'<span style="font-family:JetBrains Mono,monospace;font-size:0.75rem;'
            f'color:#6B7280;min-width:36px;text-align:right;">{t.get("duration","—")}s</span>'
            f'</div>'
        )

    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid #F3F4F6;border-radius:10px;'
        f'padding:6px 16px;">{rows_html}</div>',
        unsafe_allow_html=True
    )