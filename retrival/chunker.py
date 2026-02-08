# chunker.py
import re
from typing import List, Dict

SECTION_REGEX = r"\n(\d+)\.\s([A-Z &]+)\n"

def split_layers(text: str) -> Dict[str, str]:
    """
    Split document into logical layers.
    """
    tech_marker = "TECHNICAL EXPLANATION LAYER"

    agent_part, tech_part = text.split(tech_marker)

    return {
        "agent_knowledge_base": agent_part.strip(),
        "technical_explanation_layer": tech_marker + tech_part.strip()
    }


def split_sections(layer_text: str) -> List[Dict]:
    """
    Split a layer into numbered sections (1–9).
    Each section is a single chunk.
    """
    matches = list(re.finditer(SECTION_REGEX, layer_text))
    sections = []

    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(layer_text)

        sections.append({
            "section_id": int(match.group(1)),
            "section_title": match.group(2).strip(),
            "text": layer_text[start:end].strip()
        })

    return sections


def build_chunks(text: str, source: str) -> List[Dict]:
    """
    Build final RAG chunks.
    Layer → Section = Chunk
    """
    chunks = []
    layers = split_layers(text)

    for layer_name, layer_text in layers.items():
        sections = split_sections(layer_text)

        for sec in sections:
            chunks.append({
                "text": sec["text"],
                "metadata": {
                    "source": source,
                    "layer": layer_name,
                    "section_id": sec["section_id"],
                    "section_title": sec["section_title"],
                    "chunk_id": f"{layer_name}_S{sec['section_id']}",
                    "audience": "internal" if layer_name == "agent_knowledge_base" else "client"
                }
            })

    return chunks
