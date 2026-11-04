"""LLM 실패 시 규칙 기반 문장의 표현 규칙 테스트 (내부 키 노출·점 추정치 금지)."""

import pytest

from app import llm_formatter

PATTERN_RESULT = {
    "impacts": [{"factor": "exercise", "label": "운동 시간", "impact": 0.3, "lag": 0}],
}
WHATIF_RESULT = {
    "label": "수면 +1시간",
    "current": {"range": {"min": 56, "max": 79}},
    "changed": {"range": {"min": 64, "max": 86}},
    "estimatedDifference": 7.1,
}


@pytest.fixture(autouse=True)
def no_llm(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(llm_formatter, "_client", None)


def test_pattern_fallback_uses_label_not_internal_key():
    sentence = llm_formatter.summarize_habit_pattern(PATTERN_RESULT)
    assert "운동 시간" in sentence
    assert "exercise" not in sentence


def test_whatif_fallback_shows_ranges_not_point_estimate():
    sentence = llm_formatter.summarize_whatif(WHATIF_RESULT)
    assert "56~79" in sentence
    assert "64~86" in sentence
    assert "7.1" not in sentence


def test_whatif_fallback_without_ranges_has_no_number():
    sentence = llm_formatter.summarize_whatif({"label": "야식 줄이기", "estimatedDifference": 3.2})
    assert "야식 줄이기" in sentence
    assert "3.2" not in sentence
