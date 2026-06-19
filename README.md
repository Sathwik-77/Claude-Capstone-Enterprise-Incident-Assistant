# 🔍 Enterprise Incident Investigation Assistant

An AI-powered multi-agent system that investigates security incidents from logs and policy documents — and produces a structured investigation report.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)
![Anthropic](https://img.shields.io/badge/Anthropic-Claude-purple?style=flat-square)
![LangChain](https://img.shields.io/badge/LangChain-RAG-teal?style=flat-square)
![ChromaDB](https://img.shields.io/badge/Vector_DB-ChromaDB-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-gray?style=flat-square)

---

## Overview

This project was built as a capstone for a real-world AI engineering curriculum. It demonstrates how to combine RAG, multi-agent orchestration, reliability patterns, and an MCP server into a production-style pipeline — using nothing but the Anthropic API and open-source tooling.

Drop in your security logs and policy PDFs. Ask a question like _"Investigate the failed login activity"_. A chain of specialised agents retrieves evidence, identifies suspicious events, determines root causes, evaluates risk, reviews the findings, and writes a full incident report.

---

## Agent pipeline

```
Researcher → Incident → Root Cause → Risk → Reviewer → Report Writer
```

The incident, root-cause, and risk agents can also run in **parallel** via `ThreadPoolExecutor` for faster turnaround on large log sets.

---

## Project phases

### Phase 1 — RAG pipeline (`backend/`)
Loads PDFs (ISO 27001, security policy) and incident log files into ChromaDB via Anthropic Voyage embeddings. Exposes `search_chunks(query)` as the retrieval API for all agents.

### Phase 2 — Agent layer (`agents/`)
Six specialised agents share an `AgentState` TypedDict and are orchestrated sequentially (or in parallel) by `orchestrator.py` to produce a final incident report.

### Phase 3 — Reliability layer (`reliability/`)
Wraps every LLM call with retry, timeout, and RAG fallback. Emits structured `.jsonl` logs with per-agent timing and status for observability.

### Phase 4 — MCP server (`mcp_server/`)
Exposes `search_incidents()`, `list_logs()`, and `investigate_incident()` as MCP tools so Claude Desktop can trigger a full investigation via natural language.

### Phase 5 — Streamlit dashboard (`frontend/`)
Reads the structured log file and renders an interactive dashboard — incident summary, severity badge, agent execution timeline, and full trace.

---

## Tech stack

| Layer | Technology |
|---|---|
| LLM | Claude (Anthropic API) |
| Embeddings | Voyage-2 |
| Vector database | ChromaDB |
| Orchestration | LangChain + custom agents |
| API server | FastAPI |
| Dashboard | Streamlit |
| Reliability | Tenacity (retry/timeout) |
| Tool protocol | MCP (Model Context Protocol) |

---

## Project structure

```
incident-investigation-assistant/
│
├── agents/                  # All agent files + orchestrator + state
│   ├── researcher.py
│   ├── incident_agent.py
│   ├── root_cause_agent.py
│   ├── risk_agent.py
│   ├── reviewer.py
│   ├── report_writer.py
│   ├── orchestrator.py
│   └── state.py
│
├── backend/                 # RAG pipeline
│   ├── document_loader.py
│   ├── chunker.py
│   ├── vector_store.py
│   └── rag_service.py
│
├── frontend/
│   └── app.py               # Streamlit dashboard
│
├── reliability/             # Retry, timeout, fallback, logging
│   ├── retry_handler.py
│   ├── timeout_handler.py
│   ├── fallback_handler.py
│   └── structured_logger.py
│
├── mcp_server/
│   └── server.py            # MCP tool definitions
│
├── mcp_client/
│   └── client.py
│
├── KnowledgeBase/           # PDF policies (ISO 27001, security policy)
├── logs/                    # Incident .txt log files
├── vector_db/               # Persisted ChromaDB store
├── .env                     # ANTHROPIC_API_KEY goes here
└── requirements.txt
```

---

## Quick start

```bash
# 1. Clone and install
git clone https://github.com/your-username/incident-investigation-assistant
cd incident-investigation-assistant
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# 3. Add your documents
# Place PDF policies in KnowledgeBase/
# Place incident .txt log files in logs/

# 4. Build the vector store
python backend/rag_service.py

# 5. Run a full investigation
python agents/orchestrator.py

# 6. Launch the dashboard (optional)
streamlit run frontend/app.py
```

---

## Example output

Given the query _"Investigate suspicious login activity"_, the pipeline produces:

```
=================================================
INCIDENT INVESTIGATION REPORT
=================================================
User Query:
  Investigate suspicious login activity.

Evidence Retrieved:
  - Incident_Log_1.txt
  - Security Policy.pdf

Findings:
  Incident:   Three consecutive login failures detected for user admin.
  Root Cause: Possible brute-force attempt from external IP.
  Risk:       High severity — successful admin login after repeated failures.

Review Comments:
  - MFA enforcement was disabled during the incident window.
  - New account creation immediately after admin login is suspicious.

Recommendations:
  - Lock accounts after 5 failed attempts.
  - Enforce MFA for all privileged users.
  - Review and audit the temp.support account.
=================================================
```

---

## Knowledge base

The system accepts any combination of:
- **Policy PDFs** — ISO/IEC 27001, internal security policies
- **Incident logs** — structured `.txt` files with timestamped events
- **Standards** — NIST, SOC 2, or other compliance documents

---

## Environment variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key (required) |

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

_Built as a capstone project for an AI engineering curriculum · Anthropic API · Python 3.11+_
