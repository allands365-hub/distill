#input_type_name: NotifySlackInput
#output_type_name: NotifySlackOutput
#function_name: notify_slack

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel
from lemma_sdk import FunctionContext, Pod


class NotifySlackInput(BaseModel):
    issue_id: str
    channel: str = "U09SHBF7L8K"


class NotifySlackOutput(BaseModel):
    ok: bool
    ts: Optional[str] = None
    channel: str


async def notify_slack(ctx: FunctionContext, data: NotifySlackInput) -> NotifySlackOutput:
    pod = Pod.from_env()

    issue = pod.table("issues").get(data.issue_id)

    title = issue.get("title") or "(no title)"
    priority = issue.get("priority") or "?"
    status = issue.get("status") or "?"
    reasoning = issue.get("reasoning") or ""

    lines = [
        f"🚨 P0 triaged: {title}",
        f"Priority: {priority} | Status: {status}",
    ]
    if reasoning:
        lines.append(reasoning)
    text = "\n".join(lines)

    result = pod.connectors.execute(
        "slack",
        "chat_post_message",
        {"body": {"channel": data.channel, "text": text}},
    ).to_dict()["result"]

    return NotifySlackOutput(
        ok=bool(result.get("ok", False)),
        ts=result.get("ts"),
        channel=result.get("channel", data.channel),
    )
