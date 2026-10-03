# Security policy

## Supported versions

| Version | Supported |
| --- | --- |
| 1.x | Yes |
| 0.2.x and older | No |

Fixes are released for the latest 1.x version only. If you are still on
0.2.x, upgrade. The README has a migration table.

## Reporting a vulnerability

Do not open a public issue for a security problem. Report it privately
through GitHub instead:
[open a security advisory](https://github.com/nimaxin/init-data-py/security/advisories/new).

Include:

- the versions of init-data-py and Python you used
- the init data, or a script that produces it, that shows the problem
- what you expected to happen and what happened instead

Use a test bot in your report. Never send a token for a bot that is in use.

You should get a reply within 7 days. Once the problem is confirmed, a fix is
released and an advisory is published. You are credited in it unless you
prefer not to be.

## Scope

This library decides whether init data really came from Telegram. A report is
in scope if it makes that decision wrong. For example:

- init data that was forged, or changed after signing, passes
  `validate_by_hash` or `validate_by_signature`
- expired init data passes while an expiry is set
- a validator returns a value that differs from the one Telegram signed
- the hash comparison leaks timing information

These are problems in the calling code, not in this library:

- trusting the result of `parse`, which does not validate anything
- passing `expires_in=0`, which turns replay protection off
- leaking your bot token
- replaying valid init data before it expires. Init data carries no nonce,
  so a captured query string stays valid for its whole lifetime. Keep
  `expires_in` short.

Report a problem in a dependency to that project.
