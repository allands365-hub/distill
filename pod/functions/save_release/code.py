#input_type_name: SaveReleaseInput
#output_type_name: SaveReleaseResult
#function_name: save_release

from __future__ import annotations
from typing import List
from pydantic import BaseModel


class SaveReleaseInput(BaseModel):
    notes_md: str
    issue_ids: List[str] = []


class SaveReleaseResult(BaseModel):
    release_id: str


async def save_release(ctx, data: SaveReleaseInput) -> SaveReleaseResult:
    from lemma_sdk import Pod
    pod = Pod.from_env()
    created = pod.table("releases").create(
        {"notes_md": data.notes_md, "issue_ids": data.issue_ids}
    )
    return SaveReleaseResult(release_id=str(created["id"]))
