# Setup Checklist

본인이 직접 해야 할 작업. 첫 영상 만들기 전에 1회만.

## 1. YouTube 채널
- [ ] 새 Google 계정 생성 (메인 계정과 분리 권장)
- [ ] YouTube 채널 생성
- [ ] 채널 이름 결정 (TBD — Day 1 회의)
- [ ] 채널 한 줄 소개 (TBD)
- [ ] 채널 아트 (5개 이상 발행 후로 미뤄도 OK)

## 2. API 키 발급
- [ ] **Anthropic API** — 기존 키 사용
- [ ] **Pexels API** — https://www.pexels.com/api/ (무료, 즉시 발급)
- [ ] Reddit은 인증 불필요 (공개 JSON 엔드포인트 사용)

## 3. TypeCast 계정
- [ ] 가입: https://typecast.ai/
- [ ] 무료 체험: 약 3,000자 (~5개 영상 분량)
- [ ] 보이스 후보 시청 후 1개 고정:
  - 호빈 (차분/지적)
  - 진우 (다큐멘터리)
  - 도윤 (정보 전달)
- [ ] Day 2까지 1개 보이스로 락인

## 4. 로컬 환경
- [ ] Python 3.12 확인
- [ ] ffmpeg 설치: `brew install ffmpeg`
- [ ] `pip install -r requirements.txt`

## 5. 환경 변수
```bash
cp .env.example .env
# .env 파일 열어서 ANTHROPIC_API_KEY, PEXELS_API_KEY 채우기
```

## 6. 첫 테스트 (smoke test)
```bash
# 1. r/koreatravel 또는 r/KoreanFood에서 글 1-3개 골라
mkdir -p videos/000-smoke
# 2. videos/000-smoke/sources.json 에 아래 형식으로 저장
#    [{"url": "...", "title": "...", "content": "..."}, ...]

# 3. 스크립트 생성
python scripts/generate_script.py 000-smoke

# 4. videos/000-smoke/script.txt 를 TypeCast에 붙여넣고
#    audio.mp3 로 받아서 videos/000-smoke/audio.mp3 에 저장

# 5. 영상 합성
python scripts/assemble_video.py 000-smoke

# 6. videos/000-smoke/final.mp4 확인
```

## v0.1 의도적 비포함 (수동 처리 또는 v0.2)
- BGM: YouTube Studio 업로드 후 추가 또는 외부 편집기 사용
- 썸네일: YouTube가 자동 생성하는 거 그대로 사용 (Week 3에 재평가)
- Reddit 자동 크롤링: 큐레이션 품질 위해 v0.1은 수동 선정

## Decisions to lock in Week 1
`README.md`의 "미결정 사항" 섹션 참조.
