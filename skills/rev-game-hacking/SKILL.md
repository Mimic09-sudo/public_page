---
name: rev-game-hacking
description: 게임/시뮬레이션 바이너리 reversing을 담당합니다. Unity/Unreal/커스텀 엔진의 게임 로직, 치트 방지 우회, 세이브 포맷 해석, 리소스 추출, 게임 내 숨겨진 조건 분석을 수행합니다.
license: MIT
metadata:
  domain: ctf
  layer: rev
  subcategory: game-hacking
  language: ko
---

You must say "REV SKILL ACTIVE" once before analysis.

## Local execution base

Load and follow `ctf-wsl-toolchain` before local extraction, analysis, emulation, or patching. This skill controls the game-reversing methodology; `ctf-wsl-toolchain` controls WSL entry, installed binaries, Python runtime, paths, and tool discovery. Do not ask the user to operate the toolchain.

## 역할

- 게임 또는 시뮬레이션 형태의 reversing 문제를 전담합니다.
- Unity(IL2CPP/Mono), Unreal, Godot, 커스텀 엔진 등 게임 엔진 기반 바이너리를 분석합니다.
- 게임 로직 추출, 승리/클리어 조건 역추적, 세이브/리플레이 포맷 해석, 리소스(에셋) 추출을 수행합니다.
- 안티치트/무결성 검사 우회가 필요한 경우 최소한의 패치 또는 우회 경로를 찾습니다.

## Oracle 메타 실행 규칙

- 언제 load: 게임 엔진 기반 바이너리, 세이브/리플레이 조작, 게임 로직 역추적이 핵심일 때 load합니다.
- 같이 load할 skill: 네이티브 코드 추적은 `rev-static`, .NET 난독화 해제는 `rev-obfuscation`과 함께 진행합니다.
- 언제 안 load: 게임이 아닌 일반 바이너리라면 `rev-static`으로 전환합니다.

### 첫 10분 체크리스트

- **0-2분**: 엔진 시그니처(Unity/Unreal/Godot/커스텀)와 리소스 파일 구조를 식별합니다.
- **2-4분**: 입력 이벤트, 승리/실패 문자열, 상태 관리 클래스(GameManager류)를 문자열/xref로 고정합니다.
- **4-7분**: Update/Tick 루프와 상태 전이 지점을 찾아 클리어 조건 경로를 좁힙니다.
- **7-10분**: 세이브/리플레이/무결성 검사 유무를 판별하고 `rev-static`/`rev-obfuscation`/`rev-delivery` 연계 계획을 확정합니다.

- 산출물: 게임 로직 분석 결과(핵심 상태/조건), 조작된 세이브(해당 시), 패치본(필요 시)

## 사용할 때

- 문제 바이너리가 게임 또는 게임 엔진으로 빌드된 경우
- Unity `.dll`, `global-metadata.dat`, `level*`, `*.assets`, `*.bundle` 파일이 포함된 경우
- Unreal `.pak`, `.uasset`, `.umap` 파일이 존재하는 경우
- 세이브 파일 조작, 리플레이 조작, 인게임 치트 코드 발견이 핵심인 경우
- 간단한 게임(텍스트 어드벤처, 퍼즐, 미로)이지만 승리 조건이 숨겨져 있는 경우
- anti-cheat, integrity check, license validation이 게임 형태로 래핑된 경우

## 우선 원칙

- 게임 엔진을 먼저 식별합니다. 엔진에 따라 도구 체인이 완전히 달라집니다.
- 게임 로직과 엔진 코드를 분리합니다. 분석 대상은 게임 로직(스크립트, 씬, 이벤트)입니다.
- 승리/클리어 조건부터 역추적합니다. flag 출력, 스코어 조건, 숨겨진 씬 전환을 먼저 찾습니다.
- 리소스 추출은 목적이 있을 때만 수행합니다. 전체 에셋 덤프는 시간 낭비입니다.
- 패치는 최소 범위로 합니다. 게임 전체를 리빌드하지 않습니다.
- 이 skill은 **게임 형태 문제 전용**입니다. 일반 리버싱은 `rev-static`으로 전환합니다.

## 절차

### 1단계: 엔진 식별 및 구조 파악

```
필수 확인:
- 파일 구조에서 엔진 시그니처 확인
  - Unity: UnityPlayer.dll, Assembly-CSharp.dll, global-metadata.dat, *.assets
  - Unreal: *.pak, *.uasset, UnrealEngine 문자열
  - Godot: *.pck, project.godot
  - 커스텀: main loop 패턴, SDL/GLFW/raylib imports
- 스크립팅 레이어 확인
  - Unity Mono: .NET DLL → dnSpy/ILSpy로 직접 디컴파일
  - Unity IL2CPP: il2cppdumper → 메타데이터에서 클래스/메서드 복원
  - Unreal Blueprint: *.uasset에서 Blueprint 노드 추출
  - Lua/Python 임베디드: 스크립트 파일 직접 추출
- 빌드 설정 확인
  - Debug/Release, stripping 여부, 난독화 여부
```

### 2단계: 게임 로직 추출

```
엔진별 도구:
- Unity Mono: dnSpy, ILSpy, dotPeek → Assembly-CSharp.dll 분석
- Unity IL2CPP: il2cppdumper → dummy DLL 생성 → 오프셋 매핑 → IDA/Ghidra
- Unreal: UnrealPakTool, FModel, UAssetAPI → 에셋 추출 및 분석
- Godot: gdre_tools → .pck 추출, GDScript 디컴파일
- 커스텀 엔진: 일반 정적 분석 (rev-static으로 전환 가능)

핵심 추적 대상:
- 게임 상태 관리 클래스/구조체 (GameManager, LevelController 등)
- 입력 처리 (키 입력, 마우스, 터치)
- 조건 분기 (if score >= X, if allItemsCollected, if secretFound)
- 이벤트/콜백 (OnTriggerEnter, OnCollision, OnLevelComplete)
- 타이머/프레임 카운터 기반 로직
```

