"""Lightweight duplicate/related detection for demo scale.

Preserves OSS Warden's design (combine title+body, similarity threshold, scored
matches, auto-link to the best one) using stdlib difflib instead of pgvector.
"""
from difflib import SequenceMatcher
from typing import List, Dict, Any, Optional


def _normalize(item: Dict[str, str]) -> str:
    return f"{item.get('title','')} {item.get('body','')}".lower().strip()


def detect_duplicates(
    item: Dict[str, str],
    existing: List[Dict[str, Any]],
    threshold: float = 0.6,
) -> Dict[str, Any]:
    query = _normalize(item)
    candidates = []
    for other in existing:
        score = SequenceMatcher(None, query, _normalize(other)).ratio()
        candidates.append({"id": other["id"], "score": round(score, 4)})

    candidates.sort(key=lambda c: c["score"], reverse=True)

    linked_to: Optional[str] = None
    if candidates and candidates[0]["score"] >= threshold:
        linked_to = candidates[0]["id"]

    return {"linked_to": linked_to, "candidates": candidates}
