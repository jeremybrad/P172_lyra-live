# Receipt: Canonical Layout Migration Pass
Date: 2026-02-26
Repository: /Users/jeremybradford/SyncedProjects/P172_lyra-live
Branch: codex/standards-align-20260226

Scope:
- Layout migration toward C010 canonical directories with compatibility shims.

Actions:
- Created canonical directories: 40_src, 50_data, 60_tests.
- Migrated legacy trees: `lyra_live/` -> `40_src/lyra_live`, `tests/` -> `60_tests`, `data/` -> `50_data`.
- Created compatibility shims at legacy paths:
  - `lyra_live` -> `40_src/lyra_live`
  - `tests` -> `60_tests/tests`
  - `data` -> `50_data`
- Updated README structure references for new canonical locations.

Commands:
- `mkdir -p 40_src 50_data 60_tests`
- `mv lyra_live 40_src/`
- `mv tests 60_tests/`
- `mv data 50_data/`
- `ln -s 40_src/lyra_live lyra_live`
- `ln -s 60_tests/tests tests`
- `ln -s 50_data data`
- `python3 - <<'PY' ...` (README path update)

Verification:
- Ran repo contract + Windows filename validators.
- Ran `git status` to confirm shim+structure changes staged conceptually.
- Unit test command still blocked by environment dependency (`ModuleNotFoundError: No module named 'mido'`) until dependencies are installed.

Correction pass:
- Normalized migration nesting so canonical roots are direct (`40_src/lyra_live`, `50_data`, `60_tests`) rather than nested intermediary directories.
- Repointed compatibility shims:
  - `tests` -> `60_tests`
  - `data` -> `50_data`
- Removed nested `.DS_Store` artifacts in `40_src/lyra_live`.
