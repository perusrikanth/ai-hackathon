from openai import OpenAI
from src.utils.config import Config
from src.automation.script_templates.base_script import generate_base_playwright_script


client = OpenAI(api_key=Config.OPENAI_KEY)


class ScriptGeneratorAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
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


        response = client.chat.completions.create(
            model="google/gemini-pro-1.5",  # also available on openrouter
            messages=[{"role": "user", "content": prompt}]
        )


        steps = response.choices[0].message.content.split("\n")
        return generate_base_playwright_script(steps)