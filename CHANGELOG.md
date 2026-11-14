# Changelog

## 0.2.6 (2026-11-14)
- `--client` (and every generated patch row) now writes `name: <package-name>` instead of `name: ./index.js`: the rc3 host attaches a package's browser half only to a Loader row whose specifier is the bare package name, and the bundle smoke's G4 accepts only a package-root row named after `manifest.name`. The generated README explains the rule; tests assert the row name.
- Generated `engines.node` is `>=24.9.0`; generated `engines.dsh` / `peerDependencies["@deepseek-ai/dsh"]` are `>=0.2.2-0 <0.3.0` (the `-0` bound is what includes the rc prerelease under npm's default semver).
- Generated README installs the checkout with `dsh plugin --profile web add .` (the old `add <name>` hit the registry, not the checkout), and the install smoke uses the host on `PATH` instead of `npx @deepseek-ai/dsh` (which resolves npm `latest` = rc.1, not rc.3).
- Generated `scripts.check`, the generated README, the CLI next-step, and all five READMEs pin `dsh-standards@1.6.11` and pass `--host-version 0.2.2-rc.3`, so C-2 is actually judged; the wording no longer claims the skeleton "passes host-spec checks" — a static check is not a runtime or install result, and without a host version C-2 is NA, not a pass.
- READMEs: generated-file/declaration tables show the new engine/peer values and the package-name patch row; the CLI's own Node `>=20` requirement is now stated separately from the generated skeleton's `>=24.9.0`.
- Tests: added assertions for generated engines/peer/patch row/README commands/CLI output; `node --test test/*.test.js` 3/3.

## 0.2.5 (2026-11-14)
- Generated README/CLI next-step uses `dsh-standards@1.6.10` (was 1.6.9); existing generated plugins are unaffected.

## 0.2.4 (2026-11-08)
- Generated README gains an optional, read-only GitHub Actions snippet using `PerryLink/dsh-check-action@v1` (advisory, no comment, no required check).

## 0.2.3 (2026-11-08)
- Generated README, CLI hints, and diagrams no longer tell users to run the non-existent `dsh-dev check/test/submit`, `dsh-ready`, and `entry-validate` commands.
- The next-step path is now executable: the read-only `dsh-standards@1.6.10` ENTRY check, `npm pack --dry-run`, and an install smoke via `@deepseek-ai/dsh plugin --profile demo add .`.
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
