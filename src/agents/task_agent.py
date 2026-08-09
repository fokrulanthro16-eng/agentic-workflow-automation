import os
import sys
import logging
import json
import urllib.request
import csv
from io import StringIO
from datetime import datetime
from typing import AsyncGenerator

# Import Antigravity SDK elements
try:
    from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig
    ANTIGRAVITY_AVAILABLE = True
except ImportError:
    ANTIGRAVITY_AVAILABLE = False

from google import genai
from google.genai import types

logger = logging.getLogger("TaskmasterAgent")
logging.basicConfig(level=logging.INFO)

# --- Core Tool Definitions ---

def read_data_file(filepath: str) -> str:
    """
    Reads the content of a local text, markdown, or CSV file from the project workspace.
    
    Args:
        filepath: The relative path to the target file.
        
    Returns:
        The content of the file as a string.
    """
    logger.info(f"[Tool: read_data_file] Reading path: {filepath}")
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        target_path = os.path.abspath(os.path.join(base_dir, filepath))
        
        # Security sandbox validation
        if not target_path.startswith(base_dir):
            return "Error: Security block. Cannot read files outside the project workspace."

        if not os.path.exists(target_path):
            return f"Error: Target file not found at path: {filepath}"
            
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"[Tool: read_data_file] Successfully read {len(content)} bytes.")
        return content
    except Exception as e:
        logger.error(f"[Tool: read_data_file] Failed: {e}")
        return f"Error reading file: {str(e)}"


def FileReadTool(filepath: str) -> str:
    """
    Reads the contents of a local text or CSV file from the project workspace.
    
    Args:
        filepath: The relative path to the target file.
        
    Returns:
        The content of the file as a string.
    """
    return read_data_file(filepath)


