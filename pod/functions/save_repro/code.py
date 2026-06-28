#input_type_name: SaveReproInput
#output_type_name: SaveReproResult
#function_name: save_repro

from __future__ import annotations
from pydantic import BaseModel


class SaveReproInput(BaseModel):
    issue_id: str
    reproduced: bool = False
    steps: str = ""
    evidence: str = ""
    root_cause: str = ""


class SaveReproResult(BaseModel):
    ok: bool
    issue_id: str


async def save_repro(ctx, data: SaveReproInput) -> SaveReproResult:
    from lemma_sdk import Pod
    pod = Pod.from_env()

    evidence_text = data.evidence or ""
    if data.root_cause:
        evidence_text = evidence_text + "\n\nRoot cause: " + data.root_cause

    patch = {"reproduced": data.reproduced, "repro_evidence": evidence_text}
    if data.steps:
        patch["repro_steps"] = data.steps

    pod.table("issues").update(data.issue_id, patch)
    return SaveReproResult(ok=True, issue_id=data.issue_id)
