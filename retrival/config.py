from pathlib import Path

# absolute path to retrival/
BASE_DIR = Path(__file__).resolve().parent

# absolute path to data/chroma
CHROMA_DIR = BASE_DIR / "data" / "chroma"

COLLECTION_NAME = "ai_agent_kb"
