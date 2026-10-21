# Python/ctypes 기반 pwnable 유형 가이드

Python 서비스가 `ctypes`로 C/C++ shared library를 호출하는 문제에 적용합니다. 이 유형의 핵심은 특정 heap 기법이 아니라, Python과 native 코드 사이의 변환·수명·메모리 관리 경계에서 exploit primitive를 정확히 도출하는 것입니다.

분석 전에 stack, heap, FSOP 같은 최종 기법을 정하지 않습니다. 먼저 세 계층을 모델링하고, 실제로 확보한 leak/read/write/control primitive와 보호기법에 맞춰 기법을 선택합니다.

## 1. 세 계층으로 모델링

### Python wrapper

- 사용자 입력 파싱, 범위 검사, hex/base64 변환
- 객체와 native pointer의 저장 방식
- 메뉴 한 번을 처리하는 동안 생성·해제되는 Python 객체
- 예외, 출력, buffering, 반복문과 프로세스 종료 경로

### ctypes ABI 경계

- `argtypes`, `restype`, `Structure._fields_`
- 정수 폭과 signedness 변환
- `bytes`, `c_char_p`, `c_void_p`, pointer/array 변환
- 임시 객체의 lifetime과 callback 참조 유지
- C ABI padding, alignment, variadic call 여부

### native code와 runtime

- 실제 C 함수의 검증, allocation, copy, free 흐름
- ELF 보호기법과 shared library relocation
- glibc allocator, stdio, loader, thread 동작
- Python allocator와 libc allocator의 상호작용

사용자 입력이 세 계층을 통과하며 어떤 값과 주소로 바뀌는지 한 줄씩 추적합니다. Python 선언과 C prototype이 다르면 C ABI에서 실제로 전달되는 값이 기준입니다.

## 2. 우선 조사할 경계 취약점

### 정수 변환과 크기 계산

- Python의 arbitrary-precision 정수가 `c_uint*` 또는 `c_int*`로 축소되는지 확인합니다.
- 음수의 unsigned 변환, 큰 값의 truncation/wraparound를 확인합니다.
- native 코드의 `count * size`, `size + header`, alignment 계산에서 overflow를 확인합니다.
- 검증은 Python 값으로 하고 사용은 축소된 C 값으로 하는 TOCTOU 형태의 불일치를 찾습니다.

### 문자열과 버퍼 의미 차이

- `c_char_p`는 binary-safe buffer가 아니라 NUL-terminated string으로 취급될 수 있습니다.
- 입력 payload와 반환 leak이 첫 NUL에서 잘리는지 확인합니다.
- Python이 전달한 bytes 길이와 C 함수가 신뢰하는 별도 length가 일치하는지 확인합니다.
- `bytes.fromhex`, encode/decode, 자동 terminator가 실제 native buffer에 어떤 바이트를 만드는지 확인합니다.
- 고정 버퍼, flexible array, pointer-to-pointer가 Python 선언에서 잘못 모델링됐는지 확인합니다.

### 포인터와 lifetime

- free 후 Python 컨테이너에 pointer가 남는지 확인합니다.
- 같은 pointer를 여러 index/object가 공유하는지 확인합니다.
- 반환된 pointer의 소유권과 해제 주체가 불명확한지 확인합니다.
- 임시 `c_char_p`/buffer 또는 callback이 native 코드에 저장된 뒤 Python에서 수명이 끝나는지 확인합니다.
- `restype` 누락으로 pointer 반환값이 기본 `int`로 잘리거나 sign-extend되는지 확인합니다.

### 구조체와 ABI 불일치

- C 구조체의 padding/alignment와 `ctypes.Structure` 레이아웃을 비교합니다.
- flexible array member를 pointer field처럼 잘못 선언했는지 구분합니다.
- 함수 인자 개수·타입·calling convention 불일치를 확인합니다.
- packed 구조체, bit-field, union, callback prototype은 직접 `sizeof`와 field offset을 검증합니다.

### 동시성과 재진입

- native 함수가 GIL을 놓는지, callback이 Python으로 재진입하는지 확인합니다.
- thread가 같은 native object를 공유하면 lifetime race와 double free 가능성을 확인합니다.
- signal, destructor, error path에서 중복 정리가 일어나는지 확인합니다.

## 3. wrapper 동작도 exploit state의 일부

Python은 단순한 입출력 프록시가 아닙니다.

- 작은 객체는 pymalloc, 큰 문자열·bytes·extension 객체는 libc `malloc`을 사용할 수 있습니다.
- `input`, 긴 hex 문자열, decode, `ctypes` 변환, `print`, 예외 처리 사이에 예상하지 않은 allocation/free가 발생할 수 있습니다.
- 이 allocation은 unsorted bin을 정렬하거나 free chunk를 split/reuse해 native heap 상태를 바꿀 수 있습니다.
- 직접 TTY 실행과 `socat`/pipe/socket 실행은 buffering, 초기 객체, arena 상태가 다를 수 있습니다.

각 메뉴 명령을 하나의 원자적 C 호출로 가정하지 않습니다. 필요한 경우 allocator breakpoint, watchpoint, `strace`, GDB call trace로 Python 단계까지 포함해 상태 전이를 확인합니다.

## 4. primitive 표부터 작성

Exploit 기법을 선택하기 전에 다음 표를 채웁니다.

| Primitive | 확인할 제한 |
|---|---|
| allocation | 크기 변환, 실제 chunk 크기, allocator 종류, 횟수/index 제한 |
| free/lifetime | dangling pointer, 중복 free, alias, nulling 여부 |
| read/leak | 시작 주소, 최대 길이, NUL truncation, 반복 가능성 |
| write | 시작 주소, 길이, NUL/문자 제한, partial write, 반복 가능성 |
| address control | pointer 전체/일부 제어, alignment, safe-linking 영향 |
| control flow | 함수 pointer, vtable, return address, callback, 종료 경로 |

