"""
Simple keyword-based RAG engine for agent knowledge libraries.

This is intentionally lightweight to avoid heavy vector DB dependencies.
In production, this can be replaced with pgvector, Chroma, or FAISS.
"""
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SimpleRAG:
    """Keyword-based retrieval over a directory of Markdown files."""

    def __init__(self, library_path: Path):
        self.library_path = Path(library_path)
        self.documents: List[Dict[str, Any]] = []
        self._load_documents()

    def _load_documents(self):
        if not self.library_path.exists():
            logger.warning(f"Library path does not exist: {self.library_path}")
            return

        for md_file in sorted(self.library_path.glob("*.md")):
            try:
                content = md_file.read_text(encoding="utf-8")
                self.documents.append({
                    "source": md_file.name,
                    "content": content,
                    "chunks": self._chunk(content),
                })
            except Exception as e:
                logger.error(f"Failed to load {md_file}: {e}")

        logger.info(f"Loaded {len(self.documents)} documents from {self.library_path}")

    def _chunk(self, text: str, max_chunk_size: int = 1500) -> List[str]:
        """Split text into chunks by headers."""
        sections = re.split(r"\n(?=#+\s)", text)
        chunks = []
        current = ""
        for section in sections:
            if len(current) + len(section) > max_chunk_size and current:
                chunks.append(current.strip())
                current = section
            else:
                current += "\n\n" + section
        if current.strip():
            chunks.append(current.strip())
        return chunks or [text]

    def _tokenize(self, text: str) -> set:
        """Simple Spanish-aware tokenization."""
        text = text.lower()
        text = re.sub(r"[^\w\sáéíóúñ]", " ", text)
        words = text.split()
        # Remove very common stop words
        stop = {
            "el", "la", "de", "que", "y", "a", "en", "un", "ser", "es",
            "por", "con", "su", "para", "una", "lo", "del", "al", "las",
            "los", "se", "son", "esto", "esta", "pero", "más", "o", "sus",
        }
        return {w for w in words if len(w) > 2 and w not in stop}

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Return the top-k most relevant chunks for a query."""
        if not self.documents:
            return []

        query_tokens = self._tokenize(query)
        scored = []

        for doc in self.documents:
            for idx, chunk in enumerate(doc["chunks"]):
                chunk_tokens = self._tokenize(chunk)
                score = len(query_tokens & chunk_tokens)
                # Boost title/header matches
                headers = re.findall(r"^#+\s+(.+)$", chunk, re.MULTILINE)
                header_tokens = self._tokenize(" ".join(headers))
                score += len(query_tokens & header_tokens) * 2
                if score > 0:
                    scored.append({
                        "source": doc["source"],
                        "chunk_index": idx,
                        "content": chunk,
                        "score": score,
                    })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def get_context(self, query: str, top_k: int = 3) -> Optional[str]:
        """Get a single context string from retrieved chunks."""
        results = self.retrieve(query, top_k)
        if not results:
            return None
        parts = []
        for r in results:
            parts.append(f"## Fuente: {r['source']}\n{r['content']}")
        return "\n\n".join(parts)
