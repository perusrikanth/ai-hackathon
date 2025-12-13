from openai import OpenAI
from src.utils.config import Config


client = OpenAI(api_key=Config.OPENAI_KEY)


class FlowDiscoveryAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )

    def discover(self, url):
        prompt = f"""
        Analyze the webpage at {url}.
        Identify the most important user flows (login, signup, checkout, search, etc.).
        Respond using a JSON list of steps.
        """


        response = client.chat.completions.create(
            model="anthropic/claude-3.5-sonnet",  # or any OpenRouter model
            messages=[{"role": "user", "content": prompt}]
        )


        return response.choices[0].message.content