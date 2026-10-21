---
name: rev-55-sol-bridge
description: High-throughput controller for authorized offline or local reversing CTF work. Use for "$rev-55-sol-bridge", "ctf-speed", "리버싱 스킬", "빠른 리버싱", or requests to solve one or many rev challenges quickly with verified answers. Optimized to stabilize GPT-5.5 and also usable with GPT-5.6 Sol.
---

# Rev 5.5 Sol Bridge

## Local execution base

Load and follow `ctf-wsl-toolchain` before local triage or tool execution. This bridge controls reversing scope, lane choice, pivots, and verification; `ctf-wsl-toolchain` controls WSL entry, installed binaries, Python runtime, paths, and tool discovery. Do not ask the user to operate the toolchain.

Maximize verified reversing solves per hour. This skill controls scope, triage, lane choice, pivots, scratch state, and verification. It does not make GPT-5.5 equal to GPT-5.6 Sol.

`rev-final-fastpath` remains the deep reversing playbook. Do not duplicate or replace it. Load it only after this bridge has selected a lane and the compact lane card is insufficient.

## Quick Invocation

Treat any of these as `ctf-speed` unless the user selects another mode:

- `$rev-55-sol-bridge`
- `ctf-speed`
- `리버싱 스킬`
- `리버싱 스킬 써줘`
- `빠른 리버싱`
- `브릿지 켜줘`
- `rev bridge`
- `문제 라인업`
- `문제 라업`
- `lineup`
- `5.6처럼`
- `성능 끌어올려`
- `극한`
- `hard boost`

The defaults already mean: prioritize verified answers, skip writeups, and avoid external submission. If the supplied folder contains multiple challenge directories, use `ctf-sweep` automatically.

## Non-Negotiables

1. Work only within the user-authorized CTF, wargame, crackme, or local target scope.
2. A candidate is solved only after the strongest available verification. A patch used for observation is not a solve.
3. Preserve original artifacts. Put incomplete probes, dumps, and temporary patches under `work/rev/<challenge>/` unless the user chose another scratch path.
4. Do not submit to a scoreboard or remote service beyond necessary challenge interaction unless the user explicitly asks.
5. Never infer a flag wrapper, success state, primitive, architecture, or input format without evidence.
6. Screenshots are evidence aids, not solve verification. Do not let screenshot work expose session tokens, private account data, or delay a solve beyond the user's speed goal. Flag or submitted-answer screenshots are allowed only when the user explicitly says they are needed for a lineup/report.

## Execution Kernel

Use this loop. Keep triage broad and cheap; keep deep analysis to one lane.

### 1. Establish the boundary

- Identify the challenge root, target artifacts, prompt constraints, architecture/runtime, and whether execution or network interaction is authorized.
- Run deterministic triage once when useful:
  `python C:/Users/ogh00/.codex/skills/rev-55-sol-bridge/scripts/triage.py <challenge-root>`
- For hard, stalled, or user-requested max/5.6-like GPT-5.5 runs, initialize the hard-case workspace before the second deep action:
  `python C:/Users/ogh00/.codex/skills/rev-55-sol-bridge/scripts/hardcase_init.py <challenge-root>`
  Then read [Hard reverse boost](references/hard-rev-boost.md).
- Execute the target once only when safe and cheap. Capture input shape, exact output, required files, sleeps/crashes, and whether original verification is possible.
- Existing writeups or solvers may be used only when the user permits local artifacts, the task is corpus learning/review, or they are supplied as part of the challenge.
- When the user asks for a problem lineup, contest board, ranking, or solve queue and a CTF UI/browser page is available, capture the screenshots needed to identify the lineup before deep solving: challenge list/scoreboard view, selected challenge detail/prompt, artifact/download area, and solved/flag evidence when the user explicitly allows it. Save them under `work/ctf-screenshots/<event-or-date>/` with descriptive filenames and record the paths in the board or final output. If screenshot access is unavailable or would reveal account/session/private-team data, record the reason and continue solving.

### 2. Find the success sink

Work backward from the cheapest concrete sink: success/failure branch, compare call, return code, artifact parser, service predicate, or verifier state. Do not tour the whole binary.

Choose one deep lane:

| Evidence | Lane | Read |
| --- | --- | --- |
| compares, fixed targets, transforms, managed code, VM, packing, oracle, equations | core | [Core lane cards](references/core-lanes.md) |
| stages, overlays, games, visual signals, executable farms, mass VMs, services/firmware | scale/system | [Scale and system cards](references/scale-and-systems.md) |

Cheap independent inventory commands may run together. Static, dynamic, symbolic, and emulation strategies must not all deepen at once.

### 3. Choose by information gain

Prefer the action most likely to produce a decisive artifact per unit cost:

