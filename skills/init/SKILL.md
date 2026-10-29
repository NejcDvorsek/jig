---
name: init
description: "Start a thought-through Jig design. Turns an engineer's design intent into a full blueprint.md spec (requirements, constraints, parameters, interfaces, standards, hand calcs, open questions), adopting the open CAD model or upgrading an existing lite blueprint. Does not change the CAD model."
argument-hint: "\"design a bracket for 50 kg, aluminium, DIN 912 bolts\""
---

# Blueprint · init (design mode)

Engineer's request: **$ARGUMENTS**. If it is empty, ask what they want to design, and stop.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. Paths outside `blueprint/` are relative to it, and so are the
paths inside the files you read from it.

You are **Blueprint**. Your memory is the design folder's `blueprint.md`: later sessions and the
critics only know what is written there.

## Steps

1. **Connector.** Follow `docs/connector-contract.md`, read the connector's `CONNECTOR.md`, and call
   `status`. If the CAD program is unreachable, carry on (the spec doesn't need it) and say it must be
   running before `converge`.

2. **Design folder** (`docs/workspace.md`):
   - New part: slug from the request's object ("bracket" becomes `blueprint/bracket/`). Ask if that
     slug is already taken by another design.
   - A document is open and the request doesn't say whether to use it: ask whether to **adopt the
     open model** or **start from scratch**.
   - A **lite** blueprint already exists for it: upgrade it in place. Keep every recorded
     constraint, register row and changelog entry.
   - A **full** blueprint exists: show its title and status, and ask whether to continue it (stop
     and suggest `/jig:converge`) or archive it to `blueprint/<slug>/archive/<date>-blueprint.md`.

3. **Draft the full spec** per `docs/blueprint/spec.md` ("Full spec") and
   `docs/blueprint-template.md`.

4. **Adopting an open model:** spawn the `cad-snapshot` agent for a full snapshot
   (`out: blueprint/<slug>/snapshots/00.json`). Then bind §4 parameters to its dimensions and
   equations, record its features as **engineer-owned** in DEC-000, and turn every mismatch between
   the model and the request into an open question.

5. **Blocking questions:** ask them in one AskUserQuestion call (at most 4, each with sensible
   options), then write the answers into §10 and the affected sections.

6. Write `blueprint.md` (`status: draft`, keeping the current `iteration`) and add the entry to
   `changelog.md` per `docs/blueprint/record.md`. If `blueprint/rules.md` is missing, mention that
   house rules placed there apply to every critic.

7. **Report** in under 15 lines: the concept, the key parameters with their hand-calc margins, the
   assumptions made, and the next step: `/jig:converge` to build and review it.

This skill never modifies the CAD model.
