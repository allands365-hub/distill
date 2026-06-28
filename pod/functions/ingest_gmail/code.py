#input_type_name: IngestGmailInput
#output_type_name: IngestGmailResult
#function_name: ingest_gmail

from __future__ import annotations
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class IngestGmailInput(BaseModel):
    # Gmail advanced-search query; default = recent inbox mail.
    query: str = "in:inbox newer_than:7d"
    max_results: int = 10


class IngestGmailResult(BaseModel):
    fetched: int
    run_id: Optional[str] = None
    note: str = ""


def _extract(msg: Dict[str, Any]) -> Dict[str, str]:
    """Defensively pull a subject + body-ish text out of a Gmail message dict.

    The exact GMAIL_FETCH_EMAILS payload shape varies; try the common fields and
    fall back to the snippet. Verify/trim once a real account is connected.
    """
    subject = msg.get("subject") or msg.get("Subject") or ""
    if not subject:
        headers = ((msg.get("payload") or {}).get("headers")) or []
        for h in headers:
            if isinstance(h, dict) and str(h.get("name", "")).lower() == "subject":
                subject = h.get("value", "")
                break
    body = (msg.get("messageText") or msg.get("body") or msg.get("snippet")
            or msg.get("preview") or msg.get("text") or "")
    if isinstance(body, dict):
        body = body.get("text") or body.get("content") or body.get("body") or body.get("data") or ""
    # emails can be long; the issues.source_text column is capped, so truncate.
    return {"subject": str(subject).strip(), "body": str(body).strip()[:4000]}


def _list_in(d: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    for key in ("messages", "emails", "items", "results", "data"):
        val = d.get(key)
        if isinstance(val, list):
            return [m for m in val if isinstance(m, dict)]
    return None


def _messages(result: Any) -> List[Dict[str, Any]]:
    """Find the message list in the (variable) operation result.

    GMAIL_FETCH_EMAILS returns the list at the TOP level (result["messages"]);
    some ops nest it under result["data"]. Check both.
    """
    if isinstance(result, list):
        return [m for m in result if isinstance(m, dict)]
    if isinstance(result, dict):
        got = _list_in(result)
        if got is not None:
            return got
        inner = result.get("data")
        if isinstance(inner, dict):
            got = _list_in(inner)
            if got is not None:
                return got
    return []


async def ingest_gmail(ctx, data: IngestGmailInput) -> IngestGmailResult:
    from lemma_sdk import Pod
    pod = Pod.from_env()

    result = pod.connectors.execute(
        "workspace-gmail",
        "GMAIL_FETCH_EMAILS",
        {
            "query": data.query,
            "user_id": "me",
            "max_results": data.max_results,
            "verbose": True,
            "include_payload": True,
        },
    ).to_dict()["result"]

    items: List[str] = []
    for m in _messages(result):
        ex = _extract(m)
        if not ex["subject"] and not ex["body"]:
            continue
        items.append("Channel: email\nTitle: " + ex["subject"] + "\n" + ex["body"])

    if not items:
        return IngestGmailResult(
            fetched=0,
            note="No emails parsed — confirm the Gmail account is connected and the query matches mail.",
        )

    raw_text = "\n---\n".join(items)
    run = pod.workflows.create_run("triage_batch")
    run_id = str(run.id)
    aw = getattr(run, "active_wait", None)
    if aw is not None and getattr(aw, "wait_type", None) == "HUMAN":
        pod.workflows.submit_form(run_id, node_id=aw.node_id, inputs={"raw_text": raw_text})
    return IngestGmailResult(fetched=len(items), run_id=run_id,
                             note="Started triage_batch on fetched emails.")
