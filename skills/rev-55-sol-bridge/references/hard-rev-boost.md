# Hard Reverse Boost

Use this when the user asks to push GPT-5.5 as close as practical to a stronger reversing model, or when a single hard challenge is likely to exceed one short pass. This does not reproduce GPT-5.6 Sol's weights. It reduces avoidable failures: context drift, whole-binary tours, premature crypto/VM claims, unbounded search, wrapper guessing, and unverified solves.

## Entry Conditions

Use this reference when any item is true:

- the user asks for 5.6-like, max, extreme, hard, or fastest-many-solves behavior on GPT-5.5
- the target is packed, stateful, custom-VM, multi-stage, Mach-O/mobile/firmware, large, or previously stalled
- two meaningful actions did not produce a new sink, target buffer, model checkpoint, candidate, or verifier result
- a solved-looking answer depends on a fragile transcription, runtime-only data, or unsupported environment

## Bootstrap

Create a hard-case scratch pad before the second deep action:

```text
python C:/Users/ogh00/.codex/skills/rev-55-sol-bridge/scripts/hardcase_init.py <challenge-root>
```

If the user supplied a different scratch directory, pass `--scratch <dir>`. The script creates:

- `rev-state.json`: phase, observations, hypotheses, current slice, candidate, verification, next action
- `inventory.json`: bounded file inventory with hashes and kinds
- `review-gate.md`: final anti-mistake checklist
- `final.txt`: compact final output template

Do not treat the generated state as truth. It is a forcing function. Replace guesses with evidence as soon as tool output exists.

## 5.5 Control Rules

Keep exactly one active phase:

- `triage`: identify files, runtime, input shape, and likely sinks
- `slice`: isolate one verifier, decryptor, dispatcher, artifact parser, or compare window
- `model`: implement the smallest forward model, hook, extractor, emulator, or oracle
- `recover`: derive the candidate input, key, artifact, or answer
- `verify`: run the strongest original or supporting check
- `review`: assume the candidate is wrong and find one fatal flaw
- `blocked`: record the external/runtime/tool blocker and cheapest next check

Do not mix phases. For example, do not keep reading new code while verifying a candidate, and do not defend a candidate during review.

## Decisive Artifact Rule

Every deep action must produce at least one concrete artifact:

- sink address or function name
- exact compare/decrypt buffer
- trace at the nearest useful boundary
- instruction grammar or reached VM opcodes
- forward-model checkpoint
- extracted stage or recovered file
- candidate input/key/artifact
- verification command and result

If two consecutive actions fail to produce one, pivot the lane or park the task.

## Builder Pass

The builder pass optimizes for a minimal working solve:

1. Run `triage.py` once unless an equivalent inventory already exists.
2. Choose one lane from evidence, not from vibes.
3. Find the success sink or the highest-level verifier first.
4. Build the smallest reproducible artifact: `solve.py`, `ex.py`, extractor, hook, interpreter, patch-for-observation, or recovered file.
5. Put all scratch under the hard-case work directory.

When a lane needs deeper mechanics, read only the relevant `rev-final-fastpath` lane or local-corpus pattern, then return to this state file. Do not load multiple deep lanes at once.

## Reviewer Pass

Before final output, read only:

- `rev-state.json`
- the produced solver/decryptor/hook/extractor
- target metadata needed to check offsets and runtime
- verification output
- `review-gate.md`

Check these failure classes:

- wrong width, signedness, endian, index order, or length
- decompiler artifact treated as real behavior
- guessed flag wrapper or transcription
- patched success branch mistaken for an accepted original input
- local dummy/sentinel mistaken for event flag
- unsupported runtime reported as model failure
- broad brute force, SMT, or emulation launched without a recorded bound

If a fatal flaw appears, return to the earliest phase capable of fixing it. Do not start a second whole solve.

## Fast Environment Pack

Use existing local tools first. Install or create shared tooling only when it directly unlocks the chosen lane and all active runs get the same tool access.

Useful Python packages by lane:

- native static: `lief`, `capstone`, `keystone-engine`
- symbolic/math: `z3-solver`, `sympy`
- crypto/archive: `pycryptodome`, `construct`
- managed/script: decompiler-specific tools already present in the workspace

Do not spend contest time building a perfect toolchain if a narrower hook, dump, parser, or model can expose the decisive buffer.

## Stop Conditions

Stop and report solved when the strongest available verification passes.

Stop and park when:

- original runtime is unavailable and no supporting replay can be built quickly
- a required server, artifact, account, or policy permission is missing
- two deep actions after a pivot still produce no decisive artifact
- the next step is a broad toolchain build unrelated to the chosen slice

For parked tasks, record one cheapest next action. Parking is a throughput decision, not a proof that the challenge is impossible.
