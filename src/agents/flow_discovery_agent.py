import os
import json
import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate


class FlowDiscoveryAgent:
    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY environment variable is not set. "
                "Please set it in your environment or .env file."
            )
        self.llm = ChatOpenAI(
            model="anthropic/claude-3.5-sonnet",
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.3
        )
        self.prompt_template = PromptTemplate.from_template(
            """Analyze the webpage at {url} and identify the most important user flows (login, signup, checkout, search, etc.).

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
        )

    def _extract_json(self, text):
        """Extract JSON from text, handling markdown code blocks and nested structures."""
        # Try to find JSON in markdown code blocks first
        json_match = re.search(r'```(?:json)?\s*(\[.*?\]|\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            return json_match.group(1).strip()
        
        # Try to find JSON array (balanced brackets)
        bracket_count = 0
        start_idx = text.find('[')
        if start_idx != -1:
            for i in range(start_idx, len(text)):
                if text[i] == '[':
                    bracket_count += 1
                elif text[i] == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        return text[start_idx:i+1].strip()
        
        # Try to find JSON object (balanced braces)
        brace_count = 0
        start_idx = text.find('{')
        if start_idx != -1:
            for i in range(start_idx, len(text)):
                if text[i] == '{':
                    brace_count += 1
                elif text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        return text[start_idx:i+1].strip()
        
        # Fallback: return original text
        return text.strip()

    def discover(self, url):
        chain = self.prompt_template | self.llm
        response = chain.invoke({"url": url})
        content = response.content
        
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
