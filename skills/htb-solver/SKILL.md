---
name: htb-solver
description: HTB machine and challenge solving workflow
---
# HTB 문제 풀이 구조 명세서

작성일: 2026-05-30

## 입력 파일 판독 결과

이 명세서는 현재 폴더의 텍스트성 자료를 근거로 작성했다.

| 파일 | 판독 결과 | 명세서 반영 |
| --- | --- | --- |
| `cap.txt` | 0바이트. 대상 IP, 서비스, 캡처 로그, 플래그 단서 없음. | 실제 박스별 풀이 경로는 확정 불가. 범용 풀이 체계와 기록 규격 중심으로 작성. |
| `student-htb-solve-system.txt` | `student-htb-solve-system/` 디렉터리 구조와 11개 설계 목차 제공. | 본 문서의 기본 구조로 사용. |
| `machines_sg-1.ovpn` | OpenVPN 설정 파일. `remote edge-sg-free-1.hackthebox.eu 1337`, `proto udp`, `dev tun` 확인. 인증서/키 블록 포함. | HTB SG VPN 연결 환경으로 취급. 인증서, 개인키, tls-auth 내용은 보고서에 원문 노출 금지. |

현재 확정 가능한 것은 "HTB 풀이 운영 체계"이며, 특정 박스의 정답 경로는 아직 확정할 수 없다. 특정 박스 풀이를 진행하려면 최소한 박스명, 대상 IP, 시작 시각, VPN 연결 여부가 추가로 필요하다.

## 1. 목표와 적용 범위

### 목표

HTB 박스 또는 챌린지를 풀 때 다음 결과물이 항상 남도록 표준 절차를 정의한다.

- 재현 가능한 명령 실행 기록
- 발견한 서비스, 취약점, 자격 증명, 권한 상승 경로의 근거
- user/root 플래그 획득 과정
- 실패한 가설과 폐기 이유
- 최종 보고서와 재사용 가능한 `case.json`

### 적용 범위

이 체계는 다음 상황에만 적용한다.

- Hack The Box에서 명시적으로 허용된 개인 랩, 시즌 머신, 챌린지, 아카데미형 실습
- 사용자가 소유하거나 허가받은 CTF/훈련 환경
- VPN으로 연결된 단일 타깃 또는 문제에서 명시한 범위

### 범위 밖

다음 행위는 이 명세서의 대상이 아니며 수행하지 않는다.

- HTB 또는 문제에서 허용하지 않은 외부 IP, 도메인, 사용자 계정 공격
- 서비스 거부, 대량 트래픽, 파괴적 데이터 삭제
- 실제 서비스 계정에 대한 credential stuffing
- 랩 밖에서 재사용 가능한 비밀키, 토큰, 세션 쿠키 공개
- 은닉, 지속성 유지, 방어 우회 목적의 작업

## 2. 진입 기준과 금지 행동

### 풀이 시작 전 체크

풀이를 시작하기 전에 아래 항목이 모두 채워져야 한다.

| 항목 | 필수 여부 | 예시 |
| --- | --- | --- |
| 박스명 또는 문제명 | 필수 | `Cap`, `Oopsie`, `Active` |
| 대상 IP/URL | 필수 | `10.10.10.x` |
| 플랫폼 | 필수 | HTB Machine, HTB Challenge |
| 연결 방식 | 필수 | `machines_sg-1.ovpn` |
| 시작 시각 | 필수 | `2026-05-30T14:55:00+09:00` |
| 로컬 작업 폴더 | 필수 | `cases/<box-name>/` |
| 금지 범위 | 필수 | 대상 외 IP, HTB 인프라 관리 도메인, 타 사용자 자원 |

### 금지 행동

- 대상 IP 범위를 임의로 넓히지 않는다.
- `10.10.0.0/16`처럼 큰 범위 스캔을 기본값으로 사용하지 않는다.
- 크래시 유발 가능성이 큰 익스플로잇은 먼저 로컬 분석 또는 안전한 옵션으로 검증한다.
- 발견한 암호, 토큰, 키는 공개 보고서에 원문으로 적지 않는다.
- VPN 설정 파일의 `<cert>`, `<key>`, `<tls-auth>` 블록은 복사, 공유, 커밋하지 않는다.
- 플래그 제출 이후에도 불필요하게 타깃을 변경하지 않는다.

