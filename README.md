# Agentic Workflow Automation

A production-ready automated agentic workspace engine designed for the **Google All Things Agentic Hackathon**.

## 📌 Submission Overview
* **Track:** The Taskmaster (Orchestrated Workflow Automation)
* **Copyright Holder:** Fokrul Islam (MIT License)
* **Repository Link:** https://github.com/fokrulanthro16-eng/agentic-workflow-automation.git

---

## 🛠️ Tech Stack
* **LLM Engine:** Gemini 3.5 Flash / Gemini 2.5 Flash (via `google-genai` SDK)
* **Agentic Framework:** Antigravity Python SDK (`google-antigravity` programmatic agent leasing and tool capabilities)
* **Execution & Server:** FastAPI, Uvicorn, Python-dotenv
* **Deployment Target:** Google Cloud Run (Containerized execution)

---

## 🏗️ Architecture Overview

The system operates as a hybrid task executor. It decomposes ambiguous developer descriptions into structured execution paths and runs them programmatically inside isolated sandboxes.

```
       [User Task Prompt]
               │
               ▼
   [Phase 1: Planning Engine] ────► Gemini API (Creates structural task steps)
               │
               ▼
[Phase 2: Execution Engine] ────► Antigravity SDK (Agent context & capability leasing)
               │
               ▼
     [Command/Tool Output]
```

1. **Planning Interface:** When a task description is received, the `TaskAutomationAgent` calls the Gemini API to format a structured plan in Markdown.
2. **Autonomous Execution:** The plan is executed via the `google.antigravity` `Agent` context. The agent binds local OS capabilities (write files, execute commands) to accomplish the goals programmatically and outputs streamed execution thoughts.
3. **Telemetry & Serving:** A FastAPI server delivers endpoints to submit tasks and receive step-by-step progress streams.

---

## 🚀 Spin-up Instructions

### Prerequisites
* Python 3.10+
* Git
* A Google Gemini API key configured as `GEMINI_API_KEY`

### Local Quickstart

1. **Clone the repository:**
   ```bash
   git clone https://github.com/fokrulanthro16-eng/agentic-workflow-automation.git
   cd agentic-workflow-automation
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables:**
   Create a `.env` file in the root folder:
   ```ini
   GEMINI_API_KEY=your_gemini_api_key_here
   PORT=8080
   ```

5. **Run via CLI (Single Task Execution):**
   ```bash
   python src/main.py --task "Create a basic python script in the scratch directory that computes prime numbers"
   ```

6. **Run via FastAPI Server:**
   ```bash
   python src/main.py --server
   ```
   Submit tasks via HTTP request:
   ```bash
   curl -X POST http://localhost:8080/api/execute \
     -H "Content-Type: application/json" \
     -d '{"task": "Run formatting on codebase"}'
   ```

---

## 📂 Project Structure
```
agentic-workflow-automation/
├── LICENSE              # MIT License
├── README.md            # Devpost/Harvard standard documentation
├── requirements.txt     # Dependencies
├── .gitignore          # Environment & credential protection
├── src/                 # Application source
│   ├── main.py          # Entrypoint (CLI / FastAPI serving)
│   └── agents/
│       ├── __init__.py
│       └── task_agent.py # Agent initialization via Antigravity & GenAI
├── tests/
│   ├── __init__.py
│   └── test_agent.py    # Unit & Integration tests
└── docs/
    └── architecture.md  # Deep technical details
```
