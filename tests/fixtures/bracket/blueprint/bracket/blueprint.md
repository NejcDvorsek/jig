---
schema: jig/blueprint@1
title: Wall bracket
connector: solidworks
model:
  - path: C:/fixtures/bracket.SLDPRT
    role: part
  - path: C:/fixtures/bracket.SLDDRW
    role: drawing
process: 3-axis CNC milling
material: EN AW-6082-T6
status: converging
iteration: 1
max_iterations: 5
personas: [dfm, standards, cost, assembly, drawing]
---

# Wall bracket

## 1. Intent

> design a bracket for 50kg load, aluminum, DIN 912 bolts, flush heads, CNC milled

## 2. Requirements

| ID | Requirement | Value | Verify by | Status |
|---|---|---|---|---|
| REQ-001 | Carries static load | 490.5 N at 100 mm from the wall, SF ≥ 2 | hand calc §7 | met |

## 3. Constraints

| ID | Constraint | Value | Kind | Source |
|---|---|---|---|---|
| CON-001 | Envelope | ≤ 120 × 60 × 40 mm | hard | init request |
| CON-002 | Fasteners | 4× ISO 4762 (DIN 912) M8, heads flush | hard | init request |
| CON-003 | Process | 3-axis CNC milling, min tool Ø6 | hard | init request |

## 4. Parameters

| ID | Name | Value | Unit | CAD binding | Locked | Rationale |
|---|---|---|---|---|---|---|
| PAR-001 | thickness | 10 | mm | `D1@Base` | no | REQ-001 bending, §7 |

## 5. Interfaces

| ID | Interface | Mates with | Definition |
|---|---|---|---|
| INT-001 | Wall mount | wall plate | 4× M8 on an 80 × 40 rectangle, datum A = back face (-z) |

## 6. Standards & tolerancing

- General tolerances: ISO 2768-mK
- Threads: ISO 965 6H
- Drawing: ISO 128, first-angle projection

## 7. Load cases & hand calculations

σ = M / W = (490.5 N × 100 mm) / (60 × 10² / 6 mm³) = 49 MPa. Rp0.2 (6082-T6) = 250 MPa, so SF = 5.1.
