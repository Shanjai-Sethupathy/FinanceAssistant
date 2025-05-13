import logging
from typing import List, Optional
import numpy as np
import pandas as pd
import os

try:
    import faiss
    _FAISS_AVAILABLE = True
except ImportError:
    faiss = None
    _FAISS_AVAILABLE = False
    logging.warning("FAISS is not installed.  FAISSRetriever will not be available.")



# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseRetriever:
    

    def __init__(self):
        """
        Initializes the retriever.
        """
        self.texts = []
        self.embeddings = []
        self.metadata = []

    def add_texts(self, texts: List[str], embeddings: np.ndarray, metadata: Optional[List[dict]] = None):

        if len(texts) != embeddings.shape[0]:
            raise ValueError(f"Number of texts ({len(texts)}) does not match number of embeddings ({embeddings.shape[0]})")
        if metadata and len(metadata) != len(texts):
            raise ValueError("Length of metadata list must match the number of texts.")
        self.texts.extend(texts)
        self.embeddings.extend(embeddings)
        self.metadata.extend(metadata if metadata else [{} for _ in texts])

    def retrieve(self, query_embedding: np.ndarray, top_k: int = 5) -> List[dict]:
        
        raise NotImplementedError("Subclasses must implement this method.")

    def get_all(self) -> List[dict]:
        
        return [
            {
                "text": text,
                "embedding": embedding,
                "metadata": metadata
            }
            for text, embedding, metadata in zip(self.texts, self.embeddings, self.metadata)
        ]


class FAISSRetriever(BaseRetriever):
    def __init__(self, embedding_dim: int):
        super().__init__()
        if not _FAISS_AVAILABLE:
            raise ImportError("FAISS is not installed. Please install it to use FAISSRetriever.")
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.embedding_dim = embedding_dim

    def add_texts(self, texts: List[str], embeddings: np.ndarray, metadata: Optional[List[dict]] = None):
        if embeddings.dtype != np.float32:
            raise ValueError("FAISS requires embeddings of dtype np.float32.")
        super().add_texts(texts, embeddings, metadata)
        self.index.add(embeddings)

    def retrieve(self, query_embedding: np.ndarray, top_k: int = 5) -> List[dict]:
        if self.index.ntotal == 0:
            raise ValueError("The FAISS index is empty. Add some texts before querying.")
        if query_embedding.dtype != np.float32:
            raise ValueError("Query embedding must be of dtype np.float32.")
        distances, indices = self.index.search(query_embedding.reshape(1, -1), top_k)
        results = []
        for i in indices[0]:
            if i != -1:
                results.append({
                    "text": self.texts[i],
                    "embedding": self.embeddings[i],
                    "metadata": self.metadata[i]
                })
        return results
