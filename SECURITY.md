# Security Policy

## Reporting a vulnerability

**Please do NOT open a public issue for security vulnerabilities.**

Instead, report privately:

- 📧 Email: **devaikaga@gmail.com** (subject: `[SECURITY] chiron`)
- Or use GitHub's **"Report a vulnerability"** (Security → Advisories → Report a vulnerability)

Include: affected file/component, reproduction steps, impact assessment, and (optionally)
a suggested fix. You will get an initial response within **7 days**.

## Scope — what counts as a vulnerability here

Chiron is a security-gated capability-acquisition platform, so these are especially relevant:

- Bypasses of the **guard hook** (`core/guard_hook.py`) or the immutable policy core
- **Scanner evasion** — malicious skill content that passes `core/scanner.py` undetected
  (prompt injection, exfiltration, pipe-to-shell, supply-chain patterns)
- **Audit chain** forgery or truncation that `python -m core verify` fails to detect
- **Sandbox escape** — network or filesystem access from `core/sandbox.py` isolated runs
- **Policy engine** decisions that violate deny-by-default (e.g. auto-installing a
  high-risk or dangerous-permission candidate without human approval)
- Privilege escalation from agent-allowed CLI commands to human-only ones (`approve`, `seal-policy`)

## Out of scope

- Vulnerabilities in Claude Code itself (report to Anthropic)
- Issues requiring a human to deliberately run `approve`/`seal-policy` on malicious content
- Denial of service against your own local installation

## Supported versions

| Version | Supported |
|---|---|
| latest `master` | ✅ |
| older commits | ❌ |
