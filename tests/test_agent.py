import unittest
import os
import sys

# Ensure src/ folder is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from agents.task_agent import TaskAutomationAgent, FileReadTool, EmailReporterTool

class TestTaskAutomationAgent(unittest.TestCase):
    def setUp(self):
        self.instructions = "Test instructions for task automation."
        self.agent = TaskAutomationAgent(system_instructions=self.instructions)

    def test_agent_initialization(self):
        """Verify that the agent class instantiates with instructions."""
        self.assertEqual(self.agent.system_instructions, self.instructions)

    def test_client_fallback_state(self):
        """Verify that the client is None if no API key is set in environment."""
        old_key = os.environ.get("GEMINI_API_KEY")
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
            
        temp_agent = TaskAutomationAgent()
        self.assertIsNone(temp_agent.client)
        
        if old_key:
            os.environ["GEMINI_API_KEY"] = old_key

    def test_fallback_plan_generation(self):
        """Verify that a plan can be generated even without an API key."""
        self.agent.client = None
        
        import asyncio
        plan = asyncio.run(self.agent.generate_task_plan("Test dummy task"))
        
        self.assertIn("Default Local Plan", plan)
        self.assertIn("Provide GEMINI_API_KEY", plan)

    def test_file_read_tool_sandbox(self):
        """Verify that FileReadTool blocks directory-traversal attempts outside project."""
        # Try to read outside project root
        res = FileReadTool("../../../../../Windows/System32/drivers/etc/hosts")
        self.assertIn("Security block", res)

    def test_email_reporter_tool(self):
        """Verify that EmailReporterTool generates a log record and returns success."""
        test_email = "test_fokrul@example.com"
        test_subj = "Hackathon Readiness Alert"
        test_body = "This is a test notification."
        
        res = EmailReporterTool(test_email, test_subj, test_body)
        self.assertIn("Success", res)
        self.assertIn(test_email, res)
        
        # Verify the log file was updated
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        log_path = os.path.join(base_dir, "docs/sent_emails.log")
        self.assertTrue(os.path.exists(log_path))
        
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn(test_email, content)
            self.assertIn(test_subj, content)

if __name__ == "__main__":
    unittest.main()
