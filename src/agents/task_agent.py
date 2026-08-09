import os
import sys
import logging
from typing import AsyncGenerator
from google import genai
from google.genai import types

# Import Antigravity SDK elements
try:
    from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig
    ANTIGRAVITY_AVAILABLE = True
except ImportError:
    ANTIGRAVITY_AVAILABLE = False

logger = logging.getLogger("TaskmasterAgent")
logging.basicConfig(level=logging.INFO)

class TaskAutomationAgent:
    def __init__(self, system_instructions: str = None):
        self.system_instructions = system_instructions or (
            "You are the Taskmaster AI Agent, designed to automate complex, multi-step developer workflows. "
            "Examine targets carefully, draft plans, and execute changes using your command line and writing tools."
        )
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        
        # Initialize Google GenAI client if API Key is present
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info("GenAI client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize GenAI client: {e}")

    async def generate_task_plan(self, task_description: str) -> str:
        """
        Uses the Gemini API to analyze the task and output a detailed technical implementation plan.
        """
        if not self.client:
            return (
                "### Local Static Plan\n"
                "- [ ] Analyze target workspace requirements.\n"
                "- [ ] Deploy task changes locally.\n"
                "- [ ] Verify syntax and integration tests.\n\n"
                "*(Note: Provide a valid GEMINI_API_KEY to generate live AI plans.)*"
            )

        prompt = (
            f"You are a Principal AI Systems Architect. Create a detailed, markdown-formatted technical plan "
            f"to complete the following automated developer workflow:\n\n"
            f"Task: '{task_description}'\n\n"
            f"Include file structural layouts, key components to create/modify, and a checklist of steps."
        )

        try:
            # Generate plan using the latest gemini model
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating plan with Gemini: {e}")
            return f"Error drafting plan: {e}. Executing with static default fallback."

    async def execute_task(self, task_description: str) -> AsyncGenerator[str, None]:
        """
        Spawns an Antigravity Agent to execute the task autonomously.
        Yields tokens representing thinking/execution output.
        """
        if not ANTIGRAVITY_AVAILABLE:
            yield "Antigravity SDK is not available in the current environment runtime. Mocking execution...\n"
            yield f"[Mock Executing]: {task_description}\n"
            yield "[Mock Done]: Task completed successfully."
            return

        config = LocalAgentConfig(
            system_instructions=self.system_instructions,
            capabilities=CapabilitiesConfig(),  # Enable command, write tools
        )

        try:
            async with Agent(config) as agent:
                # Initiate session
                response = await agent.chat(task_description)
                
                # Stream token deltas as they arrive from the agent
                async for token in response:
                    yield token
        except Exception as e:
            logger.error(f"Error running Antigravity SDK: {e}")
            yield f"\n[Agent Error]: Failed to lease or run agent: {e}\n"
