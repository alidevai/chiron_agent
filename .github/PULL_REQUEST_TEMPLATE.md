## What & why

<!-- Short description of the change and its motivation. -->

## Type

- [ ] Core code
- [ ] Skill candidate (under `contrib/skills/` — never `.claude/skills/` directly)
- [ ] Docs / CI

## Checklist

- [ ] `pytest -q` passes locally
- [ ] `python -m core verify` passes (audit chain + policy integrity)
- [ ] For skill candidates: `python -m core scan contrib/skills/<id>` passes
- [ ] No changes to constitutionally protected files (`policies/**`, `core/guard_hook.py`,
      `core/policy.py`, `core/audit.py`, `.claude/settings.json`) — or maintainer sign-off obtained
- [ ] Ponytail: no unnecessary code/dependency/capability added
- [ ] Tests added/updated for behavior changes
