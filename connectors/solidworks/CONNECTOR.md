# Connector: SolidWorks

- **MCP server:** [`sw-mcp`](https://github.com/NejcDvorsek/sw-mcp) (MIT, a fork of `solidworks-mcp` with the drawing tools), registered by this
  plugin's `.mcp.json` as server `solidworks`, pinned exactly and run with `uvx`. It drives the
  user's **running** SolidWorks over COM, on Windows only.
- **Status tool:** `get_status`
- **Start:** open SolidWorks and leave it running. The server attaches to it and does not launch it.
- **Self-test:** `uvx sw-mcp --selftest` with SolidWorks open.
- **Server guide:** read the MCP resource `solidworks://guide` before the first write in a session.
  Units, axes, face picking, drawing references and the modelling and drawing recipes are all
  there. This adapter only maps the neutral operations.

Tool names below are short names. Match the tool whose name ends in `__<short name>` (see
`docs/connector-contract.md`). This file describes the pinned server version; if the live tool list
differs, the **live tool list wins**. `read_model` is the one exception: it arrives with sw-mcp
0.2.0, so check for it once per session (see *Snapshot*) and record the result in the snapshot's
`capabilities`.

## Conventions

- Every modelling call returns volume, mass and bounding box. Compare them with your expected
  change after **every** write.
- Tools return `dimensions` as `{role: 'width@Sketch1'}`. Record these ids as the parameter's CAD
  binding in `blueprint.md` §4.

## Read operations

| Neutral op | Tool(s) | Support | Notes |
|---|---|---|---|
| `status` | `get_status` | full | SW revision, server version, active document |
| `documents` | `list_documents` | full | |
| `model_read` | `read_model(sections, wall_mm, pull, clearance_pairs)` | full for parts | sw-mcp 0.2.0+. Every body, Hole Wizard data, concave edges. `assembly` only where the live tool accepts it. See *Snapshot* |
| `features` | `list_features` | full | flags rebuild errors and under-defined sketches |
| `dimensions` | `list_dimensions` | partial | values only. Tolerances: see `annotations` |
| `equations` | `list_equations` | full | |
| `mass` | `get_mass_properties` | partial | volume, mass, area, CoM, bbox. Material name is not returned: take it from the last `set_material` result, the drawing's title block, or record a gap |
| `bbox` | `get_bounding_box` | full | parts and assemblies |
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
| `drawing` | `drawing_file(action='open')` + `list_views` | full | sheet, frame, title block, and per view: type, scale, outline, and **annotations** (id, type, shown text, value, box) |
| `annotations` | `list_views` | full | dimensions with their shown text (tolerances and fits appear in it), hole callouts, datums, GD&T frames, surface finish, notes |
| `drawing_check` | `check_drawing` | full | views/annotations off the frame or over the title block, overlaps, crossing leaders, text < 2.5 mm, likely duplicates, and **hole/cut/fillet/chamfer features no dimension or callout covers** |
| `drawing_image` | `render_drawing`, or `drawing_file(action='export', path=*.png)` | full | a picture of the sheet or a zoomed region |
| `screenshot` | `screenshot` | full | |
| `export` | `export`; drawings: `drawing_file(action='export')` | full | STEP/STL/IGES/x_t/3MF; drawings to PDF/DXF/DWG/PNG |

## Write operations

| Neutral op | Tool(s) | Notes |
|---|---|---|
| `set_dimension` | `set_dimension` | read back with `list_dimensions` |
| `set_equation` | `set_equation` (one or a list), `delete_equation` | preferred for PAR-bound values |
| `add_feature` | `add_box`, `add_disc`, `add_cylinder`, `add_cone`, `add_extruded_profile`, `add_extruded_slot`, `add_revolved_profile`, `add_swept_*`, `add_loft`, `add_boss_on_face`, `add_sketch` + `extrude_sketch` / `cut_sketch`, `cut_profile`, `cut_slot`, `cut_offset_pocket`, `add_hole`, `add_thread`, `add_fillet`, `add_full_round`, `add_chamfer`, `add_shell`, `add_rib`, `add_mirror`, `add_linear_pattern`, `add_circular_pattern`, `add_plane`, `add_axis`, `combine_bodies`, `split_body`, `add_text_on_face` | recipes in `solidworks://guide`. Prefer the Hole Wizard (`add_hole(iso=…)`) for standard ISO holes: it carries the standard into the callouts |
| `delete_feature` / `suppress_feature` / `reorder_feature` | same names | |
| `set_material` | `set_material` | |
| `set_appearance` | `set_appearance` | cosmetic |
| `make_drawing` | `make_drawing(path, sheet, scale, keep_open, max_sheet)` | ISO sheet with title block, material and mass, one counted callout per hole set, hole centres dimensioned, and `problems` returned. Save the part first. Fitted (sw-mcp 0.2.0+): views move with their annotations clear of the frame, the title block and each other; if they can't, the iso view is left out, then the next sheet up is tried to `max_sheet` (default A1). Read `sheet`, `fit.fits`, `fit.tried`, `left_out`. `fit.fits: false` means work on from step 2 of *Fitting the sheet* (`docs/blueprint/edit.md`) |
| `drawing_build` | `build_drawing(spec)` | the whole drawing from a spec (views, sections, details, dims, callouts, symbols, notes, tables, props). To change it, edit the spec and rebuild. Fitted like `make_drawing` (spec `max_sheet`, `"fit": false` to keep your own places); it never leaves views out: when `fit.fits` is false, take out or combine views in the spec and build again |
| `drawing_edit` | `drawing_file`, `add_view`, `edit_view`, `auto_layout` (also fits by footprint), `import_dimensions`, `add_dimension`, `add_symbol` (hole callout, surface finish, datum, GD&T), `add_note`, `add_table`, `edit_annotation`, `set_drawing_properties` | the small changes: one callout, one tolerance, a datum, the title block |
| `set_tolerance` | `edit_annotation(id, tolerance=[upper, lower] / fit='H7')` | on a model dimension this **changes the part**: the result says `changes_part`. Treat it as a model edit: confirm and checkpoint |
| `save` | `save_document()` (over its own file); drawings `drawing_file(action='save')` | |
| `new_document` / `open_document` | `new_document(kind)`, `open_document(path)`, `activate_document`; drawings `drawing_file(action='new'/'open')` | |
| `close_document` | `close_document(title, save)`: any part, assembly or drawing by title | without `save=true` it closes **without saving and without asking**, and reports `discarded_changes` |
| assembly | `insert_component`, `add_mate` (`mates=[…]` for several), `delete_mate`, `suppress_mate`, `set_component_transform`, `replace_component`, `delete_component`, `check_motion` | |

**Never used by Jig:** `run_script`, even when the server allows it. Blueprint works only through
typed tools, so every change can be checked, confirmed and logged.

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

## Large assemblies

On assemblies with roughly 50 or more components or 100 or more mates, the tool results get big.

- **Components in focus:** `list_components(name="Bolt*")` returns the matches and the mates that
  hold them. `brief=True` gives name, path and fixed only, `mates=False` leaves out the mates.
- **Several mates:** one `add_mate(mates=[...])` and one `delete_mate([...])` (it returns
  `mates_left`, a count), not one call per mate.
- **Swap a part:** `replace_component(component, path)` returns the kept mates, and for each broken
  one the face it held and candidate faces (`#index`) on the new part. Then `delete_mate` the
  broken ones and `add_mate(mates=[...])` them again on the candidates.

Finish with `rebuild` (`mate_errors`), and put a re-mating in the plan as one change, not one per
mate.

## Snapshot

### With `read_model` (sw-mcp 0.2.0+)

One call reads the model sections: `read_model(sections=[...], wall_mm=<threshold>, pull=<dir>)`.
Pass the snapshot sections it covers (`core`, `material`, `holes`, `radii`, `setups`, `walls`,
`draft`, and `assembly` if the live tool accepts it). `wall_mm` only with `walls`, `pull` only
with `draft`. It returns `sw-mcp/model@1`, which maps onto the snapshot like this:

| `read_model` | Snapshot | Mapping |
|---|---|---|
| `parts[]`: `name`, `path`, `mass_kg`, `volume_mm3`, `surface_area_mm2`, `centre_of_mass_mm`, `bbox_mm`, `features`, `equations` | same fields | as they are |
| `parts[].bodies` (a list) | `bodies` | its length. Several bodies are worth a line in the report |
| `parts[].dimensions[]` | `dimensions[]` | `tolerance` object → text: `bilateral` `"+0.1/-0.05"`, `symmetric` `"±0.1"`, `limit` `"10.1/10.0"`, `fit` `"H7"`, `fit_with_tolerance` `"H7 (+0.015/0)"`, `none` → `null`. Add `bound_param` from the blueprint §4 table |
| `parts[].material` | `material` | `name`, `density_kg_m3` |
| `parts[].holes`, `internal_radii_mm`, `sharp_internal_edges`, `planar_face_normals`, `setup_directions`, `wall_check`, `draft_check` | same fields | as they are (the snapshot schema follows them) |
| `assembly` | `assembly` | as it is. `mates` is already `{count, broken}` |
| `gaps[]` (`what`, `why`, `section`) | `gaps[]` | add `affects` from the section, via `docs/impact-map.md` §3 |
| `server_version`, `cad_version` | `connector` | |

Set `"source": "model_read"` and `capabilities.model_read: "full"`. If `read_model` fails as a
whole (`ok: false`), report its error. A section that comes back `null` with a gap stays a gap:
don't rebuild it with the fallback.

### Fallback (no `read_model`)

Set `"source": "derived"`, and derive the fields from the inspection tools:

- **core**: `list_features`, `list_dimensions`, `list_equations`, `get_mass_properties`,
  `list_bodies`.
- **holes**: from `list_faces` take the cylindrical faces, group them by axis and radius, and
  pair coaxial radii into counterbores. Feature names from `list_features` (`CBORE for M8`, `M6
  Tapped Hole1`) give `kind`, `standard` and `size`. `list_faces` does not say whether a cylinder is
  concave (hole) or convex (boss). Decide from the feature type, or with `measure_distance`/point-inside
  checks in an assembly, and set the hole's `confidence` low if unsure. `source: "geometry"`. Group
  identical holes into one entry with `count` and `centres_mm`.
- **internal radii / sharp internal edges**: fillet features and their radii come from
  `list_features` + `list_dimensions`. Sharp concave edges can't be told apart reliably, so set
  `sharp_internal_edges: null` unless the geometry is simple enough to reason about from
  `list_edges`.
- **setup_directions**: the distinct normals of planar faces from `list_faces`, plus the hole
  entrances.
- **walls**: `check_printability(min_wall_mm=<threshold>)`, whose `thinnest_mm` is `min_found_mm`.
- **draft_check**: for each planar face, draft = 90° − angle(normal, pull). Non-planar faces: use
  `check_printability(up=pull)` overhang output.
- **fasteners**: assembly component names/paths, such as Toolbox parts like `socket head cap
  screw_iso`.
- All of this sees **only the first body** (see *Known pitfalls*): record the others as a gap.

### Both

- **tolerances**: a drawing tolerance wins over a `null` model tolerance. For each dimension id,
  look up its annotation in the drawing's `list_views` and copy the tolerance or fit from the shown
  text into `dimensions[].tolerance` (`"±0.1"`, `"+0.05/0"`, `"H7"`). A dimension with no tolerance
  in the model or on the drawing keeps `tolerance: null`, and the general tolerance class then
  applies.
- **drawing**: open the drawing next to the part (same name, `.SLDDRW`) with `drawing_file`, read
  `list_views` and `check_drawing`, `render_drawing` to `blueprint/<slug>/shots/NN-drawing.png`,
  then `drawing_file(action='close')`, so you leave nothing open that wasn't open before.
- **images**: `screenshot`.

## Known pitfalls

- `list_faces` / `list_edges` / `add_fillet` see only the first body of a multibody part. Record the
  other bodies as a gap. `read_model` reads every body.
- Saving over a file that is still open fails. Close it first, or save to a new path.
- A drawing refers to the saved part file. Save the part before `make_drawing` / `build_drawing`, and
  again after model edits before re-checking the drawing.
- Hole callouts made with `add_symbol` / `import_dimensions` follow the model. Typing a callout's text
  by hand freezes it, so change the model and let the callout follow.
- On a low-memory warning, save and ask the engineer to restart SolidWorks between iterations,
  never mid-call.
