import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const NAME_RE = /^[a-z0-9][a-z0-9-]*$/
const VERSION = JSON.parse(fs.readFileSync(new URL('../package.json', import.meta.url), 'utf8')).version

export function usage() {
  return `dsh-start ${VERSION} — create a minimal DeepSeek Harness plugin

Usage:
  dsh-start new <name> [--dir <dir>] [--client] [--yes]

Options:
  --dir <dir>   target directory (default: ./<name>)
  --client      add a browser client entry and ./client export
  --yes         non-interactive (this tool never prompts)
  -h, --help    show this help
  -v, --version show the version

What it writes:
  package.json, cordis.patch.yml, index.js, README.md, LICENSE, .gitignore
  plus client.js when --client is used.

It does not install dependencies or publish anything.
`
}

export function parse(argv) {
  const out = { name: null, dir: null, client: false, yes: false, help: false, version: false }
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i]
    if (arg === 'new') continue
    if (arg === '--dir' || arg === '-d') out.dir = argv[++i]
    else if (arg === '--client') out.client = true
    else if (arg === '--yes' || arg === '-y') out.yes = true
    else if (arg === '--help' || arg === '-h') out.help = true
    else if (arg === '--version' || arg === '-v') out.version = true
    else if (arg.startsWith('-')) throw new Error(`unknown option: ${arg}`)
    else if (!out.name) out.name = arg
    else throw new Error(`unexpected argument: ${arg}`)
  }
  return out
}

function pkgJson(name, client) {
  const pkg = {
    name,
    version: '0.1.0',
    description: 'A DeepSeek Harness plugin.',
    license: 'Apache-2.0',
    type: 'module',
    main: './index.js',
    exports: { '.': './index.js' },
    files: ['index.js', 'cordis.patch.yml', 'README.md', 'LICENSE'],
    engines: { node: '>=24.9.0', dsh: '>=0.2.2-0 <0.3.0' },
    scripts: { check: 'npx -y dsh-standards@1.6.12 check . --scope entry --entry-claim static --no-exec --host-version 0.2.2-rc.3' },
    peerDependencies: { '@deepseek-ai/dsh': '>=0.2.2-0 <0.3.0' },
    dsh: {
      manifestVersion: 1,
      capabilities: [],
      labels: [],
      bundle: { patch: './cordis.patch.yml' },
    },
  }
  if (client) {
    pkg.exports['./client'] = './client.js'
    pkg.files.push('client.js')
    pkg.dsh.client = { platform: 'web' }
  }
  return JSON.stringify(pkg, null, 2) + '\n'
}

function patchYml(name) {
  // The row name must be the bare package name, not a relative file path: the
  // host attaches a package's browser half only to the loader row whose
  // specifier is the bare package name, and the bundle smoke's G4 accepts only
  // row.name === manifest.name (or '.'/'./').
  return `- insert:
    - id: ${name}
      name: ${name}
`
}

function indexJs(name) {
  return `export const name = '${name}'

export const inject = []

export function apply(ctx) {
  // Keep every resource inside ctx.effect so dispose is clean.
  ctx.effect(() => {
    return () => {}
  })
}
`
}

function clientJs(name) {
  return `export const name = '${name}-client'

export function apply() {}
`
}

