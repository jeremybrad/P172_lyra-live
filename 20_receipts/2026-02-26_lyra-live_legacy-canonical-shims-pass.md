# 2026-02-26 Legacy-to-Canonical Layout Pass (Second Pass)

## Scope
Second migration pass for canonical folder migration (`40_src`, `50_data`, `60_tests`) and legacy shims.

## Actions
- Verified this work is on branch `codex/standards-align-legacy-shims-20260226`.
- Confirmed shim paths after migration:
  - `lyra_live -> 40_src/lyra_live`
  - `tests -> 60_tests`
  - `data -> 50_data`
- Updated standards index resolution to prefer canonical `50_data` with legacy fallback to `data` in:
  - `cli.py`
  - `60_tests/unit/test_standards_and_improv.py`
- Updated standards resource path resolution in:
  - `40_src/lyra_live/standards/core.py`
  - `40_src/lyra_live/logging/practice_log.py`
- Updated `CLAUDE.md` one-line note to reference `60_tests/` with legacy shim note.
- Removed `60_tests/.DS_Store` and verified only `.git` metadata `.DS_Store` remains.

## Commands run
```bash
pwd; git status --short --branch
ls -la
ls -la lyra_live tests data 40_src 50_data 60_tests
rg -n "data/standards/index.yaml|/tests/|Path\(\"data/logs/|--index-path', default='data/" cli.py 40_src/lyra_live/standards/core.py 40_src/lyra_live/logging/practice_log.py 60_tests/unit/test_standards_and_improv.py CLAUDE.md README.md CONTRIBUTING.md
find . -name '.DS_Store'
```

## Key snippets
- `lyra_live` path shim:
  `lrwxr-xr-x@ ... lyra_live -> 40_src/lyra_live`
- `tests` path shim:
  `lrwxr-xr-x@ ... tests -> 60_tests`
- `data` path shim:
  `lrwxr-xr-x@ ... data -> 50_data`
- CLI canonical default index path now set to `50_data/standards/index.yaml`.
- Standards/logging helpers now resolve to canonical path first, fallback to legacy.

## Validation notes
- This pass did not execute test suites to avoid broad dependency/runtime changes.
- `find . -name '.DS_Store'` output showed only `.git/.DS_Store` (ignored by history expectations), confirming test-source cleanup.

## Files changed
- `cli.py`
- `40_src/lyra_live/standards/core.py`
- `40_src/lyra_live/logging/practice_log.py`
- `60_tests/unit/test_standards_and_improv.py`
- `CLAUDE.md`
- Canonical migration path work tree changes already in this branch (e.g. `40_src/`, `50_data/`, `60_tests/`, shim entries `lyra_live`, `tests`, `data`).
