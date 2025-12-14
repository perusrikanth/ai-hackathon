from openai import OpenAI


class Embeddings:
    def __init__(self):
        self.client = OpenAI()

    def embed(self, text):
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
