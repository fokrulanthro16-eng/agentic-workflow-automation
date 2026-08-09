import argparse
import asyncio
import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure the parent directory is in the path to find local packages
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.task_agent import TaskAutomationAgent

# Load local .env environment configurations
load_dotenv()

app = FastAPI(
    title="Taskmaster Agent Automation Engine",
    description="Automated Developer Workflows powered by Google Gemini & Antigravity SDK",
    version="1.0.0"
)

# Standard CORS setups
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
    HTTP route to draft a planning audit and queue task execution.
    """
    if not request.task.strip():
        raise HTTPException(status_code=400, detail="Task details cannot be empty.")
    
    agent = TaskAutomationAgent()
    plan = await agent.generate_task_plan(request.task)
    
    return {
        "status": "PLAN_GENERATED",
        "task": request.task,
        "plan": plan,
        "execution_notes": "To run this task with active agent execution capabilities, run via CLI: python src/main.py --task '<task>'"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "HEALTHY",
        "sdk_loaded": True
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
    
    print("[Taskmaster] Decomposing task requirements using Gemini 3.5 Flash planning engine...")
    plan = await agent.generate_task_plan(task_desc)
    print(f"\n--- Technical Execution Plan ---\n{plan}\n---------------------------------\n")
    
    print("[Taskmaster] Activating Antigravity SDK agent sandbox container...")
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
        print(f"Starting server at http://0.0.0.0:{port}")
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
    elif args.task:
        asyncio.run(run_cli(args.task))
    else:
        # Default fallback run
        demo_task = "Draft a README.md summary for a Python prime factorization script."
        asyncio.run(run_cli(demo_task))
