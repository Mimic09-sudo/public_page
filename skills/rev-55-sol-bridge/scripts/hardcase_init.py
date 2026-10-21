#!/usr/bin/env python3
"""Create a compact hard-case workspace for a reversing challenge."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path


SKIP_DIRS = {".git", ".svn", "__pycache__", ".idea", ".vscode", "work"}
HIGH_VALUE_NAMES = {
    "solve.py",
    "solver.py",
    "ex.py",
    "keygen.py",
    "hook.c",
    "writeup.md",
    "readme.md",
    "solution.md",
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip("-._")
    return slug.lower() or "challenge"


def iter_files(root: Path, limit: int) -> list[Path]:
    if root.is_file():
        return [root]
    files: list[Path] = []
    for item in root.rglob("*"):
        if not item.is_file():
            continue
        rel_dirs = item.relative_to(root).parts[:-1]
        if any(part.lower() in SKIP_DIRS for part in rel_dirs):
            continue
        files.append(item)
        if len(files) >= limit:
            break
    return files


def sha256_prefix(path: Path, max_bytes: int) -> str:
    digest = hashlib.sha256()
    read_total = 0
    with path.open("rb") as handle:
        while read_total < max_bytes:
            chunk = handle.read(min(1024 * 1024, max_bytes - read_total))
            if not chunk:
                break
            digest.update(chunk)
            read_total += len(chunk)
    suffix = "" if path.stat().st_size <= max_bytes else f":first-{max_bytes}"
    return digest.hexdigest() + suffix


def classify(path: Path) -> str:
    try:
        head = path.read_bytes()[:16]
    except OSError:
        return "unreadable"
    if head.startswith(b"\x7fELF"):
        return "ELF"
    if head.startswith(b"MZ"):
        return "PE"
    if head[:4] in {
        b"\xfe\xed\xfa\xce",
        b"\xce\xfa\xed\xfe",
        b"\xfe\xed\xfa\xcf",
        b"\xcf\xfa\xed\xfe",
        b"\xca\xfe\xba\xbe",
    }:
        return "Mach-O"
    if head.startswith(b"\x00asm"):
        return "WASM"
    if head.startswith(b"PK\x03\x04"):
        return "ZIP"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "PNG"
    if head.startswith(b"%PDF"):
        return "PDF"
    suffix = path.suffix.lower()
    if suffix in {".py", ".js", ".mjs", ".lua", ".ps1", ".bat", ".sh"}:
        return "script"
    if suffix in {".c", ".cc", ".cpp", ".h", ".cs", ".java", ".go", ".rs"}:
        return "source"
    return "data"


def inventory(root: Path, limit: int) -> list[dict]:
    rows = []
    for path in iter_files(root, limit):
        rel = path.name if root.is_file() else path.relative_to(root).as_posix()
        try:
            size = path.stat().st_size
            digest = sha256_prefix(path, 64 * 1024 * 1024)
            kind = classify(path)
        except OSError as exc:
            size = -1
            digest = f"error:{exc}"
            kind = "unreadable"
        rows.append(
            {
                "path": rel,
                "size": size,
                "kind": kind,
                "sha256": digest,
                "high_value": path.name.lower() in HIGH_VALUE_NAMES,
            }
        )
    rows.sort(key=lambda row: (not row["high_value"], row["kind"], row["path"]))
    return rows


def write_if_absent(path: Path, text: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("challenge_root", help="challenge file or directory")
    parser.add_argument("--scratch", help="scratch directory to create")
    parser.add_argument("--name", help="challenge name override")
    parser.add_argument("--max-files", type=int, default=200)
    args = parser.parse_args()

    challenge = Path(args.challenge_root).resolve()
    if not challenge.exists():
        parser.error(f"path does not exist: {challenge}")

    name = slugify(args.name or challenge.stem if challenge.is_file() else args.name or challenge.name)
    scratch = Path(args.scratch).resolve() if args.scratch else Path.cwd() / "work" / "rev" / name
    scratch.mkdir(parents=True, exist_ok=True)

    inv = inventory(challenge, max(1, args.max_files))
    now = int(time.time())
    state = {
        "phase": "triage",
        "challenge": name,
        "challenge_root": str(challenge),
        "created_unix": now,
        "artifacts": [str(challenge / row["path"]) if challenge.is_dir() else str(challenge) for row in inv[:20]],
        "observed": [
            f"{row['path']} kind={row['kind']} size={row['size']} sha256={row['sha256']}"
            for row in inv[:20]
        ],
        "lane": "",
        "lane_reason": "",
        "hypotheses": [
            {
                "claim": "",
                "evidence": [],
                "falsifier": "",
                "status": "untested",
            }
        ],
        "current_slice": "",
        "candidate": "",
        "verification": {"command": "", "result": "", "blocker": ""},
        "next_action": "Run bounded triage, choose one success sink, and write the first decisive slice.",
    }

    written = []
    state_path = scratch / "rev-state.json"
    if not state_path.exists():
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8", newline="\n")
        written.append(str(state_path))

    inventory_path = scratch / "inventory.json"
    if not inventory_path.exists():
        inventory_path.write_text(json.dumps({"challenge": str(challenge), "files": inv}, indent=2), encoding="utf-8", newline="\n")
        written.append(str(inventory_path))

    review_text = """# Hard Reverse Review Gate

Use this before calling the challenge solved.

- The answer/input/artifact comes from evidence, not wrapper guessing.
- Offsets, lengths, signedness, endianness, and widths were checked.
- The forward model has at least one checkpoint against original bytes, trace, or compare target.
- The solver/decryptor regenerates the candidate from the original artifacts.
- Original verification was run, or the runtime blocker is exact and reproducible.
- A negative test was run if the success path could be accidental, patched, cached, or ambiguous.
- If blocked, final output names one cheapest next action.
"""
    if write_if_absent(scratch / "review-gate.md", review_text):
        written.append(str(scratch / "review-gate.md"))

    final_text = """[challenge] unsolved
answer_or_artifact: none
verification: not run
files: none
uncertainty: not analyzed
next_action: run triage and select one lane
"""
    if write_if_absent(scratch / "final.txt", final_text):
        written.append(str(scratch / "final.txt"))

    print(json.dumps({"scratch": str(scratch), "written": written, "state": str(state_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