## 3. 전체 파이프라인

표준 진행 순서는 다음과 같다.

1. 케이스 초기화
2. VPN 연결 확인
3. 대상 생존 확인
4. 포트 및 서비스 식별
5. 서비스별 플레이북 선택
6. 초기 접근 가설 수립
7. 취약점 검증
8. foothold 획득
9. user 플래그 획득
10. 내부 정보 수집
11. 권한 상승 가설 수립
12. 권한 상승 실행
13. root 또는 administrator 플래그 획득
14. 증거 정리
15. 보고서 작성
16. `case.json` 지식화

각 단계는 성공, 실패, 보류 중 하나의 상태로 기록한다. 실패한 단계는 삭제하지 않고 폐기 근거를 남긴다.

## 4. 단계별 플레이북 라우팅

### `00_workflow.md`

공통 운영 절차를 담당한다.

- 케이스 폴더 생성
- 로그 파일 생성
- 타임라인 기록
- 명령 실행 규칙 적용
- 발견 사항과 가설 연결
- 보고서 생성 전 품질 점검

### `01_recon.md`

초기 정찰과 서비스 식별을 담당한다.

기본 순서:

```bash
ip addr show tun0
ping -c 2 <target>
nmap -Pn -p- --min-rate 3000 -oA scans/tcp-all <target>
nmap -Pn -sC -sV -p <ports> -oA scans/tcp-scv <target>
```

UDP는 TCP 결과가 막히거나 문제 성격상 필요할 때 제한적으로 수행한다.

```bash
nmap -Pn -sU --top-ports 100 -oA scans/udp-top100 <target>
```

기록해야 할 결과:

- 열린 포트
- 서비스명과 버전
- 운영체제 추정
- 스크립트 출력 중 인증, 경로, 배너, 도메인 단서
- 추가 라우팅이 필요한 서비스

### `02_web.md`

HTTP/HTTPS 서비스가 발견되면 적용한다.

기본 확인:

- 상태 코드, 제목, 서버 헤더
- 루트 페이지와 주요 링크
- `robots.txt`, `sitemap.xml`
- 소스 코드 주석
- 로그인, 업로드, 검색, 파일 다운로드, 리다이렉트
- 쿠키 속성, 세션 흐름
- vhost 또는 Host 헤더 기반 분기

권장 명령:

```bash
whatweb http://<target>/
curl -i http://<target>/
feroxbuster -u http://<target>/ -w <wordlist> -x php,txt,html,bak
```

웹 취약점 검증은 수동 재현을 우선한다. 자동화 도구 결과는 발견 후보로만 취급하고, 보고서에는 요청, 응답, 영향, 재현 조건을 함께 적는다.

### `03_privilege_escalation.md`

foothold 이후 권한 상승을 담당한다.

Linux 확인 항목:

```bash
id
hostname
ip addr
sudo -l
find / -perm -4000 -type f 2>/dev/null
getcap -r / 2>/dev/null
crontab -l 2>/dev/null
ls -la /etc/cron* 2>/dev/null
ss -tulpn
```

Windows 확인 항목:

```powershell
whoami /all
hostname
ipconfig /all
net user
net localgroup administrators
netstat -ano
schtasks /query /fo LIST /v
```

기록해야 할 단서:

- 현재 사용자와 그룹
- sudo 권한 또는 Windows privilege
- SUID, capability, writable path
- cron, timer, scheduled task
- 내부 서비스와 포트 포워딩 필요 여부
- 설정 파일에 남은 자격 증명
- 커널 또는 소프트웨어 버전 기반 CVE 후보

### `04_post_exploitation.md`

플래그 획득 후 정리를 담당한다.

- 플래그 파일 경로와 획득 사용자 기록
- 최종 권한 증거 기록
- 임시 파일을 만들었다면 본인 생성물만 제거
- 보고서에 민감 값 원문을 넣지 않도록 검토
- 재현 가능한 최소 경로로 공격 체인 압축

## 5. 실행 환경과 명령 실행 규칙

### 작업 폴더

케이스별 폴더는 아래 구조를 따른다.

