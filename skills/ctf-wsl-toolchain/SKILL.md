---
name: ctf-wsl-toolchain
description: Base execution layer for every authorized local CTF, wargame, or crackme solve on this laptop. Load it alongside any pwn, reversing, crypto, forensics, stego, web, mobile, game, or network solver skill so Codex uses the preinstalled Ubuntu-24.04 WSL tools directly; do not use for unrelated external targets.
---

# CTF WSL Toolchain

## Base-layer contract

- Treat this skill as the common local execution substrate for every CTF-solving skill on this laptop. It should activate automatically; the user should not need to mention it separately.
- When a domain skill such as `pwn-general`, `rev-final-fastpath`, `rev-55-sol-bridge`, or `rev-game-hacking` also applies, that skill controls the solve methodology while this skill controls the runtime, installed tools, paths, virtual environments, and host-to-WSL execution.
- Do not replace or weaken the domain skill's verification rules, solve contract, or artifact handling.

## Operating principle

- Perform the analysis and run the tools yourself in WSL. Do not turn the workflow into instructions for the user unless they explicitly ask for commands or a tutorial.
- Use distro `Ubuntu-24.04`. The normal Linux user is `mimic09`.
- Stay within the user-provided CTF, wargame, local artifact, or otherwise authorized target scope. Do not infer permission to scan unrelated external systems.
- Prefer existing tools over reinstalling them. Install an additional package only when the challenge genuinely requires it, then verify the installation.

## Select the execution path

Determine the host once at the start of the task:

- In a Windows-hosted Codex session, enter the distro through `wsl.exe`.
- In a VS Code Remote WSL or other Codex session already running inside Ubuntu WSL, execute Linux tools directly. Never nest another WSL session.

### From Windows

For a direct executable with simple arguments, call WSL without an extra shell:

```powershell
wsl.exe -d Ubuntu-24.04 -- <tool> <args>
```

For commands that need shell expansion, PATH initialization, pipelines, or redirection:

```powershell
wsl.exe -d Ubuntu-24.04 -- bash -lc '<command>'
```

PowerShell can corrupt nested Bash quoting and `$variables`. For any nontrivial workflow, create a task-local `.sh` file with `apply_patch`, invoke it as `/mnt/c/.../script.sh`, and keep generated challenge artifacts in the task workspace. Never embed a disclosed password in a command, script, or file; administrator access is available through `wsl.exe -d Ubuntu-24.04 -u root -- ...` when truly needed.

Translate unfamiliar Windows workspace paths with `wsl.exe -d Ubuntu-24.04 -- wslpath -a -u <windows-path>` instead of guessing the mount path.

### From inside WSL

Run tools and task-local shell scripts directly. Use Linux workspace paths as-is. If privileged system changes are essential and noninteractive elevation is unavailable, report the exact blocker; never store or replay a disclosed password.

Set this PATH inside non-login scripts when user-installed commands are needed:

```bash
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
```

## Canonical runtimes and entry points

- General Python/CTF packages: `ctf-python` or `/home/mimic09/ctf-tools/python-venv/bin/python`
- pwndbg: `pwndbg`; GEF alternative: `gdb-gef`
- Ghidra headless: `analyzeHeadless` or `/opt/ghidra/support/analyzeHeadless`
- SageMath: `sage`
- General tools root: `/home/mimic09/ctf-tools`
- Wordlists: `/home/mimic09/ctf-tools/SecLists`
- Payload references: `/home/mimic09/ctf-tools/PayloadsAllTheThings`
- Separate proxy runtime: `mitmproxy`, `mitmdump`, and `mitmweb`

Use `ctf-python` for pwntools, angr, z3, Crypto, Volatility, Scapy, Capstone, Unicorn, Keystone, Frida, capa, and FLOSS imports. Do not install those packages into the system Python.

Read [references/tool-map.md](references/tool-map.md) when choosing among installed tools or locating a specialized command. Run `scripts/check-toolchain.ps1` from Windows or `bash scripts/check-toolchain.sh` from WSL only when the environment appears unavailable or after modifying the toolchain; do not spend time health-checking every challenge.

## Workflow

1. Inspect the supplied artifact and identify its format before choosing a specialist tool.
2. Preserve the original and perform patches or extraction in a task-local working directory. From Windows, reference the artifact through its translated `/mnt/c/...` path; from WSL, use its native path.
3. Start with the cheapest discriminating checks (`file`, hashes, metadata, strings, headers, protections), then escalate to static analysis, emulation, debugging, symbolic execution, or brute force as evidence warrants.
4. Automate repeatable work in scripts and verify the candidate solution against the original challenge binary, service, archive, or checker.
5. Return the recovered flag or concrete result with a concise explanation and saved solver when useful. Do not make the user operate the toolchain for you.

## Failure handling

- If a command is missing, consult the tool map and check `$HOME/.local/bin`, `/usr/local/bin`, and the relevant virtual environment before installing a duplicate.
- If Python dependencies conflict, keep the general CTF and mitmproxy virtual environments separate.
- If GUI access is unnecessary, prefer headless and CLI modes. Use a GUI only when it materially improves the analysis.
- If a task requires privileged packet capture or system changes, scope the command narrowly and use WSL root directly rather than asking for or replaying a password.
