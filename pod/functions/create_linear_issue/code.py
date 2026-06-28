#input_type_name: CreateLinearIssueInput
#output_type_name: CreateLinearIssueResult
#function_name: create_linear_issue

from __future__ import annotations
from pydantic import BaseModel
from typing import Optional

TEAM_ID = "5a76158e-d8a0-4f44-ae3a-fd089cf5f8b1"

PRIORITY_MAP = {
    "P0": 1,
    "P1": 2,
    "P2": 3,
    "P3": 4,
}


class CreateLinearIssueInput(BaseModel):
    issue_id: str


class CreateLinearIssueResult(BaseModel):
    ok: bool
    url: Optional[str] = None
    identifier: Optional[str] = None


def _find_in_dict(d, *keys):
    """Recursively search nested dicts/lists for the first matching key."""
    if isinstance(d, dict):
        for k in keys:
            if k in d and d[k]:
                return d[k]
        for v in d.values():
            found = _find_in_dict(v, *keys)
            if found:
                return found
    elif isinstance(d, list):
        for item in d:
            found = _find_in_dict(item, *keys)
            if found:
                return found
    return None


async def create_linear_issue(ctx, data: CreateLinearIssueInput) -> CreateLinearIssueResult:
    from lemma_sdk import Pod
    pod = Pod.from_env()

    # Read the issue row
    row = pod.table("issues").get(data.issue_id)

    # Build title
    title = (row.get("title") or "").strip()
    if not title:
        title = (row.get("source_text") or "")[:80].strip()
    if not title:
        title = f"Issue {data.issue_id}"

    # Build description
    parts = []
    reasoning = (row.get("reasoning") or "").strip()
    if reasoning:
        parts.append(f"**Reasoning:** {reasoning}")
    repro = (row.get("repro_steps") or "").strip()
    if repro:
        parts.append(f"**Repro steps:**\n{repro}")
    channel = (row.get("source_channel") or "").strip()
    source = (row.get("source_text") or "").strip()
    if channel:
        parts.append(f"**Source channel:** {channel}")
    if source:
        parts.append(f"**Original report:**\n```\n{source}\n```")
    description = "\n\n".join(parts)

    # Map priority
    priority_str = (row.get("priority") or "").strip()
    priority_int = PRIORITY_MAP.get(priority_str, 0)

    # Build payload
    payload = {
        "title": title,
        "team_id": TEAM_ID,
        "description": description,
        "priority": priority_int,
    }

    # Execute Linear connector
    raw = pod.connectors.execute("linear", "LINEAR_CREATE_LINEAR_ISSUE", payload).to_dict()
    result = raw.get("result", raw)

    # Parse result defensively - Composio Linear returns ticket_url (not url)
    url = _find_in_dict(result, "ticket_url", "url", "issueUrl")
    identifier = _find_in_dict(result, "identifier")
    # Extract identifier from ticket_url if not found directly
    # e.g. https://linear.app/allands/issue/ALL-80/slug -> ALL-80
    if not identifier and url:
        import re
        m = re.search(r'/issue/([A-Z]+-\d+)', url)
        if m:
            identifier = m.group(1)
    if not identifier:
        identifier = _find_in_dict(result, "id")

    # Best-effort: store url in issues table
    if url:
        try:
            pod.table("issues").update(data.issue_id, {"external_url": url})
        except Exception:
            pass  # Column may not exist or write may fail — skip

    return CreateLinearIssueResult(ok=True, url=url, identifier=str(identifier) if identifier else None)
