# Connector: SolidWorks

- **MCP server:** [`sw-mcp`](https://github.com/NejcDvorsek/sw-mcp) (MIT, a fork of `solidworks-mcp` with the drawing tools), registered by this
  plugin's `.mcp.json` as server `solidworks` and run with `uvx`. It drives the user's **running**
  SolidWorks over COM, on Windows only.
- **Status tool:** `get_status`
- **Start:** open SolidWorks and leave it running. The server attaches to it and does not launch it.
- **Self-test:** `uvx sw-mcp --selftest` with SolidWorks open.
- **Server guide:** read the MCP resource `solidworks://guide` before the first write in a session. It
  holds the modelling and drawing recipes and conventions. This adapter only maps the neutral
  operations.

Tool names below are short names. Match the tool whose name ends in `__<short name>` (see
`docs/connector-contract.md`). The server is under active development, so the **live tool list
wins**. Two generations exist:

- **Base** (PyPI releases, 0.16–0.17): modelling, inspection, assemblies, and a basic `make_drawing`.
- **Drawings** (server builds that have `list_views`, `check_drawing` and the other drawing tools
  below): drawings can be read and written. Every row marked *(drawings)* needs this generation. If
  those tools are missing, use the base fallback in the same row. Builds from 2026-10-29 also merge
  the modelling and document families into one tool each (`close_document`, `open_document`,
  `add_hole(iso=…)`, …). Older builds and PyPI have the separate tools named in brackets below:
  use whichever the live tool list has.

Check once per session which generation is live, and record it in the snapshot's `capabilities`.

## Conventions

- Millimetres and degrees in every tool. New geometry starts on the Front plane (XY) and extrudes
  along +Z. Revolves turn about Y.
- Faces are picked by direction (`'+z'`, `'-x'`, `'+z:outer'`), or by `list_faces` index (`'#5'`)
  for mates.
- Every modelling call returns volume, mass and bounding box. Compare them with your expected
  change after **every** write.
- `{ok: false, error}` means nothing changed. The error names the cause.
- Tools return `dimensions` as `{role: 'width@Sketch1'}`. Record these ids as the parameter's CAD
  binding in `blueprint.md` §4.
- Drawing references, as `add_dimension` and `add_symbol` take them: `'edge:-x'` (the face facing
  -x, seen edge-on), `'hole:<feature>'`, `'feature:<name>'`, or a model point `[x, y, z]`. Sheet
  positions are in sheet mm.

## Read operations

| Neutral op | Tool(s) | Support | Notes |
|---|---|---|---|
| `status` | `get_status` | full | SW revision, server version, active document |
| `documents` | `list_documents` | full | |
| `features` | `list_features` | full | flags rebuild errors and under-defined sketches |
| `dimensions` | `list_dimensions` | partial | values only. Tolerances: see `annotations` |
| `equations` | `list_equations` | full | |
| `mass` | `get_mass_properties` | partial | volume, mass, area, CoM, bbox. Material name is not returned: take it from the last `set_material` result, the drawing's title block, or record a gap |
| `bbox` | `get_bounding_box` (also assemblies; older: `get_assembly_bounding_box`) | full | |
| `bodies` | `list_bodies` | full | |
| `faces` | `list_faces` | partial | cylinders give axis, radius, centre (use for holes). **First body only** on multibody parts |
| `edges` | `list_edges` | partial | filter by face/feature/box. **First body only** on multibody parts |
| `sketch` | `read_sketch` | full | |
| `wall_thickness` | `check_printability(min_wall_mm=…)` | full | ray-measured thin walls. Valid for any process, not just printing |
| `overhangs` | `check_printability(up=…, overhang_deg=…)` | full | with `up` = pull direction, a rough draft/undercut check |
| `components` | `list_components` | full | name, path, fixed, position, rotation, bbox, and mates |
| `mates` | `list_components`, `rebuild` | full | `rebuild` reports `mate_errors` |
| `interference` | `check_interference` | full | |
| `distance` | `measure_distance` | full | component↔component, point or axis |
| `drawing` | *(drawings)* `drawing_file(action='open')` + `list_views` | full | sheet, frame, title block, and per view: type, scale, outline, and **annotations** (id, type, shown text, value, box) |
| | base: `make_drawing` → PDF | partial | creates a basic drawing but can't read it back; the Drawing critic reads the PDF |
| `annotations` | *(drawings)* `list_views` | full | dimensions with their shown text (tolerances and fits appear in it), hole callouts, datums, GD&T frames, surface finish, notes |
| | base | none | record a gap |
| `drawing_check` | *(drawings)* `check_drawing` | full | views/annotations off the frame or over the title block, overlaps, crossing leaders, text < 2.5 mm, likely duplicates, and **hole/cut/fillet/chamfer features no dimension or callout covers** |
| `drawing_image` | *(drawings)* `render_drawing`, or `drawing_file(action='export', path=*.png)` | full | a picture of the sheet or a zoomed region |
| `screenshot` | `screenshot` | full | before 0.16.2 it could return a blank ~1 KB image: check the file size anyway |
| `export` | `export`; drawings: `drawing_file(action='export')` | full | STEP/STL/IGES/x_t/3MF; drawings to PDF/DXF/DWG/PNG |

## Write operations

| Neutral op | Tool(s) | Notes |
|---|---|---|
| `set_dimension` | `set_dimension` | read back with `list_dimensions` |
| `set_equation` | `set_equation` (a list too; older: `set_equations`), `delete_equation` | preferred for PAR-bound values |
| `add_feature` | `add_box`, `add_disc`, `add_cylinder`, `add_cone`, `add_extruded_profile` (`face=` / `plane=` / `spline=`; older: `*_on_face`, `*_on_plane`, `add_extruded_spline`), `add_revolved_profile`, `add_swept_*`, `add_loft` (sketches or `profiles_mm`; older: `add_lofted_solid`), `add_boss_on_face`, `add_sketch` + `extrude_sketch` / `cut_sketch`, `cut_profile` (`face=` / `plane=`; older: `cut_profile_on_face`, `cut_profile_through_plane`), `cut_slot`, `cut_offset_pocket`, `add_hole` (`face=`, `cbore_*`, `iso=`; older: `add_hole_on_face`, `add_counterbore_hole`, `add_hole_wizard`), `add_thread`, `add_fillet`, `add_full_round`, `add_chamfer`, `add_shell`, `add_rib`, `add_mirror`, `add_linear_pattern`, `add_circular_pattern`, `add_plane`, *(drawings)* `add_axis`, `combine_bodies`, `split_body`, `add_text_on_face` | see `solidworks://guide` for recipes. Prefer the Hole Wizard (`add_hole(iso=…)`) for standard ISO holes: it carries the standard into the callouts. With `add_axis`, `add_circular_pattern(axis=…)` turns about any axis |
| `delete_feature` / `suppress_feature` / `reorder_feature` | same names | |
| `set_material` | `set_material` | |
| `set_appearance` | `set_appearance` | cosmetic |
| `make_drawing` | `make_drawing(path, sheet, scale, keep_open)` | *(drawings)*: ISO sheet with title block, material and mass, one counted callout per hole set, hole centres dimensioned, and `problems` returned. Base: a basic sheet. Save the part first |
| `drawing_build` | *(drawings)* `build_drawing(spec)` | the whole drawing from a spec (views, sections, details, dims, callouts, symbols, notes, tables, props). To change it, edit the spec and rebuild |
| `drawing_edit` | *(drawings)* `drawing_file`, `add_view`, `edit_view`, `auto_layout`, `import_dimensions`, `add_dimension`, `add_symbol` (hole callout, surface finish, datum, GD&T), `add_note`, `add_table`, `edit_annotation`, `set_drawing_properties` | the small changes: one callout, one tolerance, a datum, the title block |
| `set_tolerance` | *(drawings)* `edit_annotation(id, tolerance=[upper, lower] / fit='H7')` | on a model dimension this **changes the part**: the result says `changes_part`. Treat it as a model edit: confirm and checkpoint |
| `save` | `save_document()` (over its own file; older: `save_part` / `save_assembly` with the path); drawings `drawing_file(action='save')` | |
| `new_document` / `open_document` | `new_document(kind)`, `open_document(path)`, `activate_document` (older: `new_part`, `new_assembly`, `open_part`, `open_assembly`); drawings `drawing_file(action='new'/'open')` | |
| `close_document` | `close_document(title, save)`: any part, assembly or drawing by title (older builds: see *Closing documents*) | without `save=true` it closes **without saving and without asking**, and reports `discarded_changes` |
| assembly | `insert_component`, `add_mate` (`mates=[…]` for several), `delete_mate`, `suppress_mate`, `set_component_transform`, `delete_component`, `check_motion` | |

**Never used by Jig:** `run_script`, even when the server runs with `--allow-scripts`. Blueprint works
only through typed tools, so every change can be checked, confirmed and logged.

## Closing documents

This is how the contract's *leave the CAD as you found it* rule works in SolidWorks.

- `list_documents` gives each open document's `title`, `path` (empty if never saved), `type`,
  `modified` and `visible`, plus which one is `current` for the tools and `active` in SolidWorks.
  Match documents by **path**, or by title for unsaved ones.
- Close by title with `close_document(title)`, or `close_document(title, save=true)` for a document
  with a confirmed edit. It needs no activation and never touches another document. A result with
  `discarded_changes: true` means changes were dropped: check `modified` first for anything Jig
  changed.
- Parts listed with `visible: false` were loaded by an open assembly. They close with that assembly
  (`close_document` refuses them). A hidden part that stays after Jig closed its own assembly is
  normal when one of the engineer's assemblies uses it too.
- `make_drawing` closes the drawing itself unless `keep_open=true`. `drawing_file(action='new'/'open')`
  and `build_drawing` leave the drawing open, so close it when that step is done.
- Close drawings before the part they show, and Jig's assemblies before parts Jig opened on their own.
- Finally, `activate_document` the engineer's previously active document, if there was one.
- **Older builds** (no `close_document`): `activate_document(title)` first, then `close_part()` for a
  part or assembly or `drawing_file(action='close')` for a drawing. Never call `close_part` without
  activating first: with no current document it closes SolidWorks' active one, which may be the
  engineer's. It can't save: save first with `save_part` / `save_assembly` and check `modified`.

## Large assemblies

On assemblies with roughly 50 or more components or 100 or more mates, the tool results get big.
Builds that have `replace_component` (2026-10-29 and later) cover this. Older builds
need the fallbacks.

| Need | Builds with `replace_component` | Older builds |
|---|---|---|
| components in focus | `list_components(name="Bolt*")`: the matches and the mates that hold them. `brief=True` for name, path and fixed only, `mates=False` without mates | `list_components` returns everything. A result too large to show is saved to a file: Grep it for the components in focus instead of reading it whole |
| several mates | one `add_mate(mates=[...])` (older: `add_mates`; a result per mate) and one `delete_mate([...])` (it returns `mates_left`, a count) | one call per mate. Each returns all the mates left, so don't re-list in between |
| swap a part | `replace_component(component, path)`: it returns the kept mates, and for each broken one the face it held and candidate faces (`#index`) on the new part. Then `delete_mate` the broken ones and `add_mate(mates=[...])` them again on the candidates | note the mates (`list_components`) and their faces (`list_faces(component=...)`), then `delete_component`, `insert_component` at the same transform, re-add the mates |

Either way, finish with `rebuild` (`mate_errors`), and put a re-mating in the plan as one change,
not one per mate. Mates name the components they hold (`components`) in the newer builds.

## Deriving snapshot fields

- **holes**: from `list_faces` take the cylindrical faces, group them by axis and radius, and
  pair coaxial radii into counterbores. Feature names from `list_features` (`CBORE for M8`, `M6
  Tapped Hole1`) give the standard. `list_faces` does not say whether a cylinder is concave (hole) or
  convex (boss). Decide from the feature type, or with `measure_distance`/point-inside checks in an
  assembly, and set the hole's `confidence` low if unsure.
- **internal radii / sharp internal edges**: fillet features and their radii come from
  `list_features` + `list_dimensions`. Sharp concave edges can't be told apart reliably, so set
  `sharp_internal_edges: null` unless the geometry is simple enough to reason about from
  `list_edges`.
- **setup_directions**: the distinct normals of planar faces from `list_faces`, plus the axes of
  holes.
- **draft_check**: for each planar face, draft = 90° − angle(normal, pull). Non-planar faces: use
  `check_printability(up=pull)` overhang output.
- **fasteners**: assembly component names/paths, such as Toolbox parts like `socket head cap
  screw_iso`.
- **tolerances** *(drawings)*: for each dimension id in `list_dimensions`, look up its annotation in
  the drawing's `list_views` and copy the tolerance or fit from the shown text into `dimensions[].tolerance`
  (`"±0.1"`, `"+0.05/0"`, `"H7"`). A dimension with no drawing annotation keeps `tolerance: null`, and
  the general tolerance class then applies.
- **drawing**: open the drawing next to the part (same name, `.SLDDRW`) with `drawing_file`, read
  `list_views` and `check_drawing`, `render_drawing` to `blueprint/<slug>/shots/NN-drawing.png`,
  then `drawing_file(action='close')`, so you leave nothing open that wasn't open before.

## Known pitfalls

- `list_faces` / `list_edges` / `add_fillet` see only the first body of a multibody part. Record the
  other bodies as a gap.
- Base generation: `add_circular_pattern` finds only axes along model Z (*(drawings)*: use
  `add_axis` + `axis=`).
- Saving over a file that is still open fails. Close it first, or save to a new path.
- Closing never prompts, so unsaved changes are lost without `save=true`. Check `modified` in
  `list_documents` before closing anything Jig changed.
- A drawing refers to the saved part file. Save the part before `make_drawing` / `build_drawing`, and
  again after model edits before re-checking the drawing.
- Hole callouts made with `add_symbol` / `import_dimensions` follow the model. Typing a callout's text
  by hand freezes it, so change the model and let the callout follow.
- Base generation: `make_drawing` gives a dimensioned sketch only, so treat Drawing flags as
  `needs-engineer`.
- Long sessions grow SolidWorks' memory. On a low-memory warning, save and ask the engineer to
  restart SolidWorks between iterations, never mid-call.
