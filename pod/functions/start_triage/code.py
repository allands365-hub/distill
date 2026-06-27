#input_type_name: StartTriageInput
#output_type_name: StartTriageResult
#function_name: start_triage

from __future__ import annotations
from pydantic import BaseModel


class StartTriageInput(BaseModel):
    raw_text: str


class StartTriageResult(BaseModel):
    run_id: str


async def start_triage(ctx, data: StartTriageInput) -> StartTriageResult:
    from lemma_sdk import Pod
    pod = Pod.from_env()
    run = pod.workflows.create_run("triage_batch")
    run_id = str(run.id)
    aw = getattr(run, "active_wait", None)
    if aw is not None and getattr(aw, "wait_type", None) == "HUMAN":
        pod.workflows.submit_form(run_id, node_id=aw.node_id, inputs={"raw_text": data.raw_text})
    return StartTriageResult(run_id=run_id)
