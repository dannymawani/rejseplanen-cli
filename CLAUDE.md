# rejseplanen-cli — local rules

> **Status: reference / upstream.** The daily-driver surface is
> `tinfoil rejs ...` (in `~/code/tinfoil/tinfoil-cli/tinfoil_core/rejs.py`).
> This repo is kept around as the original-author reference and for
> experiments against API 2.0. **Don't add features here** — port them to
> `tinfoil_core.rejs` so they're available via both the CLI and the MCP
> server (Bertram, OpenCode).
>
> Project-level CLAUDE.md is at `~/code/tinfoil/CLAUDE.md` — the same
> non-negotiables apply (library-first, secrets via `~/code/.env`,
> lokal-only, no public exposure).

## Source of truth

- **Integrated module:** `~/code/tinfoil/tinfoil-cli/tinfoil_core/rejs.py` — what actually ships.
- **Rules for the integration:** `~/code/tinfoil/tinfoil-cli/CLAUDE.md`.
- **API docs:** https://labs.rejseplanen.dk/ (API 2.0, `accessId` query param).
- **This repo:** the upstream README + tests for cross-checking response shapes.

## Layout

```
src/rejseplanen/
├── api.py        Rejseplanen API 2.0 client (requests-based)
├── cli.py        Click commands (the `rejs` binary)
├── config.py     keyring + ~/code/.env loader
├── formatter.py  Rich terminal output
└── models.py     Pydantic Location / Departure / Trip / Leg

tests/            40 unit tests — `make test`
```

## Secrets — never as flags, never committed

- API key lives in `~/code/.env` as `REJSEPLANEN_API_KEY` (for this repo) and
  `TINFOIL_REJSEPLANEN_API_KEY` (for `tinfoil rejs`). Same value, two names —
  drop the `REJSEPLANEN_API_KEY` line when this repo is no longer used.
- `~/code/.env` is **outside this repo** and chmod 600. There is a symlink at
  `./.env → ~/code/.env` so `python-dotenv` picks it up; the symlink is
  covered by `.gitignore` (the `.env` line matches symlinks too).
- **Never** commit:
  - `.env`, `.env.local`, `.env.*.local` (already in `.gitignore`)
  - Anything containing the literal API key value
  - Keyring exports or `~/.config/rejseplanen/config.json`
- Before any commit: `git diff --cached | grep -iE 'api[_-]?key|access[_-]?id'`
  should return nothing. If it does, abort and clean.

## How to work in this repo

```bash
# Setup
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"

# Test
PYTHONPATH=src python -m pytest -v        # or: make test

# Run locally
rejs search "København H"
rejs departures "København H"
```

The integrated `tinfoil` CLI uses the same API key but does **not** depend on
this package — `tinfoil_core.rejs` re-implements the thin HTTP layer using
`httpx` + Pydantic to keep its dependency surface minimal. Bug fixes that
matter (parsing edge cases, API-2.0-quirks) should land in **both** places,
but the integrated module is the one that gets used daily.

## When to touch this repo

- Verifying upstream behavior (run a query here, see the raw response).
- Cross-checking that `tinfoil_core.rejs` parses the same response shape as
  the original author's parser.
- Throwaway experiments before promoting them to `tinfoil_core.rejs`.

## When NOT to touch this repo

- Adding a new command — add it to `tinfoil_core.rejs` instead.
- Fixing a bug that only matters to the daily workflow — fix
  `tinfoil_core.rejs` (and optionally backport).
- Changing the API-key handling — that's already aligned with the
  `~/code/.env` convention; don't drift.

## Daily commands (in `tinfoil`, not here)

```bash
tinfoil rejs home              # next train(s) on your home route (configured locally)
tinfoil rejs central           # next train(s) toward your usual city station
tinfoil rejs departures "<station>"
tinfoil rejs trip "<from>" "<to>"
tinfoil rejs search "<station-or-address>"
tinfoil rejs nearby "<address>"
```

Home/central defaults live in `~/code/.env` (`TINFOIL_REJSEPLANEN_HOME_FROM`,
`_HOME_TO`, `_CENTRAL_FROM`, `_CENTRAL_TO`) — never hardcoded in this repo
or in `tinfoil_core.rejs`. Keep it that way.

All commands support `--json` for piping into other tools.
