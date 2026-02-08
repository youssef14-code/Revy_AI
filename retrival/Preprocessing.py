# preprocessing.py
import re

def preprocess_text(text: str) -> str:
    """
    Clean and normalize extracted PDF text.
    """
    # remove excessive newlines
    text = re.sub(r"\n{2,}", "\n", text)

    # normalize bullets
    text = text.replace("•", "-")

    # trim spaces
    text = text.strip()

    return text
