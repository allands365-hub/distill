#input_type_name: SaveIssueInput
#output_type_name: SaveIssueResult
#function_name: save_issue

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class SaveIssueInput(BaseModel):
    source_text: str
    source_channel: str = "other"
    title: str = ""
    item_type: str = "question"
    confidence: Optional[float] = None
    priority: Optional[str] = None
    reasoning: str = ""
    repro_steps: Optional[str] = None
    linked_to: Optional[str] = None
    status: str = "triaged"


class SaveIssueResult(BaseModel):
    issue_id: str


async def save_issue(ctx, data: SaveIssueInput) -> SaveIssueResult:
    from lemma_sdk import Pod
    pod = Pod.from_env()
    row = {
        "source_text": data.source_text,
        "source_channel": data.source_channel or "other",
        "title": data.title or "",
        "type": data.item_type or "question",
        "reasoning": data.reasoning or "",
        "status": data.status or "triaged",
    }
    if data.confidence is not None:
        row["confidence"] = data.confidence
    if data.priority:
        row["priority"] = data.priority
    if data.repro_steps:
        row["repro_steps"] = data.repro_steps
    if data.linked_to:
        row["linked_to"] = data.linked_to
    created = pod.table("issues").create(row)
    return SaveIssueResult(issue_id=str(created["id"]))
