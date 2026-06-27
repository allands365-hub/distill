# Distill — AI Bug Triage & Release Operator

**Date:** 2026-06-27
**Status:** Design approved (pending written-spec review)
**Built on:** Lemma SDK (open-source AI-native software platform), cloud-hosted
**Hackathon track:** Engineering — AI Bug Triage & Release Operator

---

## 1. Problem & Target User

**Target user:** A 2–10 person startup engineering team with no dedicated PM or
triage owner. Bug reports, feature requests, and customer complaints arrive
scattered across Slack, email, GitHub, and support channels in inconsistent,
messy formats. Nobody has time to read, classify, prioritize, deduplicate, and
track all of it, so real bugs get buried and release notes are an afterthought.

**The pain is concrete and universal at this scale:** the cost of a missed P0
or a duplicate-driven wild goose chase is high, but the team can't justify a
full-time triage process.

**What Distill does:** turns messy, multi-source feedback into organized,
prioritized, deduplicated issues with reproduction steps, pauses low-confidence
calls for a human, tracks fixes, and generates release notes from shipped work —
the "triage" half *and* the "release operator" half.

---

## 2. Scope (Hackathon Demo)

Judges weight **problem clarity (35%)**, **product judgment (25%)**,
**execution / does the core loop work (25%)**, and **SDK utilisation (15%)**.
The discipline is one tight, genuinely-working core loop — shallow but reliable
at every stage — over a broad-but-shallow demo.

**In scope (must work on stage):**

1. Ingest a **batch paste/upload** of mixed messy feedback (controllable, zero
   external auth, reliable for a live demo).
2. **Classify** each item (bug / feature / question / duplicate / spam) with a
   confidence score.
3. **Prioritize** bugs P0–P3 (deterministic rubric).
4. **Deduplicate & link** related items.
5. Generate **reproduction steps** for bugs.
6. **Human approval gate** for low-confidence / P0 items.
7. **Track** issue status (incoming → triaged → approved → fixed).
8. Generate **release notes** from issues marked fixed.
9. A **minimalistic operator App UI** (triage board + "Generate release notes"
   button).

**Out of scope (architected for, not built):** live Slack/Gmail/GitHub
ingestion surfaces (the batch path proves the loop; surfaces are a swap-in),
semantic-embedding dedup at scale (demo uses a lighter matcher), auth/multi-tenant,
analytics.

---

## 3. Architecture

Distill is one Lemma **pod** (a directory of plain files: tables, agents,
workflows, functions, app). One **Workflow** is the spine; everything else hangs
off it.

### 3.1 Core loop (the Workflow)

```
Batch paste/upload
   │
   ▼
[split_batch]  (Function)   → N raw feedback items
   │
   ▼  per item:
   1. Triage Agent          → {type, confidence, reasoning}        [Haiku]
   2. detect_priority       (Function) → P0–P3 (bugs only, no LLM)
   3. detect_duplicates     (Function) → linked_to + related list
   4. Reproduction Agent    → repro_steps (bugs only)              [Sonnet]
   5. Approval Gate         (Approval) → pause if confidence < 0.7 OR P0
   6. write issue row       → issues table
   │
   ▼
Release Notes Agent  (triggered by button) → rolls up status="fixed" → releases table  [Sonnet/Opus]
```

### 3.2 Lemma primitives (the SDK-utilisation story)

| Primitive | Use in Distill |
|---|---|
| **Tables** | `issues` (triaged output), `releases` (generated notes) |
| **Files** | `triage-rules.md`, `priority-rubric.md` — editable playbooks driving agent behavior (ported from OSS Warden prompts) |
| **Agents** | Triage, Reproduction, Release-Notes — scoped roles + structured output |
| **Functions** | `split_batch`, `detect_priority` (deterministic, no LLM), `detect_duplicates`, `transition_status` |
| **Workflow** | The end-to-end loop: function → agent → decision → approval → write |
| **Approvals** | Low-confidence (<0.7) or P0 items pause for a human decision |
| **App** | Minimalistic operator UI: triage board + release-notes generation |

This deliberately exercises **six** distinct Lemma primitives in service of the
problem (not decoration), which is the SDK-utilisation criterion.

### 3.3 Models (bring-your-own Anthropic key)

| Agent / step | Model | Rationale |
|---|---|---|
| Triage (classify) | `claude-haiku-4-5` | High-volume structured extraction; fast + cheap |
| `detect_priority` | none (Function) | Deterministic keyword/impact scoring — free, instant |
| `detect_duplicates` | none (Function) | Lightweight text similarity for demo scale |
| Reproduction | `claude-sonnet-4-6` | Nuanced generative writing |
| Release Notes | `claude-sonnet-4-6` (Opus 4.8 optional for showcase) | Polished long-form output |

A full demo run (~15 items) costs well under $1.

---

## 4. Data Model

### `issues` table

| Field | Type | Notes |
|---|---|---|
| `id` | id | |
| `source_text` | text | original raw feedback |
| `source_channel` | enum | slack / email / github / support / other (parsed or tagged) |
| `type` | enum | bug / feature / question / duplicate / spam |
| `confidence` | number | 0.0–1.0 from triage agent |
| `priority` | enum | P0 / P1 / P2 / P3 / null (bugs only) |
| `reasoning` | text | agent's classification rationale |
| `repro_steps` | text | bugs only; null otherwise |
| `linked_to` | id (nullable) | original issue if duplicate/related |
| `status` | enum | incoming / triaged / needs_approval / approved / fixed |
| `created_at` | timestamp | |

