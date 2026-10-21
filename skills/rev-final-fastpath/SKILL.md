---
name: rev-final-fastpath
description: Practical fast-path solver for reversing CTF, wargame, crackme, and hybrid rev tasks. Use for ELF/PE/Mach-O/.NET/Java/WASM/PYC/mobile/script/custom-VM/packed/game/oracle/asset/stage challenges, including mass-generated VM corpora with per-instance opcode permutations, when Codex must recover the success condition, normalize or emulate only the necessary path, reconstruct artifacts, write a solver/hook/patch/decryptor, and verify against the original target.
---

# Rev Final Fastpath

## Local execution base

Load and follow `ctf-wsl-toolchain` before local triage or tool execution. This skill controls the reversing methodology and solve contract; `ctf-wsl-toolchain` controls WSL entry, installed binaries, Python runtime, paths, and tool discovery. Do not ask the user to operate the toolchain.

## Mission

Solve reversing CTF problems by reducing them to the smallest verifiable success condition.

Do not explain the whole binary first. Find the check, model only what reaches it, produce the answer or artifact, and verify on the original target.

This skill is grounded in a cross-drive local corpus spanning competition folders, wargames,
native binaries, managed/mobile targets, scripts, custom VMs, generated executable farms, assets,
writeups, solvers, hooks, dumps, and extracted stages. Treat corpus statistics as inventory evidence,
not as a substitute for per-target analysis.

## First 180 Seconds

Run this before deep analysis:

1. Inventory files and cardinality: `rg --files`, `file`, `find . -maxdepth 2 -type f`, paired-name counts, numeric ID range, missing IDs, and total compressed/uncompressed size.
2. Prefer existing local artifacts in this order: `writeup*`, `README*`, `solve.py`, `solver.py`, `ex.py`, `hook.c`, decompiled `.c`, disasm/listing, then raw binary.
3. Search anchors with `rg -n "flag|correct|wrong|success|win|license|Good|Bad|error|strcmp|memcmp|strncmp|open\\(|fopen\\(|/proc/self/exe|GVFS|QGAT|QBLK|QJFS|journal|overlay|ptrace|sigaction|sleep|time|rand|AES|base64|zlib|xor|rol|ror|opcode|vm|stage|oracle|dlopen|dlsym|memfd_create|fexecve|998244353|app\\.asar"`.
4. Execute once only if safe and cheap. Capture input shape, output strings, required files, network host/port, crashes, sleeps.
5. If there are many similar instances, compare first/middle/last samples before deep analysis: format, entry points, operand grammar, opcode bytes, sizes, and output shape.
6. Pick exactly one solve lane. Do not analyze multiple lanes deeply at the same time.

If there is no anchor after 10 minutes, switch to dynamic observation. If there is no recoverable condition after 20 minutes, switch to dump/patch/oracle.

## Scale Gate

Apply this gate before running more than 100 structurally similar targets.

- Time 10 representative executions and calculate the full-run cost before launching the batch.
- Sample at least three distant IDs. Separate stable structure from per-instance variation.
- Native-emulate one or two instances only to recover the contract, state layout, instruction grammar, and semantic anchors.
- If the corpus shares a grammar but permutes opcode bytes, derive a per-instance map and normalize into one canonical bytecode ISA.
- Move the hot loop into a lightweight interpreter/extractor. Do not use full native emulation for every item once a scalable model exists.
- Stream or batch archive entries, preserve numeric order explicitly, use worker chunks, and keep a raw checkpoint so a long run can resume.

## Lane Decision

Choose the cheapest lane matching observed evidence.

### 1. Direct Constant / Compare Chain

Use when there are `cmp al, imm`, byte-by-byte checks, `strcmp`, `memcmp`, fixed `.rodata` targets, or many tiny check functions.

Actions:

- Locate compare caller and input length check.
- Extract target bytes in compare order, not memory order.
- Rebuild the input by following index writes, permutations, and early exits.
- Ignore decoy functions and UI code.

Output: direct input, small extractor, or keygen.

### 2. Inverse Transform

Use when input is transformed by xor/add/sub/rol/ror/sbox/base64/custom alphabet/matrix/RNG/round functions before comparison.

