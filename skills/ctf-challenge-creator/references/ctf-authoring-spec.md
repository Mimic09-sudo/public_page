# CTF Authoring Specification Reference

## Reference Table Of Contents

- 1. 목표와 적용 범위
- 2. 진입 기준과 금지 행동
- 3. 전체 파이프라인
- 4. 단계별 플레이북 라우팅
- 5. 실행 환경과 명령 실행 규칙
- 6. 상태 저장 구조
- 7. 기록 이벤트 규격
- 8. 보고서 템플릿
- 9. `case.json` 지식화 스키마
- 10. 완료 기준과 품질 체크리스트
- 11. 샘플 문제 적용 결과


작성일: 2026-06-08

## 입력 구조 해석 결과

이 문서는 `student-htb-solve-system/`의 풀이 운영 구조를 CTF 문제 제작 운영 구조로 변환한 명세서다. 핵심 원칙은 다음과 같다.

- HTB 풀이의 "정찰 → 검증 → 익스플로잇 → 보고서" 흐름을 CTF 제작의 "기획 → 구현 → 검증 풀이 → 배포 → 보고서" 흐름으로 대응한다.
- 로그 기록과 보고서 작성은 HTB 풀이 전용 절차가 아니라 모든 CTF 문제 제작에 필수로 적용한다.
- 문제 파일, 빌드 산출물, 배포 산출물, 플래그, 의도 풀이, 검증 로그를 분리해서 관리한다.
- 공개 배포물에는 소스, 플래그 원문, 생성 시드, 내부 키, author-only 노트를 포함하지 않는다.

## 1. 목표와 적용 범위

### 목표

CTF 문제를 만들 때 다음 결과물이 항상 남도록 표준 절차를 정의한다.

- 문제 기획 의도와 카테고리, 난이도, 대상 학습 포인트
- 재현 가능한 빌드 기록과 배포 패키지
- 의도 풀이 경로와 검증 가능한 solver
- 난이도 조정과 힌트 설계 근거
- 실패한 설계안과 폐기 이유
- 공개용 writeup과 운영용 author report
- 재사용 가능한 `case.json`

### 적용 범위

이 체계는 다음 제작 작업에 적용한다.

- CTF 대회 문제 제작
- 내부 교육용 보안 문제 제작
- 로컬 실습용 리버싱, 포렌식, 웹, 암호, pwn, misc 문제 제작
- 사용자가 소유하거나 허가받은 인프라에서 실행되는 문제 환경 제작

### 범위 밖

다음 행위는 이 명세서의 대상이 아니며 수행하지 않는다.

- 제3자 서비스, 실제 계정, 실제 데이터를 공격 대상으로 삼는 문제
- 참가자 시스템에 피해를 주는 악성 동작
- 지속성 유지, 은닉, 전파, 실제 랜섬웨어 동작
- 실서비스 credential stuffing 또는 외부 IP 스캔 유도
- 배포물에 개인키, API 토큰, 실제 비밀번호, 내부 주소를 포함하는 행위

## 2. 진입 기준과 금지 행동

### 제작 시작 전 체크

| 항목 | 필수 여부 | 예시 |
| --- | --- | --- |
| 문제명 | 필수 | `Ransom`, `Baby Login`, `Broken RSA` |
| 카테고리 | 필수 | rev, web, pwn, crypto, forensics, misc |
| 목표 난이도 | 필수 | easy, medium, hard |
| 대상 참가자 수준 | 필수 | 입문자, 중급자, 고급자 |
| 핵심 풀이 아이디어 | 필수 | anti-debug 우회 후 복호화 키 복구 |
| 플래그 형식 | 필수 | `SCA{...}` |
| 로컬 작업 폴더 | 필수 | `cases/<challenge-name>/` |
| 배포 방식 | 필수 | 파일 배포, Docker 서비스, remote service |
| 금지 범위 | 필수 | 외부 네트워크 공격, 실제 파일 파괴, 비밀 원문 공개 |

### 금지 행동

