#input_type_name: DupInput
#output_type_name: DupResult
#function_name: detect_duplicates

from __future__ import annotations
from difflib import SequenceMatcher
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


def _normalize(item: Dict[str, str]) -> str:
    return f"{item.get('title','')} {item.get('body','')}".lower().strip()


def _ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def find_duplicates(item: Dict[str, str], existing: List[Dict[str, Any]],
                    threshold: float = 0.6) -> Dict[str, Any]:
    query = _normalize(item)
    q_title = (item.get("title") or "").lower().strip()
    candidates = []
    for other in existing:
        combined = _ratio(query, _normalize(other))
        o_title = (other.get("title") or "").lower().strip()
        # Title-to-title similarity catches paraphrased duplicates whose bodies
        # differ in structure (e.g. one has numbered repro steps, one is prose).
        title_sim = _ratio(q_title, o_title) if (q_title and o_title) else 0.0
        score = max(combined, title_sim)
        candidates.append({"id": other["id"], "score": round(score, 4)})
    candidates.sort(key=lambda c: c["score"], reverse=True)
    linked_to: Optional[str] = None
    if candidates and candidates[0]["score"] >= threshold:
        linked_to = candidates[0]["id"]
    top = candidates[0]["score"] if candidates else 0.0
    return {"linked_to": linked_to, "top_score": top, "candidates": candidates}


class DupInput(BaseModel):
    title: str = ""
    body: str = ""
    threshold: float = 0.6


class DupResult(BaseModel):
    linked_to: Optional[str] = None
    top_score: float = 0.0


async def detect_duplicates(ctx, data: DupInput) -> DupResult:
    from lemma_sdk import Pod
    pod = Pod.from_env()
    rows = pod.records.list("issues", limit=500).to_dict()["items"]
    existing = [{"id": str(r["id"]), "title": r.get("title") or "",
                 "body": r.get("source_text") or ""} for r in rows]
    r = find_duplicates({"title": data.title, "body": data.body}, existing, data.threshold)
    return DupResult(**r)
