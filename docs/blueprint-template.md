---
schema: jig/blueprint@1
title: <Part or assembly name>
connector: solidworks            # which CAD connector drives this design
model:                           # CAD files this blueprint owns (empty until created)
  - path: <path/to/part.SLDPRT>
    role: part                   # part | assembly | drawing
process: <CNC milling | sheet metal | casting | injection moulding | FDM | ...>
material: <EN AW-6082-T6 | S235JR | PA12 | ...>
quantity:                        # parts per order or year; empty = unknown. Opens the Cost critic above 5
cost_target:                     # e.g. "€40 per part"; empty = none. Opens the Cost critic
status: draft                    # lite | draft | converging | converged | stopped
parent:                          # assembly slug, if this part belongs to one
iteration: 0
max_iterations: 5
personas: [dfm, standards, cost, assembly, drawing]
---

# <Title>

> Full form, as `init` writes it. Everyday work starts a **lite** blueprint: this frontmatter plus
> only the sections that have content (usually §3, §9, §11). See `docs/workspace.md`.

## 1. Intent

> The engineer's request, quoted word for word. Never edited after init.

## 2. Requirements

What the design must achieve. Each has a way to verify it.

| ID | Requirement | Value | Verify by | Status |
|---|---|---|---|---|
| REQ-001 | Carries static load | 50 kg (490.5 N) at tip, safety factor ≥ 2 | hand calc §7 | open |

Status: `open` · `met` · `not met` · `unverifiable` (with reason)

## 3. Constraints

Limits the solution must stay within. `hard` means a violation is a critical flag; `soft` means a warning.

| ID | Constraint | Value | Kind | Source |
|---|---|---|---|---|
| CON-001 | Envelope | ≤ 120 × 60 × 40 mm | hard | init request |
| CON-002 | Fasteners | DIN 912 / ISO 4762 socket head cap screws | hard | init request |
| CON-003 | Process | 3-axis CNC milling, min tool Ø6 | hard | Q-002 answer |
| CON-004 | Mounting holes accept M10 | ISO 273 medium Ø11 | hard | "so an M10 bolt fits" (2026-10-28) |

## 4. Parameters

The bridge between spec and model. Blueprint changes the model through these first.
`locked: yes` means only the engineer may change the value.

| ID | Name | Value | Unit | CAD binding | Locked | Rationale |
|---|---|---|---|---|---|---|
| PAR-001 | thickness | 8 | mm | `thickness` (global variable) | no | REQ-001 bending, §7 |

## 5. Interfaces

Mating parts, bolt patterns, datums and fits to the outside world.

| ID | Interface | Mates with | Definition |
|---|---|---|---|
| INT-001 | Wall mount | customer wall plate | 4× M10 on 80 × 40 rectangle, datum A = back face |

## 6. Standards & tolerancing

- General tolerances: ISO 2768-mK
- Fits: e.g. Ø10 H7/g6 at the pivot
- Threads: ISO 965 metric coarse, 6H/6g
- Drawing standard: ISO 128 / ISO 129, first-angle projection, GPS per ISO 1101
- House rules: `blueprint/rules.md` in the project (if present, every critic applies it)

## 7. Load cases & hand calculations

No FEA in v1. Each load-carrying requirement gets a short, checkable calculation: formula, inputs
(PAR ids), result, margin.

## 8. Decisions

| ID | Iter | Decision | Alternatives considered | Rationale | Source |
|---|---|---|---|---|---|
| DEC-001 | 0 | Single milled block, no welds | welded plate; bent sheet | CON-003; low volume | init |

## 9. Red Line register

One row per flag fingerprint (`persona:rule:target`). Blueprint keeps this table. Critics never see
earlier iterations.

| Fingerprint | Sev | Status | Opened | Closed | Resolution / rationale |
|---|---|---|---|---|---|

Status:
- `open`: not handled yet
- `fixed`: change applied, gone from the latest red line
- `deferred`: accepted for now, with rationale. Only warnings and infos can be deferred by Blueprint
- `rejected`: Blueprint disagrees, with evidence
- `needs-engineer`: a critical flag Blueprint cannot or must not resolve alone (it conflicts with a
  locked parameter or a hard requirement, or needs information only the engineer has)
- `overridden`: the engineer decided. Blueprint never reopens it

## 10. Open questions

| ID | Question | Blocking? | Answer |
|---|---|---|---|
| Q-001 | Is the load static or vibrating? | yes (REQ-001 SF) | |

## 11. History

| Iter | Date | Changes to model | Changes to spec | Red line (C/W/I) |
|---|---|---|---|---|
| 0 | <date> | — | created | — |