function readme(name, client) {
  const patchRule = client
    ? `## Client patch row

The \`cordis.patch.yml\` row is \`${name}\` — the **bare package name**, not a
relative path such as \`./index.js\`. The host attaches a package's browser
half only to the loader row whose specifier is the bare package name, and the
bundle smoke (G4) accepts only a package-root row named after
\`package.json#name\` (or \`.\` / \`./\`). Keep the row as written when you
edit the patch.

`
    : ''
  return `# ${name}

A DeepSeek Harness plugin created with \`dsh-start\`.

## Install (local checkout)

\`\`\`sh
dsh plugin --profile web add .
\`\`\`

\`dsh plugin\` forwards to pnpm, so \`add .\` installs this checkout. Use the
package name only after you publish it (\`dsh plugin --profile web add ${name}\`).

${patchRule}## Declarations

\`package.json\` is JSON, so it cannot carry comments — do not add any.

\`dsh.capabilities\` and \`dsh.labels\` are declared as empty arrays. An empty
array means this plugin uses none of them. Declare only the capabilities and
labels the code actually uses: \`ctx.fs\` needs \`fs:read\` (or \`fs:write\`),
\`ctx.tools.register\` needs \`tools:register\`, and so on. Once the code uses
one of those APIs the matching capability is mandatory — leaving it out turns
the checker's hint into a failure.

## Next

\`\`\`sh
# read-only static ENTRY check; requires Node >= 24.9.
# --host-version makes C-2 (engines.dsh) judge against the host you target;
# without a host version C-2 is NA (compatibility not judged), not a pass.
npx -y dsh-standards@1.6.12 check . --scope entry --entry-claim static --no-exec --host-version 0.2.2-rc.3

# packaging check: confirm which files npm will publish
npm pack --dry-run

# install smoke: link this checkout into a throwaway profile
dsh plugin --profile demo add .
\`\`\`

## Publish

1. Add a \`repository\`, \`homepage\`, and a \`dsh-plugin\` GitHub topic.
2. Run the static check above and read the report; fix what it flags. The
   command passes \`--host-version 0.2.2-rc.3\`; without a host version C-2 is
   NA, not a pass.
3. Run the install smoke above, start the host once, and confirm the plugin loads.
4. Publish with npm and submit to the market you use.

The static check covers the static part of ENTRY only: it does not install or
run the package, and it is not a certification or a host-install result. Passing
it is not a runtime result and does not mean the plugin was installed.

## Optional CI

The action is advisory: it posts no required check unless you set \`fail-on\`.
Keep the workflow read-only.

\`\`\`yaml
name: entry-check
on: [pull_request]
permissions:
  contents: read
jobs:
  entry:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: PerryLink/dsh-check-action@v1
        with:
          comment: false
          fail-on: none
\`\`\`
`
}

function gitignore() {
  return `node_modules/
dist/
*.log
.DS_Store
`
}

export function create(name, target, { client = false } = {}) {
  if (!NAME_RE.test(name)) throw new Error(`invalid package name: ${name} (use lowercase letters, digits, hyphens)`)
  const resolved = path.resolve(target)
  if (fs.existsSync(resolved)) {
    const entries = fs.readdirSync(resolved)
    if (entries.length > 0) throw new Error(`target directory is not empty: ${resolved}`)
  }
  fs.mkdirSync(resolved, { recursive: true })
  const files = {
    'package.json': pkgJson(name, client),
    'cordis.patch.yml': patchYml(name),
    'index.js': indexJs(name),
    'README.md': readme(name, client),
    '.gitignore': gitignore(),
  }
  if (client) files['client.js'] = clientJs(name)
  for (const [file, content] of Object.entries(files)) {
    fs.writeFileSync(path.join(resolved, file), content)
  }
  const license = fileURLToPath(new URL('../LICENSE', import.meta.url))
  fs.copyFileSync(license, path.join(resolved, 'LICENSE'))
  return { dir: resolved, files: Object.keys(files).concat('LICENSE') }
}

export async function main(argv, options = {}) {
  let args
  try {
    args = parse(argv)
  } catch (error) {
    console.error(error.message)
    console.error(usage())
    return 1
  }
  if (args.help) {
    console.log(usage())
    return 0
  }
  if (args.version) {
    console.log(VERSION)
    return 0
  }
  if (!args.name) {
    console.error('missing plugin name')
    console.error(usage())
    return 1
  }
  const target = args.dir || args.name
  try {
    const result = create(args.name, target, { client: args.client })
    console.log(`created ${result.dir}`)
    for (const file of result.files) console.log(`  ${file}`)
    console.log('\nNext:')
    console.log(`  cd ${path.relative(process.cwd(), result.dir) || '.'}`)
    console.log('  npx -y dsh-standards@1.6.12 check . --scope entry --entry-claim static --no-exec --host-version 0.2.2-rc.3')
    console.log('  dsh plugin --profile demo add .')
    if (args.client) {
      console.log('  (with --client, keep the cordis.patch.yml row name equal to the package name)')
    }
    return 0
  } catch (error) {
    console.error(error.message)
    return 1
  }
}
