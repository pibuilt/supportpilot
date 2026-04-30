from typing import List, Dict


def normalize_text(text: str) -> set:
    return set(text.lower().split())


def keyword_overlap_score(query: str, chunk_preview: str) -> float:
    query_tokens = normalize_text(query)
    chunk_tokens = normalize_text(chunk_preview)

    if not query_tokens:
        return 0.0

    overlap = query_tokens.intersection(chunk_tokens)

    return len(overlap) / len(query_tokens)


def rerank_results(query: str, results: List[Dict]) -> List[Dict]:
    reranked = []

    for result in results:
        semantic_score = float(result.get("score", 0.0))

        chunk_text = (
            result.get("preview")
            or result.get("chunk_text")
            or result.get("content")
            or ""
        )

        keyword_score = keyword_overlap_score(query, chunk_text)

        final_score = (0.7 * semantic_score) + (0.3 * keyword_score)

        result["semantic_score"] = semantic_score
        result["keyword_score"] = keyword_score
        result["rerank_score"] = final_score

        reranked.append(result)

    reranked.sort(key=lambda x: x["rerank_score"], reverse=True)

    return reranked