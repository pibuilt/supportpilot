from typing import List
import re

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)


CLAUSE_PATTERNS = [
    r"^\d+\.\s+.+$",
    r"^SECTION\s+\d+[\s:\-].+$",
    r"^ARTICLE\s+[IVXLC]+[\s:\-].+$",
]


def _is_clause_header(
    line: str,
) -> bool:

    line = line.strip()

    for pattern in CLAUSE_PATTERNS:

        if re.match(
            pattern,
            line,
            re.IGNORECASE,
        ):
            return True

    return False


def _extract_clauses(
    text: str,
) -> List[str]:

    lines = text.splitlines()

    clauses = []

    current_clause = []

    for line in lines:

        if (
            _is_clause_header(
                line
            )
            and current_clause
        ):

            clauses.append(
                "\n".join(
                    current_clause
                ).strip()
            )

            current_clause = [
                line
            ]

        else:

            current_clause.append(
                line
            )

    if current_clause:

        clauses.append(
            "\n".join(
                current_clause
            ).strip()
        )

    return clauses


def _split_large_clause(
    clause: str,
    chunk_size: int,
    overlap: int,
) -> List[str]:

    splitter = (
        RecursiveCharacterTextSplitter(
            chunk_size=chunk_size * 6,
            chunk_overlap=overlap * 6,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
            ],
        )
    )

    return splitter.split_text(
        clause
    )


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> List[str]:

    if not text:
        return []

    clauses = (
        _extract_clauses(
            text
        )
    )

    chunks = []

    for clause in clauses:

        word_count = len(
            clause.split()
        )

        if word_count <= chunk_size:

            chunks.append(
                clause
            )

        else:

            chunks.extend(
                _split_large_clause(
                    clause,
                    chunk_size,
                    overlap,
                )
            )

    return chunks