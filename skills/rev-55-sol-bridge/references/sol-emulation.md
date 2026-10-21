# GPT-5.5 Control Harness

Use this only for hard, ambiguous, resumed, or repeatedly failing reversing work. It cannot reproduce GPT-5.6 Sol's weights; it reduces avoidable 5.5 errors through explicit phase control and independent verification.

## Phase Lock

Only one phase may drive the next deep action:

1. `triage`: inventory and find candidate sinks
2. `slice`: isolate one check/data/trace window
3. `model`: build a forward model, interpreter, extractor, hook, or oracle
4. `recover`: derive the candidate input/artifact/key
5. `verify`: test the original target and supporting checkpoints
6. `review`: assume the candidate is wrong and search for one fatal flaw
7. `blocked`: record an external/runtime/policy blocker

Change phase only when its output artifact exists or a recorded falsifier forces a pivot. Do not mix fresh discovery into `verify` or defend the candidate during `review`.

## Compact State

Use `work/rev-state.json` or a per-challenge file:

```json
{
  "phase": "slice",
  "challenge": "",
  "artifacts": [],
  "observed": [],
  "lane": "",
  "lane_reason": "",
  "hypotheses": [
    {"claim": "", "evidence": [], "falsifier": "", "status": "untested"}
  ],
  "current_slice": "",
  "candidate": "",
  "verification": {"command": "", "result": "", "blocker": ""},
  "next_action": ""
}
```

Rules:

- `observed` contains only tool/file/trace/runtime facts.
- Keep at most three hypotheses; each needs a cheapest falsifier.
- Keep paths, offsets, hashes, widths, and checkpoints; remove prose.
- If `next_action` is attempted twice without decisive evidence, change the action, lane, or phase.
- On resume, read state, current solve artifact, and last verification output before any large source/decompiler file.

## Error-Reduction Controls

### Context gate

Search and read bounded windows. Do not load whole decompiler output, giant logs, old narratives, or the deep playbook before the lane requires them.

### Evidence labels

Keep facts, inferences, and guesses distinct. Formatting conventions, flag prefixes, primitive names, branch reachability, and field meanings remain guesses until supported.

### First-bad-checkpoint rule

For transforms, VMs, parsers, and simulations, place checkpoints at stable boundaries. On mismatch, fix the first divergent checkpoint rather than rethinking later stages.

### Forward-before-inverse rule

Do not invert decompiler prose. Implement the shortest executable forward slice and match a table, trace, dump, or target first.

### Timed dynamic fallback

If static recovery cannot expose the decisive buffer after two meaningful slices, hook/trace the closest compare, decrypt, unpack, or verifier boundary.

### Bounded search rule

Before brute force, SAT/SMT, `angr`, or native emulation, record the exact domain/slice and why it is tractable. If the bound is not explicit, the search is not ready.

### Environment accounting

Keep sandbox, OS, missing runtime, network, account, and policy failures separate from model/solver failures. Never label an environment-blocked candidate as accepted.

## Builder and Reviewer Passes

Use two passes for nontrivial or fragile solves.

### Builder

Produce the smallest solve artifact and verification attempt. Optimize for progress; avoid narrative.

### Reviewer

Read only state, the solve artifact, target metadata, and verification output. Check:

- offsets, lengths, numeric widths, signedness, endianness
- permutation/round/RNG consumption order
- parser/runtime semantics and dependency assumptions
- whether the success branch is reachable on the unmodified original
- whether a local dummy/sentinel or visible decoy was mistaken for the event answer
- whether the reported wrapper and transcription come from evidence

If a fatal flaw appears, return to the first phase capable of fixing it. Do not start a second full solve from scratch.

## Failure Router

| Symptom | Diagnosis | Cheapest next move |
| --- | --- | --- |
| many reads, no decisive model | context drift | state snapshot; choose sink and one slice |
| candidate rejected | width/order/state bug | find first bad forward checkpoint |
| compare bytes unavailable | runtime-only data | dump operands closer to sink |
| VM/path explosion | overmodeled dispatcher | trace one path; test branch dependence |
| SMT/angr timeout | slice/domain too wide | split checkpoints, use algebra/MITM/DFA |
| hook output noisy twice | observation point too early/wrong | move to compare/decrypt boundary |
| artifact parses but token is unclear | transcription ambiguity | preserve raw; independent parse/view |
| original cannot execute | environment blocker | record exact error/hash; build strongest supporting replay |
| Daybreak/TAC intervention | access/policy blocker | preserve state; continue only with an available authorized model |

## Deep Playbook Handoff

Pull `rev-final-fastpath` only after the lane is selected and this harness has a concrete missing technique. Copy the chosen tactic and its required evidence into state, then return to one phase and one lane. Do not follow several deep-playbook lanes simultaneously.

## Final Gate

Do not claim solved unless all applicable items exist:

- concrete answer/input/artifact or reproducible solver/hook/extractor
- exact reproduction command
- strongest original verification result, or an explicit blocker
- forward/checkpoint support for nontrivial recovery
- one-sentence remaining uncertainty
