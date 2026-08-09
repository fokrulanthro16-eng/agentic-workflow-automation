from dotenv import load_dotenv
load_dotenv()

import argparse
import asyncio
import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure the parent directory is in the path to find local packages
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.task_agent import TaskAutomationAgent

app = FastAPI(
    title="Taskmaster Agent Automation Engine",
    description="Automated Developer Workflows powered by Google Gemini & Antigravity SDK",
    version="1.0.0"
)

# Standard CORS configurations for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskRequest(BaseModel):
    task: str

@app.post("/api/execute")
async def execute_task_endpoint(request: TaskRequest):
    """
    Non-streaming endpoint: returns the planned checklist for the given task.
    """
    if not request.task.strip():
        raise HTTPException(status_code=400, detail="Task details cannot be empty.")
    
    agent = TaskAutomationAgent()
    plan = await agent.generate_task_plan(request.task)
    
    return {
        "status": "PLAN_GENERATED",
        "task": request.task,
        "plan": plan,
        "execution_notes": "To run this task with live agent tool-execution streams, use /api/execute/stream"
    }

@app.post("/api/execute/stream")
async def stream_task_endpoint(request: TaskRequest):
    """
    Streaming endpoint: executes the task using the Antigravity SDK / Gemini workflow
    and streams back the token logs and progress in real time.
    """
    if not request.task.strip():
        raise HTTPException(status_code=400, detail="Task details cannot be empty.")
        
    agent = TaskAutomationAgent()
    
    async def event_generator():
        try:
            async for token in agent.execute_task(request.task):
                yield token
        except Exception as e:
            yield f"\n[HTTP Stream Error]: {str(e)}\n"
            
    return StreamingResponse(event_generator(), media_type="text/plain")

@app.post("/run-workflow/")
async def run_workflow_endpoint(request: TaskRequest):
    """
    Core Hackathon API endpoint: executes the task, collects all streamed tokens,
    and returns a unified plan and execution report in JSON format.
    """
    if not request.task.strip():
        raise HTTPException(status_code=400, detail="Task details cannot be empty.")
        
    agent = TaskAutomationAgent()
    plan = await agent.generate_task_plan(request.task)
    
    tokens = []
    try:
        async for token in agent.execute_task(request.task):
            tokens.append(token)
    except Exception as e:
        tokens.append(f"\n[Error during execution]: {e}")
        
    execution_result = "".join(tokens)
    
    return {
        "status": "SUCCESS",
        "task": request.task,
        "plan": plan,
        "execution_result": execution_result
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "HEALTHY",
        "gemini_api_configured": bool(os.getenv("GEMINI_API_KEY"))
    }

async def run_cli(task_desc: str):
    """
    CLI handler to output planning logs and stream agent reasoning tokens in real time.
    """
    print("\n" + "="*70)
    print("  TASKMASTER AUTOMATION ENGINE | CLI Execution Matrix")
    print("="*70)
    print(f"  Task Input: {task_desc}")
    print("="*70 + "\n")
    
    agent = TaskAutomationAgent()
    
    print("[Taskmaster] Decomposing task requirements using Gemini planning engine...")
    plan = await agent.generate_task_plan(task_desc)
    print(f"\n--- Technical Execution Plan ---\n{plan}\n---------------------------------\n")
    
    print("[Taskmaster] Spawning Taskmaster Agent Sandbox...")
    print("[Taskmaster] Streaming execution output:")
    print("-" * 50)
    
    try:
        async for token in agent.execute_task(task_desc):
            sys.stdout.write(token)
            sys.stdout.flush()
        print("\n" + "-" * 50)
        print("[Taskmaster] Workflow execution sequence completed.")
    except Exception as e:
        print(f"\n[Taskmaster] Execution aborted: {e}")
    print("="*70 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Taskmaster Agent Automation Engine CLI")
    parser.add_argument("--task", type=str, help="Describe the developer workflow task to automate")
    parser.add_argument("--server", action="store_true", help="Launch the FastAPI server")
    args = parser.parse_args()

    if args.server:
        port = int(os.getenv("PORT", "8080"))
        print(f"\n=======================================================")
        print(f"  TASKMASTER API Server starting on port {port}")
        print(f"  Check API health at http://localhost:{port}/api/health")
        print(f"=======================================================\n")
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
    elif args.task:
        asyncio.run(run_cli(args.task))
    else:
        # Default fallback run
        demo_task = "Fetch the users mock database metrics and generate a Markdown report saved at docs/team_report.md"
        asyncio.run(run_cli(demo_task))
