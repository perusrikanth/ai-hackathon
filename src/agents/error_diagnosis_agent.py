from openai import OpenAI
from src.utils.config import Config


client = OpenAI(api_key=Config.OPENAI_KEY)


class ErrorDiagnosisAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
        
    def diagnose(self, stderr):
        prompt = f"""
        Analyze this Playwright error:
        {stderr}


        Explain what went wrong and suggest a fix.
        """


        response = client.chat.completions.create(
            model="meta-llama/llama-3.1-70b-instruct",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content