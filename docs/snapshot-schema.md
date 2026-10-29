# Snapshot schema (`jig/snapshot@1`)

A snapshot is the neutral, CAD-independent picture of the model that the Red Line critics review.
The `cad-snapshot` agent writes it to `blueprint/<slug>/snapshots/NN[-tag].json`.

**Partial snapshots.** Everyday work reads only the sections the selected critics need (see
`impact-map.md` §3). A partial snapshot sets `"partial": true` and lists `"sections"`. The
fields of sections that were not read are left out entirely (not `null`), so nobody mistakes them
for gaps. `core` is always present. A `focus` field repeats what the snapshot was taken for.

**Seeded snapshots.** After an edit, Blueprint has already read much of the model: mass, bbox,
features, dimensions, the interference check, hole positions. It writes those readings as a partial
snapshot, `snapshots/NN-edit.json`, with `"source": "edit"`. It takes only values read **after the
last write**, and a section only if every field of it was read. The review snapshot then starts from
this **seed**: `"seeded_from": "snapshots/NN-edit.json"` and `"sources": {"core": "edit", "holes":
"edit", "walls": "snapshot"}` say which section came from where. Only the missing sections are read
again.

Rules:
- Units: always **mm, kg, degrees, mm², mm³**. Convert if the connector reports anything else.
- Unknown is `null`, never a guess. Every `null` that a critic might need gets an entry in `gaps`.
- Keep it compact (aim under ~150 KB). Summarise faces and edges as shown below rather than dumping
  them raw; keep raw lists only for small parts (< 200 faces).
- Values come from the CAD model, not from `blueprint.md`. The snapshot shows what *is* modelled, the
  blueprint what *should* be.

```jsonc
{
  "schema": "jig/snapshot@1",
  "iteration": 2,
  "taken_at": "2026-10-28T14:05:00Z",
  "connector": { "name": "solidworks", "cad_version": "SOLIDWORKS 2026", "server_version": "0.16.0" },

  "partial": true,                                   // false = every section read
  "sections": ["core", "holes", "material"],
  "focus": "4× CBORE for M8 → M10 counterbore",      // null for a full snapshot
  "seeded_from": "snapshots/02-edit.json",           // null when everything was read fresh
  "sources": { "core": "edit", "holes": "edit", "material": "snapshot" },

  "document": { "type": "part", "name": "bracket", "path": "C:/.../bracket.SLDPRT", "saved": true },

  // What the connector could provide this time: full | partial | none
  "capabilities": { "features": "full", "dimensions": "full", "annotations": "none", "drawing": "partial" },

  "parts": [
    {
      "name": "bracket",
      "path": "C:/.../bracket.SLDPRT",
      "material": { "name": "6082-T6 (SS)", "density_kg_m3": 2700 },   // null if unassigned
      "mass_kg": 0.412, "volume_mm3": 152600, "surface_area_mm2": 48210,
      "centre_of_mass_mm": [40.0, 25.1, 4.0],
      "bbox_mm": { "min": [0,0,0], "max": [120,60,40], "size": [120,60,40] },
      "bodies": 1,

      "features": [
        { "name": "Base", "type": "Extrusion", "suppressed": false, "error": null }
      ],
      "dimensions": [
        { "id": "D1@Base", "feature": "Base", "value": 8.0, "unit": "mm",
          "tolerance": null, "bound_param": "PAR-thickness" }   // PAR id from blueprint.md if bound
      ],
      "equations": [ { "name": "thickness", "value": 8.0, "expression": "8" } ],

      // Derived from faces/edges: the snapshot agent fills these from the raw topology
      "holes": [
        { "diameter_mm": 9.0, "depth_mm": 8.0, "through": true, "axis": [0,0,1],
          "centre_mm": [12,12,4], "counterbore": { "diameter_mm": 15.0, "depth_mm": 8.6 },
          "feature": "CBORE for M8", "thread": null, "count_same": 4 }
      ],
      "internal_radii_mm": [ { "radius": 3.0, "feature": "Fillet1", "count": 4 } ],
      "sharp_internal_edges": 2,              // concave edges with no fillet, null if not derivable
      "planar_face_normals": [ { "normal": [0,0,1], "count": 3, "area_mm2": 9000 } ],
      "setup_directions": ["+z", "-z", "+x"], // distinct directions a machinist must reach
      "wall_check": { "threshold_mm": 2.0, "min_found_mm": 3.1, "thin_spots": [] },
      "draft_check": { "pull": "+z", "min_draft_deg": 0.0, "faces_below_1deg": 6 },  // only if requested
      "faces_raw": null                       // raw list only for small parts
    }
  ],

  "assembly": {                               // null for a single part
    "components": [ { "name": "bracket-1", "part": "bracket", "fixed": true, "transform": null } ],
    "fasteners": [ { "component": "M8x25-1", "designation": "ISO 4762 M8x25", "count": 4 } ],
    "mates": [ { "name": "Concentric1", "type": "concentric", "ok": true } ],
    "interference": [ { "a": "bracket-1", "b": "plate-1", "volume_mm3": 12.5 } ],
    "clearances": [ { "a": "bracket-1", "b": "cover-1", "min_distance_mm": 0.4 } ]
  },

  "drawings": [                               // empty if none
    { "path": "C:/.../bracket.SLDDRW", "pdf": "C:/.../bracket.pdf",       // pdf: null if none
      "image": "blueprint/bracket/shots/02-drawing.png",
      "sheet": { "size": "A3", "scale": "1:2", "projection": "first angle" },
      "views": [ { "name": "front", "type": "model", "scale": "1:2" },
                 { "name": "A-A", "type": "section", "scale": "1:2" } ],
      "annotations": [                        // null = connector can't read them; then read pdf/image
        { "id": "RD1@Drawing View1", "view": "front", "type": "dimension",
          "text": "120 ±0.1", "value": 120.0, "dimension_id": "D1@Base" },
        { "id": "…", "view": "front", "type": "hole_callout", "text": "4X Ø11 THRU / ⌴ Ø18 ↧ 10.6" },
        { "id": "…", "view": "top", "type": "gtol", "text": "⌖ Ø0.2 A B" },
        { "id": "…", "view": "top", "type": "datum", "text": "A" }
      ],
      "title_block": { "material": "EN AW-6082-T6", "weight": "0.41 kg", "part_no": null },  // fields read, null = empty
      "problems": [ { "kind": "uncovered_feature", "what": "Fillet2 has no dimension" } ],    // drawing check
      "stale": false }                        // true if the part changed after the drawing was last rebuilt/saved
  ],

  "images": [ { "view": "iso", "path": "blueprint/bracket/shots/02-iso.png" } ],

  "gaps": [
    { "what": "dimension tolerances", "why": "connector cannot read tolerances (annotations: none)",
      "affects": ["standards", "assembly", "drawing"] }
  ]
}
```

## Field notes

- `bound_param` links a CAD dimension to a parameter in `blueprint.md` (`PAR-…`). Blueprint
  writes the binding into the blueprint; the snapshot agent copies it over by matching the dimension
  id against the blueprint's parameter table.
- `holes` is the most useful derived field: Standards checks it against clearance-hole and thread
  tables, Assembly against the mating part, Cost counts sizes (tool changes).
- `setup_directions`: the distinct outward normals of machined faces that a 3-axis machine must
  reach. It is a rough count of setups.
- `fasteners` come from component names, file names or the connector's hardware library. If the
  designation can't be determined, keep the name and set `designation: null`.
