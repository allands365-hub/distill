#input_type_name: SetStatusInput
#output_type_name: SetStatusResult
#function_name: set_status

from __future__ import annotations
from pydantic import BaseModel


class SetStatusInput(BaseModel):
    issue_id: str
    status: str


class SetStatusResult(BaseModel):
    issue_id: str
    status: str


async def set_status(ctx, data: SetStatusInput) -> SetStatusResult:
    from lemma_sdk import Pod
    pod = Pod.from_env()
    pod.table("issues").update(data.issue_id, {"status": data.status})
    return SetStatusResult(issue_id=data.issue_id, status=data.status)
