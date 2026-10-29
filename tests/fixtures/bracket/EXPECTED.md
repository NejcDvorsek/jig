# Bracket fixture: planted defects

Run each critic on `blueprint/bracket/blueprint.md` + `blueprint/bracket/snapshots/01.json` (no focus,
so every flag has `scope: review`). A critic **passes** if it raises every "must" item at the stated
severity or higher, raises no critical outside its list, and returns valid `jig/flags@1` JSON.

| Persona | Must catch | Severity | Planted as |
|---|---|---|---|
| standards | clearance hole Ø8.4 for M8 is below ISO 273 fine (8.4 is fine, medium is 9.0): acceptable, **not** critical | ≤ info | trap: tests that it doesn't over-flag |
| standards | counterbore depth 6.0 for M8 (head 8 mm): head proud, but CON-002 says flush | critical | `holes[0].counterbore.depth_mm` |
| standards | CAD material 6061 ≠ blueprint EN AW-6082-T6 | critical | `parts[0].material` |
| standards | tolerances: interface holes carry none | info/warning | `dimensions[].tolerance` all null |
| dfm | 4 sharp internal corners in Pocket1, CNC with min tool Ø6 | critical | `sharp_internal_edges.groups` |
| dfm | pin hole Ø3 × 36 deep: depth/dia = 12 | critical | `holes[1]` (depth/Ø) |
| dfm | 4 setup directions on 3-axis | warning | `setup_directions` |
| assembly | envelope 125 mm > CON-001 120 mm | critical | `bbox_mm.size[0]` |
| cost | no cost target / quantity | info | blueprint has none |
| cost | unit-cost estimate | info | always |
| drawing | Pocket1 and Pin hole not dimensioned | warning+ | `problems` |
| drawing | third-angle projection vs ISO first angle (§6) | warning+ | `sheet.projection` |
| drawing | title block: no general tolerance, no part number (its material 6061 matches the model; the mismatch with the spec is Standards') | warning+ | `title_block` |

Note on the trap: ISO 273 gives M8 clearance holes of 8.4 (fine), 9 (medium) and 10 (coarse). Ø8.4 is a valid fine fit.
A critic that calls it critical is over-flagging.

**One owner per problem** (critic-protocol, *Topic owners*): the material mismatch is flagged only by Standards, the 125 mm
envelope only by Assembly, and the M8 hole pattern's position only by Assembly. Drawing flags neither the
material nor the envelope, because the drawing shows the model correctly.
