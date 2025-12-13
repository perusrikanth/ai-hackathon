import os
import json
import re
from openai import OpenAI


class FlowDiscoveryAgent:
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

    def _extract_json(self, text):
        """Extract JSON from text, handling markdown code blocks."""
        # Try to find JSON in markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\[.*?\]|\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)
        
        # Try to find JSON object/array directly
        json_match = re.search(r'(\[.*?\]|\{.*?\})', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)
        
        return text.strip()

    def discover(self, url):
        prompt = f"""Analyze the webpage at {url} and identify the most important user flows (login, signup, checkout, search, etc.).

You MUST respond with ONLY a valid JSON array. Each item should be a flow object with:
- "name": string (e.g., "Login", "Signup", "Checkout")
- "description": string (brief description of the flow)
- "steps": array of strings (list of steps in the flow)

Example format:
[
  {{
    "name": "Login",
    "description": "User authentication flow",
    "steps": ["Navigate to login page", "Enter credentials", "Click login button"]
  }},
  {{
    "name": "Search",
    "description": "Product search functionality",
    "steps": ["Enter search query", "Click search button", "View results"]
  }}
]

Respond with ONLY the JSON array, no additional text or explanation."""

        response = self.client.chat.completions.create(
            model="anthropic/claude-3.5-sonnet",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that responds with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        content = response.choices[0].message.content
        
        # Extract and parse JSON
        try:
            json_text = self._extract_json(content)
            flows = json.loads(json_text)
            return {"flows": flows, "url": url}
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return error structure
            return {
                "error": "Failed to parse JSON response",
                "raw_response": content,
                "url": url
            }
