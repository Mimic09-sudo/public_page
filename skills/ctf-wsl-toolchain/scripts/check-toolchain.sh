#!/usr/bin/env bash
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"

for command_name in ctf-python pwndbg gdb-gef r2 analyzeHeadless sage; do
    command_path="$(command -v "$command_name")"
    printf '%-18s %s\n' "$command_name" "$command_path"
done

ctf-python -c 'import pwn, angr, z3, capstone, unicorn; print("ctf-python imports OK")'
sage -c 'assert factor(123456) == factor(2**6 * 3 * 643); print("SageMath OK")'
