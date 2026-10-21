---
name: resume-progress-log
description: Maintain a persistent, concise recovery journal for every Codex task that uses tools, changes files, waits, or spans multiple steps. Always use alongside any other applicable skill so interrupted work can resume from verified state; skip only direct one-shot answers with no resumable work.
---

# Resume Progress Log

## Purpose

Maintain enough durable state to continue after a crash, interruption, context loss, handoff, or new session without repeating completed work. This is an execution journal, not a verbose transcript or a substitute for verification.

## Journal location and selection

- Store journals under `~/.codex/task-logs/YYYY-MM-DD/` using `<HHMMSS>-<short-slug>.md`.
- Use one journal per task. Keep its path stable for the life of the task.
- At task start, inspect recent unfinished journals only if the workspace and objective plausibly match. Resume an existing journal only when the match is unambiguous; otherwise create a new one.
- Windows and WSL on this laptop share the same task-log directory through the configured link.

## Required journal shape

Keep a compact current-state block near the top:

```markdown
# Task: <short title>

- Status: active | waiting | blocked | complete
- Started: <ISO-8601 timestamp>
- Updated: <ISO-8601 timestamp>
- Workspace: <absolute path>
- Objective: <one sentence>

## Latest checkpoint

- Completed: <verified work already done>
- Current state: <what exists or is running now>
- Next action: <one exact next step>
- Files/artifacts: <created or modified paths>
- Commands/tests: <commands and short observed results>
- Decisions/assumptions: <material choices only>
- Blockers/questions: <none or concrete blocker>

## Milestones

- <timestamp> — <concise durable event>
```

Update the current-state block in place and append only meaningful milestones. Do not let the file grow into a command transcript.

## Checkpoint timing

1. Create or resume the journal before the first material tool call or mutation.
2. Update it after each material tool batch or completed milestone.
3. Checkpoint immediately before and after a long-running, risky, destructive, privileged, or external-state action.
4. Record changed files and actual verification results after mutations.
5. If the task pauses, blocks, redirects, or receives new user input, record the exact stop point and next action before switching context when possible.
6. Before the final response, mark the journal `complete` and record the delivered outcome and strongest verification.

## Resume protocol

- Read the latest checkpoint and relevant milestone entries.
- Verify the live filesystem, processes, git state, or external state before trusting recorded completion.
- Continue from `Next action` only after that verification.
- If the journal conflicts with live state, update it with the discrepancy and follow live evidence.
- Never infer permission from a prior log entry; current user instructions and authorization still govern.

## Privacy and scope

- Never store passwords, tokens, cookies, private keys, raw credentials, or unnecessary sensitive content.
- Redact secrets and record only safe identifiers, paths, hashes, or the fact that a credential is required.
- Do not copy large outputs, source files, or full conversation text into the journal.
- Keep logs outside repositories unless the user explicitly requests repository-local project logs.
- A journal write is bookkeeping only and must not broaden the actual task.
