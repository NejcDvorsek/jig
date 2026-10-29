---
name: snapshot
description: "Read the current CAD model (read-only) into a neutral Jig snapshot JSON under blueprint/<design>/snapshots/. Use when the engineer wants a full machine-readable picture of the model, e.g. for debugging the connector or before a manual review."
argument-hint: "[sections, e.g. core,holes] [extra checks, e.g. \"draft pull=+z\"]"
---

# Blueprint · snapshot

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. Paths outside `blueprint/` are relative to it.

1. Resolve the design folder (`docs/workspace.md`). This skill may create the folder
   (`snapshots/` only). If there is no blueprint, pass the active document as `model`.
2. `out` = `blueprint/<slug>/snapshots/NN-snap.json`, where `NN` is the blueprint's iteration (00 if
   none), with a `-b`, `-c` … suffix if the file exists.
3. Spawn the `cad-snapshot` agent with `blueprint`, `model` (if needed), `out`, and the
   `sections` / `checks` from `$ARGUMENTS`.
4. Relay its short report. On `ERROR`, say what to start (from the connector's `CONNECTOR.md`).
