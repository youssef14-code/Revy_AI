from langchain_text_splitters import RecursiveCharacterTextSplitter
import re


def clean_text(text: str) -> str:
    """
    Clean raw document text for RAG ingestion.
    """
    # Remove page numbers (Page 1, Page 2, etc.)
    text = re.sub(r'Page\s+\d+', '', text, flags=re.IGNORECASE)

    # Remove common footer/header patterns
    text = re.sub(r'©.*', '', text)
    text = re.sub(r'Confidential.*', '', text, flags=re.IGNORECASE)

    # Normalize excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Normalize spaces & tabs
    text = re.sub(r'[ \t]+', ' ', text)

    return text.strip()


def extract_faqs(text: str):
    """
    Extract FAQs as individual chunks.
    Returns: (clean_text_without_faqs, faq_chunks)
    """
    faq_pattern = re.compile(
        r'(Q:\s.*?\nA:\s.*?)(?=\nQ:|\Z)',
        re.DOTALL | re.IGNORECASE
    )

    faqs = faq_pattern.findall(text)
    text_without_faqs = faq_pattern.sub('', text)

    faq_chunks = [faq.strip() for faq in faqs]

    return text_without_faqs.strip(), faq_chunks



ABBREVIATIONS = {
    "CRM": "Customer Relationship Management",
    "AI": "Artificial Intelligence",
    "NLP": "Natural Language Processing"
}

def expand_abbreviations(text: str) -> str:
    for abbr, full in ABBREVIATIONS.items():
        pattern = rf'\b{abbr}\b'
        replacement = f"{full} ({abbr})"
        text = re.sub(pattern, replacement, text)
    return text



def semantic_chunk(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=80,
        separators=[
            "\n\n",  # sections
            "\n",    # paragraphs
            ".",     # sentences
            " "
        ]
    )

    return splitter.split_text(text)



def preprocess_document(raw_text: str):
    # Step 1: Clean
    text = clean_text(raw_text)

    # Step 2: Expand abbreviations (optional)
    text = expand_abbreviations(text)

    # Step 3: Extract FAQs
    main_text, faq_chunks = extract_faqs(text)

    # Step 4: Semantic chunking
    main_chunks = semantic_chunk(main_text)

    # Step 5: Attach metadata
    documents = []

    for chunk in main_chunks:
        documents.append({
            "text": chunk,
            "metadata": {
                "intent": "general",
                "source": "AI agent_docs"
            }
        })

    for faq in faq_chunks:
        documents.append({
            "text": faq,
            "metadata": {
                "intent": "faq",
                "source": "AI agent_docs"
            }
        })

    return documents
