# Blueprint capability: Record

Every model or spec change leaves a trace. This runs after every Edit, every Spec change and every
critic run that produced flags, including quick "just do it" edits.

## blueprint.md

- Model changed: bump `iteration` to `NN` (the checkpoint number). Set `status` to
  `converging` inside a loop, and otherwise keep `lite` / `draft` / `converged`. A converged design
  that is edited goes back to `draft`.
- Add the §4 values, §8 decisions, §9 register changes (with opened/closed iteration) and §10
  questions.
- Add one §11 History row: iteration, date, model changes, spec changes, the critics that ran, and
  their counts (C/W/I).

## changelog.md

Append, newest at the bottom:

```text
## NN · 2026-10-28 · "make the mounting holes take M10"          ← the engineer's request, quoted
- Model: CBORE for M8 → ISO 4762 M10 counterbore, 4× (Δm −0.012 kg expected, −0.0118 kg measured)
- Spec: CON-004 mounting holes accept M10 (hard) ← "so an M10 bolt fits"
- Red Line: Standards, Assembly, Drawing (hole on INT-001). Skipped DFM, Cost: not affected
- Flags: 1 critical fixed (standards:standards.clearance-hole:bracket/CBORE), 1 needs-engineer (drawing callouts)
- Checkpoint: checkpoints/NN/
```

With "review later", the Red Line line reads `Red Line: pending (Standards, Assembly)` instead, and
`/jig:redline` later turns it into `Red Line: done in NN-review`.

Read-only runs (questions) are not recorded. Review runs record one line, with critics and counts.

## Result line

End every orchestrated request with one line in the chat:
*"Ran Standards + Assembly (hole on interface INT-001). Skipped DFM / Cost / Drawing: not
affected. Logged as change 04."*
