# skinloop-be

SkinLoop의 백엔드 (FastAPI).

- **session/records/demo**: DB(SQLAlchemy) 기반. 이 레포에서 구현.
- **patterns/whatif**: AI 분석을 **in-process**로 호출(`src.habit_pattern`·`src.whatif`) +
  `llm_formatter`로 문장화. `src/`는 `../skinloop-ai/src`의 복사본이다.

## 로컬 실행

```bash
cd skinloop-be
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 로컬은 DATABASE_URL 미설정 시 SQLite(sqlite:///./skinloop.db) 사용.
# 최초 1회 테이블 생성(로컬 편의용. 프로덕션 스키마는 사람이 수동 적용):
python -c "from app.db import init_db; init_db()"

uvicorn app.main:app --reload --port 8000
```

- 헬스체크: http://localhost:8000/health · API 문서: http://localhost:8000/docs
- `src/`를 찾지 못하면 앱은 정상 부팅되고 patterns/whatif만 **503 AI_UNAVAILABLE**로 응답한다.

## 테스트

```bash
pytest              # 인메모리 SQLite, 테스트마다 격리 (session/records/demo/seed/skin_score)
```

통계 계산 자체의 검증은 `skinloop-ai/`의 테스트가 맡는다(여기선 API 계약과 폴백을 확인).

## 구조

```
app/
├─ main.py            FastAPI 앱 + CORS + 예외 핸들러(400/{error} 변환) + 라우터 등록
├─ config.py          환경변수(DATABASE_URL, CORS_ORIGINS)
├─ db.py              SQLAlchemy 엔진/세션/Base. init_db()는 로컬·테스트용
├─ models.py          모델 4테이블(sessions·records·analyses·experiments), 포터블 타입
├─ schemas.py         DB 스키마(CamelModel) + AI-payload 스키마(RecordsPayload 등)
├─ deps.py            get_db · require_session(X-Anon-Token → 세션, 401)
├─ skin_score.py      calc_skin_score (spec §3)
├─ seed.py            28일치 시드 생성 + 완료 실험 1건 (spec §7)
├─ llm_formatter.py   계산 결과 → 한국어 문장화 (OpenAI, 실패 시 규칙 기반)
├─ analysis/frame.py  MIN_RECORDS · load_session_records (records 공용 헬퍼)
└─ routers/           session · records · patterns · whatif · demo
```

## 엔드포인트

| 메서드 | 경로 | 방식 | 상태 |
| --- | --- | --- | --- |
| POST | /api/session | DB | ✅ 익명 토큰 멱등 발급 |
| POST | /api/records | DB | ✅ 저장 + skin_score, 400/409 |
| GET | /api/records | DB | ✅ 세션별 목록(오름차순) |
| GET/DELETE | /api/demo | DB | ✅ 28일 시드 적재/해제(멱등) |
| GET | /api/patterns | AI in-process | ✅ 세션 기록(DB) → 분석 + 문장화 |
| POST | /api/whatif | AI in-process | ✅ 세션 기록(DB) → 시나리오 + 문장화 |
| GET | /api/experiments | DB | ✅ 세션별 실험 목록 |

## AI 연동 (open-questions A1 = in-process)

patterns/whatif는 세션 기록을 DB에서 읽어 `src.habit_pattern`·`src.whatif`로 직접 계산하고
`llm_formatter`로 문장화한다. `OPENAI_API_KEY`가 없거나 호출이 5초를 넘기거나 실패하면
규칙 기반 문장으로 대체한다. `src/`의 정본은 `../skinloop-ai/src`다(`src/VENDORED.md`).

상세 명세는 루트의 `spec.md` 및 `docs/spec/`.
