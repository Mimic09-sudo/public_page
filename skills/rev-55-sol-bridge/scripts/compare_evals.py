#!/usr/bin/env python3
"""Aggregate reversing eval manifests around verified solve throughput."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path


def load_manifest(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"manifest must be a JSON object: {path}")
    data["_path"] = str(path)
    return data


def profile_name(run: dict) -> str:
    explicit = run.get("profile")
    if explicit:
        return str(explicit)
    parts = [run.get("model"), run.get("reasoning_effort"), run.get("skill_revision")]
    return "/".join(str(part) for part in parts if part not in (None, "")) or "unspecified"


def is_blocked(run: dict) -> bool:
    return bool(run.get("blocker_type")) or str(run.get("status", "")).lower() == "blocked"


def is_verified_solve(run: dict) -> bool:
    return (
        str(run.get("status", "")).lower() == "solved"
        and bool(run.get("original_verification"))
        and not bool(run.get("false_positive"))
        and not is_blocked(run)
    )


def numeric(run: dict, key: str) -> float | None:
    value = run.get(key)
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def median_or_none(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def aggregate(runs: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for run in runs:
        grouped[profile_name(run)].append(run)

    rows: list[dict] = []
    for profile, items in grouped.items():
        eligible = [run for run in items if not is_blocked(run)]
        solved = [run for run in eligible if is_verified_solve(run)]
        wall = [numeric(run, "wall_seconds") for run in eligible]
        wall = [value for value in wall if value is not None and value >= 0]
        verified_times = [
            numeric(run, "time_to_verified_seconds")
            if numeric(run, "time_to_verified_seconds") is not None
            else numeric(run, "wall_seconds")
            for run in solved
        ]
        verified_times = [value for value in verified_times if value is not None and value >= 0]
        solved_tokens = [numeric(run, "tokens") for run in solved]
        solved_tokens = [value for value in solved_tokens if value is not None and value >= 0]
        total_hours = sum(wall) / 3600 if wall else 0.0

        rows.append(
            {
                "profile": profile,
                "runs": len(items),
                "eligible": len(eligible),
                "blocked": len(items) - len(eligible),
                "solved": len(solved),
                "solve_rate_pct": (len(solved) / len(eligible) * 100) if eligible else None,
                "solves_per_hour": (len(solved) / total_hours) if total_hours > 0 else None,
                "median_verified_seconds": median_or_none(verified_times),
                "median_tokens_per_solve": median_or_none(solved_tokens),
                "false_positives": sum(bool(run.get("false_positive")) for run in items),
                "lane_switches": sum(int(numeric(run, "lane_switches") or 0) for run in eligible),
            }
        )
    rows.sort(
        key=lambda row: (
            -(row["solve_rate_pct"] if row["solve_rate_pct"] is not None else -1),
            -(row["solves_per_hour"] if row["solves_per_hour"] is not None else -1),
            row["profile"],
        )
    )
    return rows


def fmt(value: object, decimals: int = 1) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.{decimals}f}"
    return str(value)


def print_summary(rows: list[dict]) -> None:
    print("| profile | runs | eligible | blocked | solved | solve_rate | solves/hour | median_verified_s | median_tokens/solve | false_pos | lane_switches |")
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for row in rows:
        rate = "" if row["solve_rate_pct"] is None else f"{row['solve_rate_pct']:.1f}%"
        print(
            f"| {row['profile']} | {row['runs']} | {row['eligible']} | {row['blocked']} | "
            f"{row['solved']} | {rate} | {fmt(row['solves_per_hour'], 2)} | "
            f"{fmt(row['median_verified_seconds'])} | {fmt(row['median_tokens_per_solve'], 0)} | "
            f"{row['false_positives']} | {row['lane_switches']} |"
        )


def print_details(runs: list[dict]) -> None:
    print()
    print("| run | challenge | profile | status | verified | blocker | wall_s | tokens |")
    print("| --- | --- | --- | --- | --- | --- | ---: | ---: |")
    for run in sorted(runs, key=lambda item: (str(item.get("challenge", "")), str(item.get("run_id", item["_path"])))):
        print(
            f"| {run.get('run_id', run['_path'])} | {run.get('challenge', '')} | {profile_name(run)} | "
            f"{run.get('status', '')} | {'yes' if is_verified_solve(run) else 'no'} | "
            f"{run.get('blocker_type', '')} | {fmt(numeric(run, 'wall_seconds'))} | {fmt(numeric(run, 'tokens'), 0)} |"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", nargs="*", help="JSON run manifests")
    parser.add_argument("--details", action="store_true", help="also print individual runs")
    parser.add_argument("--json", action="store_true", help="emit aggregate JSON")
    args = parser.parse_args()

    if not args.manifest:
        parser.print_usage()
        print("minimum fields: run_id, challenge, model/profile, status, wall_seconds")
        print("a solve also requires non-empty original_verification")
        return 0

    try:
        runs = [load_manifest(Path(path)) for path in args.manifest]
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

    rows = aggregate(runs)
    if args.json:
        print(json.dumps({"profiles": rows}, indent=2, ensure_ascii=False))
        return 0

    print_summary(rows)
    if args.details:
        print_details(runs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
