# Download Filter Parity Checklist

Use this checklist to validate that download filtering behavior is consistent after recent fixes.

## Preconditions

1. `qBittorrent` connection is configured and healthy.
2. Download filter settings are saved in `/_index/setting/download-filter`.
3. At least one actor subscription download exists.

## Scenario A: Data Domain Clarity

1. Open `/_index/download` and confirm the info banner says this page is realtime downloader tasks.
2. Open actor subscribe all-downloads modal and confirm the info banner says it is subscription history.
3. Verify counts can differ between pages without being treated as a bug.

## Scenario B: Failed/Waiting Semantics

1. In `/_index/download`, toggle "显示失败" off.
2. Confirm items tagged `整理失败` are filtered out by backend response.
3. Toggle advanced status to `失败/等待` and confirm only failed-tagged or waiting tasks remain.

## Scenario C: Subtitle Behavior

1. Enable `skip_subtitle_only` in filter settings.
2. For a torrent containing video + subtitle files, verify subtitles are still retained.
3. For a subtitle-only torrent, verify subtitle files are filtered out.

## Scenario D: Cleanup Contract Rendering

1. In `/_index/download`, run preview cleanup for a single torrent.
2. Confirm estimated size displays from `deleted_size_mb`.
3. Run batch cleanup preview and confirm list rows show `name`, `deleted_files`, and `message`.

## Scenario E: Sorting

1. In `/_index/download`, open advanced filters.
2. Switch sort to `进度` and `大小`; confirm ordering changes.
3. Switch date sort asc/desc and confirm list reverses accordingly.

## Pass Criteria

- No contradictory success/failed behavior between backend toggles and frontend view.
- No subtitle loss in mixed video+subtitle torrents when only subtitle-only skipping is enabled.
- Cleanup preview/result fields render correctly with no missing key placeholders.
