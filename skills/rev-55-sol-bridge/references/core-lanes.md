# Core Lane Cards

Read this after triage selects a core lane. Each card defines the first decisive artifact, the shortest route, and the pivot condition. Keep only one card active.

## Direct Compare

**Enter when:** length checks, `strcmp`/`memcmp`, byte compares, fixed constants, or many tiny validators reach success.

**First artifact:** compare sink, input length, target bytes, and compare order.

**Route:**

1. Start at the success/failure branch and identify its controlling compare.
2. Recover target bytes in logical compare order, including index writes and permutations.
3. Script extraction if the check is repeated or split across many functions.
4. Verify the reconstructed input on the original.

**Pivot:** if operands are computed or hidden at runtime, move to Dynamic Observation. If the input is transformed first, move to Inverse Transform.

## Inverse Transform

**Enter when:** XOR/add/sub/rotate/S-box/encoding/RNG/matrix/round logic produces a target buffer.

**First artifact:** exact final target plus a forward model that matches at least one byte, round, or checkpoint.

**Route:**

1. Record width, signedness, endianness, round order, and state layout.
2. Implement the smallest forward slice; compare against a table, trace, or binary result.
3. Invert in exact reverse order. Use modular subtraction, inverse rotation/permutation, modular inverse for odd multipliers, and bit propagation for XOR shifts.
4. Brute force or SMT only the smallest lossy/unknown component.
5. Forward-replay the complete candidate before original verification.

**Pivot:** first mismatch determines the repair point. Do not rewrite the whole model. If constants/state exist only at runtime, dump them.

## Managed, Script, or Bytecode

**Enter when:** .NET, Java, Python/PYC, JS/Electron, WASM, Android, Lua, shell/batch, or a high-level payload is present.

**First artifact:** the highest-level real check function, exported verifier, IPC handler, or decoded payload.

**Route:**

1. Extract/decompile the payload before native launchers or framework code.
2. Follow data from user input to the privileged or final check.
3. Reproduce interpreter-specific semantics exactly: integer width, string encoding, expansion phases, memory offsets, and return convention.
4. Emit a small reimplementation/extractor and verify against the original runtime.

**Pivot:** if the payload decrypts or generates native code, dump after generation and switch lanes.

## Custom VM

**Enter when:** a dispatcher consumes bytecode/opcodes and updates registers, stack, RAM, or verifier state.

**First artifact:** one bounded trace table containing `pc`, raw op, operand bytes, state delta, branch decision, and input position.

**Route:**

1. Recover operand grammar before naming opcodes.
2. Name semantics by observed behavior; cross-check each with a second occurrence.
3. Decode only instructions on the validation path.
4. Test whether branch choices depend on input. Freeze the path only if evidence says they do not.
5. Build a subset interpreter or checkpoint model, then invert/symbolically solve the sliced path.

**Pivot:** dispatcher/path explosion means the slice is too wide. Trace one concrete input and move closer to the verifier tail.

## Dynamic Observation

**Enter when:** packing, runtime keys, anti-debug, self-modifying/generated code, hidden compare buffers, or noisy static setup blocks progress.

**First artifact:** a hashed buffer/trace captured at the narrowest useful boundary.

**Route:**

1. Prefer compare/decrypt/unpack sinks: `strcmp`, `memcmp`, read/open, crypto finalization, `mmap`/`mprotect`, `fexecve`, or the verifier branch.
2. Capture immediately before comparison or after transformation.
3. Record address/call site, size, hash, input used, and whether a patch changed semantics.
4. Switch back to direct, inverse, artifact, or VM analysis using the dump.

**Pivot:** two noisy captures mean the hook is too early or wrong. Move closer to the sink; do not increase dump volume.

## Oracle Automation

**Enter when:** a local/authorized service leaks prefix, membership, substring, score, timing, validity, or round state.

**First artifact:** a demonstrated predicate `ask(x) -> information` with one positive/negative or distinguishable response pair.

**Route:**

1. Fix alphabet, length assumptions, query budget, timeout, retry, and cache.
2. Separate transport errors from predicate results.
3. Automate immediately with prefix growth, binary search, candidate pruning, substring assembly, or memoization.
4. Save raw evidence for the predicate and verify the final answer.

**Pivot:** unstable responses require repeated sampling and a confidence rule. If the signal disappears, stop treating it as an oracle.

## Symbolic or Math

**Enter when:** the sliced check is explicit equations, affine/modular arithmetic, a small state machine, or bounded branch conditions.

**First artifact:** named variables, exact widths/domains, equations, and one concrete forward checkpoint.

**Route:**

1. Prefer algebra, matrix inversion, CRT, RNG recovery, DFA/BFS/DP, or MITM before general SMT.
2. Use SAT/SMT only after fixing input length and evidence-backed format constraints.
3. Use `angr` only on a sliced function or controlled address interval.
4. Replay every candidate through the forward model and then the original target.

**Pivot:** timeout or path explosion means the slice/domain is too broad. Split at checkpoints, enumerate persistent state, or derive independent halves.
