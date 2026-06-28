#input_type_name: StartSandboxReproInput
#output_type_name: StartSandboxReproResult
#function_name: start_sandbox_repro

from __future__ import annotations
from pydantic import BaseModel


class StartSandboxReproInput(BaseModel):
    issue_id: str


class StartSandboxReproResult(BaseModel):
    run_id: str


async def start_sandbox_repro(ctx, data: StartSandboxReproInput) -> StartSandboxReproResult:
    from lemma_sdk import Pod
    pod = Pod.from_env()
    run = pod.workflows.create_run("sandbox_repro")
    run_id = str(run.id)
    aw = getattr(run, "active_wait", None)
    if aw is not None and getattr(aw, "wait_type", None) == "HUMAN":
        pod.workflows.submit_form(run_id, node_id=aw.node_id, inputs={"issue_id": data.issue_id})
    return StartSandboxReproResult(run_id=run_id)
