# SESSION CONTINUITY

Date: 2026-03-10
Branch: main
Last commit: b5d601f
Repo status: Bootstrap/docs parity session closed. The supported source-based bootstrap is now truthful and reproducible on this machine, but the type backlog and optional voice/system dependencies remain open.

## Summary

- Standardized the local workflow on `python3`, a repo-local virtualenv, and the root `cli.py` entrypoint via `python3 -m cli`.
- Split optional microphone dependencies into `requirements-voice.txt` so the core bootstrap no longer depends on `aubio` and `pyaudio` building successfully.
- Added `mypy` to the baseline requirements and refreshed the main setup/operator docs to match the verified command surface.
- Wrote a focused receipt with the clean-venv evidence in `20_receipts/2026-03-10_bootstrap_docs_parity.md`.

## What was verified

- clean temp venv: `python3 -m pip install -r requirements.txt` -> success
- clean temp venv: `python3 -m cli --help` -> success
- clean temp venv: `python3 -m pytest tests/unit/test_intervals.py tests/unit/test_chords.py tests/unit/test_validator.py -q` -> `21 passed in 0.02s`
- clean temp venv: `python3 -m mypy lyra_live` -> `97 errors in 18 files`
- old all-in-one dependency set -> failed on `aubio` and `pyaudio` builds, which is why voice extras are now optional

## What remains unverified

- Any real MIDI-device or microphone-backed smoke flow
- P050-backed Ableton session orchestration
- Full unit and integration coverage in an environment with optional voice deps installed
- Whether the best next mypy move is stub/config cleanup or first-party annotation repair

## Open threads

- Decide whether to reduce third-party typing noise first (`requests`, `mido`, `numpy`, `yaml`, `pyaudio`) or to start burning down first-party mypy errors.
- Run a hardware-backed smoke pass once MIDI devices, the P050 service, and optional voice/system dependencies are available together.
- Decide whether this repo stays a documented hybrid layout or completes migration into canonical `40_src` / `60_tests`.

## Known hazards

- Optional voice support still depends on system libraries for `aubio` and `pyaudio`; the docs now say that plainly, but the extras remain environment-sensitive.
- The documented verification baseline is intentionally narrower than the full suite because hardware/audio coverage is not provisioned everywhere.
- Placeholder canonical dirs (`40_src/`, `60_tests/`) can still make the repo look more migrated than it actually is.

## Suggested next action

Pick one verification-hardening slice: either make `python3 -m mypy lyra_live` meaningfully actionable, or provision the optional voice/system dependencies and rerun the broader test surface.

## Suggested next prompt

Use `ROADMAP.md` and this continuity note to tighten P172 verification without changing product behavior. Start from the new `python3 -m cli` + `requirements.txt` baseline, decide whether to address stubs/config or first-party typing bugs first, rerun the documented checks, and capture the evidence in a new receipt.
