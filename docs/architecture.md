# Architecture Reference Manual

This document details the software layout and orchestration mechanisms of the **Agentic Workflow Automation** workspace.

## Orchestration Flow

The system employs a dual-stage execution loop (Planning and Execution) to isolate sandbox side-effects.

```
+-----------------------------------------------------------------+
|                                                                 |
|  [Developer Task] ---> [FastAPI / CLI] ---> [Taskmaster Agent]  |
|                                                     |           |
|                                                     v           |
|                                           [1: Gemini Flash API] |
|                                           (Generates Markdown)  |
|                                                     |           |
|                                                     v           |
|                                          [2: Antigravity SDK]   |
|                                          (Executes changes)     |
|                                                                 |
+-----------------------------------------------------------------+
```

### Stage 1: The Planning layer (Gemini API)
Before executing a task, the prompt is dispatched to standard Gemini reasoning models (default `gemini-2.5-flash`). The model acts as a technical architect, emitting a step-by-step implementation checklist. This step is purely descriptive and has no local write privileges.

### Stage 2: The Execution Sandbox (Antigravity SDK)
Once the plan is generated, the `google.antigravity` agent class is leased. This agent runs inside the workspace sandbox with specific system instructions. The agent reads the local directories and calls write/execute tools to complete the checklist. Output tokens are streamed back to the CLI shell or web telemetry feed.

## Interface Points

### FastAPI Gateway
The FastAPI application serves on port `8080` (or `PORT` environment override) and exposes:
- `POST /api/execute`: Receives a JSON task payload and returns the structured plan.
- `GET /api/health`: Provides deployment status and diagnostics.

### Command Line CLI
The entry point `src/main.py` provides a direct pipeline for executing tasks in local terminals. Running with the `--task` flag bypasses server hosting and executes the agent directly.