def fetch_api_data(endpoint: str) -> str:
    """
    Fetches JSON data from a remote or mock web API endpoint (e.g., users, products, metrics).
    
    Args:
        endpoint: The target API endpoint URL or a mock indicator name.
        
    Returns:
        The fetched data as a JSON string.
    """
    logger.info(f"[Tool: fetch_api_data] Querying: {endpoint}")
    mock_endpoints = {
        "users": [
            {"id": 101, "name": "Fokrul Islam", "role": "Principal Systems Engineer"},
            {"id": 102, "name": "Sarah Connor", "role": "Site Reliability Engineer"},
            {"id": 103, "name": "Miles Dyson", "role": "Lead Cyberneticist"}
        ],
        "products": [
            {"sku": "SG-101", "name": "Sovereign-Guard Gateway", "category": "Security", "price": 45000.00},
            {"sku": "TM-202", "name": "Taskmaster Agent Executor", "category": "Automation", "price": 8500.00}
        ],
        "metrics": {
            "platform_status": "OPERATIONAL",
            "active_sandboxes": 4,
            "tasks_running": 2,
            "threat_protection_level": "MAXIMUM"
        }
    }
    
    cleaned_key = endpoint.strip("/").split("/")[-1].lower()
    if cleaned_key in mock_endpoints:
        logger.info(f"[Tool: fetch_api_data] Mock endpoint match: '{cleaned_key}'")
        return json.dumps(mock_endpoints[cleaned_key], indent=2)

    try:
        if not (endpoint.startswith("http://") or endpoint.startswith("https://")):
            return f"Error: Invalid protocol. Endpoint '{endpoint}' must start with http:// or https://"
            
        req = urllib.request.Request(
            endpoint, 
            headers={'User-Agent': 'TaskmasterAgent/1.0'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = response.read().decode('utf-8')
        logger.info(f"[Tool: fetch_api_data] HTTP fetch successful from {endpoint}")
        return data
    except Exception as e:
        logger.error(f"[Tool: fetch_api_data] Fetch failed: {e}")
        return f"Error fetching API data: {str(e)}"


def generate_markdown_report(title: str, content: str, output_path: str) -> str:
    """
    Generates a structured markdown report and saves it to the local project workspace.
    
    Args:
        title: The header title of the report.
        content: The detailed markdown body content of the report.
        output_path: Relative file path to save the report (e.g., 'docs/report.md').
        
    Returns:
        A success message indicating the saved file location.
    """
    logger.info(f"[Tool: generate_markdown_report] Outputting to: {output_path}")
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        target_path = os.path.abspath(os.path.join(base_dir, output_path))
        
        if not target_path.startswith(base_dir):
            return "Error: Security block. Cannot write files outside the project workspace."

        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        report_content = (
            f"# {title}\n\n"
            f"*Generated by Taskmaster AI Agent*\n"
            f"*Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
            f"---\n\n"
            f"{content}\n"
        )
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        logger.info(f"[Tool: generate_markdown_report] Report successfully written.")
        return f"Success: Report generated and saved at: {output_path}"
    except Exception as e:
        logger.error(f"[Tool: generate_markdown_report] Write failed: {e}")
        return f"Error creating report: {str(e)}"


def parse_csv_summary(csv_data: str) -> str:
    """
    Parses a raw CSV text data string and calculates summary statistics (averages, totals).
    
    Args:
        csv_data: The raw CSV content string.
        
    Returns:
        A formatted report summarizing the CSV data.
    """
    logger.info("[Tool: parse_csv_summary] Parsing CSV data.")
    try:
        f = StringIO(csv_data.strip())
        reader = csv.reader(f)
        headers = next(reader, None)
        if not headers:
            return "Error: Empty CSV data provided."

        rows = list(reader)
        total_rows = len(rows)
        
        numeric_sums = {}
        numeric_counts = {}
        
        for row in rows:
            for i, val in enumerate(row):
                if i >= len(headers):
                    continue
                try:
                    num_val = float(val)
                    numeric_sums[i] = numeric_sums.get(i, 0.0) + num_val
                    numeric_counts[i] = numeric_counts.get(i, 0) + 1
                except ValueError:
                    pass

        summary_lines = [
            f"CSV Summary Report",
            f"==================",
            f"Total Records: {total_rows}",
            f"Headers: {', '.join(headers)}",
            ""
        ]

        for idx, col_name in enumerate(headers):
            if idx in numeric_sums:
                total = numeric_sums[idx]
                count = numeric_counts[idx]
                avg = total / count if count > 0 else 0.0
                summary_lines.append(f"- Column '{col_name}': Total Sum = {total:.2f}, Average = {avg:.2f} (Calculated from {count} records)")
            else:
                summary_lines.append(f"- Column '{col_name}': Non-numeric text data")

        report = "\n".join(summary_lines)
        logger.info("[Tool: parse_csv_summary] Summary parse completed.")
        return report
    except Exception as e:
        logger.error(f"[Tool: parse_csv_summary] Parse failed: {e}")
        return f"Error parsing CSV data: {str(e)}"


def EmailReporterTool(recipient_email: str, subject: str, report_body: str) -> str:
    """
    Simulates sending an email report and logs the output in the project's outbox ledger.
    
    Args:
        recipient_email: The target recipient's email address.
        subject: The email subject line.
        report_body: The detailed content of the report to email.
        
    Returns:
        A success message indicating the email was dispatched and logged.
    """
    logger.info(f"[Tool: EmailReporterTool] Dispatched email to {recipient_email} under subject '{subject}'")
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        log_path = os.path.abspath(os.path.join(base_dir, "docs/sent_emails.log"))
        
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        email_record = (
            f"=======================================================\n"
            f"EMAIL DISPATCHED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"To: {recipient_email}\n"
            f"Subject: {subject}\n"
            f"Body:\n{report_body}\n"
            f"=======================================================\n\n"
        )
        
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(email_record)
            
        logger.info("[Tool: EmailReporterTool] Email logged in docs/sent_emails.log")
        return f"Success: Email dispatched successfully to {recipient_email} and logged in docs/sent_emails.log."
    except Exception as e:
        logger.error(f"[Tool: EmailReporterTool] Dispatch failed: {e}")
        return f"Error sending email: {str(e)}"


# List of exposed custom tools
EXPOSED_TOOLS = [
    read_data_file,
    FileReadTool,
    fetch_api_data,
    generate_markdown_report,
    parse_csv_summary,
    EmailReporterTool
]

# --- Taskmaster Agent Orchestration ---

class TaskAutomationAgent:
    def __init__(self, system_instructions: str = None):
        self.system_instructions = system_instructions or (
            "You are the Taskmaster AI Agent, designed to automate complex, multi-step developer workflows.\n"
            "You are equipped with tools: FileReadTool, EmailReporterTool, fetch_api_data, generate_markdown_report, and parse_csv_summary.\n"
            "Analyze task prompts, invoke appropriate tools, and draft clear final summaries."
        )
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Taskmaster Gemini GenAI Client initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize GenAI client: {e}")

    async def generate_task_plan(self, task_description: str) -> str:
        """
        Uses the Gemini API to analyze the task and output a detailed technical implementation plan.
        """
        if not self.client:
            return (
                "### Default Local Plan\n"
                "- [ ] Review task requirements.\n"
                "- [ ] Execute workflow using local fallback tools.\n"
                "- [ ] Generate output artifacts.\n\n"
                "*(Provide GEMINI_API_KEY environment variable for live AI planning)*"
            )

        prompt = (
            f"You are a Principal Software Architect. Draft a step-by-step technical plan to accomplish "
            f"this developer task:\n"
            f"Task: '{task_description}'\n\n"
            f"Specify which tools (FileReadTool, EmailReporterTool, fetch_api_data, generate_markdown_report, parse_csv_summary) are required."
        )

        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating plan: {e}")
            return f"Error drafting plan: {e}. Proceeding directly to sandbox execution."

    async def execute_task(self, task_description: str) -> AsyncGenerator[str, None]:
        """
        Main execution router. Uses Antigravity SDK if available; otherwise falls back 
        to an interactive Gemini-driven function routing loop.
        """
        if ANTIGRAVITY_AVAILABLE:
            yield "[Antigravity] Initiating lease for Sandboxed Developer Agent...\n"
            config = LocalAgentConfig(
                system_instructions=self.system_instructions,
                capabilities=CapabilitiesConfig(),
                tools=EXPOSED_TOOLS
            )
            try:
                async with Agent(config) as agent:
                    response = await agent.chat(task_description)
                    async for token in response:
                        yield token
                return
            except Exception as e:
                logger.error(f"Antigravity SDK execution error: {e}. Transitioning to API fallback.")
                yield f"[Antigravity Alert] Runtime error: {e}. Transitioning to Gemini API Fallback...\n"
        
        # Run live Gemini tool execution fallback
        async for token in self._run_gemini_fallback(task_description):
            yield token

    async def _run_gemini_fallback(self, task_description: str) -> AsyncGenerator[str, None]:
        """
        A resilient multi-turn fallback engine using standard Gemini function-calling
        to execute python tools locally and compile results.
        """
        if not self.client:
            yield "[System Alert] No active Gemini API Key. Mocking task execution...\n"
            yield f"[Mock Run] Executing: '{task_description}'\n"
            yield "[Mock Run] Task completed successfully.\n"
            return

        yield "[Gemini API] Spawning Agentic workflow loop (Gemini 2.5 Flash)...\n"
        
        tools_map = {
            "read_data_file": read_data_file,
            "FileReadTool": FileReadTool,
            "fetch_api_data": fetch_api_data,
            "generate_markdown_report": generate_markdown_report,
            "parse_csv_summary": parse_csv_summary,
            "EmailReporterTool": EmailReporterTool
        }

        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=task_description,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instructions,
                    tools=EXPOSED_TOOLS,
                    temperature=0.1
                )
            )

            function_calls = response.function_calls
            if function_calls:
                tool_results = []
                for call in function_calls:
                    name = call.name
                    args = call.args
                    yield f"\n[Agent Thought] Triggering local tool: {name}({args})\n"
                    
                    if name in tools_map:
                        try:
                            res = tools_map[name](**args)
                            tool_results.append(f"Tool '{name}' output:\n{res}")
                        except Exception as tool_err:
                            tool_results.append(f"Tool '{name}' failed with error: {tool_err}")
                    else:
                        tool_results.append(f"Tool '{name}' is not supported.")
                
                yield "\n[Gemini API] Processing tool outputs to compile final report...\n"
                compiled_results = "\n\n".join(tool_results)
                
                follow_up_prompt = (
                    f"Here are the execution outputs of the tools you requested:\n\n"
                    f"{compiled_results}\n\n"
                    f"Analyze this data and provide your final completion summary report."
                )
                
                final_res = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=follow_up_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_instructions,
                        temperature=0.1
                    )
                )
                yield "\n[Final Agent Report]\n"
                yield final_res.text
            else:
                yield "\n[Final Agent Report]\n"
                yield response.text

        except Exception as e:
            logger.error(f"Gemini workflow loop failed: {e}")
            yield f"\n[Agent Failure] Encountered error: {str(e)}\n"
