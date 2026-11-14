import assert from 'node:assert/strict'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { spawnSync } from 'node:child_process'
import test from 'node:test'

const BIN = new URL('../bin/dsh-start.js', import.meta.url).pathname

function temp() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'dsh-start-'))
}

test('creates a host plugin skeleton', () => {
  const dir = temp()
  const out = spawnSync(process.execPath, [BIN, 'new', 'demo-plugin', '--dir', dir, '--yes'], { encoding: 'utf8' })
  assert.equal(out.status, 0, out.stderr)
  const pkg = JSON.parse(fs.readFileSync(path.join(dir, 'package.json'), 'utf8'))
  assert.equal(pkg.name, 'demo-plugin')
  assert.equal(pkg.dsh.manifestVersion, 1)
  assert.deepEqual(pkg.dsh.capabilities, [])
  assert.deepEqual(pkg.dsh.labels, [])
  assert.deepEqual(Object.keys(pkg.dsh), ['manifestVersion', 'capabilities', 'labels', 'bundle'])
  assert.equal(pkg.dsh.bundle.patch, './cordis.patch.yml')
  assert.equal(pkg.exports['./client'], undefined)
  assert.ok(fs.existsSync(path.join(dir, 'cordis.patch.yml')))
  assert.ok(fs.existsSync(path.join(dir, 'LICENSE')))

  // Generated baseline: the 0.2.2 line is Node >=24.9 and rc3 is a prerelease,
  // so the range needs the `-0` lower bound.
  assert.deepEqual(pkg.engines, { node: '>=24.9.0', dsh: '>=0.2.2-0 <0.3.0' })
  assert.equal(pkg.peerDependencies['@deepseek-ai/dsh'], '>=0.2.2-0 <0.3.0')
  assert.match(pkg.scripts.check, /dsh-standards@1\.6\.11/)
  assert.match(pkg.scripts.check, /--host-version 0\.2\.2-rc\.3/)

  // The patch row is the bare package name, not ./index.js.
  const patch = fs.readFileSync(path.join(dir, 'cordis.patch.yml'), 'utf8')
  assert.match(patch, /name: demo-plugin/)
  assert.doesNotMatch(patch, /name: \.\/index\.js/)

  // The generated README must install the checkout (add .) and judge C-2.
  const readme = fs.readFileSync(path.join(dir, 'README.md'), 'utf8')
  assert.match(readme, /dsh plugin --profile web add \./)
  assert.match(readme, /--host-version 0\.2\.2-rc\.3/)
  assert.match(readme, /C-2 is NA \(compatibility not judged\), not a pass/)
  assert.match(out.stdout, /dsh-standards@1\.6\.11/)
})

test('creates a client plugin with --client', () => {
  const dir = temp()
  const out = spawnSync(process.execPath, [BIN, 'new', 'demo-client', '--dir', dir, '--client'], { encoding: 'utf8' })
  assert.equal(out.status, 0, out.stderr)
  const pkg = JSON.parse(fs.readFileSync(path.join(dir, 'package.json'), 'utf8'))
  assert.equal(pkg.exports['./client'], './client.js')
  assert.deepEqual(pkg.dsh.capabilities, [])
  assert.deepEqual(pkg.dsh.labels, [])
  assert.deepEqual(Object.keys(pkg.dsh), ['manifestVersion', 'capabilities', 'labels', 'bundle', 'client'])
  assert.equal(pkg.dsh.client.platform, 'web')
  assert.ok(fs.existsSync(path.join(dir, 'client.js')))

  // rc3 attaches the browser half only to a Loader row whose specifier is the
  // bare package name; the generated row must be demo-client, not ./index.js.
  const patch = fs.readFileSync(path.join(dir, 'cordis.patch.yml'), 'utf8')
  assert.match(patch, /- id: demo-client\n      name: demo-client\n/)
  assert.doesNotMatch(patch, /name: \.\/index\.js/)

  // --client writes the rule into the generated README.
  const readme = fs.readFileSync(path.join(dir, 'README.md'), 'utf8')
  assert.match(readme, /## Client patch row/)
  assert.match(readme, /bare package name/)
  assert.match(readme, /bundle smoke \(G4\)/)

  // The CLI receipt warns about the row name on the --client path.
  assert.match(out.stdout, /keep the cordis\.patch\.yml row name equal to the package name/)
})

test('refuses a non-empty target', () => {
  const dir = temp()
  fs.writeFileSync(path.join(dir, 'keep.txt'), 'x')
  const out = spawnSync(process.execPath, [BIN, 'new', 'demo', '--dir', dir], { encoding: 'utf8' })
  assert.equal(out.status, 1)
  assert.match(out.stderr, /not empty/)
})
