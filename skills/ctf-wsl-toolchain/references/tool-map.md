# Installed CTF tool map

Use this as a routing guide, not as a requirement to run every tool.

## Baseline triage and build

- `file`, `strings`, `xxd`, `hexdump`, `readelf`, `objdump`, `nm`, `ldd`, `checksec`
- `gcc`, `g++`, multilib, `clang`, `llvm`, `nasm`, `yasm`, `make`, `cmake`
- `strace`, `ltrace`, `patchelf`, `pwninit`
- Cross-architecture execution: `qemu-aarch64`, `qemu-arm`, `qemu-mips`, `qemu-mipsel`, and other QEMU user targets

## Pwn and binary exploitation

- Debuggers: `pwndbg`, `gdb-gef`, `gdb-multiarch`, `lldb`
- Automation: `ctf-python` with pwntools
- ROP and mitigations: `ROPgadget`, `ropper`, `one_gadget`, `seccomp-tools`, `checksec`
- Heap and libc references:
  - `/home/mimic09/ctf-tools/how2heap`
  - `/home/mimic09/ctf-tools/libc-database`
  - `/home/mimic09/ctf-tools/glibc-all-in-one`

## Reversing, mobile, and managed code

- `analyzeHeadless` / Ghidra, `r2` / radare2, `lldb`
- `jadx`, `apktool`, `aapt`, `adb`
- `upx`, `pycdc`, `frida`, `capa`, `floss`, `apkid`
- Java, Go, Rust, Mono, and MinGW build/runtime support is installed.
- PyInstaller extraction: `/home/mimic09/ctf-tools/pyinstxtractor`

## Crypto and constraint solving

- `sage`, `pari-gp`, `gap`, `maxima`
- `ctf-python` packages include `z3`, PyCryptodome, SymPy, and common number/constraint libraries.

## Forensics, documents, and steganography

- `vol` / Volatility 3, `binwalk`, `foremost`, `bulk_extractor`, `sleuthkit`
- `exiftool`, `yara`, `oletools`, `pdf-parser.py` and other Didier Stevens utilities
- `steghide`, `stegseek`, `zsteg`, `stegoveritas`, `pngcheck`, ImageMagick
- Password recovery: `hashcat`, `john`, `fcrackzip`, `pdfcrack`

## Web, network, and services

- Discovery/traffic: `nmap`, `masscan`, `tshark`, `tcpdump`, Wireshark tooling
- Web testing: `sqlmap`, `ffuf`, `gobuster`, `wfuzz`, `nikto`, `whatweb`, `dirb`
- Proxying and instrumentation: `mitmproxy`, `mitmdump`, `mitmweb`, `frida`
- Protocol and Windows-domain helpers: Impacket commands through the CTF Python environment
- Credential testing tools such as `hydra` are installed; use only against explicit challenge targets.

## Corpora and helper repositories

- SecLists: `/home/mimic09/ctf-tools/SecLists`
- PayloadsAllTheThings: `/home/mimic09/ctf-tools/PayloadsAllTheThings`
- DidierStevensSuite: `/home/mimic09/ctf-tools/DidierStevensSuite`

## Python environment separation

- General CTF venv: `/home/mimic09/ctf-tools/python-venv`
- mitmproxy venv: `/home/mimic09/ctf-tools/mitmproxy-venv`
- Use their entry-point wrappers from `/home/mimic09/.local/bin`; do not merge the environments because their dependency constraints differ.
