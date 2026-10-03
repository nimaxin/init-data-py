# Contributing

Bug reports, fixes and documentation improvements are all welcome.

For a security problem, follow [SECURITY.md](SECURITY.md) instead of opening
an issue.

## Before you start

Open an issue before working on a new feature or a change to the public API,
so the approach can be agreed first. Small fixes and documentation changes can
go straight to a pull request.

## Setting up

This project uses [uv](https://docs.astral.sh/uv/) and needs Python 3.10 or
newer. Fork the repository, then:

```bash
git clone https://github.com/<your-username>/init-data-py
cd init-data-py
uv sync --extra ed25519
```

## Checks

CI runs these on every pull request. Run them before you push:

```bash
uv run python -m unittest discover --verbose   # tests
uv run ruff check .                            # lint
uv run ruff format --check .                   # format
uv run mypy                                    # type check
```

CI also runs the tests without the `ed25519` extra, to make sure the core
works with no dependencies. To do the same locally:

```bash
uv run --exact python -m unittest discover --verbose
```

`--exact` removes the extra from the environment. The next
`uv sync --extra ed25519` puts it back.

## Guidelines

- The core has no runtime dependencies. Keep it that way. Anything that needs
  one goes behind an optional extra, like `ed25519`.
- Hash the query string exactly as it was received. Never rebuild a value
  from a parsed model before hashing it.
- Behaviour follows the
  [Telegram spec](https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app).
  When code depends on a rule from it, link the section in a comment.
- Every fix comes with a test that fails without it.
- For validation tests, prefer real init data captured from Telegram over data
  signed by this library. Add it to `tests/vectors.py`. Capture it with a
  throwaway bot and revoke the token before you push. The vector keeps
  working, because validation never contacts Telegram. It also contains your
  Telegram user details, so only add data you are happy to publish.
- Public functions and classes need type hints and a docstring. Mypy runs in
  strict mode.

## Pull requests

- Keep each pull request to one change.
- Write commit messages in the
  [Conventional Commits](https://www.conventionalcommits.org/) style, like
  the existing history: `fix: reject a signature that is not valid base64url`.
- Add an entry to `CHANGELOG.md` under an `[Unreleased]` heading at the top,
  unless the change is internal only.
- Update the README if you change the public API.

Releases are made by the maintainer.