- 참가자 PC의 실제 파일을 암호화, 삭제, 변조하지 않는다.
- 네트워크 전파, 지속성 등록, 권한 탈취 기능을 넣지 않는다.
- 의도 풀이와 무관한 위험 기능을 장식 목적으로 넣지 않는다.
- 공개 배포물에 플래그 원문, 생성 스크립트 시드, author note를 포함하지 않는다.
- 외부 API, 실제 계정, 개인 서버에 의존하는 문제를 기본값으로 만들지 않는다.
- 참가자 풀이가 대회 인프라 밖의 대상을 공격하도록 설계하지 않는다.
- 검증되지 않은 난독화, 패킹, exploit 코드를 그대로 배포하지 않는다.

## 3. 전체 파이프라인

표준 제작 순서는 다음과 같다.

1. 케이스 초기화
2. 문제 목표와 카테고리 확정
3. 핵심 취약점 또는 풀이 아이디어 설계
4. 플래그 형식과 생성 방식 확정
5. 위협 모델과 안전 제한 정의
6. 문제 원본 구현
7. 빌드 및 패키징 자동화
8. 의도 solver 작성
9. 클린 환경에서 검증 풀이
10. 비의도 풀이와 과도한 guess 가능성 점검
11. 힌트와 난이도 조정
12. 배포 산출물 생성
13. 공개 파일 민감정보 점검
14. 운영 로그와 증거 정리
15. author report 작성
16. 공개 writeup 작성
17. `case.json` 지식화

각 단계는 성공, 실패, 보류 중 하나의 상태로 기록한다. 실패한 설계와 폐기한 접근도 삭제하지 않고 `timeline.md`에 남긴다.

## 4. 단계별 플레이북 라우팅

### `00_workflow.md`

공통 운영 절차를 담당한다.

- 케이스 폴더 생성
- `timeline.md`, `progress.md`, `notes.md` 생성
- 명령 실행 로그와 빌드 로그 저장
- author-only 자료와 public 자료 분리
- 산출물 체크섬 기록
- 보고서 작성 전 품질 점검

로그와 보고서는 모든 문제 제작에서 필수다. 파일 배포형, 서버형, 리버싱, 웹, 포렌식, 암호 문제 모두 동일하게 적용한다.

### `01_concept_design.md`

문제 기획과 풀이 경로 설계를 담당한다.

- 카테고리와 난이도 설정
- 참가자가 배워야 할 핵심 개념 정의
- 의도 풀이 단계 설계
- false lead와 힌트 설계
- 플래그 위치와 획득 조건 정의
- 안전 제한과 금지 동작 확인

### `02_challenge_build.md`

문제 구현, 빌드, 패키징을 담당한다.

- 소스 코드 작성
- 생성 스크립트 작성
- Dockerfile 또는 빌드 스크립트 작성
- 배포 파일 생성
- 공개/비공개 파일 분리
- 체크섬과 버전 기록
- 빌드 로그 저장

### `03_validation_and_solve.md`

의도 풀이 검증과 품질 검사를 담당한다.

- author solver 작성
- 클린 환경에서 배포 파일만으로 풀이
- 플래그 획득 재현
- 비의도 풀이 가능성 점검
- 난이도와 소요 시간 측정
- 검증 로그와 증거 저장

### `04_release_and_maintenance.md`

배포, 운영, 사후 정리를 담당한다.

- 최종 배포 패키지 생성
- 공개 설명문과 힌트 작성
- 문제 서버 실행 절차 기록
- 운영 중 장애 대응 기록
- 공개 writeup과 author report 정리
- 재사용 가능한 교훈을 `case.json`에 반영

## 5. 실행 환경과 명령 실행 규칙

### 작업 폴더

케이스별 폴더는 아래 구조를 따른다.

```text
cases/<challenge-name>/
  case.json
  timeline.md
  progress.md
  notes.md
  src/
  build/
  dist/
  private/
  solver/
  evidence/
  logs/
  report.md
  writeup.md
```

### 폴더 역할

| 경로 | 목적 |
| --- | --- |
| `src/` | 문제 원본 소스 |
| `build/` | 중간 빌드 산출물 |
| `dist/` | 참가자에게 배포할 최종 파일 |
| `private/` | 플래그 원문, 생성 시드, author-only 자료 |
| `solver/` | 의도 풀이 스크립트와 검증 코드 |
| `evidence/` | 스크린샷, 풀이 증거, 해시 |
| `logs/` | 빌드, 실행, 검증 로그 |
| `report.md` | 운영용 author report |
| `writeup.md` | 공개 가능한 writeup |

