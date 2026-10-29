---
name: converge
description: "Run the full Jig loop on one design. Blueprint builds or updates the CAD model to match the spec, all of the design's Red Line critics review it in parallel, Blueprint triages their flags and applies fixes, and it repeats until no critical flags remain, a stop condition hits, or the iteration cap is reached. For new designs and release reviews; everyday changes go through the orchestrator."
argument-hint: "[design] [--max N] [--personas dfm,standards,...]"
disable-model-invocation: true
---

# Blueprint · converge (loop mode)

Arguments: `$ARGUMENTS`. A design name picks the folder. `--max N` overrides `max_iterations`
(default 5, and never more than 10 unless the engineer says so). `--personas` overrides the
blueprint's list.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. Paths outside `blueprint/` are relative to it, and so are the
paths inside the files you read from it.

## Pre-flight

1. Resolve the design folder (`docs/workspace.md`). A missing or **lite** blueprint is upgraded first
   with `skills/init/SKILL.md`, because the loop needs requirements to converge against.
2. §10 has no unanswered **blocking** question. Otherwise ask them (AskUserQuestion, up to 4) and
   write the answers in.
3. The connector's `status` responds (`docs/connector-contract.md`). Call `documents`: that list is
   the engineer's (*Leave the CAD as you found it* in the contract).
4. **Confirm the run once** with AskUserQuestion, showing: the personas, the iteration cap, what
   Blueprint may change (unlocked PARs, its own features), what it won't (locked PARs, engineer-owned
   features, `overridden` rows), and the checkpoint location. Offer **Start** · **Change limits** ·
   **Cancel**. Inside the loop, passes run without further confirms. The guardrails below bound them.
5. Set `status: converging`.

## Loop

Repeat for `k = 1 … max`:

**A. Blueprint pass.** On `k = 1`, align the model with the spec: build it if `model:` is empty, or
otherwise apply the spec changes since the last History row. On later passes, apply the **fix**
decisions from C. Use `docs/blueprint/edit.md` (checkpoint, apply, read back, save, requirement
re-check), then `docs/blueprint/record.md`.

**B. Red Line pass.** Follow `docs/blueprint/review.md` with tag `NN`, every persona, `full`, and
no focus or baseline (so `scope: review`).

**C. Triage.** Follow `docs/blueprint/triage.md` (loop mode) to update the register. Count the **open
criticals**, meaning critical rows with status `open` or `fix`, and the **unverified hard checks**,
meaning `needs-engineer` rows from a `checkable: false` flag on a hard CON or a REQ.

**D. Decide.**

| Condition | Result |
|---|---|
| open criticals = 0, unverified hard checks = 0, and no critic failed | **converged** |
| every remaining critical is `needs-engineer`, or only unverified hard checks remain | **stopped: needs engineer** |
| the same open-critical fingerprints after two passes in a row | **stopped: no progress** |
| a CAD write failed in two consecutive passes, or the connector is gone | **stopped: CAD error** |
| the same critic failed twice in a row | **stopped: critic failed** |
| the connector warns about CAD memory or resources | **stopped: CAD resources** (ask for a restart) |
| `k == max` | **stopped: iteration cap** |
| otherwise | next pass. Print `NN · C/W/I · fixed x · deferred y` |

Warnings never keep the loop running on their own. **Tidy pass:** once converged, if open warnings
remain that triage would **fix**, run one more A + B. Keep its result only if it adds no critical;
otherwise restore that pass's checkpoint and log why.

## Finish

1. Set `status` to `converged` or `stopped`, with the reason in §11. Save the model, then close
   what Jig opened, per the contract. The model stays open between passes, but not after the loop.
2. Report in under 20 lines: the outcome and reason, iterations used, the final key parameters and
   requirement status, what still needs the engineer (questions, including each unverified hard
   check and how to confirm it, deferred warnings worth a look, other gaps no critic could check),
   and how to steer: edit `blueprint.md` (values, `locked: yes`, set
   register rows to `overridden`, answer §10), then run converge again.

## Guardrails

- Never change a `locked` PAR or an `overridden` decision, and never delete or reorder an
  engineer-owned feature.
- Never write before that iteration's checkpoint exists.
- If the engineer interrupts, finish the current CAD call, save, record the state in §11, and
  finish as above.
