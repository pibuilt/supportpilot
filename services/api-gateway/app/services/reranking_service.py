from typing import List, Dict


def normalize_text(text: str) -> set:
    return set(text.lower().split())


def keyword_overlap_score(query: str, chunk_text: str) -> float:
    query_tokens = normalize_text(query)
    chunk_tokens = normalize_text(chunk_text)

    if not query_tokens:
        return 0.0

    overlap = query_tokens.intersection(chunk_tokens)

    return len(overlap) / len(query_tokens)


def rerank_results(query: str, results: List[Dict]) -> List[Dict]:
    reranked = []

    query_lower = query.lower()

    for result in results:
        semantic_score = float(result.get("score", 0.0))

        chunk_text = (
            result.get("chunk_text")
            or result.get("preview")
            or result.get("content")
            or ""
        )

        chunk_lower = chunk_text.lower()

        keyword_score = keyword_overlap_score(
            query,
            chunk_text,
        )

        exact_phrase_bonus = (
            0.15 if query_lower in chunk_lower else 0.0
        )

        query_terms = query_lower.split()

        keyword_matches = sum(
            1 for term in query_terms
            if term in chunk_lower
        )

        density_bonus = min(
            keyword_matches * 0.03,
            0.15,
        )

        final_score = (
            (0.65 * semantic_score)
            + (0.25 * keyword_score)
            + exact_phrase_bonus
            + density_bonus
        )

        boosted_result = result.copy()

        boosted_result["semantic_score"] = round(
            semantic_score,
            4,
        )

        boosted_result["keyword_score"] = round(
            keyword_score,
            4,
        )

        boosted_result["keyword_matches"] = keyword_matches

        boosted_result["rerank_score"] = round(
            final_score,
            4,
        )

        reranked.append(boosted_result)

    reranked.sort(
        key=lambda x: x["rerank_score"],
        reverse=True,
    )

    return reranked