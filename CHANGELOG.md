# Changelog

## Unreleased · 2026-10-29

- **Drawings fit their sheet.** A drawing with anything outside the frame, on the title block or
  running into another view is not finished. Edit's new *Fitting the sheet* lists what to do: lay
  out again, leave out views that add nothing, combine views (section, detail, half view), go up a
  sheet size at the same scale, and past A1 ask the engineer. The Drawing critic checks it as
  `drawing.layout`. With sw-mcp 0.2.0, `make_drawing` and `build_drawing` do the layout and sheet
  steps themselves and report `fit`.
- **Snapshot in one call.** New optional connector operation `model_read`: the server derives the
  snapshot's model sections itself. SolidWorks maps it to sw-mcp's `read_model`, with the old face/edge
  recipe as the fallback for builds without it. Release this together with the `.mcp.json` pin bump to the sw-mcp release
  that ships `read_model`.
- **Seeded snapshots are gone** (`NN-edit.json`, `seeded_from`, `sources`): Edit no longer writes
  readings for the review to reuse, and every review snapshot is read fresh.
- Snapshot schema **`jig/snapshot@2`**: holes are one entry per set, with `count` + `centres_mm`
  (was `count_same` + one `centre_mm`), `kind`, `standard`/`size`/`fit`, `entrance`, `body`,
  `source` and `confidence`. `sharp_internal_edges` is `{count, groups}` with each group's edge
  direction, so DFM can tell vertical pocket corners from floor edges. `mates` is `{count, broken}`.
  `draft_check` gains `faces` and `undercut_faces`. The snapshot carries `source`
  (`model_read` | `derived`). The bracket fixture is updated.
- **Unverified hard checks need the engineer.** A critic that can't run a check guarding a hard
  constraint or a requirement names its id in the flag's `requirement`. Triage turns that into
  `needs-engineer` with a blocking §10 question and marks the REQ `unverifiable`, the orchestrator
  shows it under *Couldn't check*, and converge no longer reports **converged** while one is open.
  An answer in §10 closes it as `overridden`.
- The SolidWorks server is pinned exactly (`sw-mcp==0.1.0`) instead of a range. A server update
  now ships as a Jig release. `CONNECTOR.md` now describes only the pinned server: the
  base/drawings generations, the older tool names and the conventions repeated from
  `solidworks://guide` are gone, and so is `server-requests.md`.
- Simpler critics: `docs/critic-protocol.md` now holds the method, the `jig/flags@1` output and the
  topic owners, so each critic reads one file instead of three (`flag-schema.md` is gone, impact-map
  §6 points there). The output JSON is no longer repeated in each agent.
- One review procedure, `docs/blueprint/review.md`, used by the orchestrator, `redline` and
  `converge`.
- Converge no longer writes `redlines/summary.md`. Its contents were already in the blueprint
  (§9 register, §10 questions, §11 History counts) and in the final report.
- Tiers 1 and 2 are one "change" path with a **baseline** switch (interface, requirement-bound
  parameter, assembly, or several kinds of change).
- One table of process wall thresholds (the snapshot agent's); DFM judges against
  `wall_check.threshold_mm`. "Leave the CAD as you found it" is stated once, in the contract.
- SolidWorks connector: uses `close_document`, `open_document`, `save_document`, `add_hole(iso=…)`
  and the other merged tools of newer server builds, with the old names as fallbacks.

## 0.1.0 · 2026-10-28

- Named Jig (was "Blueprint + Red Line"; those remain the names of the drafter and the critics).

- Orchestrator as the default entry point: classifies everyday requests, picks Blueprint capabilities
  and only the affected Red Line critics (impact map), confirms before every model write, records
  stated constraints.
- Blueprint capabilities: inspect, edit, spec, triage, record. Lite blueprints per part or assembly.
- Design mode: init and converge skills. Plus redline, snapshot and doctor.
- Red Line critics: DFM, standards, cost, assembly, drawing, with focus, baseline and change/pre-existing scope.
- Neutral snapshot (full or partial) and flag schemas, connector contract.
- SolidWorks connector (sw-mcp >= 0.1, bundled via uvx).
- Speed: the review snapshot is seeded from the edit's own readings. Each topic has one owning
  critic, and triage merges repeats. A Cost gate (needs a cost target or a quantity above 5), "review
  later" with batched pending reviews, and "review: X only". The snapshot agent and the Cost,
  Drawing and Standards critics run on Sonnet. Large-assembly notes in the SolidWorks adapter, and
  `server-requests.md` for the MCP server.
- Leaves the CAD program as it found it: every document Jig opens is closed at the end of the run,
  and the engineer's open documents are never closed.
