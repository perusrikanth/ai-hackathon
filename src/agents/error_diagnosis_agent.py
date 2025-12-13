import os
from openai import OpenAI


class ErrorDiagnosisAgent:
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

    def diagnose(self, stderr):
        prompt = f"""
        Analyze this Playwright error:
        {stderr}


        Explain what went wrong and suggest a fix.
        """

        response = self.client.chat.completions.create(
            model="meta-llama/llama-3.1-70b-instruct",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
