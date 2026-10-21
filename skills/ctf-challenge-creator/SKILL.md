---
name: ctf-challenge-creator
description: Create, scaffold, validate, package, and document CTF challenges with a mandatory authoring workflow. Use when Codex is asked to make or design a CTF problem/challenge, convert a challenge-production spec into repeatable procedure, create challenge folders/templates, define intended solve paths, write solvers, run build/solve validation, perform release audits, or produce author reports/writeups for categories such as rev, web, pwn, crypto, forensics, or misc.
---

# CTF Challenge Creator

## Core Rules

- Treat logs and reports as mandatory for every CTF challenge, not optional HTB-only artifacts.
- Keep `private/` and `dist/` strictly separated; never place flags, seeds, keys, or author-only notes in public release files unless exposure is the intentional puzzle mechanic.
- Prefer safe local CTF behavior: no real file destruction, propagation, persistence, credential stuffing, or attacks against third-party targets.
- Build the smallest reproducible challenge that matches the stated category, difficulty, and intended learning objective.
- Always validate final challenge solvability: build from clean state, run the distributed artifact, run the solver against `dist/` only, confirm the recovered answer is accepted by the challenge, run release audit, and record all logs.
- Record failed designs and discarded assumptions in `timeline.md` when they affect the final design.

## Standard Workflow

1. Define scope: challenge name, category, difficulty, flag format, target audience, release type, and explicit forbidden behavior.
2. Design the intended path: learning objective, required observations, exploit/analysis step, intermediate result, and flag recovery.
3. Scaffold the case folder and copy templates from `assets/`.
4. Implement source/build artifacts while keeping author-only material in `private/`.
5. Create or update a solver that uses only `dist/` artifacts.
6. Run build, runtime smoke test, solver validation from `dist/` only, recovered-answer acceptance test, checksum generation, and release audit; save logs under `logs/`.
7. Update `case.json`, `timeline.md`, `progress.md`, `report.md`, and `writeup.md`.
8. Summarize release readiness and unresolved risks before handing off.

## Case Folder Contract

Use this structure unless the user or existing repo has a stronger convention:

```text
cases/<challenge-name>/
  case.json
  timeline.md
  progress.md
  notes.md
  src/
  build/
  dist/
  private/
  solver/
  evidence/
  logs/
  report.md
  writeup.md
```

Mandatory outputs:

- `timeline.md`: major decisions, commands, builds, validation, release changes.
- `progress.md`: current state and next actions.
- `logs/build-*.log`: reproducible build output.
- `logs/solve-*.log`: solver validation output.
- `logs/validate-*.log`: end-to-end build/run/solve/acceptance validation output when available.
- `logs/release-audit-*.log`: public package secret/safety audit.
- `evidence/checksums.txt`: hashes for public artifacts.
- `report.md`: internal author report.
- `writeup.md`: public-safe writeup.
- `case.json`: structured knowledge record.
- `challenge.md`: mandatory challenge description file with problem statement, category, flag field, solve code reference, and solve explanation.

## Assets

Copy these templates when scaffolding a new case:

- `assets/case.template.json` -> `cases/<challenge-name>/case.json`
- `assets/progress.template.md` -> `cases/<challenge-name>/progress.md`
- `assets/timeline.template.md` -> `cases/<challenge-name>/timeline.md`
- `assets/report.template.md` -> `cases/<challenge-name>/report.md`
- `assets/writeup.template.md` -> `cases/<challenge-name>/writeup.md`
- `assets/challenge.template.md` -> `cases/<challenge-name>/challenge.md`

Create empty `notes.md` if no template is needed. Keep `challenge.md` present for every challenge; if the final flag is user-provided later, write `사용자 입력 대기` or a private reference instead of inventing a flag.

## Validation Commands

Adapt these commands to the project build system. For every finalized challenge, validation is not complete until the solver output is checked against the actual challenge artifact and any missing/unsolvable path has been ruled out:

```bash
make clean
make build 2>&1 | tee logs/build-$(date +%Y%m%d-%H%M%S).log
make release 2>&1 | tee logs/release-$(date +%Y%m%d-%H%M%S).log
python3 solver/solve.py 2>&1 | tee logs/solve-$(date +%Y%m%d-%H%M%S).log
# If the challenge is an executable/verifier, feed the recovered solver answer back into it.
# Store this as logs/validate-*.log and fail if the artifact rejects the solver answer.
sha256sum dist/* | tee evidence/checksums.txt
find dist -type f -print | sort
```

For release audits, check for accidental private material:

```bash
grep -R "SCA{" -n dist || true
grep -R "PRIVATE\|SECRET\|TOKEN\|author" -n dist || true
```

If the flag is intentionally embedded, verify it is not trivially exposed unless that is the intended difficulty.

## When More Detail Is Needed

Read `references/ctf-authoring-spec.md` when the task requires a full policy/specification, detailed playbook routing, `case.json` schema fields, report sections, event formats, or completion checklists.
