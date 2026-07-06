"""Heuristics for selecting user messages worth saving as memories."""

from __future__ import annotations

import re


class MemoryExtractor:
    """Extracts likely durable user facts from conversation."""

    _PATTERNS = (
        re.compile(r"^\s*i am\s+.+", re.IGNORECASE),
        re.compile(r"^\s*i'm\s+.+", re.IGNORECASE),
        re.compile(r"^\s*im\s+.+", re.IGNORECASE),
        re.compile(r"^\s*i have\s+.+", re.IGNORECASE),
        re.compile(r"^\s*i own\s+.+", re.IGNORECASE),
        re.compile(r"^\s*i ride\s+.+", re.IGNORECASE),
        re.compile(r"^\s*i like\s+.+", re.IGNORECASE),
        re.compile(r"^\s*i prefer\s+.+", re.IGNORECASE),
        re.compile(r"^\s*i live\s+.+", re.IGNORECASE),
        re.compile(r"^\s*my\s+\w.+", re.IGNORECASE),
    )

    def extract(self, message: str) -> str | None:
        """Return a memory-worthy fact if the message looks durable."""
        normalized = " ".join(message.strip().split())
        if len(normalized) < 8 or normalized.endswith("?"):
            return None

        for clause in self._candidate_clauses(normalized):
            if any(pattern.match(clause) for pattern in self._PATTERNS):
                return clause.rstrip(".") + "."

        return None

    def _candidate_clauses(self, message: str) -> list[str]:
        clauses = [clause.strip() for clause in re.split(r"[.!?]+", message) if clause.strip()]
        return clauses or [message]
