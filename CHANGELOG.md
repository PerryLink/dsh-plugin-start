# Changelog

## 0.2.2 (2026-11-03)
- Generated `package.json` declares `dsh.capabilities` and `dsh.labels` as empty arrays, so "uses none" is explicit instead of missing.
- Generated README gains a Declarations section: no comments in JSON, declare only what the code uses, and add the matching capability before calling APIs such as `ctx.fs` or `ctx.tools.register`.

## 0.2.1 (2026-11-02)
- Generated package includes `engines.dsh` and `peerDependencies["@deepseek-ai/dsh"]`.

## 0.2.0
- C3 is FLOW-only in the generated README.

## 0.1.0
- Initial scaffold.
