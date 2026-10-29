---
name: redline
description: "Run a Red Line review on demand, with explicitly chosen personas (default all) on the current CAD model of a design. Takes a snapshot, runs the stateless critics in parallel, saves and shows their flags. Does not change the model. Use when the engineer explicitly asks for a red line or specific critics; for \"check this\" in everyday work the orchestrator picks the critics itself."
argument-hint: "[personas, e.g. dfm,cost] [focus: <what to look at>]"
---

# Red Line · review

Arguments: `$ARGUMENTS`. Personas default to the blueprint's `personas`, or all five, with Cost
only past the Cost gate (`docs/impact-map.md` §1). An optional `focus:` narrows the review.

**Pending reviews.** With no arguments, first look in `changelog.md` for entries marked
`Red Line: pending (…)` (changes made with "review later"). If there are any, review them all in
this one run: the personas are the union of their pending lists, and the focus is the union of
their changed targets. The baseline is the snapshot from before the first pending change, if one
exists. Afterwards, mark those entries `Red Line: done in NN-review`.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. Paths outside `blueprint/` are relative to it.

1. **Design folder:** resolve it (`docs/workspace.md`). Without a blueprint, create a lite one per
   `docs/blueprint/spec.md`, because critics need at least the model, process and material. If the
   process is unknown, ask for it in one question: DFM and Cost depend on it.
2. **Review:** follow `docs/blueprint/review.md` with tag `NN-review`, the chosen personas, and
   `focus` and `baseline` when they apply.
3. **Triage and show:** follow `docs/blueprint/triage.md` to merge the flags into the register.
   Show them critical first, and mark the fingerprints the register already knows. Record one line
   per `docs/blueprint/record.md`.
4. Offer to apply the **fix** items: that goes through the orchestrator's plan and confirm.
