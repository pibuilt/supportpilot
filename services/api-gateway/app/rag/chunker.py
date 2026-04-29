from typing import List


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Splits text into overlapping word chunks.
    Current implementation uses word approximation.
    Future phases can replace with tokenizer-aware chunking.
    """

    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = words[start:end]

        chunks.append(" ".join(chunk))

        if end >= len(words):
            break

        start += chunk_size - overlap

    return chunks