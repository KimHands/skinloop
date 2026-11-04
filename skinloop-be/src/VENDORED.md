# vendored: ../../skinloop-ai/src

이 디렉터리는 같은 레포 `skinloop-ai/src/`를 **복사(vendoring)**한 것이다. Docker 빌드 컨텍스트가 `skinloop-be/`라서 사본을 둔다.
BE가 `from src.habit_pattern import analyze_patterns` / `from src.whatif import run_whatif`로
in-process 호출한다(BE↔AI in-process 결정: docs/plan/open-questions.md A1).

- 정본은 `skinloop-ai/src/`. 계산 로직은 거기서 고치고 여기로 다시 복사한다.
- 계약: `skinloop-ai/docs/integration_contract.md`
- 의존성: numpy/pandas/scipy/scikit-learn (requirements.txt)
