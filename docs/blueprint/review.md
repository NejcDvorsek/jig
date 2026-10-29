# Blueprint capability: Review

Snapshot the model and run Red Line critics on it. The orchestrator (after an edit, or for a review
request), `redline` and `converge` all review this way and differ only in what they pass in. Paths
are relative to the plugin root.

## Inputs (from the caller)

- `personas`: the critics to run. Apply the Cost gate (`docs/impact-map.md` §1) unless the
  engineer named Cost.
- `tag`: names the files. `NN` after a model change, `NN-review` for a read-only review, with a
  suffix `-b`, `-c` … if that name exists. Never overwrite a file.
- `focus` (optional): the changed targets plus one line on what changed, or what the engineer asked
  about. None means a full review (`scope: review`).
- `baseline` (optional): the snapshot from before the change.
- `full` (optional): read every section, as converge does.

## Steps

1. **Snapshot** to `blueprint/<slug>/snapshots/<tag>.json`. Sections are the union of
   `docs/impact-map.md` §3 for the personas (all of them with `full`).
   - If Edit left a seed `snapshots/NN-edit.json` that holds every needed section, write it out as
     the snapshot yourself (`partial`, `sections`, `focus`, `seeded_from`) and spawn nothing.
   - Otherwise spawn `cad-snapshot` with `blueprint`, `out`, `sections`, `focus`, and `seed` if one
     exists: it reads only what the seed lacks. On `ERROR`, stop and report.
2. **Critics.** Spawn them all **in one message, in parallel** (`jig:redline-<persona>`), each with
   only:
   ```
   blueprint: blueprint/<slug>/blueprint.md
   snapshot: <snapshot path>
   iteration: <tag>
   also_running: <the other critics in this run>
   focus: <focus>                     (if given)
   baseline: <before snapshot>        (if given)
   rules: blueprint/rules.md          (if it exists)
   ```
   Pass nothing else: no register, no earlier flags.
3. **Save** each result to `blueprint/<slug>/redlines/<tag>/<persona>.json`. Invalid JSON gets one
   retry. After that, save the raw text as `<persona>.error.txt` and report the persona as
   **failed**, never as clean.
4. Hand the flags to **Triage** (`docs/blueprint/triage.md`).
