# Impact map

The orchestrator uses this table to decide which Red Line critics a request needs, which snapshot
sections to read, and whether to take a baseline. The engineer can edit it: it is a table on purpose, so
that every choice can be traced.

## 1. Change → critics

Classify each planned model change into one or more categories. The critics to run are the union of
the categories' ● marks. ○ means "only if the condition holds".

| Category | Examples | DFM | Standards | Cost | Assembly | Drawing |
|---|---|---|---|---|---|---|
| `hole` | hole size, thread, counterbore, hole position, pattern | ○ depth/dia > 5 or near wall | ● | | ○ on an interface or mating part | ○ drawing exists |
| `fastener` | bolt size, count, standard | | ● | ● | ● | ○ drawing exists |
| `wall` | thickness, shell, pocket depth, rib, floor | ● | | ● | ○ on an interface face | ○ drawing exists |
| `edge` | fillet, chamfer, internal radius | ● | | | | ○ drawing exists |
| `size` | outer dimensions, length, envelope | ● | | ● | ● | ○ drawing exists |
| `material` | material or heat treatment | ● | ● | ● | | ○ drawing exists |
| `interface` | mating face, datum, fit, bolt pattern | | ● | | ● | ○ drawing exists |
| `new-feature` | adding a boss, slot, cut, pattern | ● | ○ holes/threads in it | ● | ○ near an interface | ○ drawing exists |
| `delete-feature` | removing or suppressing a feature | ● | | | ○ on an interface | ○ drawing exists |
| `assembly` | insert/move a component, mates | | ○ fasteners | ○ fasteners/parts | ● | |
| `drawing` | views, dimensions, tolerances, GD&T, callouts, notes, title block | | ○ tolerances, fits | | | ● |
| `tolerance` | a tolerance or fit on a dimension (changes the part too) | | ● | ○ tight fits | ● on an interface | ● |
| `cosmetic` | names, colours, appearance | | | | | |

**After any model change on a part that has a drawing**, the Drawing critic runs with focus "is the
drawing still right for the changed features": stale values, broken or missing callouts, and the
connector's drawing-check problems. If the connector can edit drawings, the fix round may update the
drawing (re-import the callouts, move a dimension), using the same confirm as for model edits.

**Cost gate.** Cost runs only when the blueprint has a `cost_target` or a `quantity` above 5, or the
engineer asks about cost. Otherwise drop it from every row here and in §2, including release and
"check everything". Say so once in the plan's Skipped line: *"Cost: no cost target or quantity. Say
the quantity to include it."* A stated quantity or price ("we need 200 of these", "must be under €40")
is recorded per `docs/blueprint/spec.md` and opens the gate.

"On an interface" means the feature touches a face, hole or dimension listed in blueprint §5, or a
face that is mated in an assembly. When unsure, include the critic.

## 2. Review question → critics

For read-only review requests ("check this", "can it be made?"):

| The engineer asks about | Critics |
|---|---|
| manufacturability, machining, moulding, printing | DFM (+ Cost if quantity or cost is mentioned) |
| standards, tolerances, threads, fits, compliance | Standards (+ Drawing if a drawing exists) |
| cost, cheaper, quote | Cost (+ DFM) |
| fit, clash, assembly, clearance, stack-up | Assembly (+ Standards for fits) |
| the drawing, release, "ready for the shop" | Drawing + Standards; for **release**, all five |
| "check it" with no focus | all personas in the blueprint (default all five) |
| "review: assembly only", "just DFM" | exactly the named critics, nothing added |

The Cost gate (§1) applies to every row.

## 3. Critic → snapshot sections

The snapshot agent reads only the union of the selected critics' sections. `core` is always read.

| Section | Contents (see `snapshot-schema.md`) | Read for |
|---|---|---|
| `core` | document, mass, bbox, features, dimensions, equations | always |
| `material` | material name and density | Standards, Cost, DFM |
| `holes` | derived holes, threads, counterbores | Standards, Assembly, Drawing, DFM (hole/new-feature) |
| `walls` | `wall_check` at the process threshold | DFM, Cost (wall) |
| `radii` | internal radii, sharp internal edges | DFM |
| `setups` | planar normals, setup directions | DFM, Cost |
| `draft` | `draft_check` (cast/moulded only) | DFM |
| `assembly` | components, fasteners, mates, interference, clearances | Assembly, Cost (fastener) |
| `drawing` | drawing paths and PDF, annotations if readable | Drawing |
| `images` | iso screenshot | on request, or DFM on complex shapes |

## 4. Pipeline and baseline

| Request | Pipeline |
|---|---|
| question, or a `cosmetic` change | Inspect → answer. A cosmetic change still gets a confirm + Record |
| any other change | plan + confirm → Edit → Review with focus (`docs/blueprint/review.md`) → Triage → Record |
| new design, release review, "converge" / "iterate until clean" | `init` and/or the `converge` loop |

**Baseline.** A change also gets a snapshot from *before* the edit, passed to the critics as
`baseline`, and a requirement re-check after it, when it spans several categories or touches an
interface (§5), a requirement-bound parameter or an assembly mate. Say why in the plan's Review
line ("with baseline (interface)").

## 5. Escalation

Escalation only goes up, and the reason is always said in the plan or result line:

- A critical flag in the change scope remains after one fix round: **offer** converge, but never
  start it without a yes.
- A planned change conflicts with a `locked` parameter, a `hard` constraint or an engineer-owned
  feature: stop before editing and ask.
- An edit fails, or the rebuild shows errors: revert, stop, report.

The engineer's words override the map:
- "quick", "just do it", "no review" mean no critics (the edit is still verified and recorded),
  and the instruction itself counts as the confirm.
- "properly", "full review", "check everything" add a baseline and every critic with a ○ in the
  change's rows.
- "converge", "iterate", "until it's clean" go to the converge loop.
- "review later", "hold the reviews", "I'll review at the end" mean no critics now. The changelog
  entry gets `Red Line: pending (<the critics the map chose>)`, and a later `/jig:redline` with no
  arguments reviews all pending entries in one run (see that skill).
- "review: <critics> only" runs exactly those critics.

## 6. Topic owners

Each topic has one critic that flags it. The table lives with the critics, in
`critic-protocol.md` (*Topic owners*), because they are the ones who read it.
