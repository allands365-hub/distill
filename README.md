# Distill — AI Bug Triage & Release Operator

Turns messy, multi-source product feedback into classified, prioritized,
deduplicated, reproduction-stepped issues with a human approval gate and
generated release notes. Built entirely on the [Lemma SDK](https://github.com/lemma-work/lemma-platform).

**Live app:** https://distill-board.apps.lemma.work  (Lemma pod: `distill`)

## What it does (the core loop)

Paste a batch of raw feedback (Slack rants, emails, GitHub issues, support notes) →
Distill runs a Lemma **workflow** that, per item:

1. **Classifies** it (bug / feature / question / duplicate / spam) with a confidence score — `triage` agent
2. **Prioritizes** bugs P0–P3 — `detect_priority` function (deterministic rubric)
3. **Deduplicates & links** related items — `detect_duplicates` function
4. **Generates reproduction steps** for bugs — `reproduction` agent
5. **Routes low-confidence / P0 items to human approval** (status `needs_approval`)
6. **Writes the triaged issue** to the `issues` table — `save_issue` function

The operator works the board, approves flagged items, marks fixes done, and clicks
**Generate Release Notes** — the `generate_release_notes` workflow rolls up fixed
issues into markdown via the `release_notes` agent.

## Architecture (all live on the `distill` pod)

| Layer | Resources |
|---|---|
| **Tables** | `issues`, `releases` (shared / RLS-off) |
| **Functions** | `split_batch`, `detect_priority`, `detect_duplicates`, `save_issue`, `gather_fixed_issues`, `save_release`, `set_status`, `start_triage`, `start_release_notes` |
| **Agents** | `triage`, `reproduction`, `release_notes` (Lemma-hosted models) |
| **Workflows** | `triage_batch` (FORM→FUNCTION→LOOP[AGENT→FUNCTION→FUNCTION→DECISION→AGENT→FUNCTION]), `generate_release_notes` |
| **Files** | `triage-rules.md`, `priority-rubric.md` (editable playbooks) |
| **App** | `distill-board` — single-file HTML operator board (live via `datastore.watchChanges`) |

The deterministic logic (`split_batch`, `detect_priority`, `detect_duplicates`) is
ported from the author's prior **OSS Warden** project and unit-tested with pytest
(`pytest -q` → 14 passing).

## Prerequisites

- Lemma CLI on PATH: `uv tool install lemma-terminal` then add `C:\Users\<you>\.local\bin` to PATH
- Authenticated: `lemma auth login`
- No model API key needed — agents use Lemma's hosted runtime.

## Run the demo

1. Open the app: https://distill-board.apps.lemma.work (sign in as the pod owner).
2. Paste the contents of [`demo/demo_batch.md`](demo/demo_batch.md) into the box → click **Triage**.
3. Watch the board populate live: the P0 data-loss crash lands in **Needs Approval**
   with reproduction steps; the vague item lands in **Needs Approval** (low confidence);
   the two CSV-export reports get linked as duplicates; the spam is filtered.
4. Click **Approve** on the flagged items → they move to **Approved**.
5. Click **Mark Fixed** on a couple → they move to **Fixed**.
6. Click **Generate Release Notes** → grouped markdown notes appear below the board.

To reset between runs: `pwsh demo/reset.ps1` (clears `issues` + `releases`).

## Build / bundle

The pod bundle lives in [`pod/`](pod/). Re-import any layer with:

```powershell
lemma pods import ./pod/<resource>/<name> --pod distill        # e.g. ./pod/agents/triage
lemma pods import ./pod --pod distill --dry-run                 # validate everything
```

Design + plan: [`docs/superpowers/specs`](docs/superpowers/specs/) and
[`docs/superpowers/plans`](docs/superpowers/plans/). Lemma conventions reference:
[`docs/superpowers/notes/lemma-conventions.md`](docs/superpowers/notes/lemma-conventions.md).