각 primitive는 한 번의 관찰이 아니라 실제 배포 경로에서 재현해 확정합니다. 우연히 남은 uninitialized/stale pointer보다 allocator 또는 프로그램 로직이 반복 생성하는 primitive를 우선합니다.

## 5. 주소 좌표계를 분리

다음 주소를 같은 것으로 취급하지 않습니다.

- Python object 주소
- ctypes wrapper object 주소
- native 구조체 주소
- `malloc` 반환 user pointer
- allocator chunk header 주소
- 구조체 내부 buffer 주소

amd64 glibc에서 user pointer와 chunk header가 일반적으로 0x10 차이나더라도 대상 allocator와 ABI에서 다시 검증합니다. UAF leak이나 bin link가 어느 좌표를 반환하는지, arbitrary write가 어느 좌표를 저장하는지 GDB로 확인합니다.

## 6. primitive에 따른 기법 선택

| 확보한 조건 | 우선 검토할 전략 |
|---|---|
| stack overwrite | canary/PIE leak 후 ret2libc, ROP, SROP |
| format string | stack/libc/PIE leak, 제한된 arbitrary write |
| UAF/double free | 대상 glibc에 맞는 tcache/fastbin/largebin 기법, overlap |
| OOB index 또는 pointer/length 분리 | arbitrary read/write 구성, 객체 overlap |
| 정수 overflow로 undersized allocation | heap overflow 또는 logical-length abuse |
| callback/function pointer 제어 | prototype과 calling convention을 맞춘 직접 control flow |
| Full RELRO/NX | stack target, 합법 vtable, 종료 경로, ROP/ORW 등 버전별 대안 |
| seccomp로 `execve` 불가 | 허용 syscall 기반 ORW/SROP |

glibc 기법은 정확한 버전과 bin 상태를 확인한 뒤 선택합니다. hooks, safe-linking, stdio vtable 검증, CET 같은 조건을 관성적으로 가정하지 않습니다. FSOP나 large-bin attack은 가능한 선택지 중 하나일 뿐 기본 경로가 아닙니다.

## 7. 제한된 read/write 다루기

- NUL-terminated read는 leak이 짧다고 해서 pointer가 없는 것이 아닙니다. 메모리의 원본과 wrapper가 반환한 범위를 구분합니다.
- NUL을 쓸 수 없으면 partial overwrite, terminator side effect, 여러 번의 prefix write, 다른 encoding 경로를 검토합니다.
- C 함수가 source 끝에 NUL 하나를 기록한다면, filler 이미지를 먼저 쓰고 필요한 NUL 위치를 높은 offset부터 prefix terminator로 심는 staged write가 가능할 수 있습니다.
- staged write 중간 상태가 invalid pointer를 만들 수 있으므로 callback, 전역 리스트, 종료 hook 등에서 객체가 사용되기 전에 완성합니다.
- 쓰기 길이를 결정하는 field 자체를 덮는다면 각 단계가 다음 write primitive를 유지하는지 확인합니다.

## 8. 분석과 exploit 작성 순서

1. executable과 모든 native library에 `file`, `checksec`, `ldd`, `readelf`를 적용합니다.
2. Docker digest, libc/Python 버전, cwd, 환경 변수, 실행 명령과 transport를 고정합니다.
3. Python 입력 하나가 native 함수 호출과 반환까지 거치는 값을 추적합니다.
4. Python 검증과 C 사용 값의 불일치를 목록화합니다.
5. primitive 표를 작성하고 GDB로 각각 최소 재현합니다.
6. 보호기법과 runtime 버전에 맞는 leak 및 control-flow 전략을 선택합니다.
7. critical allocator state를 만들기 전후로 wrapper가 수행하는 allocation을 포함해 exploit 순서를 설계합니다.
8. leak → base 계산 → write/control → trigger를 단계별 assertion과 로그로 검증합니다.
9. 실제 `socat`/socket 경로에서 여러 ASLR 실행을 반복한 뒤 remote에 적용합니다.

## 9. 실패 증상별 점검

| 증상 | 우선 확인 |
|---|---|
| pointer가 32비트처럼 잘림 | `restype` 누락, signedness, 잘못된 prototype |
| payload/leak이 특정 바이트에서 끝남 | `c_char_p`와 NUL semantics |
| native 함수 호출 전후 heap이 예상과 다름 | Python input/변환/출력의 libc allocation |
| free chunk가 작아지거나 다른 bin으로 이동 | wrapper 임시 객체가 split/reuse했는지 |
| 직접 실행만 성공하고 서비스에서 실패 | cwd, loader, buffering, `socat`/pipe 초기 상태 |
| local만 성공하고 remote에서 실패 | libc/Python/build 차이, hardcoded offset, timing/sync |
| 최종 함수 진입 직후 SIMD 명령에서 crash | ABI stack alignment |
| staged write 도중 조기 crash | 중간 invalid 상태가 callback/hook에서 사용됐는지 |

## 10. 완료 기준

- 취약점이 Python 계층, ABI 경계, native 계층 중 어디서 생기는지 명시합니다.
- primitive와 제한 조건을 exploit 코드의 주석 또는 writeup에 남깁니다.
- 주소 계산은 실제 leak과 대상 바이너리/libc 심볼에서 유도합니다.
- wrapper가 만드는 숨은 allocation을 포함한 상태 전이가 설명됩니다.
- local과 실제 배포 transport에서 반복 재현됩니다.
- remote exploit은 timeout, EOF, partial receive를 처리하고 단계별 실패 지점을 구분합니다.
