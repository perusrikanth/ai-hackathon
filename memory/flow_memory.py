import uuid
from memory.embeddings import Embeddings


class FlowMemory:
    def __init__(self, store):
        self.store = store
        self.embedder = Embeddings()

    def save_flow(self, domain, flow_json):
        vector = self.embedder.embed(flow_json)
        self.store.flow_db.add(
            ids=[str(uuid.uuid4())],
            embeddings=[vector],
            metadatas=[{"domain": domain, "flow": flow_json}]
        )

    def retrieve_similar_flows(self, domain):
        vector = self.embedder.embed(domain)
        results = self.store.flow_db.query(
            query_embeddings=[vector], n_results=3)
        return results
