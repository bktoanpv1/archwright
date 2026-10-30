"""Rebuild archify diagrams for every domain package.

Layout: domains/<domain>/src/<NN>-<name>.<type>.json -> domains/<domain>/dist/<NN>-<name>.html
A domain is a folder under domains/ whose src/ holds archify sources;
folders starting with "_" or "." are skipped.

Usage (from anywhere):
    python .archify/build.py                       # every domain, every diagram
    python .archify/build.py embedded-mcu      # one domain
    python .archify/build.py embedded-mcu 02   # diagrams whose name starts with 02

Each build runs `archify finalize` (validate, deliver, strict check, browser check).
Receipts go to domains/<domain>/.receipts/<name>/ and are replaced on every build, because
they are bound to the exact HTML bytes that build produced.
Archify location: $ARCHIFY_BIN, else ~/.agents/skills/archify/bin/archify.mjs.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                      # repo root: archify resolves meta.output from here
DOMAINS = ROOT / "domains"
ARCHIFY = Path(os.environ.get("ARCHIFY_BIN",
                              Path.home() / ".agents/skills/archify/bin/archify.mjs"))


def domains():
    return sorted(d for d in DOMAINS.iterdir()
                  if d.is_dir() and d.name[0] not in "_."
                  and any((d / "src").glob("*.*.json")))


def build(domain, spec_path):
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    kind = spec["diagram_type"]
    name = spec_path.name.removesuffix(f".{kind}.json")
    label = f"{domain.name}/{name}"
    if name == spec_path.stem:
        return label, "ERROR", f"file name must end with .{kind}.json"
    html = domain / "dist" / f"{name}.html"
    expected = html.relative_to(ROOT).as_posix()
    if spec["meta"].get("output") != expected:
        return label, "ERROR", f'meta.output must be "{expected}"'

    evidence = domain / ".receipts" / name
    shutil.rmtree(evidence, ignore_errors=True)
    html.parent.mkdir(exist_ok=True)
    proc = subprocess.run(
        ["node", str(ARCHIFY), "finalize", kind, str(spec_path), str(html),
         "--quality", spec["meta"].get("quality_profile", "showcase"),
         "--out-dir", str(evidence), "--json"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    try:
        receipt = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return label, "FAIL", (proc.stderr or proc.stdout).strip()[-300:]
    status = "PASS" if proc.returncode == 0 and receipt.get("status") == "pass" else "FAIL"
    gates = " ".join(f"{g}={r}" for g, r in receipt.get("gates", {}).items())
    errors = [d["code"] for d in receipt.get("diagnostics", []) if d.get("severity") == "error"]
    return label, status, gates + (f" errors={errors}" if errors else "")


def main():
    if not ARCHIFY.is_file():
        sys.exit(f"archify not found: {ARCHIFY} (set ARCHIFY_BIN)")
    domain_arg = sys.argv[1] if len(sys.argv) > 1 else None
    prefix = sys.argv[2] if len(sys.argv) > 2 else ""

    selected = [d for d in domains() if domain_arg in (None, d.name)]
    if not selected:
        names = ", ".join(d.name for d in domains()) or "(none)"
        sys.exit(f"unknown domain '{domain_arg}'. Available: {names}")
    jobs = [(d, p) for d in selected for p in sorted((d / "src").glob("*.json"))
            if p.name.startswith(prefix)]
    if not jobs:
        sys.exit(f"no diagram matches domain={domain_arg or '*'} prefix='{prefix}'")

    results = [build(d, p) for d, p in jobs]
    for label, status, detail in results:
        print(f"[{status:5}] {label}: {detail}")
    sys.exit(0 if all(s == "PASS" for _, s, _ in results) else 1)


if __name__ == "__main__":
    main()
