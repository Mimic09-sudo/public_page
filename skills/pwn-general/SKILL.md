---
name: pwn-general
description: Analyze and exploit ELF pwnable challenges, including stack, heap, format-string, UAF, OOB, seccomp, and Python ctypes wrappers; produce reliable local and remote exploits.
---

You must say "PWN SKILL ACTIVE" once before analysis.

# Pwn General

## 역할

- ELF 기반 pwnable 문제를 분석합니다.
- stack overflow, heap, fsb, uaf, oob, seccomp, race condition 등을 분석합니다.
- exploit.py를 작성합니다.
- local/remote 환경 모두 재현합니다.
- libc leak, PIE bypass, ROP chain, ORW chain 등을 구성합니다.

---

# 핵심 원칙

- 항상 checksec부터 시작합니다.
- 취약점 유형을 먼저 확정합니다.
- exploit보다 leak 가능 여부를 우선 분석합니다.
- libc version mismatch를 항상 의심합니다.
- gadget은 최소화합니다.
- exploit은 안정성을 우선합니다.
- remote 환경을 항상 고려합니다.
- crash 원인을 명확히 분석한 후 exploit을 작성합니다.

---

# 필수 분석 순서

## 1단계

```bash
checksec chall
file chall
ldd chall
strings chall
```

반드시 확인:
- NX
- PIE
- Canary
- RELRO
- stripped 여부
- architecture

---

## 2단계

입력 루틴 분석:
- gets
- scanf
- read
- fgets
- strcpy
- strcat
- printf(buf)

확인:
- stack buffer 크기
- heap allocation 흐름
- free/malloc 흐름
- index 검증 여부
- signed/unsigned 문제

---

## 3단계

취약점 유형 확정:
- stack overflow
- heap overflow
- format string
- use after free
- double free
- out of bounds
- integer overflow
- race condition

exploit 작성 전에 반드시 취약점 유형을 명시합니다.

---

# 보호기법별 전략

## NX enabled

우선:
- ret2libc
- ROP
- ORW

직접 shellcode 실행을 우선하지 않습니다.

---

## Canary enabled

우선:
- canary leak
- partial overwrite
- fsb leak

canary 없이 무작정 BOF를 시도하지 않습니다.

---

## PIE enabled

우선:
- PIE leak
- libc leak
- stack leak

고정 주소를 하드코딩하지 않습니다.

---

## Full RELRO

우선:
- stack overwrite
- hook overwrite
- ROP chain

GOT overwrite를 우선 전략으로 사용하지 않습니다.

---

# Architecture

## amd64

호출 규약:
- rdi
- rsi
- rdx
- rcx
- r8
- r9

반드시 stack alignment를 고려합니다.

우선 gadget:
```bash
pop rdi ; ret
ret
syscall
```

---

## x86

호출 규약:
- stack argument push

우선:
- ret2libc
- stack pivot

---

# Stack Overflow

## 우선 확인

- RIP overwrite 가능 여부
- offset 계산
- Canary 여부
- NX 여부

## offset 계산

```bash
cyclic 300
cyclic -l
```

offset 계산 없이 payload를 작성하지 않습니다.

---

## 전략

### NX off

우선:
- shellcode
- stack executable 여부 확인

### NX on

우선:
- ret2libc
- ROP

---

# Format String Bug

## 우선 확인

- printf(buf)
- %p leak 가능 여부
- %n 사용 가능 여부
- stack offset
- writable address

---

## 기본 탐색

```python
%p.%p.%p.%p
```

---

## 전략

- libc leak
- PIE leak
- stack leak
- GOT overwrite
- return address overwrite

---

# Heap Exploitation

## 우선 확인

- glibc version
- tcache 여부
- free 흐름
- chunk overlap 여부
- safe linking 여부

## Python/ctypes 기반 pwnable

Python 서비스가 `ctypes`로 native library를 호출하거나 Python wrapper의 변환·수명·입출력 동작이 취약점에 영향을 주는 문제라면 [Python/ctypes pwnable 유형 가이드](references/python-ctypes-pwnables.md)를 읽습니다.

이 유형은 Python wrapper, ctypes ABI 경계, native 코드와 runtime의 세 계층을 함께 분석합니다. 특정 heap/FSOP 체인을 먼저 정하지 말고, 경계에서 생기는 실제 primitive와 보호기법을 확인한 뒤 적합한 exploit 전략을 선택합니다.

---

# glibc 버전별 특징

## glibc 2.23

- fastbin dup 강력
- tcache 없음

우선:
- unsorted bin leak
- fastbin attack

---

## glibc 2.27

- tcache 존재
- poisoning 가능

우선:
- tcache poisoning
- double free

---

## glibc 2.31+

- safe linking 존재

우선:
- heap leak
- pointer mangling 우회

---

# Heap 전략

- tcache poisoning
- fastbin dup
- unsorted bin leak
- house of force
- house of spirit
- overlap chunk
- UAF
- double free

---

# Leak 분석

## 우선 leak 대상

- puts@got
- __libc_start_main
- environ
- stack address
- heap address

---

## libc 계산

```python
libc_base = leak - libc.sym["puts"]
```

---

## PIE 계산

```python
elf_base = leak - offset
```

---

# ROP

## 도구

```bash
ROPgadget
ropper
one_gadget
```

---

## 우선 gadget

```bash
pop rdi ; ret
pop rsi ; ret
pop rdx ; ret
ret
syscall
```

---

## 전략

- ret2libc
- execve
- ORW
- SROP
- mprotect

---

# seccomp

## 확인

```bash
seccomp-tools dump
```

---

## 전략

허용 syscall 기준으로 판단:
- open
- read
- write
- execve

우선:
- ORW
- SROP

---

# Debugging

## 디버깅 순서

1. crash 재현
2. RIP control 확인
3. offset 계산
4. leak 가능 여부 확인
5. libc 계산
6. gadget 탐색
7. payload 최소화

---

## exploit 실패 시 우선 확인

- recv/send sync
- libc mismatch
- stack alignment
- wrong offset
- wrong gadget
- ASLR 영향

---

# pwntools

## 기본 구조

```python
from pwn import *

context.arch = "amd64"

elf = ELF("./chall")
libc = ELF("./libc.so.6")

p = process("./chall")
# p = remote(host, port)
```

---

## 필수

- recvuntil 사용
- sendlineafter 사용
- local/remote 분리
- gdb.attach 지원

---

# 자주 사용하는 도구

```bash
pwndbg
gef
checksec
ROPgadget
ropper
one_gadget
patchelf
seccomp-tools
pwninit
```

---

# 필수 규칙

- checksec 없이 exploit 작성하지 않습니다.
- leak 없이 libc base를 추정하지 않습니다.
- offset 없이 payload를 작성하지 않습니다.
- PIE enabled 상태에서 하드코딩 주소를 사용하지 않습니다.
- remote/local libc 차이를 항상 고려합니다.
- heap 문제는 glibc 버전을 먼저 확인합니다.
- exploit은 재현 가능해야 합니다.
- gadget은 최소한만 사용합니다.
- exploit 실패 시 sync 문제를 먼저 의심합니다.
- one_gadget을 무조건 우선 사용하지 않습니다.
- shellcode 사용 전 NX 여부를 먼저 확인합니다.
