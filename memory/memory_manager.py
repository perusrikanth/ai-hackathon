import lancedb
from langchain_community.vectorstores import LanceDB
from langchain_openai import OpenAIEmbeddings
from pathlib import Path


class MemoryManager:
    """
    Unified memory manager that stores:
    - Flow memories
    - Repair memories
    - Visual/UI memories
    using LanceDB as the backend vector database.
    """

    def __init__(self, path: str = "memory_store"):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)

        # Initialize LanceDB connection
        self.db = lancedb.connect(str(self.path))

        # Embeddings model
        self.embeddings = OpenAIEmbeddings()

        # Ensure tables exist
        self.flow_table = self._get_or_create_table("flow_memory")
        self.repair_table = self._get_or_create_table("repair_memory")
        self.visual_table = self._get_or_create_table("visual_memory")

    # ------------------------------
    # Internal helper
    # ------------------------------
    def _get_or_create_table(self, table_name: str):
        try:
            return self.db.open_table(table_name)
        except:
            # Create empty table schema
            return self.db.create_table(
                table_name,
                data=[
                    {
                        "text": "",
                        "metadata": {},
                        # placeholder; real vectors generated on insert
                        "vector": [0.0]
                    }
                ]
            )

    # ------------------------------
    # Generic save & search
    # ------------------------------
    def save_memory(self, table, text: str, metadata: dict):
        embedding = self.embeddings.embed_query(text)

        table.add(
            [
                {
                    "text": text,
                    "metadata": metadata,
                    "vector": embedding
                }
            ]
        )

    def search_memory(self, table, query: str, k: int = 3):
        embedding = self.embeddings.embed_query(query)
        results = (
            table.search(embedding)
                 .limit(k)
                 .to_list()
        )
        return results

    # ------------------------------
    # Specific memory types
    # ------------------------------
    def save_flow(self, domain: str, flow_json: str):
        self.save_memory(
            self.flow_table,
            text=flow_json,
            metadata={"domain": domain, "type": "flow"}
        )

    def search_flows(self, domain: str):
        return self.search_memory(self.flow_table, query=domain)

    def save_repair(self, error_log: str, fix_code: str):
        combined = f"ERROR: {error_log}\nFIX: {fix_code}"

        self.save_memory(
            self.repair_table,
            text=combined,
            metadata={"type": "repair"}
        )

    def search_repair(self, error_log: str):
        return self.search_memory(self.repair_table, query=error_log)

    def save_visual_memory(self, description: str, image_vector: list):
        """Store screenshot embeddings."""
        self.visual_table.add(
            [
                {
                    "text": description,
                    "metadata": {"type": "visual"},
                    "vector": image_vector
                }
            ]
        )

    def search_visual(self, description: str, k: int = 3):
        emb = self.embeddings.embed_query(description)
        return (
            self.visual_table.search(emb)
                .limit(k)
                .to_list()
        )
