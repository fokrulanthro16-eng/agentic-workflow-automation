import unittest
import os
import sys

# Ensure src/ folder is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from agents.task_agent import TaskAutomationAgent

class TestTaskAutomationAgent(unittest.TestCase):
    def setUp(self):
        # Setup test instructions
        self.instructions = "Test instructions for task automation."
        self.agent = TaskAutomationAgent(system_instructions=self.instructions)

    def test_agent_initialization(self):
        """Verify that the agent class instantiates with instructions."""
        self.assertEqual(self.agent.system_instructions, self.instructions)

    def test_client_fallback_state(self):
        """Verify that the client is None if no API key is set in environment."""
        # Save old key
        old_key = os.environ.get("GEMINI_API_KEY")
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
            
        temp_agent = TaskAutomationAgent()
        self.assertIsNone(temp_agent.client)
        
        # Restore old key if existed
        if old_key:
            os.environ["GEMINI_API_KEY"] = old_key

    def test_fallback_plan_generation(self):
        """Verify that a plan can be generated even without an API key (fallback rules)."""
        # Ensure client is None
        self.agent.client = None
        
        # We run an async helper to test coroutine output
        import asyncio
        plan = asyncio.run(self.agent.generate_task_plan("Test dummy task"))
        
        self.assertIn("Default Local Plan", plan)
        self.assertIn("Provide GEMINI_API_KEY", plan)

if __name__ == "__main__":
    unittest.main()
