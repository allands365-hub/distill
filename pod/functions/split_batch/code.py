#input_type_name: SplitBatchInput
#output_type_name: SplitBatchResult
#function_name: split_batch

from __future__ import annotations
from typing import List, Dict
from pydantic import BaseModel

VALID_CHANNELS = {"slack", "email", "github", "support", "other"}


def split_items(raw_text: str) -> List[Dict[str, str]]:
    if not raw_text or not raw_text.strip():
        return []
    chunks = raw_text.split("\n---\n")
    items: List[Dict[str, str]] = []
    for chunk in chunks:
        channel = "other"
        title = ""
        body_lines: List[str] = []
        for line in chunk.splitlines():
            stripped = line.strip()
            low = stripped.lower()
            if low.startswith("channel:") and not body_lines:
                value = stripped.split(":", 1)[1].strip().lower()
                channel = value if value in VALID_CHANNELS else "other"
            elif low.startswith("title:") and not body_lines:
                title = stripped.split(":", 1)[1].strip()
            else:
                body_lines.append(line)
        body = "\n".join(body_lines).strip()
        if not body and not title:
            continue
        items.append({"channel": channel, "title": title, "body": body})
    return items


class SplitBatchInput(BaseModel):
    raw_text: str


class SplitItem(BaseModel):
    channel: str
    title: str
    body: str


class SplitBatchResult(BaseModel):
    items: List[SplitItem]


async def split_batch(ctx, data: SplitBatchInput) -> SplitBatchResult:
    return SplitBatchResult(items=[SplitItem(**it) for it in split_items(data.raw_text)])
