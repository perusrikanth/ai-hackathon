import os
from openai import OpenAI
from src.automation.script_templates.base_script import generate_base_playwright_script


class AdaptiveRepairAgent:
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

    def repair(self, original_script, diagnosis):
        prompt = f"""
        Original Playwright code:
        {original_script}


        Diagnosis:
        {diagnosis}


        Regenerate a corrected Playwright script.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        lines = response.choices[0].message.content.split("\n")
        return generate_base_playwright_script(lines)
