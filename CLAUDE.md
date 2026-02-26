# CLAUDE.md

You are operating on **P172_lyra-live** (Personal Project).

## Primary runbooks

- `README.md` (core setup + quick start)
- `CLAUDE_CODE_SETUP.md` (phase-by-phase implementation guidance)
- `HANDOFF.md` (agent handoff context)
- `rules_now.md` (policy pointer to C010 standards)

## Repository essentials

- Read `README.md`, `META.yaml`, `RELATIONS.yaml`, and `rules_now.md` before edits.
- Keep changes scoped, verify assumptions against code, and capture receipts for non-trivial work in `20_receipts/`.
- No local secrets in repo; use environment/config mechanisms outside the repo.

## Execution notes

- This project depends on external services for full runtime validation (P050 Ableton MCP + MIDI/audio devices).
- Core workflow commands are defined in `cli.py` and validated by `60_tests/` (legacy `tests/` path still resolves via shim).
