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

### Fitting the sheet

Every drawing Jig makes or changes must fit its sheet: no view, dimension, callout, note or table
outside the frame or on the title block, and no view running into another (the drawing check's
`outside_frame`, `over_title_block`, `view_outside_frame`, `view_over_title_block`,
`views_overlap`, and text or leaders of one view clashing with another). A drawing with any of
these is not finished: never hand it over or record it as done.

Show as many views as the part needs and no more (ISO 128-3). Before laying out, and again when
the sheet is tight, ask of each view: does it carry a dimension, or show a feature, that no other
view does? Connectors that fit the sheet themselves say so in their result (the adapter names the
field). When it still doesn't fit, work down this list and check again after each step:

1. **Reposition.** Lay the views out again by their real size with their annotations, and move a
   stray note, table or callout into free room.
2. **Leave out what adds nothing.** The iso view first. Then a view with no dimension of its own
   that shows nothing new, e.g. the side view of a flat plate: give its one size on another view or
   in a note.
3. **Combine.** A section in place of the full view it cuts; a detail view for one crowded region
   instead of a larger scale for the whole part; a half view of a symmetric part; dimensions moved
   to the view that shows the feature best, so that another view can go.
4. **Larger sheet.** The next ISO size at the same scale (A4, A3, A2, A1). Don't shrink the scale
   to make room: text and arrows don't shrink with it, so dimensions crowd.
5. **Ask.** Past A1, or when a view the shop needs would have to go, ask the engineer (a second
   sheet, or another split of views) as a §10 question.

Steps 1, 4 and leaving out the iso view only move things or change the sheet size: do them without
a new confirmation. Leaving out or replacing any other view changes what the drawing shows: put it
in the plan with its reason. Record what was left out, combined or resized, e.g. *"A3 at 1:2, iso
left out, side view replaced by section A-A."*

## Restoring

"Undo that" or "go back": close the model files in the CAD program (for the engineer's own open
documents, say so in the plan first), copy `checkpoints/NN/` over them, and reopen **only** the
ones the engineer had open. Then Record the restore as its own entry.