Actions:

- Recover final target bytes first.
- Implement the shortest forward model and test one sample against the binary or decompiled code.
- Invert in exact reverse order: round order, byte order, key schedule, matrix, permutation, RNG consumption.
- When disassembly contains long straight-line word transforms, parse it into expression chains instead of transcribing instructions. Invert XOR-shifts by bit propagation and odd multipliers with modular inverses at the exact word width.
- Fingerprint standard primitives before translating noisy decompiler output. Separate the stable algorithm skeleton from challenge-specific constants, tables, seeds, and post-processing.
- For NTT/convolution checks, move to the transform domain, divide pointwise where invertible, apply inverse NTT, and then validate the exact padded forward input.
- If inversion is messy, brute force only the smallest unknown chunk.

Output: `solve.py` with `forward()` and `inverse()` when possible.

### 3. Asset / Stage / File Recovery

Use when the target hides data in images, HWP/PDF streams, archives, resources, PE sections, sprite sheets, mem blobs, encrypted files, or generated stage2 binaries.

Actions:

- Extract embedded blobs before tracing UI/rendering.
- For bootable disk images, inspect sector boundaries and partition/boot signatures before reversing
  real-mode setup code. A sector-aligned `MZ`, `ELF`, archive, or second-stage image is usually the
  cheaper target; preserve the loader contract and hash the extracted payload.
- Identify compression/encryption wrappers: zlib, zip, base64, hex, XOR, stream cipher, image channels.
- For video or animated signals, sample frames, track stable component positions, map paired poses or states to symbols, and collapse duplicate runs before interpreting text.
- Validate extracted stage by magic/header/hash: `MZ`, `ELF`, `PK`, PNG/JPEG/HWP/PDF markers.
- Once stage2 exists, stop analyzing stage1 except for loader contract.

Output: recovered artifact plus reproducible extractor/decryptor.

### 4. Dynamic Dump / Hook

Use when static analysis is blocked by `memfd`, `fexecve`, self-modifying code, `ud2`, signal handlers, anti-debug, dispatcher loops, packed code, runtime keys, or misleading file bytes.

Actions:

- Hook the narrowest useful point: `strcmp`, `memcmp`, `strncmp`, `read`, `open`, `fopen`, `fexecve`, `mmap`, `mprotect`, `ptrace`, `sigaction`, `sleep`, crypto APIs.
- Dump buffers immediately before compare or immediately after decrypt/unpack.
- Use patching for observation only unless the challenge explicitly accepts a patched local binary.
- Reconcile dump bytes with original runtime behavior before solving.

Output: `hook.c`, debugger script, dumped stage/key/target, then final solver.

### 5. Oracle / Remote Automation

Use when the service answers membership, prefix, substring, timing, score, license validity, game status, or round prompts.

Actions:

- Rewrite the server behavior as a predicate: `ask(x) -> information`.
- Define alphabet, length, cache, retry, timeout, and query budget.
- Automate immediately. No manual round solving.
- Minimize queries with prefix growth, substring assembly, binary search, candidate pruning, or memoization.

Output: robust `ex.py` with reconnect/retry and final flag extraction.

### 6. Game State / Simulation

Use for games, maps, coordinates, timers, tick loops, anti-cheat, path constraints, casino/random state, or engine binaries.

Actions:

- Ignore renderer and engine boilerplate. Find state arrays, win function, server check, map, RNG state, and movement constraints.
- Convert continuous coordinates to grid, bitmask, graph, or state tuple.
- In Unity and similar engines, parse serialized `GameObject`, `Transform`, `Sprite`, and scene data
  before playing the game. Object names and integer coordinates can themselves form a bitmap,
  permutation, hidden path, or glyph stream even when the visible sprite is a decoy.
- If the server validates state, model the server predicate, not the client visuals.
- For deterministic continuous physics, mirror the exact integrator and solve only the low-dimensional input residual with bounded multi-start root finding. Reject NaN, tolerance, or unchecked-state shortcuts unless the original verifier actually accepts them.
- Generate legal state/path/timing sequence.

Output: path/state generator or remote automation.

