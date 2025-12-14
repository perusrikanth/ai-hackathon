import os
import uuid
from pathlib import Path
import lancedb
from langchain_openai import OpenAIEmbeddings

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class MemoryStore:
    """
    Centralized LanceDB-backed memory store for agent intelligence.
    Stores:
      - Flow memory
      - Repair memory
      - Visual memory
    """

    def __init__(self, db_path: str = "memory_store"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)

        # Connect to LanceDB
        self.db = lancedb.connect(str(self.db_path))

        # Embeddings (OpenRouter-compatible)
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base=OPENROUTER_BASE_URL,
        )

        # Tables
        self.flow_table = self._get_or_create_table("flow_memory")
        self.repair_table = self._get_or_create_table("repair_memory")
        self.visual_table = self._get_or_create_table("visual_memory")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_or_create_table(self, name: str):
        if name in self.db.table_names():
            return self.db.open_table(name)

        return self.db.create_table(
            name,
            data=[
                {
                    "id": str(uuid.uuid4()),
                    "text": "",
                    "metadata": {},
                    "vector": [0.0],
                }
            ],
            mode="overwrite",
        )

    def _embed(self, text: str):
        return self.embeddings.embed_query(text)

    # ------------------------------------------------------------------
    # Generic operations
    # ------------------------------------------------------------------

    def add(self, table, text: str, metadata: dict):
        vector = self._embed(text)
        table.add(
            [
                {
                    "id": str(uuid.uuid4()),
                    "text": text,
                    "metadata": metadata,
                    "vector": vector,
                }
            ]
        )

    def search(self, table, query: str, k: int = 3):
        vector = self._embed(query)
        return table.search(vector).limit(k).to_list()

    # ------------------------------------------------------------------
    # Flow Memory
    # ------------------------------------------------------------------

    def save_flow(self, domain: str, flow_json: str):
        self.add(
            self.flow_table,
            text=flow_json,
            metadata={"type": "flow", "domain": domain},
        )

    def search_flows(self, domain: str, k: int = 3):
        return self.search(self.flow_table, domain, k)

    # ------------------------------------------------------------------
    # Repair Memory
    # ------------------------------------------------------------------

    def save_repair(self, error_log: str, fix_code: str):
        combined = f"ERROR:\n{error_log}\n\nFIX:\n{fix_code}"
        self.add(
            self.repair_table,
            text=combined,
            metadata={"type": "repair"},
        )

    def search_repairs(self, error_log: str, k: int = 1):
        return self.search(self.repair_table, error_log, k)

    # ------------------------------------------------------------------
    # Visual Memory (optional)
    # ------------------------------------------------------------------

    def save_visual(self, description: str, image_embedding: list):
        self.visual_table.add(
            [
                {
                    "id": str(uuid.uuid4()),
                    "text": description,
                    "metadata": {"type": "visual"},
                    "vector": image_embedding,
                }
            ]
        )

    def search_visual(self, description: str, k: int = 3):
        vector = self._embed(description)
        return self.visual_table.search(vector).limit(k).to_list()
