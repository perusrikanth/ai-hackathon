from openai import OpenAI
from src.utils.config import Config
from src.automation.script_templates.base_script import generate_base_playwright_script


client = OpenAI(api_key=Config.OPENAI_KEY)


class AdaptiveRepairAgent:
    def repair(self, original_script, diagnosis):
        prompt = f"""
        Original Playwright code:
        {original_script}


        Diagnosis:
        {diagnosis}


        Regenerate a corrected Playwright script.
        """


        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
        )


        lines = response.choices[0].message.content.split("\n")
        return generate_base_playwright_script(lines)