### 7. Symbolic / Math

Use only after the check has been sliced into equations, VM arithmetic, linear constraints, modular equations, or bounded branch conditions.

Actions:

- Prefer algebra first: linear solve, modular inverse, Gaussian elimination, CRT, known RNG recovery.
- For known input/output samples of an affine map, solve its matrix and bias directly, invert the matrix, and test on held-out samples.
- Convert large boolean gate networks to SAT/SMT only after fixing length, charset, and format constraints; model gates exactly instead of decompiling them into prose.
- If only `k` persistent Boolean state bits exist, enumerate the `2^k` transition relation first and solve `(position, state)` with BFS/DP before using SAT/SMT.
- Use `z3` only after variables and equations are explicit and the user has not forbidden it.
- For split equations like `target = f(hi) + g(lo) mod 2^w`, odd-multiply ARX gates, or independent 24/32-bit halves, do meet-in-the-middle before symbolic solving.
- Use `angr` only on a sliced function or controlled address range, never the whole program by default.
- Constrain input length, charset, known prefix/suffix, and avoid path explosion.

Output: solver script with constraints and original verification.

### 8. Embedded Overlay / Dead-Code Gate / MITM

Use when the live path is a digest-only validator, while unused helper routines, self-reading code, appended filesystems, journals, reloc maps, or encrypted gate blocks contain the real solve path.

Actions:

- Separate live validation from answer derivation. A path like `SHA256(domain || input) == digest` may only verify a precomputed answer; do not spend unbounded time on preimage recovery.
- Check whether solver-looking routines are outside the `main` call graph. Dead code can still describe the intended offline construction: replay, decrypt, fold, gate functions, or target generation.
- For appended overlays, find the last marker, parse the superblock, decrypt metadata, and replay journals before trusting visible directory listings.
- Apply indirection maps exactly. Inode relocations (`qreloc`) can change journal targets, and block relocations (`breloc`) can turn a visible decoy block into the real gate block.
- Track integer widths from runtime behavior. Checkpoint folds that decompile as 32-bit may require 16-bit wrapping; one wrong width often corrupts the gate key.
- Treat visible flags and magic-looking strings as decoys until they pass the strongest verifier.
- For gate blobs shaped like `magic | nbits | target | permA | permB`, identify whether the permutations define a bit split/reassembly. If the target is `f(hi) + g(lo)`, enumerate one half, hash/sort/map it, and match the other half.
- After recovering the secret integer, derive the answer format only from evidence: binary strings, writeup, service response, or recovered generator. Do not assume `DH{}`, `FLAG{}`, `SCA{}`, or any prefix just because the challenge platform usually uses it.

Output: overlay extractor, replay/decrypt script, MITM solver, recovered secret/answer, and verification.

### 9. Managed / Script / Bytecode / Mobile

Use for .NET, Java, Python bytecode, JS/WASM, Android/mobile, Lua, batch, or custom bytecode.

Actions:

- Decompile first; do not single-step boilerplate.
- For Electron, inspect and extract `app.asar` before touching Chromium DLLs. Follow IPC handlers and crypto/file APIs from the renderer request to the privileged check.
- For Unity Mono builds, inspect `Assembly-CSharp.dll` only to locate scene/resource references, then
  read the referenced serialized assets directly. Do not assume the rendered sprite is the final
  secret when scene object placement carries a second channel.
- Peel nested script encodings one layer at a time and record each intermediate. For esoteric languages, implement only the instructions reached by the challenge program.
- For WASM/bytecode, identify exported check function, memory offsets, final compare buffer, and return convention.
- For PYC/scripts, bypass imports/anti-debug wrappers and reconstruct pure transform.
- For batch or shell obfuscation, reproduce the target interpreter's expansion phases exactly. Distinguish a reconstructed comparison literal from an input that can actually reach success.
- For custom VM, decode only opcodes on the validation path. If one concrete trace proves the branch path input-independent, freeze that path and symbolically replay it instead of exploring the dispatcher.

Output: extracted check logic or bytecode interpreter subset.

### 10. Mass-Generated / Opcode-Permutation VM / Chunk Reconstruction

