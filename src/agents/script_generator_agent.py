import os
import re
from openai import OpenAI
from src.automation.script_templates.base_script import generate_base_playwright_script


class ScriptGeneratorAgent:
    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY environment variable is not set. "
                "Please set it in your environment or .env file."
            )
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )

    def generate_script(self, flow_description):
        prompt = f"""Convert this flow description into Playwright Python code steps:

{flow_description}

You MUST output ONLY Python Playwright code statements, one per line. Each line should be a valid Playwright command like:
- await page.goto("url")
- await page.fill("selector", "value")
- await page.click("selector")
- await page.wait_for_selector("selector")

Do not include any explanations, comments, or markdown formatting. Output only the code statements."""

        response = self.client.chat.completions.create(
            model="anthropic/claude-3.5-sonnet",
            messages=[
                {"role": "system", "content": "You are a code generator that outputs only Playwright Python code statements."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        content = response.choices[0].message.content

        # Extract code from markdown code blocks if present
        code_match = re.search(
            r'```(?:python)?\s*(.*?)\s*```', content, re.DOTALL)
        if code_match:
            content = code_match.group(1)

        # Split into lines and filter out empty lines and comments
        steps = [line.strip() for line in content.split("\n")
                 if line.strip() and not line.strip().startswith("#")]

        return generate_base_playwright_script(steps)
