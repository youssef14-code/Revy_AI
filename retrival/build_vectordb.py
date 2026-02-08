import faiss
import pickle
import os

from loaders import load_pdf
from Preprocessing import preprocess_text
from chunker import build_chunks
from embeddings import EmbeddingModel

# ---------- PATH FIX ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

FAISS_INDEX_PATH = os.path.join(DATA_DIR, "faiss.index")
METADATA_PATH = os.path.join(DATA_DIR, "metadata.pkl")
# ----------------------------
PDF_PATH = r"C:\Users\hp\Desktop\Revy_AI\retrival\AI Agent Knowledge Base.pdf"
SOURCE_NAME = "AI Agent Knowledge Base"

def main():
    print("📄 Loading PDF...")
    raw_text = load_pdf(PDF_PATH)

    print("🧹 Preprocessing text...")
    clean_text = preprocess_text(raw_text)

    print("✂️ Chunking document...")
    chunks = build_chunks(clean_text, source=SOURCE_NAME)

    print("🧠 Embedding chunks (ONE TIME)...")
    embedder = EmbeddingModel()
    texts = [c["text"] for c in chunks]
    embeddings = embedder.embed_documents(texts)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    print("📁 Ensuring data directory exists...")
    os.makedirs(DATA_DIR, exist_ok=True)

    print("💾 Saving FAISS index...")
    faiss.write_index(index, FAISS_INDEX_PATH)

    # Save text + metadata together
    documents = [{"text": c["text"], "metadata": c["metadata"]} for c in chunks]
    print("💾 Saving documents + metadata...")
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(documents, f)

    print(f"✅ Done. Embedded {len(texts)} chunks.")

if __name__ == "__main__":
    main()
