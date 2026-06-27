#input_type_name: StartReleaseInput
#output_type_name: StartReleaseResult
#function_name: start_release_notes

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class StartReleaseInput(BaseModel):
    unused: Optional[str] = None


class StartReleaseResult(BaseModel):
    run_id: str


async def start_release_notes(ctx, data: StartReleaseInput) -> StartReleaseResult:
    from lemma_sdk import Pod
    pod = Pod.from_env()
    run = pod.workflows.create_run("generate_release_notes")
    return StartReleaseResult(run_id=str(run.id))
