import pytest
from pydantic import ValidationError
from phishing_detector.config.settings import Settings
from functools import lru_cache
"""
pytest discovers all test_*.py files and runs all test_* functions. A test passes if no assert fails and nothing raises
"""

# Don't use .env file. Provide the required variables, so that the default values of the un-required varaibles can be tested
def make_settings() -> Settings:
    return Settings(
        _env_file=None,
        environment="development",
        log_level="INFO",
        max_p95_latency_ms=500,
    )

def test_defaults_are_valid() -> None:
    settings = make_settings()
    assert settings.max_FPR == 0.01
    assert settings.max_review_rate == 0.05
    assert settings.environment == "development"

def test_out_of_range_review_budget_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PHISHING_MAX_REVIEW_RATE", "1.5")
    with pytest.raises(ValidationError):
        make_settings()

def test_out_of_range_FPR_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PHISHING_MAX_FPR", "2.0")
    with pytest.raises(ValidationError):
        make_settings()

"""
THIS TEST SHOULD FAIL, TO SEE IF GITHUB ACTIONS IS SET PROPERLY, AND MERGING IS PREVENTED
"""
def test_github_actions_failure() -> None:
    assert 1 == 10
