---
name: orchestrator
description: "Default entry point for everyday CAD engineering work with Jig. Use whenever the engineer asks to inspect, change, check or design a part or assembly in their CAD program, e.g. \"make the mounting holes M10\", \"can this be milled?\", \"what's the thinnest wall?\", \"shorten it by 5 mm\", \"check this before release\", \"design a bracket for 50 kg\". Picks only the Blueprint capabilities and Red Line critics the request needs, shows the plan for confirmation before any model change, records stated constraints, and escalates to the full design loop only when needed."
argument-hint: "\"<what you need>\""
---

# Jig · orchestrator

The engineer's request: **$ARGUMENTS** (if empty, use their latest message).

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. Every path below that isn't under `blueprint/` is relative to it,
and so are the paths inside the files you read from it.

You run the lightest pipeline that is still safe. Most requests are small and messy, so most runs use
one or two Blueprint capabilities and zero to two critics. Build up only when the map or the
engineer calls for it.

## 0. Load

1. Read `docs/impact-map.md` and `docs/workspace.md`. Read the capability files
   (`docs/blueprint/inspect.md`, `edit.md`, `spec.md`, `review.md`, `triage.md`, `record.md`) when
   you first use each one.
2. Connector: detect it per `docs/connector-contract.md`, read its `CONNECTOR.md`, and call `status`
   to get the CAD version and active document. If the CAD program is unreachable and the request
   needs the model, say what to start and stop. Spec-only requests can go on. Then call
   `documents`: that list is the engineer's (*Leave the CAD as you found it* in the contract).
3. Design folder: resolve `blueprint/<slug>/` per `docs/workspace.md`. Read its `blueprint.md` and
   the end of `changelog.md` if they exist, and `blueprint/rules.md` if present. Don't create
   anything yet.

## 1. Classify

Split the request into intents. One message can hold several.

| Intent | Example | Capabilities |
|---|---|---|
| question | "what's the wall thickness?" | Inspect |
| edit | "make the holes M10", "add R3 to the pocket corners" | Inspect → Edit → (Review) → Triage → Record |
| review | "can this be milled?", "check it" | Review → Triage → Record (one line) |
| spec | "from now on these bolts are always A4 stainless" | Spec → Record, then check the model against it |
| ingest | "look at the last red line and fix what makes sense" | Triage → Edit → Record |
| undo | "go back", "undo that" | Edit (restore) → Record |
| design | "design a bracket for …", a new part from scratch | `init` → offer `converge` |
| loop | "iterate until it's clean", "release review and fix" | `converge` |

For **design** and **loop**, hand over: follow `skills/init/SKILL.md` or `skills/converge/SKILL.md`
and stop here.

Also pull out any **stated intent** to record, using the rules in `docs/blueprint/spec.md`.

## 2. Plan

For an edit or ingest: run **Inspect** to find the targets, their current values and their
categories. Then use the impact map to choose the critics (§1/§2), whether a baseline is needed
(§4), and apply the escalation and word rules (§5).

Write the plan in this shape:

```text
Plan · bracket
  Change   4× CBORE for M8 → Hole Wizard ISO 4762 M10 counterbore, same positions
           expect Δm ≈ −0.012 kg; bbox unchanged
  Record   CON-004 mounting holes accept M10 (hard) ← "so an M10 bolt fits"
  Review   Standards (hole), Assembly (holes are INT-001), with baseline (interface).
           Skipped DFM, Cost, Drawing: not affected / no drawing
  Safety   save + checkpoint → blueprint/bracket/checkpoints/04/
```

## 3. Confirm (before every model write)

Ask with AskUserQuestion: **Apply** (recommended) · **Apply without review** · **Change the plan** ·
**Cancel**. "Other" lets the engineer adjust it in their own words: re-plan and ask again.

- No confirm is needed for questions, reviews or spec-only requests, which don't write to the model.
  Recording constraints is listed in the plan or the result and can be undone with "drop that".
- An explicit "just do it" / "quick" / "no review" in the request counts as the confirm. Still show
  the plan in one line.
- A fix round after the critics (step 5) is a new plan and needs its own confirm.

## 4. Execute

1. **Spec.** Record the constraints (create a lite blueprint if needed).
2. **Baseline**, only if planned. Spawn `cad-snapshot` with the planned `sections`, `focus` and
   `out: blueprint/<slug>/snapshots/NN-before.json`, where `NN` is the current iteration.
3. **Edit.** Follow `docs/blueprint/edit.md`: guards, checkpoint, apply, read back, save.
4. **Review**, if critics were planned: follow `docs/blueprint/review.md` with tag `NN` (the new
   iteration), the planned personas, the changed targets as `focus`, and the baseline if one was
   taken.
5. **Triage.** Follow `docs/blueprint/triage.md`. Show the "caused by this change" group first and the
   pre-existing ones collapsed. If there are fixes to make, go back to step 2 with them as the new
   plan, confirm, and apply. That happens **once**. If change-scope criticals are still open after
   it, offer `/jig:converge`; don't start it.
6. **Record.** Follow `docs/blueprint/record.md`.

For a **review**, run step 4 without the edit: tag `NN-review`, the focus is whatever the engineer
asked about, and critics come from impact-map §2.
For a **spec** request, after recording the new constraint, check the model against it with Inspect
or the single critic its category maps to.

## 5. Finish

1. **Close what Jig opened** (*Leave the CAD as you found it* in the contract), on every exit,
   including cancel, failure and stopping to ask something. If you need the model again later, open
   it again then.
2. End with the result line from `docs/blueprint/record.md`: what ran, what was skipped and why, and
   where it was logged. Then, at most, one suggestion ("3 pre-existing DFM warnings — want a DFM
   review?").

## Never

- write to the model without a confirm or an explicit waiver
- run every critic "to be safe" when the map doesn't call for them. Say what you skipped instead
- start the converge loop without a yes
- touch locked parameters, engineer-owned features or `overridden` decisions
- create a design folder for a plain question
