#!/usr/bin/env python3
"""Bounded, non-executing first-pass inventory for authorized reversing tasks."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import string
import subprocess
import zipfile
from pathlib import Path


SKIP_DIRS = {".git", ".svn", "__pycache__", ".idea", ".vscode", "work"}
HIGH_VALUE_NAMES = {
    "solve.py", "solver.py", "ex.py", "hook.c", "writeup.md", "readme.md",
}
SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".h", ".cs", ".java", ".go", ".rs"}
MANAGED_SUFFIXES = {".py", ".pyc", ".js", ".mjs", ".wasm", ".jar", ".class", ".apk", ".dex", ".lua", ".ps1", ".bat", ".sh"}
BINARY_SUFFIXES = {".exe", ".dll", ".so", ".dylib", ".elf", ".bin", ""}

ANCHOR_PATTERNS = {
    "success": re.compile(r"(?i)(?<![a-z0-9_])(flag|correct|success|accepted|congratulations?|well done|win)(?![a-z0-9_])"),
    "failure": re.compile(r"(?i)(?<![a-z0-9_])(wrong|incorrect|failed|failure|rejected|denied|nope|bad key)(?![a-z0-9_])"),
    "compare": re.compile(r"(?i)(?<![a-z0-9_])(strcmp|strncmp|memcmp|strcasecmp|compareto|sequenceequal)(?![a-z0-9_])"),
    "anti_debug": re.compile(r"(?i)(?<![a-z0-9_])(ptrace|isdebuggerpresent|checkremotedebuggerpresent|ntqueryinformationprocess|sigaction)(?![a-z0-9_])"),
    "runtime_stage": re.compile(r"(?i)(?<![a-z0-9_])(mmap|mprotect|virtualprotect|memfd_create|fexecve|dlopen|dlsym|loadlibrary)(?![a-z0-9_])"),
    "vm": re.compile(r"(?i)(?<![a-z0-9_])(opcode|bytecode|dispatcher|vm_execute|virtual machine)(?![a-z0-9_])"),
    "transform": re.compile(r"(?i)(?<![a-z0-9_])(base64|aes|chacha|salsa|sha256|zlib|sbox|crc32)(?![a-z0-9_])"),
    "artifact": re.compile(r"(?i)(app\.asar|/proc/self/exe|overlay|stage2|journal|qreloc|breloc)"),
    "oracle": re.compile(r"(?i)(?<![a-z0-9_])(oracle|license|score|timing|prefix)(?![a-z0-9_])"),
}


def sha256(path: Path, limit_bytes: int) -> str | None:
    if path.stat().st_size > limit_bytes:
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sampled_bytes(path: Path, sample_bytes: int) -> bytes:
    size = path.stat().st_size
    with path.open("rb") as handle:
        if size <= sample_bytes * 2:
            return handle.read()
        head = handle.read(sample_bytes)
        handle.seek(max(0, size - sample_bytes))
        tail = handle.read(sample_bytes)
    return head + b"\x00" + tail


def extract_ascii(data: bytes, minimum: int = 4) -> list[str]:
    allowed = set(bytes(string.printable, "ascii")) - {0x0B, 0x0C}
    output: list[str] = []
    buffer = bytearray()
    for value in data:
        if value in allowed and value not in (0x09, 0x0A, 0x0D):
            buffer.append(value)
        else:
            if len(buffer) >= minimum:
                output.append(buffer.decode("ascii", "replace"))
            buffer.clear()
    if len(buffer) >= minimum:
        output.append(buffer.decode("ascii", "replace"))
    return output


def extract_utf16le(data: bytes, minimum: int = 4) -> list[str]:
    output: list[str] = []
    pattern = re.compile(rb"(?:[\x20-\x7e]\x00){%d,}" % minimum)
    for match in pattern.finditer(data):
        output.append(match.group(0).decode("utf-16le", "replace"))
    return output


def detect_kind(data: bytes, suffix: str) -> str:
    if data.startswith(b"\x7fELF"):
        return "ELF"
    if data.startswith(b"MZ"):
        return "PE"
    if data[:4] in {b"\xfe\xed\xfa\xce", b"\xce\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"\xcf\xfa\xed\xfe", b"\xca\xfe\xba\xbe"}:
        return "Mach-O"
    if data.startswith(b"\x00asm"):
        return "WASM"
    if data.startswith(b"PK\x03\x04"):
        return "ZIP/container"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "PNG"
    if data.startswith(b"%PDF"):
        return "PDF"
    if data.startswith(b"\x1f\x8b"):
        return "gzip"
    if data.startswith(b"SQLite format 3\x00"):
        return "SQLite"
    if suffix in SOURCE_SUFFIXES:
        return "source"
    if suffix in MANAGED_SUFFIXES:
        return "managed/script"
    return "data"


def priority(path: Path) -> tuple[int, int, str]:
    name = path.name.lower()
    suffix = path.suffix.lower()
    score = 0
    if name in HIGH_VALUE_NAMES:
        score += 100
    if suffix in SOURCE_SUFFIXES:
        score += 60
    if suffix in MANAGED_SUFFIXES:
        score += 45
    if suffix in BINARY_SUFFIXES:
        score += 35
    if suffix in {".zip", ".tar", ".gz", ".7z", ".img", ".iso", ".png", ".dat"}:
        score += 20
    return (-score, path.stat().st_size, path.as_posix())


def archive_summary(path: Path) -> dict | None:
    try:
        if not zipfile.is_zipfile(path):
            return None
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            return {
                "entries": len(infos),
                "uncompressed_bytes": sum(item.file_size for item in infos),
                "names_sample": [item.filename for item in infos[:20]],
            }
    except (OSError, zipfile.BadZipFile):
        return None


def inspect_file(path: Path, root: Path, sample_limit: int, hash_limit: int) -> dict:
    rel = path.relative_to(root).as_posix()
    data = sampled_bytes(path, sample_limit)
    strings_found = extract_ascii(data) + extract_utf16le(data)
    deduped = list(dict.fromkeys(strings_found))
    searchable = "\n".join(deduped)
    anchors = {
        label: sorted({match.group(0) for match in pattern.finditer(searchable)})[:8]
        for label, pattern in ANCHOR_PATTERNS.items()
    }
    anchors = {label: hits for label, hits in anchors.items() if hits}
    result = {
        "path": rel,
        "size": path.stat().st_size,
        "sha256": sha256(path, hash_limit),
        "kind": detect_kind(data[:32], path.suffix.lower()),
        "magic_hex": data[:16].hex(),
        "anchors": anchors,
        "strings_sample": deduped[:16],
    }
    archive = archive_summary(path)
    if archive:
        result["archive"] = archive
    return result


def run_tool(argv: list[str], cwd: Path) -> str | None:
    if not shutil.which(argv[0]):
        return None
    try:
        process = subprocess.run(
            argv,
            cwd=str(cwd),
            text=True,
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=8,
            check=False,
        )
    except Exception as exc:  # deterministic diagnostic, not target execution
        return f"error: {exc}"
    return process.stdout[:8000]


def route_hints(inspected: list[dict]) -> list[str]:
    hints: set[str] = set()
    for item in inspected:
        kind = item["kind"]
        anchors = item["anchors"]
        if kind in {"source", "managed/script", "WASM"}:
            hints.add("managed-or-source-first")
        if "compare" in anchors or ("success" in anchors and "failure" in anchors):
            hints.add("direct-compare-sink")
        if "transform" in anchors:
            hints.add("inverse-transform")
        runtime_hits = {value.lower() for value in anchors.get("runtime_stage", [])}
        if "anti_debug" in anchors or runtime_hits.intersection({"memfd_create", "fexecve"}):
            hints.add("dynamic-observation")
        if "vm" in anchors:
            hints.add("custom-vm")
        if kind in {"ZIP/container", "PNG", "PDF", "gzip"} or "artifact" in anchors:
            hints.add("artifact-or-stage")
        if "oracle" in anchors:
            hints.add("oracle")
    return sorted(hints)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", help="challenge file or directory")
    parser.add_argument("--json", action="store_true", help="emit JSON only")
    parser.add_argument("--max-files", type=int, default=200, help="maximum prioritized files to inspect")
    parser.add_argument("--sample-kib", type=int, default=512, help="bytes sampled from each file's head and tail")
    parser.add_argument("--hash-limit-mib", type=int, default=64, help="skip full hashes above this size")
    parser.add_argument("--include-work", action="store_true", help="include scratch work directories")
    args = parser.parse_args()

    target = Path(args.path).resolve()
    if not target.exists():
        parser.error(f"path does not exist: {target}")
    root = target if target.is_dir() else target.parent

    all_files: list[Path] = [target] if target.is_file() else []
    if target.is_dir():
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            relative_parts = path.relative_to(root).parts[:-1]
            if not args.include_work and any(part.lower() in SKIP_DIRS for part in relative_parts):
                continue
            all_files.append(path)
    all_files.sort(key=priority)

    inspected = [
        inspect_file(
            path,
            root,
            sample_limit=max(1, args.sample_kib) * 1024,
            hash_limit=max(1, args.hash_limit_mib) * 1024 * 1024,
        )
        for path in all_files[: max(1, args.max_files)]
    ]

    suffix_counts: dict[str, int] = {}
    for path in all_files:
        suffix = path.suffix.lower() or "<none>"
        suffix_counts[suffix] = suffix_counts.get(suffix, 0) + 1

    native = next((item for item in inspected if item["kind"] in {"ELF", "PE", "Mach-O"}), None)
    native_path = root / native["path"] if native else None
    tool_output: dict[str, str | None] = {"file": None, "header": None}
    if native_path:
        tool_output["file"] = run_tool(["file", str(native_path)], root)
        if native["kind"] == "ELF":
            tool_output["header"] = run_tool(["readelf", "-h", str(native_path)], root)
        else:
            tool_output["header"] = run_tool(["objdump", "-f", str(native_path)], root)

    report = {
        "root": str(target),
        "file_count": len(all_files),
        "inspected_count": len(inspected),
        "total_bytes": sum(path.stat().st_size for path in all_files),
        "suffix_counts": dict(sorted(suffix_counts.items())),
        "route_hints": route_hints(inspected),
        "files": inspected,
        "tool_output": tool_output,
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0

    print(f"root: {report['root']}")
    print(f"files: {report['file_count']} inspected: {report['inspected_count']} total_bytes: {report['total_bytes']}")
    print(f"suffix_counts: {report['suffix_counts']}")
    print(f"route_hints: {', '.join(report['route_hints']) or 'none'}")
    for item in inspected[:40]:
        print()
        hash_text = item["sha256"] or "skipped(size-limit)"
        print(f"{item['path']} kind={item['kind']} size={item['size']} sha256={hash_text}")
        print(f"magic={item['magic_hex']}")
        if item["anchors"]:
            print(f"anchors={json.dumps(item['anchors'], ensure_ascii=False)}")
        if "archive" in item:
            print(f"archive={json.dumps(item['archive'], ensure_ascii=False)}")
        for value in item["strings_sample"][:8]:
            print(f"  {value[:180]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
