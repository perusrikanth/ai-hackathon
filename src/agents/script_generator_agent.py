import os
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
        prompt = f"""
        Convert this flow description into Playwright Python steps:
        {flow_description}


        Output Python statements like:
        await page.goto("...")
        await page.fill("#username", "test")
        """

        response = self.client.chat.completions.create(
            model="google/gemini-pro-1.5",  # also available on openrouter
            messages=[{"role": "user", "content": prompt}]
        )

        steps = response.choices[0].message.content.split("\n")
        return generate_base_playwright_script(steps)
