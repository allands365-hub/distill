#input_type_name: GetIssueFieldsInput
#output_type_name: GetIssueFieldsResult
#function_name: get_issue_fields

from __future__ import annotations
from pydantic import BaseModel


class GetIssueFieldsInput(BaseModel):
    issue_id: str


class GetIssueFieldsResult(BaseModel):
    title: str
    body: str
    repro_steps: str


async def get_issue_fields(ctx, data: GetIssueFieldsInput) -> GetIssueFieldsResult:
    from lemma_sdk import Pod
    pod = Pod.from_env()
    row = pod.table("issues").get(data.issue_id)
    return GetIssueFieldsResult(
        title=row.get("title") or "",
        body=row.get("source_text") or "",
        repro_steps=row.get("repro_steps") or "",
    )