### 명령 기록 규칙

모든 주요 명령은 실행 전후로 기록한다.

```text
[2026-06-08T15:00:00+09:00] command
cwd: cases/<challenge-name>
cmd: make clean && make release
result: success
artifact: dist/<challenge-name>.zip
log: logs/build-20260608-150000.log
finding: release package generated without private files
```

### 필수 로그

| 로그 | 필수 여부 | 예시 |
| --- | --- | --- |
| 제작 타임라인 | 필수 | `timeline.md` |
| 진행 상태 | 필수 | `progress.md` |
| 빌드 로그 | 필수 | `logs/build-*.log` |
| 검증 풀이 로그 | 필수 | `logs/solve-*.log` |
| 배포물 해시 | 필수 | `evidence/checksums.txt` |
| 민감정보 점검 결과 | 필수 | `logs/release-audit-*.log` |

## 6. 상태 저장 구조

`progress.md`는 사람이 읽는 진행판, `case.json`은 재사용 가능한 구조화 데이터로 사용한다.

### 상태 값

| 상태 | 의미 |
| --- | --- |
| `not_started` | 아직 착수 전 |
| `in_progress` | 진행 중 |
| `blocked` | 필수 정보 부족 또는 외부 상태 대기 |
| `validated` | 재현 성공 |
| `discarded` | 실패 또는 근거 부족으로 폐기 |
| `complete` | 해당 단계 완료 |

### 진행판 예시

```markdown
# Progress

## Scope
- Challenge: TBD
- Category: rev
- Difficulty: medium
- Flag format: SCA{...}

## Current State
- Concept: not_started
- Build: not_started
- Solver: not_started
- Validation: not_started
- Release: not_started
- Report: not_started

## Next Actions
- 핵심 풀이 아이디어 확정
- 플래그 생성 방식 결정
- 케이스 폴더 생성
```

## 7. 기록 이벤트 규격

모든 중요한 사건은 `timeline.md`에 이벤트로 남긴다.

### 이벤트 타입

| 타입 | 목적 |
| --- | --- |
| `scope` | 문제명, 카테고리, 난이도, 배포 방식 확정 |
| `decision` | 설계 선택과 이유 |
| `command` | 주요 명령 실행 |
| `build` | 빌드 또는 패키징 |
| `finding` | 의미 있는 구현/검증 발견 |
| `risk` | 안전성, 의도치 않은 풀이, 민감정보 위험 |
| `solver` | 의도 풀이 구현 또는 실행 |
| `validation` | 클린 환경 검증 |
| `release` | 배포 산출물 생성 |
| `blocker` | 진행 차단 사유 |
| `report` | 보고서 작성 또는 검토 |

### 이벤트 형식

```markdown
## 2026-06-08T15:10:00+09:00 - validation

- Stage: solve-check
- Source: logs/solve-20260608-151000.log
- Summary: Solver recovered the expected flag from dist files only
- Evidence: solver/output.txt and evidence/flag-proof.redacted.txt
- Impact: intended path is reproducible
- Next: run release audit
```

## 8. 보고서 템플릿

최종 author report는 아래 순서를 따른다.

```markdown
# <Challenge Name> CTF Author Report

## Summary
- Category:
- Difficulty:
- Flag format:
- Release type:
- Result:

## Design Goal
- Learning objective:
- Intended vulnerability or trick:
- Expected solve path:

## Safety Scope
- Allowed behavior:
- Explicitly blocked behavior:
- Sensitive files:

## Build
- Source:
- Build command:
- Artifacts:
- Checksums:

## Validation
- Solver:
- Clean environment:
- Result:
- Evidence:

## Release Audit
- Public files:
- Private files excluded:
- Secret scan result:

## Hints
- Hint 1:
- Hint 2:
- Release condition:

## Lessons Learned
- What worked:
- What failed:
- Reusable checks:
```

공개 writeup은 참가자에게 공개 가능한 내용만 포함한다. 플래그 원문, 내부 시드, private 자료, 운영 계정, 인프라 토큰은 공개 writeup에 넣지 않는다.

## 9. `case.json` 지식화 스키마

`case.json`은 다음 필드를 유지한다.

