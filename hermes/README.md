# Hermes adapter

Hermes uses the shared policy directly, not Codex's discovery mechanism. Read
the policy files in `../shared/` before choosing a visual and use the local
renderer entry point in `../tools/bin/` when rendering is warranted.

The migration inventory and Ubuntu setup are maintained in
[MIGRATION.md](MIGRATION.md). It intentionally separates portable policy from
machine-specific dependencies: the policy is Agent-agnostic and never assumes
a local username, a Mac application path, or a particular Codex home.

For an Ubuntu checkout, run the dependency commands in the migration guide,
then use these repository-relative calls:

```bash
bash tools/scripts/check-environment.sh
tools/bin/render-diagram --help
```

Do not send `PRIVATE`, `WORK`, or `UNKNOWN` content to a hosted renderer.
