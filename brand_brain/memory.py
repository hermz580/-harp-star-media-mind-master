import os
import faiss
import numpy as np
import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class BrandVectorMemory:
    """Update 4: Vector Memory (RAG) for Brand Context"""
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []

    def add_snippets(self, snippets: List[Dict[str, Any]]):
        if not snippets:
            return

        texts = [s.get('snippet', '') for s in snippets]
        embeddings = self.model.encode(texts)
        self.index.add(np.array(embeddings).astype('float32'))
        self.metadata.extend(snippets)
        logger.info(f"💾 Added {len(snippets)} snippets to Vector Memory.")

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