```text
cases/<box-name>/
  case.json
  timeline.md
  progress.md
  notes.md
  scans/
  evidence/
  exploits/
  loot/
  report.md
```

### 명령 기록 규칙

모든 주요 명령은 실행 전후로 기록한다.

```text
[2026-05-30T15:00:00+09:00] command
cwd: cases/<box-name>
cmd: nmap -Pn -sC -sV -p 21,22,80 -oA scans/tcp-scv 10.10.10.x
result: success
artifact: scans/tcp-scv.nmap
finding: ftp anonymous login disabled, http Apache 2.4.x
```

### 증거 파일 규칙

- 원본 출력은 `scans/` 또는 `evidence/raw/`에 저장한다.
- 스크린샷은 `evidence/screenshots/`에 저장한다.
- exploit 코드 수정본은 `exploits/`에 저장한다.
- 자격 증명은 `loot/credentials.redacted.md`에 마스킹해서 적는다.
- 원문 비밀은 공개 보고서에 포함하지 않는다.

### VPN 규칙

현재 폴더의 `machines_sg-1.ovpn`은 HTB SG free VPN 프로필로 보인다.

확인된 비민감 설정:

```text
client
dev tun
proto udp
remote edge-sg-free-1.hackthebox.eu 1337
auth SHA256
```

연결 확인은 다음 순서로 한다.

```bash
sudo openvpn --config machines_sg-1.ovpn
ip addr show tun0
ip route
```

보고서에는 VPN 개인키, 인증서, tls-auth 블록을 절대 붙여넣지 않는다.

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
- Box: TBD
- Target: TBD
- VPN: machines_sg-1.ovpn

## Current State
- Recon: not_started
- Foothold: not_started
- User flag: not_started
- Privilege escalation: not_started
- Root flag: not_started

## Next Actions
- 대상 IP 확정
- VPN 연결 확인
- TCP full scan 실행
```

## 7. 기록 이벤트 규격

모든 중요한 사건은 `timeline.md`에 이벤트로 남긴다.

### 이벤트 타입

| 타입 | 목적 |
| --- | --- |
| `scope` | 범위, IP, 플랫폼 확정 |
| `command` | 주요 명령 실행 |
| `finding` | 의미 있는 발견 |
| `hypothesis` | 공격 또는 권한 상승 가설 |
| `credential` | 자격 증명 후보 발견 |
| `exploit` | 취약점 검증 또는 사용 |
| `flag` | 플래그 획득 |
| `blocker` | 진행 차단 사유 |
| `decision` | 경로 선택 이유 |

### 이벤트 형식

```markdown
## 2026-05-30T15:10:00+09:00 - finding

- Stage: recon
- Source: scans/tcp-scv.nmap
- Summary: HTTP service found on 80/tcp
- Evidence: Apache version banner and default page title
- Impact: route to web playbook
- Next: run web enumeration
```

## 8. 보고서 템플릿

최종 보고서는 아래 순서를 따른다.

```markdown
# <Box Name> HTB Writeup

## Summary
- Platform:
- Difficulty:
- Target:
- Start:
- End:
- Result:

## Scope
- Authorized target:
- VPN:
- Out of scope:

## Attack Path
1. Recon identified ...
2. Web enumeration found ...
3. Foothold obtained via ...
4. Privilege escalation via ...

## Recon
### Port Scan
- Command:
- Result:
- Evidence:

### Service Notes
| Port | Service | Version | Notes |
| --- | --- | --- | --- |

## Foothold
- Vulnerability:
- Preconditions:
- Exploit steps:
- Evidence:
- User obtained:

## User Flag
- Path:
- Proof:

## Privilege Escalation
- Local enumeration:
- Weakness:
- Exploit steps:
- Evidence:
- Final user:

## Root Flag
- Path:
- Proof:

## Lessons Learned
- What worked:
- What failed:
- Reusable checks:

