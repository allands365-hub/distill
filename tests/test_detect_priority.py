from pod.functions.detect_priority.code import score_priority as detect_priority


def test_non_bug_returns_none():
    assert detect_priority("feature", "Add dark mode", "would be nice") is None


def test_p0_for_data_loss():
    r = detect_priority("bug", "Crash", "security vulnerability causes data loss")
    assert r["priority"] == "P0"


def test_p3_for_typo():
    r = detect_priority("bug", "Typo in docs", "cosmetic spelling issue")
    assert r["priority"] == "P3"


def test_bug_without_keywords_defaults_p2():
    r = detect_priority("bug", "Odd behavior", "something seems off here")
    assert r["priority"] == "P2"
    assert r["confidence"] == 0.5


def test_impact_boost_elevates_priority():
    r = detect_priority("bug", "Login broken", "not working in production for all users")
    assert r["priority"] == "P0"  # elevated from P1


def test_result_shape():
    r = detect_priority("bug", "App crash", "crash on startup")
    assert set(r) >= {"priority", "severity", "reasoning", "confidence"}
    assert 0.0 <= r["confidence"] <= 1.0
