# Workspace layout

Paths in this file are relative to the engineer's project folder (the session's working directory).

```text
blueprint/
├── rules.md                  (optional) house design rules for the whole project. Every critic applies them
└── <slug>/                   one design folder per part or assembly that the engineer works on
    ├── blueprint.md          the spec: lite at first, grows as constraints are stated
    ├── changelog.md          every model and spec change, with its reason
    ├── snapshots/NN[-tag].json
    ├── redlines/NN[-tag]/<persona>.json   (+ summary.md after a converge run)
    ├── checkpoints/NN/       model files as they were before change NN
    └── shots/
```

`NN` is the blueprint's `iteration` (two digits), bumped by every model-changing pass: an
everyday edit or a converge pass. Read-only runs reuse the current `NN` with a tag (`03-review`,
`03-b`) and never overwrite an existing file.

## Finding the design folder

1. The engineer names one ("the bracket"): use the folder whose title or slug matches.
2. Otherwise take the CAD connector's active document. Use the folder whose blueprint `model:` list
   contains that file path (compare case-insensitively, with normalised slashes).
3. None found: the slug is the document's file name in kebab-case (`Mounting Plate.SLDPRT` becomes
   `mounting-plate`). Create the folder lazily, on the first write (record, snapshot or spec),
   never just for a question.
4. Assemblies get their own folder. A part blueprint may name its parent assembly in its
   frontmatter (`parent: <slug>`), and an assembly blueprint lists its part slugs (`parts: [...]`).
   Assembly-level constraints live in the assembly blueprint.

## Lite vs full blueprint

- **Lite** (created by everyday work): frontmatter (`title`, `connector`, `model`, and `process`
  / `material` if known) plus only the sections that have content, typically §3 Constraints, §9
  Red Line register and §11 History. Sections appear as they are needed.
- **Full** (created by `init`): every section of `docs/blueprint-template.md` in the plugin.

A lite blueprint is upgraded to full in place by `init`, never replaced. Everything already
recorded stays.
