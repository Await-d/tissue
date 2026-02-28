from datetime import datetime, timedelta

from app.db.models.video_cache import VideoCache
from app.service.video_cache import VideoCacheService


def _insert_video(
    db_session,
    num,
    *,
    release_date=None,
    fetched_at=None,
    rating=4.0,
    comments_count=100,
    is_hd=False,
    is_zh=False,
    is_uncensored=False,
    actors=None,
    tags=None,
):
    db_session.add(
        VideoCache(
            num=num,
            title=f"Title {num}",
            cover=f"https://example.com/{num}.jpg",
            url=f"https://example.com/{num}",
            rating=rating,
            comments_count=comments_count,
            release_date=release_date,
            is_hd=is_hd,
            is_zh=is_zh,
            is_uncensored=is_uncensored,
            actors=actors or [],
            tags=tags or [],
            magnets=[],
            source="JavDB",
            video_type="censored",
            cycle="daily",
            rank_position=1,
            fetched_at=fetched_at or datetime.now(),
        )
    )


def test_query_videos_uses_release_date_first_and_fallback_to_fetched_at(db_session):
    now = datetime.now()
    _insert_video(
        db_session,
        "OLD-BUT-RECENT-FETCH",
        release_date=(now - timedelta(days=45)).strftime("%Y-%m-%d"),
        fetched_at=now,
        rating=4.9,
    )
    _insert_video(
        db_session,
        "NO-RELEASE-DATE",
        release_date=None,
        fetched_at=now,
        rating=4.8,
    )
    _insert_video(
        db_session,
        "RECENT-RELEASE",
        release_date=(now - timedelta(days=2)).strftime("%Y-%m-%d"),
        fetched_at=now - timedelta(days=20),
        rating=4.7,
    )
    db_session.commit()

    service = VideoCacheService(db_session)
    results = service.query_videos(days=7, limit=50)
    nums = {item["num"] for item in results}

    assert "RECENT-RELEASE" in nums
    assert "NO-RELEASE-DATE" in nums
    assert "OLD-BUT-RECENT-FETCH" not in nums


def test_query_videos_applies_hd_and_zh_filters(db_session):
    _insert_video(db_session, "MATCH", is_hd=True, is_zh=True, rating=5.0)
    _insert_video(db_session, "ONLY-HD", is_hd=True, is_zh=False, rating=4.8)
    _insert_video(db_session, "ONLY-ZH", is_hd=False, is_zh=True, rating=4.6)
    _insert_video(db_session, "NONE", is_hd=False, is_zh=False, rating=4.4)
    db_session.commit()

    service = VideoCacheService(db_session)
    results = service.query_videos(days=0, is_hd=True, is_zh=True, limit=50)
    nums = {item["num"] for item in results}

    assert nums == {"MATCH"}


def test_query_videos_prefetches_before_memory_filters(db_session):
    for index in range(1, 31):
        _insert_video(
            db_session,
            f"TOP-{index:02d}",
            rating=5.0 - (index * 0.01),
            comments_count=300 - index,
            tags=["other"],
        )

    for index in range(1, 6):
        _insert_video(
            db_session,
            f"WANTED-{index:02d}",
            rating=3.0 - (index * 0.01),
            comments_count=50 - index,
            tags=[{"name": "Wanted"}],
        )

    db_session.commit()

    service = VideoCacheService(db_session)
    results = service.query_videos(days=0, required_tags=["wanted"], limit=3, offset=0)
    nums = [item["num"] for item in results]

    assert len(nums) == 3
    assert all(num.startswith("WANTED-") for num in nums)


def test_query_videos_normalizes_actor_id_and_tag_values(db_session):
    _insert_video(
        db_session,
        "NORMALIZED-MATCH",
        actors=[{"id": " actor-001 ", "name": "Actor"}],
        tags=[{"label": "  ExcludeMe  "}, {"name": "Primary"}],
    )
    _insert_video(
        db_session,
        "SECOND-MATCH",
        actors=[{"id": "actor-001", "name": "Actor"}],
        tags=["primary"],
    )
    db_session.commit()

    service = VideoCacheService(db_session)
    results = service.query_videos(
        days=0,
        required_actor_id="actor-001",
        required_tags=["PRIMARY"],
        exclude_tags=["excludeme"],
        limit=20,
    )

    nums = {item["num"] for item in results}
    assert nums == {"SECOND-MATCH"}
