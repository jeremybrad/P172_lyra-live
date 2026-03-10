# ROADMAP

Last updated: 2026-03-10
Source: repo health / continuity probe on `main`, plus bootstrap/docs parity repair on `main`

## Now

### 1. Re-establish a trustworthy verification baseline
Why it matters: Some core logic is healthy, but the full verification story is not currently dependable enough for quick session startup or safe iteration.
Evidence: The documented bootstrap now works in a clean virtualenv with `python3 -m pip install -r requirements.txt`; `python3 -m cli --help` renders successfully; `python3 -m pytest tests/unit/test_intervals.py tests/unit/test_chords.py tests/unit/test_validator.py -q` passed 21 tests; `python3 -m mypy lyra_live` still reports 97 errors in 18 files; optional voice extras now live in `requirements-voice.txt` because `aubio` and `pyaudio` require extra system libraries on this machine.
First concrete step: Decide whether to reduce third-party typing noise with stub packages/config or to start burning down the remaining real annotation issues file by file.
Effort: M
Confidence: high
Blockers or what lowers priority: Some mypy failures are true code issues, while others are missing stubs for `requests`, `mido`, `numpy`, `pyaudio`, and `yaml`.

## Next

### 2. Decide whether the repo stays hybrid or completes the canonical migration
Why it matters: The active source and tests still live in legacy root paths, while the canonical directories mostly exist as placeholders, which slows orientation and creates false positives in tooling.
Evidence: Active code lives in `lyra_live/` and `tests/`; `40_src/lyra_live` and `60_tests/` currently contain ignored cache artifacts rather than the active source tree; `00_admin/audit_exceptions.yaml` allows the legacy dirs, but its planned destination for tests is `40_src/tests`, which conflicts with the canonical `60_tests` convention.
First concrete step: Add repo-local guidance that explicitly names the active source/test roots and the intended end state, then either migrate or simplify the placeholder directories.
Effort: M
Confidence: medium
Blockers or what lowers priority: Import-path compatibility and any external tooling that assumes the current root layout.

## Later

### 3. Run a real hardware-backed smoke pass against P050
Why it matters: The value of Lyra Live is in device-aware practice through Ableton, and that remains largely unverified in this probe.
Evidence: This probe did not install missing runtime dependencies, did not verify MIDI hardware presence, and did not hit a live P050-backed exercise flow.
First concrete step: In a provisioned environment with MIDI hardware and the P050 service available, run the documented CLI practice commands and capture a short evidence receipt.
Effort: M
Confidence: medium
Blockers or what lowers priority: Requires local hardware, audio/MIDI drivers, and the P050 Ableton MCP service.

## Completed recently

- 2026-03-10: Bootstrap/docs parity repaired; standardized on `python3 -m cli`, split optional voice extras into `requirements-voice.txt`, added `mypy` to the supported baseline, and verified the documented smoke plus pure-logic unit checks in a clean virtualenv.
- 2026-03-09: Health probe completed; roadmap and session continuity artifacts added.
- 2026-01-13 to 2026-03-09: Betty/canonical scaffolding, metadata refreshes, and evidence-sidecar additions landed on `main` (`c545851`, `5623dba`, `b38c052`, `169659e`).

## Deferred / not worth it

- Wide file moves into canonical paths before bootstrap and verification are trustworthy.
- Any product-feature expansion until the repo can be started and checked predictably again.

## Decision notes

- Treat the current repo as a documented hybrid layout, not as a completed canonical migration.
- Treat missing `AGENTS.md`, missing `CLAUDE.md`, missing roadmap, and missing session continuity as operator-continuity gaps rather than product-code defects.
