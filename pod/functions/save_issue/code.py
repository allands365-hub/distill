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
    status: str = "auto"


class SaveIssueResult(BaseModel):
    issue_id: str
    status: str


async def save_issue(ctx, data: SaveIssueInput) -> SaveIssueResult:
    from lemma_sdk import Pod
    pod = Pod.from_env()

    item_type = "duplicate" if data.linked_to else (data.item_type or "question")

    status = data.status
    if not status or status == "auto":
        if data.linked_to:
            status = "triaged"
        elif (data.confidence is not None and data.confidence < 0.7) or data.priority == "P0":
            status = "needs_approval"
        else:
            status = "triaged"

    row = {
        "source_text": data.source_text,
        "source_channel": data.source_channel or "other",
        "title": data.title or "",
        "type": item_type,
        "reasoning": data.reasoning or "",
        "status": status,
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
    return SaveIssueResult(issue_id=str(created["id"]), status=status)
