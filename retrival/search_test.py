import faiss
import pickle
import os
from embeddings import EmbeddingModel

# ---------- PATH FIX ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

FAISS_INDEX_PATH = os.path.join(DATA_DIR, "faiss.index")
METADATA_PATH = os.path.join(DATA_DIR, "metadata.pkl")
# ----------------------------
TOP_K = 5

def main():
    print("📦 Loading FAISS index...")
    index = faiss.read_index(FAISS_INDEX_PATH)

    print("📦 Loading documents + metadata...")
    with open(METADATA_PATH, "rb") as f:
        documents = pickle.load(f)

    embedder = EmbeddingModel()

    while True:
        query = input("\n🔎 Enter query (or 'exit'): ")
        if query.lower() == "exit":
            break

        q_embedding = embedder.embed_query(query)
        scores, indices = index.search(q_embedding.reshape(1, -1), TOP_K)

        print("\n📄 Results:")
        for i, idx in enumerate(indices[0]):
            doc = documents[idx]
            print(f"\n#{i+1} | score={scores[0][i]:.4f}")
            print("📄 Chunk text:")
            print(doc["text"])
            print("\n🧾 Metadata:")
            print(doc["metadata"])

if __name__ == "__main__":
    main()
