# Experimentation Plan

**작성일**: 2026-04-14
**활성 가설**: hypothesis-01

## 목적

본격 인프라 (Supabase, R2, GHA matrix, Web UI, Telegram, adapter framework 등) 투자 전에 **"한국어 단일 주제 자동 숏폼 채널이 살아남고 의미 있는 도달을 만들 수 있는가"** 를 데이터로 답한다.

이 답이 나오기 전에 짓는 모든 인프라는 **추측에 기반한 매몰 비용**이 될 위험이 있다.

## 원칙

1. **AIDLC 프로세스 밖** — Functional Design / NFR / Infrastructure Design 단계 없음
2. **타임박스** — 4주 fixed. 1회에 한해 4주 연장 허용 (단, 사전 정의된 조건 충족 시만)
3. **변수 최소화** — 한 번에 한 변수만 바꾼다. 비교 가능한 데이터 확보가 목적
4. **재사용 abstraction 금지** — 가설마다 코드 다시 씀. Claude 토큰으로 지원
5. **결과 기록은 markdown + CSV** — DB / Web UI 짓지 않음

## 짓지 않는 것 (유혹 차단 리스트)

이 리스트가 흔들리면 실험은 실패한다.

- ❌ Supabase
- ❌ Cloudflare R2 (로컬 파일 + YouTube가 스토리지)
- ❌ Telegram 봇 (수동 검토)
- ❌ Next.js / Web UI (Google Sheet)
- ❌ GitHub Actions (로컬 실행)
- ❌ Adapter framework (단일 플랫폼 하드코딩)
- ❌ StyleProfile 추출 시스템 (프롬프트 수동 작성)
- ❌ Cost ledger 시스템 (스프레드시트)
- ❌ Idempotency / run_id 시스템 (수동 관리)
- ❌ Pipeline A / C (Pipeline B의 수동 버전만)

## 짓는 것

- `generate.py`: 토픽 → 스크립트 (Claude API) → TTS → ffmpeg 합성 → mp4
- `metrics.csv`: 영상별 데이터 수기 입력 템플릿
- 영상별 `log.md`: 제작 시간, 비용, 결정 사항 기록

총 코드량 **~300줄 이내** 목표. 초과 시 abstraction 유혹에 빠진 신호.

## 실험 사이클

```
Phase 1 (현재): hypothesis-01 — 외국인의 한국 음식 경험
  ↓ (4주)
결정 게이트
  ├─ Pass → U1 재설계 후 본격 진행
  ├─ Fail → hypothesis-02 (다른 가설)
  └─ Mixed → 4주 연장 (1회만 허용)
```

## 결정 게이트 (가설 공통)

각 가설의 성공 기준은 가설 README에 정의되지만, 공통 판정 룰:

| 결과 패턴 | 결정 |
|----------|------|
| 5개 지표 중 **3개 이상 Pass** | U1 재설계 단계로 graduation |
| **2개 이하 Pass** | 가설 폐기. 다음 가설 또는 프로젝트 재고 |
| **3-4개 Pass + 한 변수 조정으로 개선 가능 명백** | 4주 연장 1회 허용 (조건 명시) |

연장은 한 번뿐이다. 두 번째 "한 번만 더"는 금지.

## 위험 등록부

| 위험 | 대응 |
|------|------|
| 채널 cold start로 데이터가 콘텐츠 품질이 아닌 채널 신규성 때문일 가능성 | 절대 평균 대신 **영상 간 상대 비교**로 신호 추출 |
| 운영자 번아웃 / 4주 못 채움 | Week 2 끝 mid-checkpoint. 미달 시 즉시 일정 재조정 |
| YouTube 정책 위반 (수익화 거절, reused content 경고, AI slop) | 첫 5개 영상 후 채널 상태 확인. 경고 시 즉시 중단 후 재설계 |
| 저작권 클레임 (DMCA strike) | 4주간 0건이어야 함. 1건이라도 오면 가설 폐기 |
| 실험이 어느 순간 "그냥 채널 운영"으로 변질 | 매주 회고 (`decisions.md`) 강제. "이건 실험인가, 운영인가" 자문 |
| 1차 가설 실패 시 의욕 상실 | 가설 폐기는 **실패가 아니라 데이터 획득**임을 사전 명시 |

## 회고 / 결정 로그

- `experiments/decisions.md` — 매주 1회 회고 + 모든 graduation/폐기 결정
- 가설별 `videos/NNN-{slug}/log.md` — 영상 제작 단위 결정 사항

## 기존 AIDLC U1 산출물과의 관계

`aidlc-docs/construction/U1/functional-design/`의 산출물은:

- **삭제하지 않는다** — 사고 결과는 자산
- **수정하지 않는다** — 가설 검증 후 재작성 대상
- **참조 자료로 강등** — 가설 결과로 검증/반박될 후보군

가설 graduation 시점에 어떤 부분이 살아남고 어떤 부분이 폐기/수정되는지 명시적으로 결정한다.