Use when an archive contains hundreds or thousands of paired `vm`/`program.bin` instances, each validates or emits a fixed-size chunk, and opcode numbers vary while operand grammar and program topology remain stable.

Actions:

- Inventory IDs and test whether `count * chunk_size` resembles an artifact size. Decrypt the first two chunks early and test magic/header continuity (`PNG`, `ELF`, `MZ`, `PK`, PDF, dimensions/chunk headers).
- Emulate one representative native VM to locate `vm_execute(state, program, size)`, I/O boundaries, bytecode PC, stack/register layout, RAM base, target/key offsets, and success/failure tail.
- Trace reads from the program buffer. Treat repeated host read sites as opcode/operand fetch helpers and recover instruction boundaries from fetch addresses.
- Identify stable operand tags before opcode semantics, such as `imm64`, register, direct memory, and `memory[register + base]`.
- Recover each opcode permutation from structural anchors and repeated idioms: first `mov/push/pop`, modulo reduction for `div/mul/sub`, recombination for `add`, verifier tail for `xor/eq/branches`, fixed I/O patterns for syscalls, and memory-access shapes for load/store.
- Normalize actual opcode bytes to a canonical ISA, then run a compact interpreter only as far as needed to expose target/key/chunk data.
- Reassemble chunks by numeric ID. Preserve the exact raw byte stream and hash it before optional trimming, decompression, or format repair.
- For visual secrets, produce tight crops and discriminative color/channel views. Segment ambiguous glyphs and obtain an independent reading; never guess lookalikes such as `6/e`, `d/8`, `b/6`, or omit a wrapper shown by evidence.

Output: opcode normalizer, fast bytecode interpreter, ordered chunk solver, raw reconstructed artifact, and exact answer.

Verification:

1. Recovered chunks make representative original VMs print success.
2. The first two chunks form a coherent artifact header, not only a coincidental magic.
3. Full raw length equals `instance_count * chunk_size`; record its hash before transformations.
4. Container CRCs/checksums parse successfully and the artifact opens.
5. Any visual token is read twice from independent enhanced views and its exact wrapper comes from evidence.

### 11. Batch Plugin / Embedded Executable Farm

Use when one controller loads hundreds or thousands of shared libraries, decrypts many embedded executables, or launches children through `dlopen`/`dlsym`, `LoadLibrary`, `memfd_create`, or `fexecve`.

Actions:

- Recover the controller's exact order, per-item interface, input/output size, and success/failure contract before analyzing individual workers.
- Sample distant workers and cluster them by structural instruction anchors or primitive family. Extract constants from stable offsets only after cross-sample confirmation.
- Model each worker as a compact reversible operation, then invert the controller chain in reverse order. Keep width, endianness, rotation, padding, and post-XOR explicit.
- For embedded executables, parse or dump the container once, preserve each raw child, and identify the per-child key/argument contract. Do not repeatedly launch the whole farm when static extraction or a compact emulator suffices.
- Verify representative workers in isolation and the complete forward chain against the original controller.

Output: ordered manifest, worker classifier/extractor, inverse-chain solver, and original verification.

### 12. Local Service / Firmware Composition

Use when a challenge ships a native daemon, root filesystem, init scripts, database seed, web pages,
or container recipe and the answer spans more than one boundary.

Actions:

- Build and bind the service to loopback only. Replace missing remote secrets with unmistakable local
  sentinels and record which outputs are local placeholders.
- Recover the route table and model each boundary separately: request parser, authentication/session,
  database query, LDAP or other backend, crypto wrapper, configuration writer, and response renderer.
- Turn injection behavior into a precise oracle. Distinguish query success, account lookup, password
  verification, and authenticated handler reachability; similar error pages are not equivalent states.
- Treat public-key values by semantic role, not proximity. Label modulus, public exponent, private
  exponent, ciphertext, byte order, padding, and serialization from call arguments such as
  `BN_mod_exp`, `BN_mod_inverse`, `BN_bn2binpad`, and `BN_bn2lebinpad`.
- Search authenticated diagnostics and preview endpoints for bounded memory disclosure before trying
  key factoring or password brute force. Cross-check the leaked object against its allocation site.
