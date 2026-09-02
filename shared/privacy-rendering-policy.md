# Privacy and rendering policy

## Labels

| Label | Meaning | Rendering boundary |
| --- | --- | --- |
| `PUBLIC` | Deliberately public, non-sensitive material | Local by default; hosted fallback only with explicit authorization for this request |
| `PRIVATE` | Personal, confidential, or access-controlled material | Local-only; never hosted |
| `WORK` | Employer, customer, internal, or proprietary material | Local-only; never hosted |
| `UNKNOWN` | Missing, ambiguous, or unverified classification | Treat as sensitive: Local-only; never hosted |

## Decision table

1. If the user explicitly identifies content as public and the output is authorized, classify `PUBLIC`.
2. If it contains personal, confidential, internal, customer, credential, or access-controlled information, classify `PRIVATE` or `WORK` as appropriate.
3. If provenance, audience, or sensitivity cannot be verified, classify `UNKNOWN`.
4. `PRIVATE`, `WORK`, and `UNKNOWN` may use local CLI tools and local Chrome only. They must never reach hosted renderers, remote fonts, CDNs, telemetry, or public fallback services.
5. A prior authorization does not carry across projects or requests; ask again when hosted rendering is material.

Hosted services such as Kroki or QuickChart are not in the default path and are never used as an automatic failure workaround.
