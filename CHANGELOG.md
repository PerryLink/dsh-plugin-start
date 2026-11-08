# Changelog

## 0.2.3 (2026-11-08)
- Generated README, CLI hints, and diagrams no longer tell users to run the non-existent `dsh-dev check/test/submit`, `dsh-ready`, and `entry-validate` commands.
- The next-step path is now executable: the read-only `dsh-standards@1.6.9` ENTRY check, `npm pack --dry-run`, and an install smoke via `@deepseek-ai/dsh plugin --profile demo add .`.
- Generated `package.json` gains an optional `check` script that runs the same static ENTRY check; it is not wired into `prepublishOnly` because the checker requires Node >= 24.9.

## 0.2.2 (2026-11-03)
- Generated `package.json` declares `dsh.capabilities` and `dsh.labels` as empty arrays, so "uses none" is explicit instead of missing.
- Generated README gains a Declarations section: no comments in JSON, declare only what the code uses, and add the matching capability before calling APIs such as `ctx.fs` or `ctx.tools.register`.

## 0.2.1 (2026-11-02)
- Generated package includes `engines.dsh` and `peerDependencies["@deepseek-ai/dsh"]`.

## 0.2.0
- C3 is FLOW-only in the generated README.

## 0.1.0
- Initial scaffold.
