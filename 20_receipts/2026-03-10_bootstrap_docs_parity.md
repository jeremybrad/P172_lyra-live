# Receipt: Bootstrap And Documentation Parity Repair

Date: 2026-03-10
Repo: P172_lyra-live
Branch: main
PRD: not required for this docs-and-bootstrap repair

## What changed

- Standardized the documented local workflow on `python3`, a source checkout, and the root `cli.py` entrypoint via `python3 -m cli`.
- Split optional voice dependencies into `requirements-voice.txt` so the supported core bootstrap no longer depends on `aubio` and `pyaudio` building successfully.
- Added `mypy` to `requirements.txt` so the documented type-check command is available in the supported baseline install.
- Updated the main operator/docs surfaces (`README.md`, `HANDOFF.md`, `ARCHITECTURE.md`, `CLAUDE_CODE_SETUP.md`, `PHASE1_TASKS.md`) plus the continuity artifacts to reflect the new verified path.
- Added `.venv/` to `.gitignore` to match the documented local virtualenv flow.

## Why

The repo's docs were pointing at three incompatible stories at once:

- `README.md` used bare `python -m cli`
- several setup docs used `python -m lyra_live.cli`
- `README.md` also advertised `pip install -e .` even though the repo has no packaging metadata

On this machine, `python` is not installed, the real CLI entrypoint is the root `cli.py`, and the old `requirements.txt` made clean bootstrap fail because `aubio` and `pyaudio` require extra system libraries. The repair keeps product behavior unchanged while making the supported bootstrap and verification path truthful.

## Evidence of verification

- `python --version` -> `command not found`
- clean temp venv (old dependency layout): `python3 -m pip install -r requirements.txt mypy` -> failed while building `aubio` (`PyUFuncGenericFunction` signature mismatch) and `pyaudio` (`portaudio.h` not found)
- clean temp venv (updated dependency layout): `python3 -m pip install -r requirements.txt` -> success
- clean temp venv (updated dependency layout): `python3 -m cli --help` -> success; Click rendered the full command list
- clean temp venv (updated dependency layout): `python3 -m pytest tests/unit/test_intervals.py tests/unit/test_chords.py tests/unit/test_validator.py -q` -> `21 passed in 0.02s`
- clean temp venv (updated dependency layout): `python3 -m mypy lyra_live` -> `97 errors in 18 files`

## Files touched

- `.gitignore`
- `requirements.txt`
- `requirements-voice.txt`
- `README.md`
- `HANDOFF.md`
- `ARCHITECTURE.md`
- `CLAUDE_CODE_SETUP.md`
- `PHASE1_TASKS.md`
- `ROADMAP.md`
- `00_admin/SESSION_CONTINUITY.md`
- `20_receipts/2026-03-10_bootstrap_docs_parity.md`
