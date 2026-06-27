"""Deterministic P0-P3 priority detection for bugs.

Ported from OSS Warden (src/agents/priority_detection.py). No LLM call.
"""
from typing import Optional, Dict, Any

PRIORITY_KEYWORDS = {
    "P0": {
        "severity": "critical",
        "description": "Critical - Immediate attention required",
        "keywords": [
            "crash", "crashes", "crashing", "data loss", "data corruption",
            "lost data", "security", "vulnerability", "exploit", "breach",
            "cannot use", "completely broken", "unusable", "production down",
            "outage", "critical", "all users affected", "system down",
        ],
    },
    "P1": {
        "severity": "high",
        "description": "High - Major functionality broken",
        "keywords": [
            "broken", "not working", "doesn't work", "fails", "error",
            "exception", "major bug", "blocking", "blocker", "urgent",
            "many users affected", "core functionality", "production issue",
        ],
    },
    "P2": {
        "severity": "medium",
        "description": "Medium - Minor bug with workaround",
        "keywords": [
            "slow", "performance", "sluggish", "minor bug", "small issue",
            "edge case", "some users", "workaround available", "inconsistent",
            "intermittent",
        ],
    },
    "P3": {
        "severity": "low",
        "description": "Low - Cosmetic or trivial issue",
        "keywords": [
            "typo", "cosmetic", "visual", "nice to have", "enhancement",
            "improvement", "documentation", "spelling", "formatting",
            "low priority", "minor", "trivial",
        ],
    },
}

IMPACT_BOOST_KEYWORDS = [
    "production", "urgent", "blocker", "critical", "all users", "everyone",
    "always", "every time",
]

PRIORITY_ORDER = ["P0", "P1", "P2", "P3"]


def detect_priority(
    classification_type: str, title: str, body: str
) -> Optional[Dict[str, Any]]:
    if classification_type != "bug":
        return None

    text = f"{title} {body or ''}".lower()

    scores: Dict[str, Dict[str, Any]] = {}
    for priority, cfg in PRIORITY_KEYWORDS.items():
        matched = [k for k in cfg["keywords"] if k in text]
        if matched:
            scores[priority] = {"score": len(matched), "keywords": matched}

    if not scores:
        return {
            "priority": "P2",
            "severity": "medium",
            "reasoning": "No specific severity indicators found - defaulting to medium.",
            "confidence": 0.5,
            "matched_keywords": [],
        }

    for priority in PRIORITY_ORDER:
        if priority not in scores:
            continue
        result = scores[priority]
        boosts = [k for k in IMPACT_BOOST_KEYWORDS if k in text]

        final = priority
        if len(boosts) >= 2 and priority != "P0":
            idx = PRIORITY_ORDER.index(priority)
            final = PRIORITY_ORDER[idx - 1]

        confidence = min(0.95, 0.6 + result["score"] * 0.1 + len(boosts) * 0.05)

        reason_parts = []
        if result["keywords"]:
            kws = ", ".join(f"'{k}'" for k in result["keywords"][:3])
            reason_parts.append(f"Contains {kws}")
        if boosts:
            reason_parts.append(
                "Impact indicators: " + ", ".join(f"'{b}'" for b in boosts[:2])
            )
        if final != priority:
            reason_parts.append(f"Elevated from {priority} due to high impact")
        reasoning = ". ".join(reason_parts) + "."

        return {
            "priority": final,
            "severity": PRIORITY_KEYWORDS[final]["severity"],
            "reasoning": reasoning,
            "confidence": round(confidence, 2),
            "matched_keywords": result["keywords"],
        }

    return {
        "priority": "P2", "severity": "medium",
        "reasoning": "Default medium priority.", "confidence": 0.5,
        "matched_keywords": [],
    }
