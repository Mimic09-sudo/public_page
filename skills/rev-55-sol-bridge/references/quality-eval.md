# Quality Evaluation

Use this to compare skill revisions, GPT-5.5 profiles, or GPT-5.5 against GPT-5.6 Sol on authorized offline reversing tasks. The primary metric is verified solve throughput, not prose quality.

## Fair Protocol

1. Create a blind workspace containing only the prompt and original artifacts. Exclude known answers, writeups, solvers, notes, and prior state unless evaluating resume behavior.
2. Hold prompt, artifacts, sandbox, tool access, and time budget constant. Change only the model, reasoning effort, or skill revision under test.
3. Use representative task shapes, not one favorable challenge.
4. Record access/policy/environment blocks separately; exclude them from model-quality denominators but report them.
5. Count a solve only when the manifest records the strongest available original verification.
6. Do not promote a revision from a single run. Prefer repeated trials for stochastic or borderline tasks when budget permits.

Representative set:

- direct compare or reversible transform
- managed/script/bytecode or custom VM
- packed/runtime-data or dynamic dump case
- artifact/stage/visual case
- mass corpus or service composition when those are common in the user's events

## Manifest

Use one JSON file per run:

```json
{
  "run_id": "vm-tangle-gpt55-bridge-v2-01",
  "challenge": "vm-tangle",
  "profile": "gpt55-xhigh-bridge-v2",
  "model": "gpt-5.5",
  "reasoning_effort": "xhigh",
  "skill_revision": "bridge-v2",
  "status": "solved",
  "original_verification": "accepted",
  "wall_seconds": 263,
  "time_to_verified_seconds": 263,
  "tokens": 105835,
  "false_positive": false,
  "lane_switches": 1,
  "tool_errors": [],
  "blocker_type": "",
  "notes": ""
}
```

Valid blocker categories include `account`, `policy`, `sandbox`, `runtime`, `missing-artifact`, and `remote-unavailable`.

Run all calculations with:

```text
python C:/Users/ogh00/.codex/skills/rev-55-sol-bridge/scripts/compare_evals.py run1.json run2.json ...
```

## Metrics in Priority Order

1. verified solve rate on eligible runs
2. verified solves per hour
3. false-positive count
4. median time to verified answer
5. median tokens per verified solve
6. wrong-lane failures and lane switches
7. repeated large reads, tool errors, and unproductive actions

Lower token or wall time is an improvement only when verification correctness is unchanged.

## Failure Labels

Use one primary label per eligible failed run:

- wrong lane or late pivot
- context drift/repeated reads
- hallucinated primitive/format/wrapper
- forward-model width/order/state error
- missed dynamic observation point
- symbolic/path explosion before slicing
- incomplete deliverable
- missing or weak verification
- false-positive success interpretation

Keep account/policy/runtime failures out of this list and report them as blockers.

## Promotion Gate

Keep a bridge change only when representative results show at least one improvement without worse correctness:

- higher verified solve rate or solves/hour
- lower median time to verified answer
- fewer false positives or missing-verification finishes
- fewer wrong-lane or repeated-read failures
- earlier productive dynamic pivots
- lower median tokens per verified solve

Do not claim that GPT-5.5 equals GPT-5.6 Sol. Report which challenge shapes narrowed the gap, which did not, sample size, and any access blocks that prevented a fair Sol baseline.