- Verify each stage against the local daemon, but never report a local sentinel as the event flag.

Output: loopback-only launch command, stage oracle/exploit, recovered local sentinel, and a clear list
of external values still required for a real deployment.

Read [references/local-corpus-patterns.md](references/local-corpus-patterns.md) when evidence points to NTT, stateful per-position checks, batch library/executable farms, script expansion phases, small Boolean circuits, seeded record formats, runtime-generated crypto tables, instruction-chain inversion, fixed-path VMs, exact matrix/UI inversion, temporal visual recovery, continuous simulation, data-structure normalization, PyInstaller bytecode with periodic file damage, Unity scene coordinates, embedded boot payloads, or local service composition.

## Solve Contract

Every solve must end with one of these concrete products:

- `input`: exact stdin/argv/file content accepted by the original target
- `answer`: exact flag/token/secret derived offline when the original binary only contains a one-way validator
- `script`: `solve.py` or `ex.py` that regenerates the answer
- `decrypt`: recovered file/image/stage with script
- `patch`: minimal patch with explanation, only if original verification is impossible or patching is the intended task
- `hook`: hook/dump tool plus recovered data and final solver

Patch-only success is not solved unless the problem is explicitly a patching challenge.

## Corpus Learning and Writeback

When a local problem has no solver or writeup:

1. Preserve the original challenge artifacts and analyze them with the cheapest matching lane.
2. Add `solve.py`/`solver.py` and `writeup.md` to the original problem directory only after the
   solver regenerates the result and the strongest available verification succeeds.
3. Prefer extraction from symbols, tables, bytecode, or file structure over hardcoding one recovered
   answer. Include a forward check whenever the transform is reproducible.
4. State interpreter, architecture, dependency, dummy-file, or network requirements explicitly.
5. If the intended comparison is unreachable because of parser or runtime semantics, report the
   hidden value and the unreachable branch separately; do not label it an accepted input.
6. If analysis is partial, keep probes in scratch space and record the blocker. Do not install a
   speculative solver or polished writeup beside the original challenge.
7. If the corpus-learning goal is already met and the remaining answer depends on a missing server,
   redacted secret, external VM, incomplete artifact, or an unchanged solver timeout, classify it with
   evidence and move to a new pattern. Do not inflate coverage by calling that item solved.

Promote only evidence-backed, reusable techniques into this skill or its references. Never embed
challenge answers, one-off addresses, or unverified assumptions as general rules.

## Verification Rules

Use the strongest available verification:

1. Original binary prints success/flag with generated input.
2. Remote service accepts generated answer and returns flag.
3. Recovered artifact opens or contains the expected flag/data.
4. Forward model output matches the original compare target.
5. Multiple independent samples agree with the recovered oracle/model.

Record the exact command used. If verification cannot run, state the blocker and the next cheapest verification.

## Stall Transitions

When stuck, do not repeat the same depth of analysis.

- No success string -> search compare/call imports, then dynamic trace.
- Compare target hidden -> dump compare operands.
- Transform inversion unclear -> validate forward model with one sample, then invert one round only.
- Stage loader noisy -> dump stage after decrypt/unpack and analyze stage2.
- Game visuals noisy -> switch to state arrays/server predicate.
- Unity sprite is a decoy -> inspect scene hierarchy, serialized references, names, and Transform grids.
- Boot image UI is noisy -> locate aligned embedded payloads; use QEMU `-snapshot` plus monitor
  `screendump`/`sendkey` only for narrow behavioral confirmation.
- Oracle noisy -> log raw request/response and redefine predicate.
- Symbolic exploding -> slice function tighter or add concrete trace.
- A concrete VM trace fixes the path but the full bit-vector solve still times out -> split at
  checkpoints, solve per block, or retain the verified forward model and classify the instance.
- A ransomware-like payload overwrites periodic ranges with OS randomness -> map exact damage
  intervals, then look for record redundancy or replicas; do not search for a nonexistent inverse key.
