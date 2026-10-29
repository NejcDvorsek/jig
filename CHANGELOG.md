# Changelog

## 0.1.0 · 2026-10-28

- Named Jig (was "Blueprint + Red Line"; those remain the names of the drafter and the critics).

- Orchestrator as the default entry point: classifies everyday requests, picks Blueprint capabilities
  and only the affected Red Line critics (impact map), confirms before every model write, records
  stated constraints.
- Blueprint capabilities: inspect, edit, spec, triage, record. Lite blueprints per part or assembly.
- Design mode: init and converge skills. Plus redline, snapshot and doctor.
- Red Line critics: DFM, standards, cost, assembly, drawing, with focus, baseline and change/pre-existing scope.
- Neutral snapshot (full or partial) and flag schemas, connector contract.
- SolidWorks connector (solidworks-mcp >= 0.16.2, bundled via uvx).
- Speed: the review snapshot is seeded from the edit's own readings. Each topic has one owning
  critic, and triage merges repeats. A Cost gate (needs a cost target or a quantity above 5), "review
  later" with batched pending reviews, and "review: X only". The snapshot agent and the Cost,
  Drawing and Standards critics run on Sonnet. Large-assembly notes in the SolidWorks adapter, and
  `server-requests.md` for the MCP server.
- Leaves the CAD program as it found it: every document Jig opens is closed at the end of the run,
  and the engineer's open documents are never closed.
