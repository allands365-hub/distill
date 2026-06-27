#input_type_name: PriorityInput
#output_type_name: PriorityResult
#function_name: detect_priority

from __future__ import annotations
from typing import Optional, Dict, Any
from pydantic import BaseModel

PRIORITY_KEYWORDS = {
    "P0": {"severity": "critical", "keywords": [
        "crash", "crashes", "crashing", "data loss", "data corruption", "lost data",
        "security", "vulnerability", "exploit", "breach", "cannot use",
        "completely broken", "unusable", "production down", "outage", "critical",
        "all users affected", "system down"]},
    "P1": {"severity": "high", "keywords": [
        "broken", "not working", "doesn't work", "fails", "error", "exception",
        "major bug", "blocking", "blocker", "urgent", "many users affected",
        "core functionality", "production issue"]},
    "P2": {"severity": "medium", "keywords": [
        "slow", "performance", "sluggish", "minor bug", "small issue", "edge case",
        "some users", "workaround available", "inconsistent", "intermittent"]},
    "P3": {"severity": "low", "keywords": [
        "typo", "cosmetic", "visual", "nice to have", "enhancement", "improvement",
        "documentation", "spelling", "formatting", "low priority", "minor", "trivial"]},
}
IMPACT_BOOST_KEYWORDS = ["production", "urgent", "blocker", "critical", "all users",
                         "everyone", "always", "every time"]
PRIORITY_ORDER = ["P0", "P1", "P2", "P3"]


def score_priority(item_type: str, title: str, body: str) -> Optional[Dict[str, Any]]:
    if item_type != "bug":
        return None
    text = f"{title} {body or ''}".lower()
    scores: Dict[str, Dict[str, Any]] = {}
    for priority, cfg in PRIORITY_KEYWORDS.items():
        matched = [k for k in cfg["keywords"] if k in text]
        if matched:
            scores[priority] = {"score": len(matched), "keywords": matched}
    if not scores:
        return {"priority": "P2", "severity": "medium",
                "reasoning": "No specific severity indicators found - defaulting to medium.",
                "confidence": 0.5}
    for priority in PRIORITY_ORDER:
        if priority not in scores:
            continue
        result = scores[priority]
        boosts = [k for k in IMPACT_BOOST_KEYWORDS if k in text]
        final = priority
        if len(boosts) >= 2 and priority != "P0":
            final = PRIORITY_ORDER[PRIORITY_ORDER.index(priority) - 1]
        confidence = min(0.95, 0.6 + result["score"] * 0.1 + len(boosts) * 0.05)
        parts = []
        if result["keywords"]:
            parts.append("Contains " + ", ".join(f"'{k}'" for k in result["keywords"][:3]))
        if boosts:
            parts.append("Impact indicators: " + ", ".join(f"'{b}'" for b in boosts[:2]))
        if final != priority:
            parts.append(f"Elevated from {priority} due to high impact")
        return {"priority": final, "severity": PRIORITY_KEYWORDS[final]["severity"],
                "reasoning": ". ".join(parts) + ".", "confidence": round(confidence, 2)}
    return {"priority": "P2", "severity": "medium",
            "reasoning": "Default medium priority.", "confidence": 0.5}


class PriorityInput(BaseModel):
    item_type: str
    title: str = ""
    body: str = ""


class PriorityResult(BaseModel):
    priority: Optional[str] = None
    severity: Optional[str] = None
    reasoning: str = ""
    confidence: Optional[float] = None


async def detect_priority(ctx, data: PriorityInput) -> PriorityResult:
    r = score_priority(data.item_type, data.title, data.body)
    if r is None:
        return PriorityResult(reasoning="Not a bug; no priority assigned.")
    return PriorityResult(**r)