## Update Loop / Tick 기반 분석

- 게임 메인 루프를 `Init → Update → Render → Input` 순서로 분해해, 실제 조건 검증이 어디서 일어나는지 먼저 고정합니다.
- 대부분의 핵심 판정은 `Update` 함수에서 상태 전이로 처리되므로, 분기 조건과 상태 변수 변경 시점을 우선 추적합니다.
- Tick/Frame counter 기반 조건(특정 프레임 도달, N틱 유지, 쿨다운 종료)을 별도 표로 정리해 우회 또는 재현 경로를 선택합니다.

### 3단계: 승리/클리어 조건 역추적

```
flag 또는 성공 출력 지점에서 역방향 추적:
- 문자열 xref: "flag", "congratulations", "you win", "correct", "secret"
- 씬 전환: 특정 조건에서만 로드되는 숨겨진 씬/레벨
- 스코어/상태 조건: 불가능해 보이는 점수, 시간 제한, 아이템 조합
- 숨겨진 입력: 코나미 코드, 특정 키 조합, 좌표 기반 트리거
- 암호화된 에셋: 조건 충족 시 복호화되는 리소스

조건이 게임 내에서 정상적으로 달성 불가능한 경우:
→ 세이브 파일 조작, 메모리 패치, 또는 직접 복호화로 우회
```

### 4단계: 세이브/리플레이/설정 파일 분석

```
세이브 파일이 존재하는 경우:
- 포맷 식별: JSON, XML, binary, protobuf, custom serialization
- 체크섬/무결성 검사 확인 (CRC, HMAC, 커스텀 해시)
- 핵심 필드 식별: 레벨, 점수, 인벤토리, 플래그 비트
- 조작 후 로드 테스트

리플레이 파일이 존재하는 경우:
- 입력 시퀀스 포맷 파악
- 타임스탬프, 프레임 번호, 입력 이벤트 구조 분석
- 리플레이 조작으로 불가능한 상태 도달 시도
```

### 5단계: 안티치트/무결성 우회 (필요시)

```
일반적인 게임 보호 기법:
- 메모리 스캔 감지 (디버거 탐지와 유사)
- 값 변조 감지 (주기적 체크섬, 이중 저장)
- 서버 검증 (클라이언트만으로는 불완전)
- 코드 무결성 (섹션 해시 비교)

우회 전략:
- 체크 루틴 NOP 패치 (최소 범위)
- 체크섬 재계산 로직 역산
- 검증 우회보다 직접 복호화/역산 우선
- 서버가 있으면 프로토콜 분석 → solve.py에서 직접 통신
```

## State 동기화 / 네트워크 무결성

- 클라이언트-서버 상태 동기화 패턴(권한 모델, authoritative server 여부, 클라 예측/서버 보정)을 먼저 분리합니다.
- 네트워크 패킷 무결성 검사는 HMAC, 시퀀스 번호, nonce/타임스탬프 검증 순서로 확인합니다.
- 리플레이 공격은 시퀀스 재사용/윈도우 정책을 먼저 점검하고, 패킷 조작은 체크 필드 재계산 가능성 여부를 기준으로 전략을 선택합니다.

### 6단계: 자동화 및 solve.py 작성

```
자동화 전략 선택:
- 단순 복호화/역산: 플랫 solve.py
- 세이브 파일 조작: 파싱 → 수정 → 체크섬 재계산 → 저장
- 메모리 패치: patchelf 또는 바이너리 패치 스크립트
- 서버 통신: pwntools 기반 자동화
- 게임 시뮬레이션: 게임 상태기계를 Python으로 재구현

필수 출력:
- flag 문자열
- 패치가 필요한 경우 패치본 경로
- 세이브 조작인 경우 조작된 세이브 파일 경로
```

## 엔진별 도구 레퍼런스

```
Unity (Mono):
  분석: dnSpy, ILSpy, dotPeek
  에셋: AssetStudio, UABE (Unity Asset Bundle Extractor)
  패치: dnSpy (IL 편집), Harmony (런타임 패치)

Unity (IL2CPP):
  메타데이터: il2cppdumper
  분석: IDA/Ghidra + il2cppdumper 매핑
  에셋: AssetStudio

Unreal:
  추출: UnrealPakTool, quickbms + unreal_tournament_4.bms
  분석: FModel, UAssetAPI, UE4SS
  Blueprint: uasset serializer

Godot:
  추출: gdre_tools, godotdec
  분석: GDScript 디컴파일러

일반:
  에셋: quickbms (범용 추출), binwalk
  3D: Blender (모델 분석 필요시)
  오디오/이미지: ffmpeg, ImageMagick
```

## 규칙

- 엔진 식별 없이 분석을 시작하지 않습니다.
- 게임 로직과 엔진 프레임워크 코드를 명확히 구분합니다.
- 전체 에셋 덤프는 하지 않습니다. 목적이 있는 리소스만 추출합니다.
- Unity Mono의 경우 dnSpy가 IDA보다 우선입니다 (.NET이므로).
- IL2CPP의 경우 il2cppdumper 없이 IDA만으로 분석하지 않습니다.
- 세이브 파일 조작 시 반드시 체크섬/무결성 검사를 확인합니다.
- 패치 범위는 최소한으로 유지합니다. 불필요한 코드 수정은 하지 않습니다.
- 게임 실행이 필요하면 환경(OS, 라이브러리, GPU)을 먼저 확인합니다.
- 서버 연동 게임은 프로토콜 분석을 세이브 조작보다 우선합니다.