```json
{
  "schema_version": "1.0",
  "case": {
    "name": "TBD",
    "category": "rev",
    "difficulty": "medium",
    "status": "blocked",
    "created_at": "2026-06-08T00:00:00+09:00",
    "updated_at": "2026-06-08T00:00:00+09:00"
  },
  "design": {
    "learning_objective": null,
    "intended_path": [],
    "anti_goals": [],
    "estimated_solve_time_minutes": null
  },
  "safety": {
    "allowed_environment": "local CTF lab only",
    "forbidden_behaviors": [],
    "external_dependencies": []
  },
  "flag": {
    "format": "SCA{...}",
    "source_ref": "private/flag.local.txt",
    "value_redacted": null,
    "placement": null
  },
  "artifacts": {
    "source": [],
    "private": [],
    "dist": [],
    "checksums": []
  },
  "build": {
    "commands": [],
    "logs": [],
    "status": "not_started"
  },
  "validation": {
    "solver": null,
    "logs": [],
    "status": "not_started",
    "clean_environment": null
  },
  "release": {
    "package": null,
    "public_description": null,
    "hints": [],
    "status": "not_started"
  },
  "reports": {
    "author_report": "report.md",
    "public_writeup": "writeup.md",
    "status": "not_started"
  },
  "next_actions": [
    "Fill challenge name and category",
    "Define intended solve path",
    "Create reproducible build script"
  ]
}
```

### 민감정보 저장 규칙

민감한 값은 원문 대신 마스킹 또는 참조로 저장한다.

```json
{
  "type": "flag",
  "secret_ref": "private/flag.local.txt",
  "redacted": "SCA{ab***}",
  "source": "generate_flag.py",
  "included_in_dist": false
}
```

## 10. 완료 기준과 품질 체크리스트

### 완료 기준

문제 제작 완료 조건:

- 문제 범위와 카테고리가 명확히 기록됨
- 핵심 풀이 아이디어와 의도 경로가 기록됨
- 빌드가 재현 가능함
- 배포 파일이 `dist/`에 정리됨
- 배포 파일만으로 solver가 플래그를 획득함
- 클린 환경 검증 로그가 있음
- 공개 배포물에서 민감정보가 제거됨
- author report와 공개 writeup이 작성됨
- `case.json`에 핵심 지식이 구조화됨

### 품질 체크리스트

- [ ] 모든 주요 명령과 결과가 `timeline.md` 또는 `logs/`에 남아 있다.
- [ ] 빌드 명령은 복사해서 재실행 가능한 형태다.
- [ ] 배포 패키지는 `dist/` 파일만 포함한다.
- [ ] `private/` 자료가 배포물에 섞이지 않았다.
- [ ] 플래그 원문은 공개 보고서와 공개 저장소에 포함되지 않았다.
- [ ] solver는 배포 파일만 사용한다.
- [ ] 비의도 풀이 가능성을 최소 1회 점검했다.
- [ ] 문제 난이도와 힌트가 의도 풀이에 맞게 조정됐다.
- [ ] author report와 public writeup이 모두 존재한다.
- [ ] 다음 문제 제작에 재사용할 체크가 `case.json`에 남아 있다.

## 11. 샘플 문제 적용 결과

새 문제를 아직 특정하지 않은 초기 상태는 다음과 같다.

```json
{
  "case": {
    "name": "TBD",
    "status": "blocked",
    "blocker": "challenge name, category, and intended solve path are not yet defined"
  },
  "known_inputs": {
    "system_outline": "student-ctf-create-system",
    "mandatory_outputs": [
      "timeline.md",
      "progress.md",
      "logs/",
      "report.md",
      "writeup.md",
      "case.json"
    ]
  },
  "next_actions": [
    "문제명과 카테고리를 입력한다.",
    "의도 풀이 경로를 확정한다.",
    "케이스 폴더를 생성한다.",
    "빌드와 solver 검증 로그를 남긴다."
  ]
}
```

따라서 이 시점의 결론은 다음과 같다.

- 특정 문제의 구현은 아직 확정하지 않는다.
- 대신 CTF 문제 제작을 안정적으로 진행하기 위한 표준 명세서는 확정 가능하다.
- 문제명, 카테고리, 플래그 형식, 의도 풀이가 정해지면 이 명세서의 `case.json`, `progress.md`, `report.md`, `writeup.md`를 실제 문제 기준으로 채운다.
