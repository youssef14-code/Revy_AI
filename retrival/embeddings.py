# embeddings.py
from sentence_transformers import SentenceTransformer

MODEL_NAME = "intfloat/multilingual-e5-large"

class EmbeddingModel:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

    def embed_documents(self, texts):
        texts = [f"passage: {t}" for t in texts]
        return self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True
        )

    def embed_query(self, query: str):
        query = f"query: {query}"
        return self.model.encode(
            [query],
            normalize_embeddings=True
        )[0]
