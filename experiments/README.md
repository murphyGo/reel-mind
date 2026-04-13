# Experiments

AIDLC 프로세스 **밖의** 가설 검증 영역.

## 왜 분리되어 있나

`aidlc-docs/`의 정식 Construction은 검증된 요구사항을 견고하게 구현하기 위한 프로세스다. 반면 이 디렉토리는 **요구사항 자체가 검증되지 않은 단계**의 작업이다.

핵심 차이:
- AIDLC: 옳다고 합의된 것을 잘 만든다 (게이트 다수, 산출물 중심)
- experiments: 옳은지 모르는 것을 빨리 시험한다 (게이트 최소, 데이터 중심)

두 모드를 섞으면 둘 다 망가진다. 그래서 격리한다.

## 구조

```
experiments/
├── README.md                  # 이 파일
├── plan.md                    # 실험 운영 원칙, 결정 게이트
└── hypothesis-NN-{slug}/      # 개별 가설
    ├── README.md              # 가설, 성공 기준, 표준 템플릿
    ├── prompts/
    ├── scripts/
    ├── videos/
    └── data/
```

## 현재 활성 가설

- [hypothesis-01 — 외국인의 한국 음식 경험 다큐 숏폼](hypothesis-01-foreigners-korean-food/README.md)

## Graduation

가설이 통과(success criteria의 정의) 시:
1. `experiments/decisions.md`에 graduation 결정 기록
2. `aidlc-docs/construction/U1/` 산출물을 가설 결과 기준으로 **재작성** (단순 수정 아님)
3. 본격 U1 → U2 → U4 진행

가설이 실패 시:
1. `experiments/decisions.md`에 폐기 사유 기록
2. `hypothesis-02-{new-slug}/` 시작 또는 프로젝트 자체 재고

## 비-규칙 (이게 더 중요)

- **AIDLC 게이트 적용 금지** — 여기는 functional design / NFR / infrastructure design 단계 없다
- **재사용 가능한 abstraction 짓기 금지** — 가설마다 처음부터 다시 쓴다
- **타임박스 위반 금지** — 4주는 4주다, 5주가 아니다
