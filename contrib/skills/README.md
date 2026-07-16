# Community skill candidates

Put your proposed skill here as `contrib/skills/<your-skill-id>/SKILL.md` and open a PR
(see [CONTRIBUTING.md](../../CONTRIBUTING.md)).

This directory holds **candidates only** — nothing here is loaded or executed by the agent.
CI scans every candidate with the static security scanner. After review, a maintainer runs
the real pipeline (`stage → eval → promote`), which is the only path into `.claude/skills/`.

Not: Bu dizindeki hiçbir şey agent tarafından yüklenmez/çalıştırılmaz; yalnızca inceleme
bekleyen adaylardır. Kurulumun tek yolu staging → eval → promote hattıdır.
