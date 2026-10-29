# Blueprint capability: Edit

Change the CAD model through the connector, with a checkpoint before and a check after every write.
Paths are relative to the plugin root.

The engineer has **already confirmed** the plan (see the orchestrator), or has explicitly waived the
confirm ("just do it"). Never write without one of the two.

## Before the first write

1. Read the connector adapter `connectors/<name>/CONNECTOR.md`, and the server's own modelling
   guide if it has one (e.g. MCP resource `solidworks://guide`), once per session.
2. **Guards.** Do not touch a `locked` PAR, an `overridden` decision, or delete or reorder an
   engineer-owned feature, and do not break a `hard` constraint. If the plan needs to, stop and ask.
   This should have been caught at planning.
3. **Checkpoint.** Save the document, then copy every file in the blueprint's `model:` list to
   `blueprint/<slug>/checkpoints/NN/`, where `NN` is the iteration about to start. If the document has
   never been saved, ask for a path. If saving fails (the file is read-only or locked by PDM), stop
   and ask.

## Each change

1. Prefer, in this order: `set_equation` / `set_dimension` on an existing value, then adding a
   feature, then deleting or reordering a feature.
2. Before calling, write down the **expected effect** (Δvolume / Δmass / bbox, or the read-back value).
3. Apply it, then compare the returned or read-back values with the expectation. Rebuild errors
   count as failure.
4. On a mismatch or failure: undo (restore the old value, or delete the feature just added), try
   at most one alternative, then stop and report with the connector's error text.
5. If a PAR is bound to the value, update its §4 value (and the binding, if the dimension id
   changed).

## After the last change

- **Keep your readings.** If critics are planned, write what you read **after the last write** as
  a seed snapshot `blueprint/<slug>/snapshots/NN-edit.json` (`docs/snapshot-schema.md`, *Seeded
  snapshots*): `core` (the final `features`, `dimensions`, `mass`, `bbox` read-back), plus any other
  planned section you read in full along the way (holes, interference, clearances). Raw readings only,
  with no judgement. Drop anything read before a later write.
- Save the document. Don't close anything yet: the review may still need it (the orchestrator's
  Finish step closes it).
- If any changed value feeds a §7 hand calculation or a §2 requirement, recompute it and update
  the requirement's status. A requirement that turns to `not met` is reported like a critical flag.
- Hand over to **Record**.

## Drawings

A drawing edit (`drawing_edit` / `set_tolerance` in the adapter) follows the same rules: it is in the
confirmed plan, the checkpoint includes the drawing file, and every change is read back (the
annotation's shown text). Prefer changes that stay linked to the model (re-imported callouts, a
tolerance on a model dimension) over typed text, which freezes. A tolerance set on a model dimension
changes the part: count it as a model change. Run the connector's drawing check afterwards. New
problems from your edit get fixed or reported.

## Restoring

"Undo that" or "go back": close the model files in the CAD program (for the engineer's own open
documents, say so in the plan first), copy `checkpoints/NN/` over them, and reopen **only** the
ones the engineer had open. Then Record the restore as its own entry.