- Digest preimage impossible -> look for offline generator clues: overlays, dead-code helpers, target constructors, local writeups/solvers, or recovered artifacts.
- Visible filesystem entry is a decoy -> inspect hidden/quarantined entries, replay effects, and relocation maps.
- Anti-debug wasting time -> patch/hook anti-debug only to observe buffers.
- Patcher gets success but no flag -> recover real input/state; patch result is only a clue.
- Thousands of similar VMs are slow under Unicorn -> stop the batch, normalize opcode permutations, and switch to a bytecode interpreter.
- Hundreds of libraries or child executables repeat a contract -> stop reading workers individually; extract order, cluster families, and invert the compact operation chain.
- Same operand grammar but different opcode bytes -> infer semantic maps from structural idioms per instance; do not reuse sample 0's raw opcode table.
- Heavy constant setup hides a bytewise early exit -> trace branch decisions or VM instruction counts; do not trust wall-clock timing.
- Reconstructed image opens but the token is tiny or ambiguous -> preserve the raw artifact, crop, isolate a discriminative channel, segment glyphs, and independently verify the transcription.

## Local Workspace Heuristics

Apply these because this workspace already contains many solved or partially solved problems:

- If `.c` exists beside a binary, treat it as the fastest first-pass map, but confirm weird control-flow warnings against runtime behavior.
- If `.i64` or IDA sidecar files exist, assume a prior manual analysis may have named functions or left useful artifacts.
- If `solve.py`, `solver.py`, or `ex.py` exists, read it before rebuilding the same math.
- If a writeup exists, mine only the lane, check function, constants, and verification command; do not copy irrelevant narrative.
- If many dumps/stages exist, identify the newest or final one by writeup references, file magic, or solver usage.
- If a local `flag`, `flag.txt`, or dummy flag exists, distinguish local test flag from remote real flag.
- If there are both original and patched binaries, verify against the original unless the filename and writeup prove patching is the objective.
- If no solver/writeup exists, produce both when the solve is reproducible; keep incomplete probes outside the original problem directory.
- Treat zero-byte files, empty directories, isolated clients, screenshots/CFG PDFs without a question,
  and external-machine evidence folders as incomplete cases, not unsolved reversing binaries.

## Output Format

During analysis, answer in this exact structure:

1. Core observations: three concrete facts with filenames/functions/addresses when possible.
2. Selected lane: one lane and why it is cheapest.
3. Avoided paths: at least two tempting but wasteful paths.
4. Immediate actions: up to five specific commands/actions.
5. Stall transitions: two fallback transitions.
6. Deliverable type: `input` / `answer` / `script` / `decrypt` / `patch` / `hook`.
7. Original verification: exact binary/service/artifact check.
8. Confidence: high / medium / low, with the main remaining uncertainty.

For final solved output, include:

- answer or artifact path
- solver/hook/decrypt script path
- verification command/result
- remaining uncertainty, if any

## Hard Bans

- Do not start with a full binary tour.
- Do not read huge decompiler output from top to bottom before finding anchors.
- Do not choose `angr` as the first move unless the problem is explicitly an angr exercise or a tiny sliced function.
- Do not force `z3` onto odd-multiply ARX, split-half gates, or MITM-shaped equations.
- Do not call something crypto/VM/obfuscation without evidence.
- Do not assume a flag prefix or format. Test wrappers only as candidates when evidence supports them.
- Do not treat a digest-only input gate as the only answer path when dead-code solvers or appended artifacts exist.
- Do not spend time on renderer, UI, CRT, libc, STL, engine, or framework code unless it gates success.
- Do not stop at "looks correct"; verify on the original target.
- Do not native-emulate every item in a mass-generated VM corpus after a stable bytecode grammar is known.
- Do not execute hundreds of untrusted child binaries when a controller table, static worker extractor, or three-sample classifier can recover the same contract.
- Do not reuse one instance's opcode bytes when the corpus permutes semantics per VM.
- Do not use wall-clock timing as a prefix oracle when a large constant setup dominates execution.
- Do not modify, trim, or repair a reconstructed artifact before recording its exact raw length and hash.
- Do not submit a visually ambiguous token from one crop or invent/omit its wrapper.
- Do not write an incomplete or unverified solver/writeup into the original challenge directory.
