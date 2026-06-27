# Priority Rubric (bugs only)

Priority is assigned deterministically by the detect_priority function; this file
documents the rubric for humans reviewing approvals.

- **P0 Critical** — data loss, security vulnerability, production outage, crash,
  "cannot use", "broken for everyone".
- **P1 High** — major functionality broken, many users affected, hard workaround,
  "not working", "blocker".
- **P2 Medium** — minor bug, some users, workaround available, performance, intermittent.
- **P3 Low** — cosmetic, typo, documentation, formatting, trivial.

Impact indicators (production, urgent, blocker, all users, everyone, always,
every time): two or more elevate the bug one level. Bugs with no keyword match
default to P2.