1. supplied source, script, verifier, or high-level payload
2. success sink, compare caller, constants, imports, and cross-references
3. compare/decrypt operand dump or one concrete trace
4. smallest forward model and checkpoints
5. bounded algebra, MITM, brute force, or sliced SMT
6. broad decompilation, whole-program symbolic execution, or full native emulation only with evidence that cheaper routes cannot work

Every deep action should produce at least one of: a new observed fact, sink address, target buffer, instruction grammar, model checkpoint, extracted artifact, candidate input, or verification result. After two actions without one, pivot instead of repeating the lane.

### 4. Build the smallest solve artifact

Produce the minimum reusable object that reaches the solve contract: input, answer, `solve.py`, `ex.py`, extractor, hook/dump tool, recovered artifact, or intended patch.

- For transforms, prove a forward byte/round/checkpoint before inversion.
- For VMs, recover only the validation path and freeze a concrete path only after proving its branch choices are input-independent.
- For hidden runtime data, move the observation point closer to compare/decrypt rather than widening static analysis.
- For symbolic work, write explicit variables, widths, endianness, constraints, and bounds before invoking a solver.
- For large corpora, learn the stable contract from distant samples, then replace repeated native execution with a compact extractor/interpreter.

### 5. Verify and stop

Use the strongest available check:

1. original binary/service accepts or returns success/flag
2. recovered artifact parses/opens and contains unambiguous expected data
3. forward replay exactly reproduces the original target/final state
4. independent samples agree with the recovered model or oracle

Record the exact command and exact result. Add a negative test only when success could be accidental, patched, cached, or ambiguous. Once the solve contract is met, stop analyzing and move to the next challenge.

## State Without Overhead

Do not force a disk state file for a green task solved in one short pass. Create `work/rev-state.json` or a per-challenge state file when any is true:

- the task is hard, packed, stateful, multi-stage, or a mass corpus
- analysis has crossed two deep tool actions
- the lane changes
- the task is parked, resumed, or likely to cross context compaction
- multiple challenges are being swept

Keep only: observed facts, active lane and reason, up to three hypotheses with cheapest falsifiers, current artifact/candidate, next action, verification, and blocker. Never store narrative notes that can be regenerated.

For hard, ambiguous, resumed, or repeatedly failing work, read [5.5 control harness](references/sol-emulation.md).

## Modes

| Mode | Trigger | Rule |
| --- | --- | --- |
| `ctf-speed` | default single challenge | one strong verification, no writeup |
| `ctf-sweep` | multiple challenges | read [CTF throughput](references/ctf-speed.md), rank by expected verified solves/time, park early |
| `hard` | no anchor, packed/stateful/custom VM/large target, repeated failure | create state and read the control harness |
| `hard-boost` | user asks for max/5.6-like GPT-5.5 behavior, or a hard task stalls | run `scripts/hardcase_init.py`, read [Hard reverse boost](references/hard-rev-boost.md), then keep one phase and one lane |
| `review` | candidate or solver already exists | audit it before searching for a different answer |
| `corpus-learning` | user requests reusable local writeback | write beside originals only after regeneration and strongest verification |
| `blocked` | missing artifact/server/runtime/account/policy | record the exact blocker and cheapest reproducible next check |

## Pulling the Deep Playbook

Read `C:/Users/ogh00/.codex/skills/rev-final-fastpath/SKILL.md` only when:

- a lane is selected but its bridge card lacks the needed technique
- evidence matches a specialized local corpus pattern
- a mass VM, overlay/journal, Unity/visual, boot payload, executable farm, or service-composition case needs deeper mechanics
- the user explicitly asks for both skills

Read only the directly relevant section of `rev-final-fastpath/references/local-corpus-patterns.md`. Bring the chosen tactic back into the compact state and continue with one active lane.

## Fast Pivots

- no sink from strings/imports -> trace compare/call boundaries
- hidden compare target -> dump operands
- forward model mismatch -> isolate the first bad checkpoint; fix width/order/state there
- VM explosion -> trace one path, test branch dependence, model only reached opcodes
- SMT or `angr` explosion -> slice tighter, split checkpoints, or use algebra/MITM
- packed/staged loader noise -> dump immediately after unpack/decrypt and switch to the payload
- huge repeated corpus -> sample distant instances, normalize grammar, stop native batch execution
- artifact/token ambiguity -> preserve raw bytes/hash and obtain an independent parse or view
- unavailable original runtime -> mark verification blocked; do not convert a supporting check into acceptance

## Output

During `ctf-speed`, report only:

```text
[challenge] solved: <answer-or-artifact>
verification: <exact command/result>
files: <solver/hook/extractor/artifact paths>
uncertainty: <none or one material caveat>
```

For unsolved work, report the exact blocker, strongest evidence, saved state path, and one cheapest next action. For skill/model comparisons, read [Quality evaluation](references/quality-eval.md) and use `scripts/compare_evals.py`; do not claim model equality from one challenge.
