"""Check Red Line outputs against the jig/flags@1 contract and print a summary.

Usage: python tests/check_flags.py <folder with <persona>.json files>
Exit code 1 if any file breaks the contract.
"""
import json
import pathlib
import sys

TOP = {"schema", "persona", "iteration", "summary", "flags"}
FLAG = {"rule", "target", "severity", "title", "evidence", "requirement", "recommendation",
        "suggested_change", "confidence", "checkable", "scope"}
SEVERITY = {"critical", "warning", "info"}
SCOPE = {"change", "pre-existing", "review"}
KINDS = {"set_dimension", "set_equation", "add_feature", "delete_feature", "set_material",
         "drawing_edit", "spec_change", "engineer_decision", "none"}


def check(path: pathlib.Path) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"not valid JSON: {exc}"]
    errors = [f"missing top-level key {k!r}" for k in sorted(TOP - data.keys())]
    if data.get("schema") != "jig/flags@1":
        errors.append(f"schema is {data.get('schema')!r}")
    persona = data.get("persona") or path.stem
    for i, flag in enumerate(data.get("flags", [])):
        where = f"flag {i} ({flag.get('rule') or flag.get('title', '?')})"
        errors += [f"{where}: missing {k!r}" for k in sorted(FLAG - flag.keys())]
        if flag.get("severity") not in SEVERITY:
            errors.append(f"{where}: severity {flag.get('severity')!r}")
        if flag.get("scope") not in SCOPE:
            errors.append(f"{where}: scope {flag.get('scope')!r}")
        if not str(flag.get("rule", "")).startswith(persona + "."):
            errors.append(f"{where}: rule should start with {persona + '.'!r}")
        kind = (flag.get("suggested_change") or {}).get("kind")
        if kind not in KINDS:
            errors.append(f"{where}: suggested_change.kind {kind!r}")
        if flag.get("checkable") is False and flag.get("severity") != "info":
            errors.append(f"{where}: checkable=false must be info")
    return errors


def main() -> int:
    folder = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    failed = False
    for path in sorted(folder.glob("*.json")):
        errors = check(path)
        data = {}
        if not errors or not errors[0].startswith("not valid JSON"):
            data = json.loads(path.read_text(encoding="utf-8"))
        counts = {s: sum(f.get("severity") == s for f in data.get("flags", [])) for s in SEVERITY}
        status = "OK  " if not errors else "FAIL"
        print(f"{status} {path.name:16} C{counts['critical']} W{counts['warning']} I{counts['info']}")
        for flag in data.get("flags", []):
            print(f"       {flag.get('severity', '?')[:4].upper():4} {flag.get('rule', '?'):40} {flag.get('target', '?')}")
        for err in errors:
            print(f"     ! {err}")
        failed |= bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
