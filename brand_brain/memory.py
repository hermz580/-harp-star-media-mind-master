import os
import faiss
import numpy as np
import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from .core.events import bus, Event

logger = logging.getLogger(__name__)

class Cortex:
    """Update 12: Unified Memory & Knowledge Graph (The Cortex)"""
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        # Update 12: Simple Knowledge Graph (Conceptual Relationships)
        self.knowledge_graph = {}

    async def add_snippets(self, snippets: List[Dict[str, Any]]):
        if not snippets:
            return

        texts = [s.get('snippet', '') for s in snippets]
        embeddings = self.model.encode(texts)
        self.index.add(np.array(embeddings).astype('float32'))
        self.metadata.extend(snippets)

        # [Apex Update 12] Extract relationships for Graph
        for s in snippets:
            path = s.get('path', 'unknown')
            # Heuristic: link path to its content snippets
            if path not in self.knowledge_graph:
                self.knowledge_graph[path] = []
            self.knowledge_graph[path].append("content_snippet")

        await bus.emit(Event("memory_updated", {"count": len(snippets), "total": self.index.ntotal}, source="cortex"))
        logger.info(f"🧠 Added {len(snippets)} snippets to Unified Cortex.")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if self.index.ntotal == 0:
            return []

        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), top_k)

        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx < len(self.metadata):
                results.append(self.metadata[idx])
        return results

    def get_graph_data(self):
        """Returns nodes and links for UI Topology visualization"""
        nodes = []
        links = []

        # Core Root
        nodes.append({"id": "BRAND_BRAIN", "type": "core", "group": 1})

        for i, path in enumerate(list(self.knowledge_graph.keys())[:20]):
            nodes.append({"id": path, "type": "asset", "group": 2})
            links.append({"source": "BRAND_BRAIN", "target": path})

        return {"nodes": nodes, "links": links}
