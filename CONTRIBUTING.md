# Contributing

Thanks for helping improve Lyra Live.

## Environment setup

- Install dependencies: `pip install -r requirements.txt`
- Optional: create and use a local virtual environment.

## Verification commands

- Run unit tests: `python3 -m pytest 60_tests/unit -q`
- Run full tests: `python3 -m pytest 60_tests -q`
- Use local entrypoint: `python3 -m cli --help`

## Pull request expectations

- Keep changes focused and documented in `20_receipts/`.
- Update `META.yaml` and `CHANGELOG.md` when behavior changes materially.
- Avoid committing generated artifacts, local data, or credentials.
