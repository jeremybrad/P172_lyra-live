# P172 Lyra Live

Intelligent ear training with MIDI hardware awareness. Python 3.9+, CLI via `python3 -m cli`.

## Build & Test

```bash
source .venv/bin/activate
python3 -m pip install -r requirements.txt

# Supported test baseline (no hardware/audio deps required)
python3 -m pytest tests/unit/test_intervals.py tests/unit/test_chords.py tests/unit/test_validator.py -q

# Voice exercises need optional extras (may fail on some systems)
python3 -m pip install -r requirements-voice.txt

# Type checking — 97 known errors as of 2026-03-10, do not fix opportunistically
python3 -m mypy lyra_live
```

## Architecture Constraints

- Source lives at `lyra_live/` (root level), NOT `40_src/`. Tests at `tests/`, NOT `60_tests/`.
- `40_src/` and `60_tests/` are placeholder dirs from incomplete canonical migration — ignore them.
- P050 Ableton MCP is an upstream dependency — NEVER modify P050 code from this repo.
- Only 3 unit test files form the verified baseline. Running `pytest tests/` without voice deps will fail.

## Session State

See @00_admin/SESSION_CONTINUITY.md for open threads and resume context.
