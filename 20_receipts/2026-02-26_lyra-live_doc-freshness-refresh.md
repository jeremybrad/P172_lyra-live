# 2026-02-26 Lyra-live documentation freshness refresh

## Scope
Freshness remediation from `bbot render docs.freshness.v1` for repo `P172_lyra-live`.

## Actions
- Ran `bbot render docs.freshness.v1` before updates and recorded stale files:
  - `META.yaml` (last reviewed outdated)
  - `RELATIONS.yaml` (v1 format with missing v2 ownership fields)
- Updated `/Users/jeremybradford/SyncedProjects/P172_lyra-live/META.yaml`:
  - Set `project.last_reviewed` to `2026-02-26`
  - Updated canonical folder labels to `30_config`, `40_src`, `50_data`, `60_tests`
  - Refreshed `files` map to current canonical docs/code file set
- Updated `/Users/jeremybradford/SyncedProjects/P172_lyra-live/RELATIONS.yaml`:
  - Upgraded from v1 to v2 format
  - Added `repo` field and explicit `owns` / `must_not_own`
  - Added dependency/relationship entries for `P050_ableton-mcp` and `P171_elevenlabs-music-mcp`
  - Added `relates_to` entry for `C010_standards`

## Commands
```bash
bbot render docs.freshness.v1
```

## Verification
- Re-run performed after updates (see subsequent command log entry) and used to confirm stale items were addressed.
