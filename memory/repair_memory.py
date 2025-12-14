import uuid
from memory.embeddings import Embeddings


class RepairMemory:
    def __init__(self, store):
        self.store = store
        self.embedder = Embeddings()

    def save_fix(self, error_log, fix_code):
        vector = self.embedder.embed(error_log)
        self.store.repair_db.add(
            ids=[str(uuid.uuid4())],
            embeddings=[vector],
            metadatas=[{"error": error_log, "fix": fix_code}]
        )

    def retrieve_similar_fix(self, error_log):
        vector = self.embedder.embed(error_log)
        return self.store.repair_db.query(query_embeddings=[vector], n_results=1)
