---
name: doctor
description: "Check that Jig can run here. Checks uv/uvx, the bundled CAD connector MCP servers, whether the CAD program is running and reachable, which connector capabilities are live, duplicate server registrations, and the project's design folders. Use when setting up, or when a connector call fails."
---

# Jig · doctor

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. Paths outside `blueprint/` are relative to it.

Run these checks and report one table (check · result · fix):

1. **uv:** `uvx --version`. If it's missing, install uv (on Windows:
   `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`), then
   restart Claude Code. The bundled connectors start through `uvx`.
2. **Connectors:** for each folder in `connectors/`, read `CONNECTOR.md` and check whether its status
   tool is available (match by short name, see `docs/connector-contract.md`).
   - Not available: the server failed to start. Suggest `/mcp` to see its error, and the connector's
     self-test command.
   - Available under more than one prefix (e.g. the user's own `solidworks` registration and the
     plugin's): this is fine, and the user's own is used. Removing one avoids confusion.
3. **CAD reachable:** call each available status tool. Report the CAD version, server version and
   active document. If the program isn't running, the fix is the "Start" line in its `CONNECTOR.md`.
4. **Live capabilities:** compare the adapter's operation table with the tools actually available.
   List the operations that are `partial` or `none`, any new tools that fill a gap (the server is
   under active development), and which Red Line checks each gap limits.
5. **Project:** list the design folders under `blueprint/` with their title, status (lite / draft /
   converging / converged / stopped) and iteration, plus whether `blueprint/rules.md` exists and
   whether each blueprint's `model:` files exist.

End with the single next step that fits: just ask for what you need (the orchestrator handles it),
`/jig:init "<intent>"` for a new design, or `/jig:converge` to continue one.
