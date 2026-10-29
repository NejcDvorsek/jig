# Blueprint capability: Spec

Keep `blueprint/<slug>/blueprint.md` true to what the engineer wants. Paths are relative to the
plugin root.

## Capturing constraints from everyday requests (always on)

Every request is scanned for **stated intent**: a statement about what the design must or should
be, beyond the one-off change.

| Engineer says | Record as |
|---|---|
| "must", "has to", "needs to", "always", "never", "is required", a number with a reason | `hard` CON or REQ |
| "prefer", "ideally", "try to", "should" | `soft` CON |
| a one-off instruction ("make this hole 10 mm") | nothing in the spec, only the changelog |
| a one-off instruction with a reason ("make it 10 mm so an M10 bolt fits") | the reason: `CON: holes accept M10 (hard)`. The size itself goes to the changelog |
| a quantity or price ("we need 200 a year", "it's a one-off prototype", "must stay under €40") | frontmatter `quantity` / `cost_target` (a one-off prototype is `quantity: 1`), plus a `hard` CON for a price limit |

Rules:
- Quote the engineer's words in the row's source column, with the date.
- Requirements are measurable demands (load, life, mass). Constraints are limits on the solution
  (envelope, process, fastener standard). When unsure, use CON.
- **Conflicts:** if the new statement contradicts an existing row, don't overwrite it. Show both
  rows and ask which wins. Then mark the loser `superseded by <id>`.
- Duplicates: if the statement repeats an existing row, leave the row as it is.
- House-wide rules ("we never use M3 here") belong in `blueprint/rules.md`. Ask once whether the
  engineer means this part or all parts.
- Every recorded row is listed in the orchestrator's plan as *"Will record: …"*, so the engineer sees
  it and can say "drop that".
- A new constraint can already be violated by the model. After recording it, the orchestrator checks
  it, by Inspect or by the critic its category maps to.

## Creating a lite blueprint

On the first write for a design that has none, create `blueprint/<slug>/blueprint.md` with
frontmatter (`schema`, `title`, `connector`, `model`, `status: lite`, `iteration: 0`, and
`process` / `material` if known from the model or request) and only the sections that have content.
See `docs/workspace.md`. Also create `changelog.md` with a `# Changelog` heading.

## Full spec (design mode)

Used by `init`. Fill every section of `docs/blueprint-template.md`:
- §1 the request quoted word for word
- §2 measurable requirements in SI, with conversions shown and a verification method each
- §3 constraints, `hard` when stated and `soft` for your defaults
- §4 the handful of defining parameters, sized with a first §7 hand calc
- §5 interfaces, §6 standards (defaults ISO 2768-mK, ISO 286, ISO 965, first-angle projection,
  marked as defaults)
- §8 DEC-001: the concept and the rejected alternatives
- §10 the assumptions you made. A question is **blocking** only if a wrong guess would change the
  concept (process, load direction, mounting interface, quantity)

## Engineer edits to the file

The engineer may edit `blueprint.md` by hand at any time. Before any write, compare it against the
last §11 History row. Engineer edits always win and are never reverted.
