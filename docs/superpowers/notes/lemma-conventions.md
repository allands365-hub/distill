# Lemma Conventions (discovered from CLI + lemma-builder skill, 2026-06-27)

CLI `lemma` 0.5.3 (sdk 0.5.3). Auth: `allands365@gmail.com`, org "Allands365's Space".
Bundle = directory of plain files imported with `lemma pods import`. **Bundle is the
source of truth; import upserts by name and replaces grants/graphs wholesale.**
Add `C:\Users\Allan\.local\bin` to PATH to use `lemma`. Reference skill on disk:
`C:\Users\Allan\.claude\skills\lemma-builder\` (SKILL.md + references/*.md).

## Bundle layout (folder name MUST equal each resource's `name`)
```
pod/
  pod.json
  tables/<name>/<name>.json
  functions/<name>/<name>.json + code.py     # JSON carries permissions.grants
  agents/<name>/<name>.json    + instruction.md
  workflows/<name>/<name>.json
  apps/<name>/<name>.json + source/
  files/<folder>/.folder.json                # file CONTENTS don't bundle; upload via CLI
```
Build order: tables → files → functions → agents → workflows → schedules → surfaces → app → seed.
Validate without writing: `lemma pods import ./pod --dry-run`. Partial import OK:
`lemma pods import ./pod/tables/issues`. JSONC (`//`, `/* */`, trailing commas) allowed.

## pod.json
`{ "format_version": 2, "name": "...", "description": "..." }`

## Tables
- Auto columns: `id`, `created_at`, `updated_at`, `user_id` — NEVER declare them.
- `enable_rls`: true = per-user private rows; **false = shared team data** (use false so
  the workflow + app see every row).
- Column types: BOOLEAN DATE DATETIME ENUM FILE_PATH FLOAT INTEGER JSON SERIAL TEXT USER UUID VECTOR.
- ENUM: `{"name","type":"ENUM","required":bool,"default":"x","options":[...]}`. `required:false`
  with no default = nullable. FK: `"foreign_key": {"references": "people.id"}`.
- Records/file contents do NOT round-trip through import — seed via CLI after import.

## Functions (deterministic Python)
- `functions/<name>/code.py` — first lines are required headers:
  `#input_type_name: X`, `#output_type_name: Y`, `#function_name: <name>` (== folder name),
  optional `#python_packages: a, b`.
- Signature: `async def <name>(ctx: FunctionContext, data: <Input>) -> <Output>` with pydantic models.
- `from lemma_sdk import FunctionContext, Pod`; `pod = Pod.from_env()` (delegated identity).
  `pod.table(n).create/get/update/delete`, `pod.records.list(...).to_dict()["items"]`, `pod.query(sql)`.
- `<name>.json`: `{"name","description","type":"API"|"JOB","code":{"$file":"code.py"},"permissions":{"grants":[...]}}`.
- **Schemas are immutable after create** — to change input/output shape, delete+recreate (or version name).
- LOCAL-TEST PATTERN (keep pytest working without lemma_sdk installed): put `from __future__ import
  annotations` right after the header comments, keep pure helper + pydantic models at module top,
  and do `from lemma_sdk import Pod` lazily INSIDE the handler. Tests import the pure helper.

## Agents (judgment)
- `agents/<name>/<name>.json` + `instruction.md` (system prompt via `{"$file":"instruction.md"}`).
- Fields: `name, description, instruction, toolsets:[...], visibility, output_schema, permissions.grants`,
  optional `input_schema`, `agent_runtime:{"profile_id":"..."}`.
- **`output_schema`** (JSON Schema) is the contract for workflow/tool consumption — without it the
  agent returns a plain string. Define exact fields + `required`.
- Toolsets: POD WORKSPACE_CLI SKILLS WEB_SEARCH USER_INTERACTION SPEECH SUBAGENTS. For reading/writing
  pod tables use `POD`. Zero access by default — grant every table the agent touches.
- A workflow AGENT node lands the agent output under `<node_id>.<field>`.

## Workflows (process / human-in-the-loop)
- `start.type`: MANUAL | SCHEDULED | DATASTORE_EVENT | EVENT (non-manual needs `start.config`).
- Nodes: FORM (human step) | AGENT | FUNCTION | DECISION | LOOP | WAIT_UNTIL | END.
- Expressions are JMESPath. Input mapping: `{"type":"expression","value":"node.field"}` or
  `{"type":"literal","value":...}`. Run context: `<node_id>.<field>`, `start.payload.*`, `loop.item/index/count`.
- DECISION: `config.rules:[{"condition":"x.confidence >= `0.7`","next_node_id":"..."}]`. Backtick literals.
  No-match → FIRST-listed outgoing edge (the else branch). Give each branch a distinct target.
- LOOP: `config:{items_path, item_var_name, child_node_id}`; body output = `{results:[...],count}`.
- FORM: `config.input_schema` (+ optional assignee). Submitted fields → `<form_id>.<field>`.
- **Approval/low-confidence pattern:** `AGENT classify → DECISION (confidence >= 0.7?) → auto / FORM human_review`.
- Run: `lemma workflows run <wf> --data '{...}'` (submits entry FORM). `runs submit-form <run-id> --data ...`.

## Models / runtime
- Only `system:lemma` runtime (ACTIVE, credentials provisioned, OpenAI-compatible). Catalog:
  minimax-m3 (default), glm-5.2, kimi-k2.7-code, kimi-k2.6, deepseek-v4-pro, deepseek-v4-flash.
  **No Anthropic/Claude** — use Lemma-hosted models. Omit `agent_runtime` to use the default model.
  To pin a specific model, create an org runtime profile (`lemma runtime profiles create`) — optional.

## Apps (operator UI)
- `lemma app init <dir> --html` = single no-build `index.html` wired to the host-served lemma-sdk
  (simplest, no build step — best for the demo). Or full Vite project without `--html`.
  Styles: neobrutal | editorial | soft | terminal. nav: sidebar | topbar | single-page.
- App reads/writes pod tables via the JS SDK + `watchChanges` for live updates.
- Deploy: `lemma app deploy`. Open: `lemma app open`.

## Key gotchas
- Zero access by default → grant every table a function/agent touches (`MISSING_WORKLOAD_RESOURCE_GRANT`).
- Workflow FUNCTION/AGENT nodes run as the run owner, RLS-scoped → use SHARED tables for cross-row work.
- Agent needs `output_schema` for reliable downstream JMESPath mapping.
- Decision literals need backticks: `` == `true` ``, `` >= `0.7` ``.
