# <문제명> 문제 설명

## 문제 분야
- <reversing/web/pwn/crypto/forensics/misc>

## 문제 설명

참가자에게 공개할 문제 설명을 작성한다.

## 배포 파일
- `dist/<artifact>`

## Flag
- 상태: 사용자 입력 대기
- private 참조: `private/flag.local.txt`

## 풀이 코드
- 경로: `solver/solve.py`
- 실행: `python3 solver/solve.py`

## 풀이 설명

1. 핵심 단서를 확인한다.
2. 문제 구조를 분석한다.
3. Solver 또는 수동 절차로 플래그를 복구한다.
4. 실제 문제 파일에서 검증한다.

## 검증 방법

```bash
make validate
```

`make validate`가 build, solver, 실제 artifact acceptance, audit를 모두 통과해야 완료로 본다.
