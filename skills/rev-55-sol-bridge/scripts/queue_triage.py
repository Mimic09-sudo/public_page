#!/usr/bin/env python3
"""Rank local reversing challenge folders by expected fast-solve value."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SKIP_DIRS = {".git", ".svn", "__pycache__", ".idea", ".vscode", "work"}
SOLVE_NAMES = {"solve.py", "solver.py", "ex.py", "keygen.py", "hook.c"}
DOC_NAMES = {"writeup.md", "readme.md", "solution.md"}
SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".h", ".cs", ".java", ".go", ".rs"}
HIGH_LEVEL_SUFFIXES = {".py", ".pyc", ".js", ".mjs", ".wasm", ".jar", ".class", ".apk", ".dex", ".lua", ".ps1", ".bat", ".sh"}
HEAVY_SUFFIXES = {".i64", ".idb", ".qcow2", ".ova", ".vmdk", ".iso", ".img"}
CORPUS_WORDS = {"vm", "worker", "instance", "program", "chunk", "farm"}
HARD_WORDS = {"packed", "upx", "anti-debug", "antidebug", "obfuscated", "virtualized"}


def visible_files(path: Path, limit: int = 10000) -> list[Path]:
    files: list[Path] = []
    for item in path.rglob("*"):
        if not item.is_file():
            continue
        relative_dirs = item.relative_to(path).parts[:-1]
        if any(part.lower() in SKIP_DIRS for part in relative_dirs):
            continue
        files.append(item)
        if len(files) >= limit:
            break
    return files


def classify(path: Path) -> dict:
    files = visible_files(path)
    if not files:
        return {
            "name": path.name,
            "path": str(path),
            "status": "blocked",
            "score": -999,
            "file_count": 0,
            "total_bytes": 0,
            "reason": ["no-files"],
        }

    names = [item.name.lower() for item in files]
    suffixes = [item.suffix.lower() for item in files]
    total = sum(item.stat().st_size for item in files)
    joined_names = " ".join(names)

    score = 0
    reasons: list[str] = []

    if any(name in SOLVE_NAMES for name in names):
        score += 55
        reasons.append("existing-solve-artifact")
    if any(name in DOC_NAMES for name in names):
        score += 35
        reasons.append("existing-notes")
    if any(suffix in SOURCE_SUFFIXES for suffix in suffixes):
        score += 35
        reasons.append("source-or-decompile")
    if any(suffix in HIGH_LEVEL_SUFFIXES for suffix in suffixes):
        score += 25
        reasons.append("high-level-payload")
    if len(files) <= 4 and total <= 10 * 1024 * 1024:
        score += 15
        reasons.append("small-target")
    elif len(files) <= 12 and total <= 40 * 1024 * 1024:
        score += 7
        reasons.append("bounded-target")

    if any(suffix in HEAVY_SUFFIXES for suffix in suffixes):
        score -= 20
        reasons.append("heavy-artifact")
    if any(word in joined_names for word in HARD_WORDS):
        score -= 15
        reasons.append("packing-or-obfuscation-hint")
    corpus_hits = sum(1 for word in CORPUS_WORDS if word in joined_names)
    if len(files) > 200 or corpus_hits >= 3:
        score -= 18
        reasons.append("mass-corpus-hint")
    if len(files) > 2000:
        score -= 20
        reasons.append("very-many-files")
    if total > 512 * 1024 * 1024:
        score -= 25
        reasons.append("large-total-size")

    if score >= 35:
        status = "green"
    elif score >= 0:
        status = "yellow"
    else:
        status = "red"

    return {
        "name": path.name,
        "path": str(path),
        "status": status,
        "score": score,
        "file_count": len(files),
        "total_bytes": total,
        "reason": reasons or ["no-strong-hint"],
    }


def candidate_roots(root: Path) -> list[Path]:
    children = [item for item in root.iterdir() if item.is_dir() and item.name.lower() not in SKIP_DIRS]
    root_files = [item for item in root.iterdir() if item.is_file()]
    target_suffixes = SOURCE_SUFFIXES | HIGH_LEVEL_SUFFIXES | {".exe", ".dll", ".so", ".elf", ".bin", ".wasm", ".jar", ".apk"}
    root_has_target = any(item.name.lower() in SOLVE_NAMES or item.suffix.lower() in target_suffixes for item in root_files)
    if children and (len(children) > 1 or not root_has_target):
        return children
    return [root]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="event directory or one challenge")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        parser.error(f"path does not exist: {root}")

    rows = [classify(path) for path in candidate_roots(root)]
    order = {"green": 0, "yellow": 1, "red": 2, "blocked": 3}
    rows.sort(key=lambda row: (order[row["status"]], -row["score"], row["name"].lower()))

    if args.json:
        print(json.dumps({"root": str(root), "targets": rows}, indent=2, ensure_ascii=False))
        return 0

    print("| status | score | files | bytes | name | reason |")
    print("| --- | ---: | ---: | ---: | --- | --- |")
    for row in rows:
        print(
            f"| {row['status']} | {row['score']} | {row['file_count']} | "
            f"{row['total_bytes']} | {row['name']} | {','.join(row['reason'])} |"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
