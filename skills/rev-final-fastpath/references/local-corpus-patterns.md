# Local Corpus Pattern Playbooks

Use this reference only when concrete evidence matches one of these shapes. These playbooks were distilled from solved and partially solved reversing corpora; they are not permission to assume a technique without anchors.

## Contents

- [Keep Huge Artifacts Searchable](#keep-huge-artifacts-searchable)
- [Fingerprint Standard Primitives](#fingerprint-standard-primitives)
- [Extract and Invert Instruction Chains](#extract-and-invert-instruction-chains)
- [Solve Stateful Per-Position Verifiers](#solve-stateful-per-position-verifiers)
- [Freeze Input-Independent VM Paths](#freeze-input-independent-vm-paths)
- [Reverse Batch Shared-Library Chains](#reverse-batch-shared-library-chains)
- [Reverse Embedded Executable Farms](#reverse-embedded-executable-farms)
- [Forge Checked Record Formats](#forge-checked-record-formats)
- [Normalize Data Structures Before Solving](#normalize-data-structures-before-solving)
- [Respect Script Expansion Phases](#respect-script-expansion-phases)
- [Lift Boolean Circuits into Finite-State Machines](#lift-boolean-circuits-into-finite-state-machines)
- [Invert Exact Matrices and UI Semantics](#invert-exact-matrices-and-ui-semantics)
- [Recover Temporal Visual Signals](#recover-temporal-visual-signals)
- [Mirror Continuous Simulations](#mirror-continuous-simulations)
- [Peel Managed and Layered Containers](#peel-managed-and-layered-containers)
- [Model Sparse Destruction Before Recovering Large Data](#model-sparse-destruction-before-recovering-large-data)
- [Recover Unity Scene Data Channels](#recover-unity-scene-data-channels)
- [Peel Boot Images Before Reversing Loaders](#peel-boot-images-before-reversing-loaders)
- [Separate Local Service Boundaries](#separate-local-service-boundaries)
- [Verification Matrix](#verification-matrix)

## Keep Huge Artifacts Searchable

Treat multi-megabyte or multi-gigabyte decompiler output as a database, not a document.

1. Record file size, target architecture, imports, strings, and adjacent solver artifacts.
2. Search stable anchors: compare calls, success/failure text, crypto constants, table sizes, loader APIs, file magic, and exported worker names.
3. Extract only the relevant function or bounded line window into scratch space.
4. Confirm decompiler types, shifts, widths, and intrinsics against disassembly or a runtime sample.
5. Never let generated CRT/framework code dominate the analysis budget.

## Fingerprint Standard Primitives

Recognize the skeleton before translating expressions:

- `998244353`, primitive roots, bit reversal, and butterfly loops indicate NTT. If `target = NTT(input) * NTT(kernel)`, divide pointwise and inverse-transform; reject zero denominators or handle them as constrained coefficients.
- A 256-byte evolving permutation with two indices indicates RC4-like KSA/PRGA. Preserve every swap and replay state before inverting any custom post-layer.
- AES, DES, SM4, TEA/XTEA, CRC, FNV, and carryless-multiply code should be identified by round topology, table shape, constants, or instructions, not names alone.
- Deterministically generated S-boxes, round constants, IVs, or keys are recoverable by replaying the seed schedule. Do not freeze one runtime dump when regeneration is simpler and verifiable.
- For architecture-specific crypto intrinsics, a tiny native harness or faithful emulator may be safer than manually translating compiler-specific vector expressions. Cross-check one intermediate block.

Always separate `standard primitive` from `custom key/table/seed/post-XOR`. Invert the complete wrapper in exact reverse order and forward-check the result.

## Extract and Invert Instruction Chains

Use this when a verifier compiles hundreds or thousands of straight-line operations over independent fixed-width words.

1. Parse disassembly into semantic operations and split the graph by output word. Preserve instruction width, signedness, and rotate count.
2. Cancel operations in reverse order. Use modular subtraction for addition, reverse rotations, and the modular inverse of an odd multiplier modulo `2^w`.
3. Invert `x ^ (x >> k)` by recovering high bits first or by repeated doubling shifts; use the symmetric low-to-high method for left shifts.
4. When an operation loses information, isolate only that step for bounded search or SMT instead of symbolically executing the whole function.
5. Forward-run every recovered word through the parsed chain and compare the exact target array.

For periodic lane layouts, transpose records by lane before solving. Infer the period from repeating structure, score per-lane rotate/XOR parameters against hard format constraints, and reassemble in original order.

## Solve Stateful Per-Position Verifiers

Use this when bytecode or a loop transforms one candidate byte, performs a local check, then mutates rolling state.

1. Split execution at the per-position `CHECK` boundary.
2. Snapshot only the live state: registers, accumulators, key index, and relevant memory.
3. Enumerate the allowed alphabet for the current position from the snapshot.
4. Keep candidates that satisfy the local check; require uniqueness when the format should determine one byte.
5. Commit the winning transition and continue with its updated state.
6. Verify the final state and replay the entire original verifier.

This is cheaper and more reliable than symbolic execution of the full VM when each check localizes one byte.

## Freeze Input-Independent VM Paths

Use this when a custom VM has a noisy or disguised dispatcher but one concrete trace reaches the check without input-dependent control flow.

1. Record one complete trace as `(pc, opcode, operands, branch outcome)` and taint every branch condition from candidate input.
2. Prove the visited branch decisions are input-independent for the accepted input shape. If any decision is tainted, keep that branch symbolic or enumerate only its bounded alternatives.
3. Replay the fixed trace in a compact symbolic model over the actual input words; omit unreachable handlers and fake object/framework plumbing.
4. If a long VM transform is affine in the input despite nonlinear-looking code, execute the program on a zero buffer to recover its fixed XOR mask, then confirm with basis or random probes.
5. Try the fast inverse first. If challenge instances differ near the final loop, start symbolic execution at that loop with the pre-loop state already concrete.
6. Replay the candidate through the original VM or service.

## Reverse Batch Shared-Library Chains

Use when a controller loads many `.so`/DLL files and calls the same exported function.

1. Recover the exact load/call order from the controller, trace, or table. Preserve duplicates and numeric ordering.
2. Inspect first, middle, and last workers. Determine the fixed ABI, buffer width, and whether workers mutate in place or return a value.
3. Cluster implementations by structural anchors instead of full disassembly equality. Examples include add/xor/rotate patterns and AES-ECB, DES-ECB, or RC4 call shapes.
4. Extract only per-worker constants: immediate, rotation count, key bytes, IV, or post-XOR mask.
5. Build one forward and inverse function per family. Apply inverse workers in reverse controller order.
6. Forward-run the recovered input through all workers and compare the controller target exactly.

If thousands of workers exist, disassemble functions programmatically and cache a manifest. Manually validate at least one worker per family.

## Reverse Embedded Executable Farms

Use when a parent stores many ELF/PE children in a table or blob and launches them with `memfd_create`/`fexecve`, process creation, or a custom loader.

1. Locate the container table: offset, length, key/material, child ID, and alignment.
2. Extract or dump every child once. Record hashes before modification.
3. Derive the child's argument/input and exit-code/output contract from a few samples.
4. Search stable per-child offsets only after confirming identical layout across distant samples.
5. Recover per-child targets or keys statically where possible. If behavior classification is required, probe a small controlled set and cache results.
6. Reconstruct the ordered answer and verify representative children plus the parent.

Do not launch a large unknown executable corpus merely to inventory it. Prefer parsing, disassembly, sandboxed sampling, and a compact semantic model.

## Forge Checked Record Formats

Use when the verifier parses records and later feeds decoded fields to a command, query, path, or success sink.

1. Write the format as `magic | lengths | seed/id | payload | checksum` with exact endianness and terminators.
2. List parser invariants: sort order, unique fields, bounds, CRC/hash domain, padding, and record count.
3. Trace semantic use after parsing. Construct the desired decoded payload rather than corrupting unrelated fields.
4. Mirror the target PRNG implementation and consumption count exactly. Python's RNG is not a substitute for libc `rand()` or a custom xorshift.
5. For time-derived seeds, calculate a bounded candidate window from observed clock behavior and reconnect deterministically.
6. Locally reparse and revalidate every forged record before submission.

## Normalize Data Structures Before Solving

UI and container structures often hide a simple permutation.

- Convert circular linked-list bits into an indexed bit vector; express rotate/reverse/invert steps as permutations.
- Convert boards, tiles, sprites, or packed glyph rows into a matrix/bitstream before reasoning about characters.
- Convert trace handler addresses to canonical opcode names using image base plus handler offset.
- Convert known plaintext/ciphertext samples of a modular affine transform into `y = W*x + b`; solve `W,b`, invert `W`, and test a held-out pair.

The normalized representation must preserve index order, bit order, integer width, and wraparound.

## Respect Script Expansion Phases

Use this when a batch or shell challenge reconstructs commands from variables, substring
operations, delayed expansion, or `eval`-like features.

1. Parse assignments and substitutions according to the target interpreter. Preserve quoting,
   case rules, negative indices, and the distinction between parse-time and execution-time
   expansion.
2. Reconstruct the command after exactly one expansion phase. Do not recursively expand newly
   generated `%NAME%` or `$NAME` syntax unless the script explicitly invokes a second parser,
   `CALL`, `eval`, delayed expansion, or an equivalent mechanism.
3. Separate the hidden comparison value from a reachable accepted input. A reconstructed condition
   can reveal the intended answer while remaining impossible to satisfy in the original parse phase.
4. Run the original interpreter with the recovered environment or argument and record whether the
   success branch is actually reachable. Report interpreter quirks instead of silently treating an
   embedded literal as an accepted input.

## Lift Boolean Circuits into Finite-State Machines

Use this when a verifier is implemented as gates, latches, flip-flops, or large generated Boolean
expressions over a small persistent state.

1. Identify state elements, reset state, input bit order, clock/phase order, and the final accepted
   state. For JK flip-flops preserve `Q' = (J & ~Q) | (Q & ~K)` and pair every J/K function correctly.
2. If combinational functions are pure but their decompilation is unwieldy, evaluate only those
   bounded functions over every state/input combination. Do not execute unrelated `main`, I/O, or
   success code.
3. Convert `k` Boolean state elements into a DFA with at most `2^k` states. Build byte transitions
   in the verifier's exact bit order.
4. Use dynamic programming or BFS over `(position, state)` and the allowed alphabet. Retain one
   predecessor per state instead of brute-forcing the full input space.
5. Forward-check the recovered input through the transition table, then feed it to the original
   target and confirm the exact success state or output.

## Invert Exact Matrices and UI Semantics

Use this when a challenge checks a matrix-derived target but accepts clicks, cards, tiles, or another semantic action list.

1. Recover the matrix equation and solve it with exact integers, modular arithmetic, or rational fractions. Do not use floating-point inversion when entries must be exact.
2. Forward-multiply the recovered matrix before interpreting it as actions.
3. Reconstruct the UI's list-building semantics in reverse. Duplicate visible values require position-aware prefix/suffix constraints or DFS; a value-to-first-index map is insufficient.
4. Convert the semantic result back to exact click indices or coordinates, then render any resulting grid or glyph independently.
5. Verify every round against the local verifier or protocol, not only a visually plausible message.

## Recover Temporal Visual Signals

Use this when information is encoded across video frames or animated object poses.

1. Sample at a rate that preserves state changes, then segment discriminative colors or components in a stable color space such as HSV.
2. Cluster component centroids into fixed spatial prototypes. Represent each frame by prototype IDs or paired poses rather than raw pixels.
3. Reject incomplete/noisy frames using component count, area, and distance thresholds.
4. Collapse consecutive identical states into runs, map the stable states to symbols, and keep timing only if evidence shows it carries information.
5. Validate the decoded stream with an independent wrapper, checksum, known alphabet, or original checker.

## Mirror Continuous Simulations

Use this when acceptance depends on deterministic physics or another floating-point iteration.

1. Reproduce the exact update order, constants, precision, clamping, and iteration count. Verlet, Euler, and semi-implicit Euler are not interchangeable.
2. Define the final verifier residual over only the controllable inputs.
3. Use bounded multi-start Newton, secant, or another root solver in that low-dimensional space; calculate numerical Jacobians only after matching the forward simulation.
4. Confirm the candidate remains finite and within all intermediate and final constraints. Explicitly test whether NaN or tolerance quirks are real gates, not assumed shortcuts.
5. Run the original target with the recovered inputs and record its final residual or success output.

## Peel Managed and Layered Containers

- Electron: parse `app.asar`, isolate application JS from Chromium runtime files, and trace renderer -> preload bridge -> main-process IPC -> crypto/file check.
- PyInstaller/PYC: extract the archive and bytecode first; treat the launcher as packaging unless it adds a real gate. For a mismatched bytecode version, recover the embedded interpreter version and use a cross-version marshal/disassembly tool instead of executing the payload.
- Nested encoders: decode one layer at a time, save intermediate bytes, identify custom alphabets, and verify each layer by re-encoding.
- Android/smali: search application package code and native libraries before reading framework classes.
- Recursive file-loading VM: log `(stage, file, pc, state hash)`, prevent accidental cycles, and checkpoint every recovered stage.

## Model Sparse Destruction Before Recovering Large Data

Use this when a ransomware-like program copies a database, record store, disk image, or archive and
then overwrites periodic ranges.

1. Peel packagers first. For PyInstaller, identify the bundled Python version, extract the entry code
   object, and use a version-aware marshal/disassembler when the host Python cannot import the bytecode.
2. Reconstruct the writer as intervals rather than prose: initial offset, skipped bytes, bytes written,
   stride, final partial write, random source, and whether one buffer is reused. Calculate the exact set
   of destroyed and preserved ranges for each file size.
3. Distinguish encryption from destruction. Bytes replaced with operating-system randomness have no
   inverse key; recovery must come from file-format redundancy, paired indexes, replicas, checksums,
   parity, predictable padding, or an unaffected copy.
4. Inspect boundaries around several distant damage intervals before parsing the entire multi-gigabyte
   file. Infer record alignment and whether corruption cuts headers, payloads, or both.
5. Stop at a reproducible damage map when the supplied corpus lacks enough redundancy for unique
   reconstruction. Record payload hash, bytecode version, interval formula, and the missing recovery
   primitive instead of running unbounded brute force.

## Recover Unity Scene Data Channels

Use this when a Unity build displays a suspiciously easy sprite, coordinate hint, or fake flag.

1. Decompile `Assembly-CSharp.dll` just far enough to identify the scene transition and referenced
   sprite/resource fields.
2. Load the Unity data directory and enumerate `GameObject`, `Transform`, `RectTransform`, `Sprite`,
   `Texture2D`, and relevant `MonoBehaviour` objects per serialized file.
3. Preserve asset-file name and path ID when following a `PPtr`; identical path IDs in different
   files are unrelated.
4. Normalize integer-positioned objects into a grid. Names such as `Square`, `Tile`, or numbered
   clones often encode a 3x5/5x7 font, bitmap, route, or permutation independent of rendering.
5. Decode the normalized grid with explicit glyph signatures and verify the original scene hash.
   Keep extracted visible sprites as evidence of a decoy, not as the final answer by default.

## Peel Boot Images Before Reversing Loaders

Use this when a small `.img` boots directly into a crackme, custom UI, or protected-mode program.

1. Inspect the first sector, `0x55aa` signature, sector-aligned magic, and total image size.
2. Search from sector boundaries for `MZ`, `ELF`, compressed data, or a stage table. Validate the
   candidate's native header before opening it in a decompiler.
3. Analyze the embedded payload's compare path first. Treat the boot sector as a loader unless it
   transforms input or payload bytes.
4. For behavioral checks, boot a copy-on-write instance with QEMU `-snapshot`. When graphics prevent
   terminal interaction, use an HMP/QMP monitor with `sendkey` and `screendump`; never modify the
   original image merely to automate input.
5. Distinguish typed input from the checker's normalized input, especially for keyboard layouts,
   Hangul/IME decomposition, scan-code tables, shifted punctuation, and custom text renderers.

## Separate Local Service Boundaries

Use this when a native challenge daemon combines web parsing, SQL/LDAP, sessions, cryptography, and
device-style settings endpoints.

1. Start the supplied container on `127.0.0.1` with deterministic sentinel secrets. Confirm health
   and one known-good login before probing flaws.
2. Draw a boundary table: user-controlled fields, parser caps/decoding, SQL statement, account object,
   password transform, session token, authenticated routes, and each response distinction.
3. Implement blind extraction against the narrowest stable response predicate. Save only final values;
   do not print every growing prefix for 512-byte ciphertexts or keys.
4. Reconstruct crypto object roles from initialization and call order. A nearby BIGNUM may be `n`,
   `e`, `d`, `p`, `q`, or temporary `phi`; prove which one an endpoint serializes and whether it uses
   big- or little-endian output.
5. Test stage reachability independently. An authenticated endpoint that leaks a private exponent is
   not usable for first-stage login unless a separate session/authentication flaw reaches it.
6. Report the strongest local result and the exact circular dependency or missing external value when
   the real deployment cannot be completed offline.

## Verification Matrix

Choose at least one strong check and one independent supporting check:

| Shape | Strong check | Supporting check |
| --- | --- | --- |
| Inverse transform | Original target accepts input | Forward output equals target bytes |
| Batch workers | Full controller accepts | One worker per family round-trips |
| Embedded children | Parent accepts ordered result | Distant child samples accept |
| Stateful verifier | Original verifier reaches final success | Each local step is unique and final state matches |
| Script expansion | Original interpreter confirms reachability or unreachability | One-pass reconstructed command matches every fragment |
| Boolean circuit | Original target accepts the recovered input | DFA replay reaches the exact final state |
| Artifact recovery | Parser/viewer opens exact artifact | Magic, length, hash, CRC, or padding validates |
| Record forge | Service/parser reaches intended sink | Local parser reproduces every invariant |
| Unity scene channel | Serialized objects decode to the token | Decoy sprite and scene reference chain agree |
| Boot image payload | Embedded target accepts or forward-checks input | Sector/header/hash and QEMU UI agree |
| Local service chain | Loopback daemon returns sentinel at each reached stage | Static route/query/crypto model matches runtime |

If the original cannot run on the current architecture, state that limitation and retain exact intermediate hashes so later verification is reproducible.
