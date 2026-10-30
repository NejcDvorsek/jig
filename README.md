# Jig

*A jig holds the work and guides the tool so every part comes out right. This one does that for AI in your CAD.*

https://github.com/user-attachments/assets/d11cb1b0-ee66-4194-9ba5-494125389d1b

A Claude Code plugin for mechanical engineers working in real CAD. Ask for what you need in plain
language, like "make the mounting holes M10", "can this be milled?" or "design a bracket for 50 kg".
The **orchestrator** picks only the steps and reviewers the request needs:

- **Blueprint** keeps the design's spec and changes the model, checking every write.
- **Red Line** critics review only what the change can affect: DFM, standards, cost, assembly,
  drawing.
- You see the plan and confirm it before anything in the model changes.

For new designs there is also a thought-through mode: a full spec first, then a build → review → fix
loop until no critical flags remain. The pattern (a stateful drafter plus stateless critics) comes from
Google's Elephant-Goldfish model.

![How Jig works](docs/media/how-jig-works.png)

**CAD connectors:** SolidWorks (bundled). The agents are CAD-agnostic, and more connectors can be
added without changing them (see [Adding a connector](#adding-a-connector)).

## Install

Requirements: Windows with SolidWorks installed and **running**, Claude Code, and
[uv](https://docs.astral.sh/uv/getting-started/installation/).

```text
/plugin marketplace add NejcDvorsek/jig
/plugin install jig@jig-cad
```

The plugin registers its SolidWorks MCP server, [`sw-mcp`](https://github.com/NejcDvorsek/sw-mcp), itself,
and uv fetches it from PyPI on first start, so there's nothing else to configure. Check the setup with
`/jig:doctor`.

To update, run `/plugin marketplace update jig-cad`, update `jig` in `/plugin`, and restart Claude
Code. Each Jig version pins the `sw-mcp` server version it was tested with, so the server updates
along with it.

## Examples

All examples come from one real project: a vertical camera-positioning frame with Y and Z ball-screw
drives (39 BOM items). An engineer modelled the assembly by hand in SolidWorks. Jig was used on it
afterwards, to review it, change it and draw it.

### From a solid part to bent sheet metal

*"is the Y plate manufacturable?"* The DFM critic found that the plate under the Y ball nut was a
solid 10 mm hat section with sharp (R0) inner corners. It can't be laser cut and bent, as the spec
requires. Jig proposed splitting it, and on the engineer's yes it built two new parts: a flat
laser-cut plate and a small 3 mm U-bracket for the nut housing. The old part file was left as it
was.

| Before: one solid hat section, R0 bends | After: flat laser-cut plate, 10 mm | After: bent U-bracket, 3 mm |
|---|---|---|
| ![Solid hat section before](docs/media/examples/nut-bracket-before.png) | ![Flat laser-cut plate](docs/media/examples/nut-bracket-after-plate.png) | ![Bent U-bracket](docs/media/examples/nut-bracket-after-u.png) |

In the assembly the U-bracket (orange) bridges the notch in the plate (blue), bolted to it by its
flanges, and holds the Y ball-nut housing. Jig replaced the old plate in place, mated both parts and checked the clearance to the
ball-nut flange (3 mm):

![Plate and U-bracket in the assembly](docs/media/examples/nut-bracket-assembly.png)

*"change the part from extruded to sheet metal and create a drawing"*. Jig rebuilt the U-bracket as a
SolidWorks sheet-metal part (4 bends, R4.5, K 0.42) with the same holes and the same mass
(0.175 kg), checked the flat blank against a hand calculation (233.19 × 95 mm), and made the drawing
with the flat pattern and bend notes:

![Nut bracket Y drawing with flat pattern](docs/media/examples/nut-bracket-drawing.png)

### Missing bolt holes, and a problem nobody asked about

*"there are holes missing for the brackets that join the camera plate to the Y plate"*. Jig read the
hole positions off the two angle brackets (yellow) and added matching Ø9 holes: 4 in the Y plate
(blue) and 8 in the camera plate (green), each one checked coaxial with its bracket hole (offset
0.0 mm).

| Camera plate with the 8 new holes | The joint in the assembly |
|---|---|
| ![Camera plate with new holes](docs/media/examples/bolt-holes-plate-x.png) | ![Brackets joining the plates](docs/media/examples/bolt-holes-assembly.png) |

The change touched an interface, so the Standards and Assembly critics reviewed it. They:

- wrote out the fasteners: 12× ISO 4762 M8×30-8.8 + ISO 7089 washer + ISO 7040 nut, with heads
  inside the bracket, because nuts there would clash at the corner holes;
- checked the clearance to the linear module below (59 mm);
- found a **1.13 mm overlap** between a bracket and the Y plate that was already in the model and
  now sits under a bolted joint. It went to the engineer as a critical flag, not a silent fix.

### Assembly drawing with BOM

*"give me a balloon drawing of the assembly with a bill of materials"*. Three views, one balloon per
BOM item, and a CSV of the BOM. Parts hidden in the model (camera, lenses, protective glass) are
drawn as dashed outlines.

![Assembly drawing with balloons and BOM](docs/media/examples/assembly-bom.png)

### Overall dimensions

*"a separate drawing with the overall dimensions of the assembly"*

![Overall dimensions drawing](docs/media/examples/assembly-dimensions.png)

## Everyday use

Just ask. The orchestrator triggers automatically, or you can call it:
`/jig:orchestrator "<what you need>"`.

| You say | What runs |
|---|---|
| "what's the thinnest wall?" | Inspect only. No critics, nothing written |
| "make the mounting holes M10 so the new bolts fit" | plan → **your confirm** → edit → Standards + Assembly (focused on those holes) → records *CON: holes accept M10* |
| "add R3 to the pocket corners" | plan → confirm → edit → DFM |
| "change it to 6082, it's cheaper" | plan → confirm → edit → Cost + Standards + DFM |
| "can this be milled?" | DFM (+ Cost) review, no changes |
| "these bolts are always A4 stainless from now on" | records the constraint, then checks the model against it |
| "undo that" | restores the last checkpoint |
| "design a bracket for 50 kg …" / "release review" | design mode (below) |

Each change ends with one line saying what ran and why, e.g. *"Ran Standards + Assembly (hole on
interface INT-001). Skipped DFM / Cost / Drawing: not affected. Logged as change 04."* Flags caused by
your change come first; problems that were already there are listed separately.

How it decides is a readable, editable table: [`docs/impact-map.md`](docs/impact-map.md).

| Request | Pipeline |
|---|---|
| questions, cosmetic changes | inspect / edit only |
| any other change | edit + the affected critics, focused on the change |
| new designs, release, "iterate until clean" | full spec + converge loop (offered, never started without a yes) |

A change that touches an interface, a requirement-bound value or an assembly, or several kinds of
change at once, also gets a **baseline**: a snapshot from before the edit, so the critics can tell
what the change caused, plus a requirement re-check. "Just do it" skips the critics (the edit is
still verified and logged), and "full review" adds the baseline and every possibly affected critic.

**Faster runs.** The reviews take most of the time, so you choose when they run:

| Say | Effect |
|---|---|
| "quick: …" / "just do it: …" | no snapshot and no critics. The edit is still checked and logged |
| "… review later" | no critics now. The change is logged as *pending*, and `/jig:redline` later reviews all pending changes in one run |
| "… review: assembly only" | exactly the critics you name |
| "it's a one-off prototype" / "we need 200 a year" | recorded as the quantity. Cost runs only with a cost target or a quantity above 5 |

The snapshot reads only the sections the chosen critics need. With a server that has `read_model`
(sw-mcp 0.2.0 or later) that is one call, and holes, concave edges, walls and setups come from the
SolidWorks API rather than being guessed from faces. Older servers fall back to a slower recipe.
Each topic has one owning critic (`docs/critic-protocol.md`), so a problem is reported once.
The snapshot agent and the Cost, Drawing and Standards critics run on Sonnet. DFM and Assembly use
your session's model. Change a critic's `model:` line in `agents/` to adjust this.

**The spec builds up as you work.** The first change to a part creates a small blueprint for it.
Every "it has to…" you say is recorded as a constraint and shown in the plan, so you can say "drop
that". Later reviews check against everything recorded.

## Design mode

```text
/jig:init "bracket for a 50 kg static load, aluminium, 4× DIN 912 M10 to the wall, CNC milled"
/jig:converge
```

`init` writes the full spec: requirements, constraints, parameters sized by hand calculation,
interfaces, standards and open questions. `converge` asks once, then loops: Blueprint builds or
updates the model, all five critics review it in parallel, and Blueprint fixes, defers or escalates
each flag. It stops at zero open criticals, when only your decisions are left, when two passes make
no progress, on a CAD error, or at the iteration cap (default 5).

To steer, edit `blueprint.md`: change values, set `locked: yes` on a parameter, answer open questions,
or mark a flag `overridden`. Then run it again.

## Commands

| Command | Use | Changes the model? |
|---|---|---|
| `/jig:orchestrator "<anything>"` | default entry point (also automatic) | only after your confirm |
| `/jig:init "<intent>"` | full spec for a new design | no |
| `/jig:converge [--max N]` | full build/review loop | yes, after one confirm |
| `/jig:redline [dfm,cost] [focus: …]` | explicit review with chosen critics | no |
| `/jig:snapshot` | dump the model to neutral JSON | no |
| `/jig:doctor` | check uv, connector, CAD, project | no |

## What ends up in your project

```text
blueprint/
├── rules.md                 (optional) house design rules. Every critic applies them
└── <part-or-assembly>/      one folder per design you touch
    ├── blueprint.md         spec: constraints, parameters, decisions, flag register (lite → full)
    ├── changelog.md         every change: your request, what changed, which flags, checkpoint
    ├── snapshots/  redlines/  checkpoints/  shots/
```

## How it works

- **Critics are a pure function**: `(blueprint, snapshot, focus, baseline) → flags`. Because they only
  see neutral files, they don't depend on the CAD system.
- **A critic can't block with a guess.** A critical flag needs cited evidence. A check the data can't
  support is `info`, "unverifiable".
- **Safety:** a checkpoint copy of the model before every change, no writes to locked parameters or
  to your own features without asking, and the typed CAD tools only (no scripts).

| Persona | Checks |
|---|---|
| DFM | wall thickness, draft, undercuts, internal radii vs tool, hole depth, setups (per process) |
| Standards | ISO 2768, ISO 286 fits, ISO 273 clearance holes, DIN 974 counterbores, threads, EN materials |
| Cost | stock utilisation, material, setups, tool variety, tolerances, fasteners, unit-cost estimate |
| Assembly | interference, clearances, hole-pattern alignment, fits, worst-case/RSS stack-ups, tool access |
| Drawing | title block, projection, views, dimensions, hole callouts, GD&T, surface finish (reads the PDF) |

There is no FEA in v1. Blueprint keeps hand calculations for each load requirement in the spec.

## Known limits (SolidWorks connector)

- It runs on Windows only and needs SolidWorks already open. The server attaches to it but won't
  start it.
- Only SolidWorks is supported for now. Jig is built to work with other CAD programs, but SolidWorks
  is the only connector so far.
- Long sessions slow SolidWorks down, because its memory use grows over time. On a low-memory
  warning, save and restart SolidWorks between runs, never during one.

See [`connectors/solidworks/CONNECTOR.md`](connectors/solidworks/CONNECTOR.md).

## Adding a connector

Write one adapter file. Critics, schemas, the orchestrator and the loop stay untouched. See
[`docs/connector-contract.md`](docs/connector-contract.md).

## License

MIT. The connector server [`sw-mcp`](https://github.com/NejcDvorsek/sw-mcp) is a separate MIT-licensed
project, installed from PyPI at runtime. It is a fork of Henk Jan Baard's
[SolidWorks-MCP](https://github.com/hjbaard/SolidWorks-MCP).