## Appendix
- Key commands:
- Artifacts:
- Redacted credentials:
```

## 9. `case.json` 지식화 스키마

`case.json`은 다음 필드를 유지한다.

```json
{
  "schema_version": "1.0",
  "case": {
    "name": "TBD",
    "platform": "Hack The Box",
    "type": "machine",
    "status": "blocked",
    "created_at": "2026-05-30T00:00:00+09:00",
    "updated_at": "2026-05-30T00:00:00+09:00"
  },
  "scope": {
    "target": null,
    "allowed_hosts": [],
    "vpn_profile": "machines_sg-1.ovpn",
    "notes": "cap.txt is empty; target is not yet defined."
  },
  "environment": {
    "vpn_remote": "edge-sg-free-1.hackthebox.eu:1337",
    "vpn_proto": "udp",
    "tun_interface": "tun0"
  },
  "services": [],
  "findings": [],
  "hypotheses": [],
  "credentials": [],
  "artifacts": [],
  "flags": {
    "user": {
      "status": "not_started",
      "path": null,
      "value_redacted": null
    },
    "root": {
      "status": "not_started",
      "path": null,
      "value_redacted": null
    }
  },
  "next_actions": [
    "Fill box name and target IP",
    "Connect VPN",
    "Run initial TCP scan"
  ]
}
```

### 자격 증명 저장 규칙

자격 증명 항목은 원문 대신 마스킹 또는 참조로 저장한다.

```json
{
  "type": "password",
  "username": "user",
  "secret_ref": "loot/credentials.local.md",
  "redacted": "P@ssw***",
  "source": "config.php",
  "validated": true,
  "scope": "target-only"
}
```

## 10. 완료 기준과 품질 체크리스트

### 완료 기준

머신 풀이 완료 조건:

- 대상 범위가 명확히 기록됨
- 초기 정찰 결과가 저장됨
- foothold 획득 과정이 재현 가능함
- user 플래그 획득 증거가 있음
- 권한 상승 과정이 재현 가능함
- root 또는 administrator 플래그 획득 증거가 있음
- 최종 보고서에 민감 정보가 마스킹됨
- `case.json`에 핵심 지식이 구조화됨

챌린지 풀이 완료 조건:

- 문제 파일, 입력값, 실행 환경 기록
- 취약점 또는 풀이 아이디어 설명
- 재현 스크립트 또는 수동 절차 기록
- 플래그 도출 근거 기록

### 품질 체크리스트

- [ ] 모든 주장에 명령 출력, 파일, 스크린샷 중 하나 이상의 근거가 있다.
- [ ] 실패한 시도도 핵심 경로 판단에 영향을 줬다면 기록했다.
- [ ] 자동화 도구 결과를 수동으로 검증했다.
- [ ] 공개 가능한 보고서에서 VPN 키, 토큰, 쿠키, 실제 비밀값을 제거했다.
- [ ] 명령어는 복사해서 재실행 가능한 형태다.
- [ ] 최종 공격 경로가 최소 단계로 정리되어 있다.
- [ ] 다음에 비슷한 박스를 풀 때 재사용할 체크가 `case.json`에 남아 있다.

## 11. 현재 폴더 샘플 적용 결과

현재 폴더 기준으로 가능한 초기 상태는 다음과 같다.

```json
{
  "case": {
    "name": "TBD",
    "status": "blocked",
    "blocker": "cap.txt is empty and no target IP or box name is available"
  },
  "known_inputs": {
    "cap_txt": "empty",
    "system_outline": "student-htb-solve-system.txt",
    "vpn_profile": "machines_sg-1.ovpn"
  },
  "confirmed_environment": {
    "vpn_remote": "edge-sg-free-1.hackthebox.eu:1337",
    "vpn_proto": "udp",
    "vpn_device": "tun"
  },
  "next_actions": [
    "박스명과 대상 IP를 입력한다.",
    "VPN 연결 후 tun0 인터페이스를 확인한다.",
    "케이스 폴더를 생성한다.",
    "TCP full scan과 service scan을 실행한다."
  ]
}
```

따라서 이 시점의 결론은 다음과 같다.

- 실제 문제 풀이 보고서는 아직 작성할 수 없다.
- 대신 HTB 풀이를 안정적으로 진행하기 위한 표준 명세서는 확정 가능하다.
- `cap.txt`에 대상 정보나 캡처 내용이 추가되면 이 명세서의 `case.json`, `progress.md`, `report.md`를 실제 박스 기준으로 채우면 된다.
