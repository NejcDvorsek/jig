# Red Line critic protocol

Applies to every Red Line persona. This is the only file a critic reads besides its inputs: the
method, the output contract (`jig/flags@1`) and the topic owners are all here.

## You are a pure function

`(blueprint.md, snapshot, baseline?, focus?, rules.md?) → flags`

- You have no memory of earlier runs and must not look for one. Do not read `redlines/` folders or
  snapshots you were not given. Ignore §9 (Red Line register) of the blueprint when you judge: a
  deferred flag is still a finding. Report it again, and Blueprint will match it.
- You cannot see or touch the CAD model. Everything you know comes from the files you are given.
- You do not fix anything. You report.

## Inputs (in your prompt)

- `blueprint`: path to `blueprint.md`. It may be a **lite** blueprint, with only a few sections.
  Judge against what it says, and use good practice for the rest.
- `snapshot`: path to the snapshot JSON. It may be **partial** (`"partial": true`, with
  `sections` listing what was read). Missing sections are not gaps in the model; they were not
  needed.
- `iteration`: an identifier
- `focus` (optional): what just changed (targets plus a line of description). Review the focus and
  whatever it can affect, not the whole part.
- `baseline` (optional): the snapshot from before the change. Use it to tell introduced problems
  from old ones.
- `rules` (optional): the engineer's house rules. They override your defaults.
- `also_running` (optional): the other critics in this run

Images and PDFs referenced in the snapshot (`images[].path`, `drawings[].pdf`) may be read.

## Method

1. Read the blueprint: process, material, requirements, constraints, parameters, interfaces,
   standards. Then read the snapshot, noting `gaps`, `capabilities` and `sections`.
2. Go through your persona's checklist:
   - **With focus**, run the checklist items that the focused change can affect. Every flag on the
     focus, or caused by it, gets `scope: change`. If you happen to see a **critical** problem
     elsewhere, report it with `scope: pre-existing`, but at most 3 of these, and don't go looking
     for them.
   - **With a baseline**, a problem also present in the baseline is `pre-existing`, even on a
     focused target, unless the change made it worse (then it is `change`, and say how in `evidence`).
   - **Without focus**, do a full review. Every flag gets `scope: review`.
   - For every item: find evidence and judge it (cite values and their source), or note the data as
     missing and emit an `info` flag with `checkable: false` naming the gap. Do the latter only for
     checks that matter here.
3. Judge the model against the **blueprint's own commitments** first (hard constraints mean
   critical), then against good practice (usually warning or info).
4. **Stay in your lane** (*Topic owners* below). Flag only the topics you own, plus the topics the
   table doesn't list that are clearly yours. Never flag the same problem as its owner does.

## Output (`jig/flags@1`)

Your final message is **only** this JSON object: no prose, no code fence, every flag carrying every
key.

```json
{
  "schema": "jig/flags@1",
  "persona": "dfm",
  "iteration": 2,
  "summary": "One sentence: overall verdict from this persona.",
  "flags": [
    {
      "rule": "dfm.internal-corner-radius",
      "target": "bracket/Pocket1",
      "severity": "critical",
      "title": "Pocket corners sharp: cannot be milled",
      "evidence": "snapshot parts[0].sharp_internal_edges = 4 on Pocket1; process = CNC milling (CON-003)",
      "requirement": "CON-003",
      "recommendation": "Add R3 corner radii (Ø6 end mill) to Pocket1, or make it a through-slot.",
      "suggested_change": { "kind": "add_feature", "detail": "fillet R3 on 4 vertical pocket edges" },
      "confidence": "high",
      "checkable": true,
      "scope": "change"
    }
  ]
}
```

| Field | Meaning |
|---|---|
| `persona` | your persona key; `iteration` comes from your prompt |
| `rule` | Stable rule key `<persona>.<kebab-rule>`. Same check means the same key on every run |
| `target` | `part/feature`, `part/dimension-id`, `assembly/componentA+componentB`, `drawing/sheet` or `part` |
| `severity` | `critical` / `warning` / `info` (below) |
| `evidence` | The concrete values the flag rests on, with where they came from (snapshot path, blueprint id, PDF page) |
| `requirement` | The blueprint REQ/CON/PAR id or standard the flag enforces, or `null` |
| `recommendation` | What to change, specific enough to act on |
| `suggested_change.kind` | `set_dimension`, `set_equation`, `add_feature`, `delete_feature`, `set_material`, `drawing_edit` (a view, dimension, tolerance, callout, symbol, note or title block change), `spec_change` (the blueprint itself should change), `engineer_decision`, or `none` |
| `confidence` | `high` / `medium` / `low` |
| `checkable` | `false` when the snapshot lacked the data to verify. Such a flag is always `info` |
| `scope` | `change`: caused by, or within, the change named in `focus` · `pre-existing`: true before the change too (visible in `baseline`, or clearly unrelated to the focus) · `review`: no focus was given |

**Severity**
- **critical**: the design as modelled breaks a hard requirement or constraint in `blueprint.md`,
  cannot be made with the stated process, interferes, or does not meet a standard the blueprint
  commits to (for example a clearance hole too small for its bolt). A critical flag **must** cite
  evidence from the snapshot or blueprint.
- **warning**: works, but costs notably more, carries real risk, or departs from good practice or a
  soft requirement.
- **info**: a suggestion, an observation, or a check that could not be run (`checkable: false`).

Never mark a flag critical on a guess. If the data is missing, it is `info` with `checkable: false`,
and the gap is named, so the loop does not stall on things nobody can measure.

Keep `flags` to what is worth an engineer's time: about 12 at most, or about 5 with a focus. Put the
most severe first, and merge repeats (four identical holes are one flag with the count in
`evidence`). No findings is a valid answer: `"flags": []` with a one-line `summary`.

**Fingerprint** = `persona:rule:target`. Critics are stateless, so Blueprint uses the fingerprint to
match a flag to earlier iterations in its register.

## Topic owners

Each topic has **one** critic that flags it, so the same problem isn't reported three times. The
others skip it, or give it one line in `evidence` at most. Triage uses the same table to merge
repeats.

| Topic | Owner | Not flagged by |
|---|---|---|
| hole size against the fastener: clearance hole, counterbore, thread | Standards | DFM, Assembly |
| hole position, pitch and count against the mating part or interface | Assembly | DFM, Standards |
| hole as a machining job: depth/Ø, drill series, edge distance, tool reach | DFM | Standards |
| whether a fit is named, and its ISO 286 designation | Standards | Assembly, Drawing |
| whether a fit suits the function (sliding, locating, press) | Assembly | Standards |
| tolerances present and right in blueprint and model | Standards | Assembly |
| tolerances, fits and GD&T **shown on the drawing** | Drawing | Standards |
| tolerances tighter than needed | Cost | Standards |
| setup directions and setup count | DFM | Cost (it uses them only in `cost.estimate`) |
| material designation and EN naming | Standards | Drawing (except a title block that disagrees with the model) |
| the model breaking the blueprint (envelope, material, sizes) | the owner in this table | Drawing: it judges the drawing against the model only |
| envelope and bounding box | Assembly | DFM, Cost |
| fastener length, grip and tool access | Assembly | Standards |
| fastener designation | Standards | Assembly |
| fastener count and variety | Cost | Assembly |

A critic that sees a **critical** problem in a topic it doesn't own adds one `info` flag
`<persona>.handoff` naming the owner, but only if that owner is not listed in `also_running`.
