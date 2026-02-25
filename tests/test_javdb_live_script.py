import pytest

from scripts.check_javdb_live import run_check


@pytest.mark.live_network
def test_javdb_live_censored_daily():
    result = run_check(video_type="censored", cycle="daily", include_previews=False)
    if result.get("blocked"):
        pytest.skip(f"live network blocked: {result.get('blocked_reason')}")
    assert result["pass"], result