### `releases` table

| Field | Type | Notes |
|---|---|---|
| `id` | id | |
| `notes_md` | text | generated release notes (markdown) |
| `issue_ids` | list | issues rolled up into this release |
| `generated_at` | timestamp | |

---

## 5. Component Contracts (units, isolated & testable)

- **`split_batch(raw_text) -> [item]`** — splits a pasted blob into discrete
  feedback items (by delimiter/heuristic). Pure, deterministic, unit-testable.
- **Triage Agent** — input: one item + `triage-rules.md`; output (structured):
  `{type, confidence, reasoning}`. No side effects; behavior driven by the File.
- **`detect_priority(type, title, body) -> {priority, confidence, reasoning}`** —
  ported P0–P3 keyword rubric + impact boost. Returns null for non-bugs. Pure.
- **`detect_duplicates(item, existing_issues) -> {linked_to, related[]}`** —
  similarity match against existing rows; returns best link + scored candidates.
- **Reproduction Agent** — input: a bug item; output: structured repro steps.
- **Approval Gate** — decision function: pause iff `confidence < 0.7` or
  `priority == P0`; otherwise auto-advance.
- **Release Notes Agent** — input: issues with `status == fixed`; output:
  grouped, human-readable markdown notes.

Each unit has a clear input/output contract and can be exercised independently
of the others, which keeps the workflow and the App thin.

---

## 6. Operator App UI (minimalistic)

A single-page operator board:

- **Input panel:** textarea to paste/upload a batch + "Triage" button (kicks off
  the workflow).
- **Board:** columns by status — Incoming → Triaged → Needs Approval → Approved →
  Fixed. Each card shows type badge, priority badge (color-coded P0–P3),
  confidence, and links to related issues.
- **Approval action:** cards in "Needs Approval" have approve / reject controls
  that resolve the workflow's Approval step.
- **Release notes:** a "Generate Release Notes" button; output renders as
  markdown in a panel.

Visual style: clean, minimal, high-contrast, color-coded priority. No
decorative complexity — the data *is* the interface.

---

## 7. Reuse from OSS Warden

OSS Warden (the user's prior HF-MCP-Hackathon GitHub-triage system, at
`F:\Claude_Files\oss_warden`) provides battle-tested **logic and prompts**; its
**infrastructure is discarded** because Lemma replaces it.

**Port (logic/prompts):**

- Classification prompt template (bug/feature/question/duplicate/spam +
  confidence scoring + type-mapping) → Triage Agent + `triage-rules.md`.
- P0–P3 keyword rubric, impact-boost, confidence math
  (`src/agents/priority_detection.py`) → `detect_priority` Function +
  `priority-rubric.md`.
- Duplicate-detection design (combine title+body, threshold, scored matches,
  auto-link) → `detect_duplicates` Function.
- `reproduce_bug_task` / `generate_response_task` prompts (`src/config/tasks.yaml`)
  → Reproduction Agent / Release Notes Agent.
- Confidence-driven human-in-the-loop ("knows when it's unsure") → Approval Gate.

**Discard (Lemma replaces):** Blaxel, Modal, Supabase, Nebius, CrewAI,
GitHub OAuth/webhooks, the Gradio dashboard.

**Narrative for judges:** "We took a proven triage system that needed six
stitched-together services and rebuilt it on one SDK — then added the Release
Operator half (fix tracking + release notes) it never had."

---

## 8. Demo Script (~90 seconds)

1. Paste a messy blob of mixed feedback: a frustrated Slack rant, two emails (one
   a real P0 crash, one a feature request), a vague GitHub issue, and a near-
   duplicate of an existing issue.
2. Click **Triage**. The workflow classifies, prioritizes, links the duplicate,
   and writes reproduction steps for the bugs — cards populate the board live.
3. One low-confidence item lands in **Needs Approval**. Approve it; it advances.
4. Mark a couple of issues **Fixed**.
5. Click **Generate Release Notes** → polished markdown notes appear.

Controllable, no live network dependency, and it visibly hits all four judging
criteria in one flow.

---

## 9. Build Sequence (high level — detailed plan to follow)

1. Lemma pod scaffold + `issues` / `releases` tables.
2. `split_batch` + `detect_priority` Functions (port rubric) with unit tests.
3. Triage Agent + `triage-rules.md` / `priority-rubric.md` playbooks.
4. `detect_duplicates` Function.
5. Reproduction Agent.
6. Workflow wiring + Approval Gate.
7. Release Notes Agent + trigger.
8. Operator App UI.
9. Seed demo dataset + end-to-end dry run.

---

## 10. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Lemma cloud setup friction | Use the Lemma CLI + installed Lemma skills (the platform is designed to be built by Claude Code); validate auth early |
| Live-demo flakiness | Batch input + pre-seeded dataset; rehearse the exact blob |
| Scope creep across 4 stages | Each stage shallow-but-working; deterministic Functions where possible to reduce LLM variability |
| Agent output drift | Structured outputs + the editable playbook Files; deterministic priority/dedup as Functions |
