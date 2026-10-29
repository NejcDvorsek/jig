# Blueprint capability: Triage

Weigh Red Line flags. Critics advise and Blueprint decides; the engineer overrides. Paths are
relative to the plugin root.

## Merge into the register

Each flag's fingerprint is `persona:rule:target`. Add or update its row in blueprint §9 (create the
section if this is a lite blueprint):

| Flag | Decision |
|---|---|
| critical, fixable without touching a locked PAR, hard constraint or engineer-owned feature | **fix** |
| critical that conflicts with one of those, needs information only the engineer has, or has `engineer_decision` | **needs-engineer**, plus a §10 question |
| critical that the critic got wrong (misread the data) | **rejected**, quoting the evidence. Use this sparingly: unsure means not wrong |
| warning | **fix** if cheap and conflict-free, otherwise **deferred** with a rationale |
| `checkable: false` whose `requirement` is a hard CON or a REQ | **needs-engineer**, plus a **blocking** §10 question that says what couldn't be checked and how the engineer can confirm it (e.g. "Tolerances can't be read from the model. Does the drawing show ±0.05 on INT-001?"). Mark a REQ `unverifiable (<gap>)` in §2. Merge gaps on the same requirement into one question |
| info | logged. **fix** only if trivial. Any other `checkable: false` means recording the gap |
| `drawing_edit` suggestion | **fix** if the connector can edit drawings and the value comes from the spec; otherwise **needs-engineer** |
| row already `overridden`, or `rejected` with no new evidence | unchanged |
| a `fixed` row that reappears | reopened, as a regression |
| an open row whose fingerprint is absent now, with that persona run and the target in focus | **fixed** |
| an unverifiable row the engineer answered in §10 | **overridden**, quoting the answer. The REQ becomes `met (engineer: <answer>)` or `not met`. A later run that can check it (`checkable: true`) judges it normally |

**Repeats across critics.** Before deciding, merge flags from different critics that describe the
same problem on the same target (the same hole pitch, the same counterbore). Keep the owner's flag
from *Topic owners* in `docs/critic-protocol.md`, at the highest severity any of them gave, and note the others in its
row ("also: dfm, assembly"). Decide and show it once.

When critics conflict (Cost wants thinner, DFM thicker), resolve it against §2 and §3 and record a
DEC row that cites both fingerprints.

If a flag shows the **spec** is wrong or incomplete (a missing fit, an undefined process), fix the
spec through **Spec** before changing the model.

## Everyday presentation (orchestrator)

Show flags in two groups. Never bury the change's effects under old problems.

```text
Caused by this change
  ● CRITICAL  Standards · clearance hole Ø9.0 too small for M10 (ISO 273 fine 10.5) — 4× CBORE for M10
              → set hole Ø11.0 (medium)                                           [fix]
  ▲ warning   Drawing · hole callouts now stale on bracket.SLDDRW                [needs-engineer]

Pre-existing (3, not caused by this change)
  ▲ DFM · 2 sharp internal pocket corners (Pocket2) · ▲ Cost · 4 setup directions · …

Couldn't check (needs you)
  ? Standards · INT-001 position ±0.05: tolerances not readable from the model    [Q-004]
```

The *Couldn't check* group lists only the unverifiable rows on a hard CON or a REQ. Other gaps stay
in the register.

The proposed **fix** items become a new plan, which goes through the orchestrator's confirm again.
That fix round runs once. If change-scope criticals are still open after it, offer converge.
Pre-existing flags are fixed only when the engineer asks.

## Loop mode (converge)

The same decisions apply, with every flag in scope. The loop's stop rules are in the converge skill.
