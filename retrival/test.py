from loaders import load_pdf
from Preprocessing import preprocess_text
from chunker import build_chunks

raw = load_pdf(r"C:\Users\Lenovo\OneDrive - Alexandria National University\Desktop\revy_ai\retrival/AI Agent Knowledge Base.pdf")
clean = preprocess_text(raw)
chunks = build_chunks(clean, "AI Agent Knowledge Base.pdf")

print(len(chunks))  # should be 18
print(chunks[1])
    