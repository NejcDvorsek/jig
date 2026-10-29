# SolidWorks MCP: requests from Jig

Things in `solidworks-mcp` that cost Jig time in real sessions. `CONNECTOR.md` (*Large
assemblies*) says how Jig uses each one, with a fallback for builds that lack it.

**Status 2026-10-29:** 1 to 4 are in the local build (branch `feature/drawings-and-modelling-gaps`,
unreleased): `delete_mate` takes a list and returns `mates_left`, there are new `add_mates` and
`replace_component` tools, and `list_components` has `name` / `mates` / `brief`. Unit tests pass. The
live SolidWorks tests haven't run yet. 5 is still open. Since then the local build also merges tool families (106 → 91 tools):
`close_document(title, save)` closes any document by title without activating it first, and
`add_mate(mates=[...])` replaces `add_mates`.

Measured on a 102-component assembly with about 300 mates (2026-10-29): 23 mate calls, 10 broken
mates after a part swap, and a `list_components` result too large to read directly.

| # | Request | Why | Payoff |
|---|---|---|---|
| 1 | `add_mate`, `delete_mate`, `suppress_mate` return only `ok`, the mate name and a `mates_left` count by default (full list with `verbose=true`) | each call now returns all ~300 mates | high, cheap |
| 2 | Batch mate tools: `add_mates([...])`, `delete_mates([...])`, one rebuild at the end, a result per item | 23 calls → 2 | high |
| 3 | `replace_component(component, path)` keeps the transform and re-attaches what it can. It returns the mates that broke, each with its type, the other component, and the face it used (type, normal or axis, a point), plus candidate faces on the new part | re-mating 10 broken mates by hand | medium |
| 4 | `list_components(filter="Bolt*", fields=[...], mates=false)`, or `summary=true` (name, path, fixed and mate count only) | 102 parts was too large to read | medium, cheap |
| 5 | Optional: `list_holes()`, holes derived on the server (Ø, depth, axis, centre, counterbore, thread, feature), and a `read_model(sections=[...])` that returns features, dimensions, mass and bbox in one call | the snapshot agent needed 62 calls, mostly faces and holes | high, more work |

As built, `delete_mate` and `delete_component` return counts by default, with no `verbose` switch.
`list_components` gives the full list when called without arguments.
