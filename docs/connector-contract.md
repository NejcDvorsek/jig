# Connector contract

Jig never talks to a CAD system by name. Every CAD system is reached through a
**connector**: an MCP server plus one adapter file, `connectors/<name>/CONNECTOR.md`, that maps the
neutral operations below onto that server's tools.

Only Blueprint and the snapshot agent touch a connector:

| Step | Who | Operations used |
|---|---|---|
| Snapshot (model → `snapshot.json`) | `cad-snapshot` agent | read operations only |
| Inspect (questions, edit prep) | Blueprint, via the orchestrator | read operations |
| Edit (spec → model) | Blueprint, via the orchestrator or `converge` | read + write operations |

The five Red Line critics never see a connector. They read `blueprint.md` and the neutral snapshot,
so they work unchanged for any CAD system.

## Detecting the connector

1. If `blueprint.md` frontmatter has `connector: <name>`, use that one.
2. Otherwise check which connectors' `status` tools are available in this session (each
   `CONNECTOR.md` names its status tool) and call it. Use the first one that reports a running CAD session.
3. If none respond, stop and tell the engineer what to start (each `CONNECTOR.md` says how).

MCP tool names carry a prefix that depends on how the server was registered. For example
`mcp__solidworks__list_features` is a server the user registered, and
`mcp__plugin_jig_solidworks__list_features` is the one this plugin ships. Match tools by
the **short name after the last `__`**. If both are present, prefer the user's own registration,
because it is usually a newer development build.

## Neutral operations

Each adapter states, for every operation, the tool(s) to call and a support level:
`full`, `partial` (with what is missing), or `none`. The table is a starting point: CAD servers
change, so the live tool list wins. A tool the adapter doesn't mention but that clearly fills an
operation (e.g. a new `read_drawing_annotations`) may be used. Record that in the snapshot's
`capabilities`.

### Read
| Operation | Returns (neutral) |
|---|---|
| `status` | CAD product + version, connector/server version, active document |
| `documents` | open documents (part / assembly / drawing, path) |
| `model_read` | *optional, preferred.* The snapshot's model sections in **one call**, derived on the server: core, material, holes, radii, setups, walls, draft (and assembly, where supported). See below |
| `features` | feature tree in order: name, type, suppressed, rebuild error |
| `dimensions` | driving dimensions: id, feature, value, unit, tolerance if known |
| `equations` | global variables / equations |
| `mass` | volume, mass, surface area, centre of mass, material |
| `bbox` | bounding box |
| `bodies` | solid bodies per part |
| `faces` | faces with type, normal / axis, radius, area, centre |
| `edges` | edges with type, length, ends |
| `sketch` | sketch geometry + dimensions + fully-defined flag |
| `wall_thickness` | thin regions below a threshold |
| `overhangs` | faces leaning past an angle for a given build/pull direction |
| `components` | assembly components: name, source file, transform, fixed |
| `mates` | mates / joints and their health |
| `interference` | interfering component pairs + volume |
| `distance` | minimum distance between two components |
| `annotations` | model or drawing annotations: tolerances, GD&T, notes |
| `drawing` | drawing sheets, views, title block |
| `screenshot` | image of the model from a named view |
| `export` | STEP / STL / PDF etc. to a path |

### `model_read`

The snapshot is the step most likely to go wrong when an agent derives holes, edges and setups
from raw faces over dozens of calls. A connector whose server can do it in one call, from the CAD
API, offers `model_read`:

- It takes the snapshot sections it should read (`core` always), plus the wall threshold and the
  pull direction when `walls` / `draft` are asked for.
- It returns the section fields of `snapshot-schema.md`, or fields the adapter maps onto them
  one to one, plus its own `gaps`.
- It is read-only and deterministic: the same model gives the same result.

The adapter says which sections the live server covers. The snapshot agent uses `model_read` for
those, and the adapter's fallback recipe (from `faces`, `edges`, `wall_thickness` …) only for the
rest, or for builds without it. Drawings and images stay separate operations: they open documents
and write files.

### Write
| Operation | Effect |
|---|---|
| `set_dimension` | change one driving dimension |
| `set_equation` | set a global variable that drives dimensions |
| `add_feature` | any modelling feature (the adapter lists its feature tools) |
| `delete_feature` / `suppress_feature` / `reorder_feature` | edit history |
| `set_material` | assign material |
| `make_drawing` | create a drawing of the current part |
| `save` | save the current document |
| `new_document` / `open_document` | create or open a part / assembly |
| `close_document` | close one document (part, assembly or drawing) without saving |

## Rules for every connector

- **Parametric first.** Change existing models via `set_dimension` / `set_equation` before adding or
  deleting features.
- **Read back after every write.** A write counts only once a read confirms the value. Most CAD MCPs
  return measured mass/bbox after every call: compare them with the expected change.
- **Gaps are data.** If an operation is `none` or fails, the snapshot records it under `gaps`, so the
  critics can say "unverifiable" instead of guessing.
- **No arbitrary code.** Adapters use only the server's typed tools.
- **Leave the CAD as you found it.** Windows must not pile up over a day of work:
  1. **Before the first open or new**, call `documents` and keep that list: these are the engineer's
     documents.
  2. Everything Jig opens or creates (parts, assemblies, drawings, imports, scratch documents) is
     **closed again when the step that needed it is done**, at the latest at the end of the run. That
     includes runs that stop early: a failed edit, a cancel, a stop condition, or a question for the
     engineer.
  3. Before closing, keep what must be kept: a confirmed edit is already saved by Edit. A document
     opened only to read is closed without saving. If a document Jig opened shows unsaved changes Jig
     didn't make, don't close it: report it.
  4. **Never close one of the engineer's documents** (step 1's list), even if Jig worked in it.
     Make the engineer's previously active document active again.
  5. Afterwards call `documents` again and check that only the engineer's documents are left (plus
     the hidden parts their own assemblies load). Name anything Jig couldn't close in the result.
  6. Each actor closes what it opened: the `cad-snapshot` agent its own documents before it replies,
     the main session the rest. A document that was already open when an actor started is not its to
     close.

## Adding a connector

1. Ship or point to its MCP server: add an entry to `.mcp.json` (or have users register it).
2. Write `connectors/<name>/CONNECTOR.md` using `connectors/solidworks/CONNECTOR.md` as the template:
   status tool, how to start the CAD program, an operation table with support levels, conventions
   (units, axes, face naming), and known pitfalls. Map `model_read` if the server has it, and give
   a fallback recipe for the snapshot fields it doesn't cover.
3. Run `/jig:doctor` and `/jig:snapshot` on a known part, and check the
   snapshot against values read by hand in the CAD program.

Nothing else changes: critics, the snapshot schema and the loop stay the same.
