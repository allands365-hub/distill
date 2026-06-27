#input_type_name: GatherInput
#output_type_name: GatherResult
#function_name: gather_fixed_issues

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel


class GatherInput(BaseModel):
    only: Optional[str] = None  # unused; functions need an input model


class FixedIssue(BaseModel):
    title: str = ""
    type: str = ""
    priority: Optional[str] = None
    reasoning: str = ""


class GatherResult(BaseModel):
    issues: List[FixedIssue]
    ids: List[str]
    count: int


async def gather_fixed_issues(ctx, data: GatherInput) -> GatherResult:
    from lemma_sdk import Pod
    pod = Pod.from_env()
    rows = pod.records.list(
        "issues", limit=500,
        filter=[{"field": "status", "op": "eq", "value": "fixed"}],
    ).to_dict()["items"]
    issues = [FixedIssue(title=r.get("title") or "", type=r.get("type") or "",
                         priority=r.get("priority"), reasoning=r.get("reasoning") or "")
              for r in rows]
    ids = [str(r["id"]) for r in rows]
    return GatherResult(issues=issues, ids=ids, count=len(ids))
