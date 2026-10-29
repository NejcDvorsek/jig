# Blueprint capability: Inspect

Read the model to answer a question or to prepare an edit. This capability **never writes**:
not to the model, and not to the blueprint (folders are created lazily by other capabilities).

Paths are relative to the plugin root.

## Answering a question

1. Choose the smallest read that answers it, using the connector's adapter
   (`connectors/<name>/CONNECTOR.md`). Typical reads:
   - "how thick / how heavy / how big": mass, bbox, wall thickness
   - "what holes / what thread": faces plus features plus dimensions
   - "does it clash / clearance": interference, distance
   - "what did I change / why": the design folder's `changelog.md` and blueprint §8, not the model
2. Call those tools directly in the main session when the answer takes three or fewer reads. For a
   broader question ("summarise this part"), spawn the `cad-snapshot` agent with only the needed
   `sections` and answer from its snapshot.
3. Answer with the values, their units and where they came from ("min wall 2.4 mm, from
   check_printability at a 3 mm threshold"). If the connector can't give it, say so, and name what
   could (a drawing, a measurement in the CAD program).
4. If the answer shows a likely problem (a wall below the process minimum, a hole that is off a
   standard size), say so in one line and offer a focused review. Don't run critics uninvited.

## Preparing an edit

Find the targets and their current values before planning:
- the feature(s), dimension id(s) and current values the change touches
- whether each target is a `locked` PAR, bound to a requirement, engineer-owned, or on an interface
  (blueprint §4, §5, DEC-000)
- the change categories from `docs/impact-map.md` §1

If a target can't be identified unambiguously (two similar holes, an unnamed sketch), list the
candidates with their locations and ask. Do not guess which feature the engineer meant.
