#!/usr/bin/env python3
"""README visuals for dsh-plugin-start — v5 (1440x576 hero + 1100x660 flow).

Both figures are derived from what `src/start.js` actually does, not from a
shared template:

  bin/dsh-start.js     main(process.argv.slice(2)) -> process.exitCode
  src/start.js         parse(argv): `new` is skipped, --dir/-d, --client,
                       --yes/-y, --help/-h, --version/-v; an unknown option or
                       a second positional throws -> exit 1
                       main(): --help / --version short-circuit to exit 0;
                       no name -> "missing plugin name" + usage -> exit 1
                       create(name, target, {client}):
                         NAME_RE  ^[a-z0-9][a-z0-9-]*$   -> invalid package name
                         target exists && non-empty      -> target directory is
                                                            not empty (no --force)
                         mkdirSync(recursive) -> writeFileSync x5 (+client.js)
                         -> copyFileSync(LICENSE) -> {dir, files}
                       success prints "created <abs>" + one line per file + Next

  hero  (Pillow, zh/en x light/dark) — the generated specimen. A prompt bar
        (`$ npx dsh-plugin-start new my-plugin`) sits above one `my-plugin/`
        tree card: six required files plus `client.js`, drawn hollow and tagged
        `--client` because --client is the only branch in the generator. Each
        row carries the content the template actually writes. A receipt strip
        closes with `created <abs>` / `6 files` / `exit 0`, and the `Next:`
        line underneath is what the CLI prints but never runs.

  flow  (hand-written SVG, light/dark) — a *hopper with an admission gate
        ladder*, not a row of boxes: the argv bar feeds a funnel whose four
        gates narrow toward the mouth, and each of the first three gates owns
        the exact rejection message it can raise (`exit 1`). The mouth emits a
        fork: two parallel lanes — the always-written base six, and the
        `--client` delta (one new file plus three `package.json` rewrites) —
        which converge on one receipt rail. Two dashed boundary cards flank the
        hopper: what the tool refuses to do, and the three commands it prints
        but does not run.

Labels are command / field tokens plus short Chinese notes, so the light/dark
SVG pair is shared by all five README languages; only the hero carries prose
(zh / en).

Outputs (idempotent overwrite):
  docs/assets/dsh-plugin-start-hero-{zh,en}-{light,dark}.webp
  docs/assets/dsh-plugin-start-flow-v5-{light,dark}.svg

Run:  python scripts/gen-readme-assets.py
Needs: Pillow, plus msyh.ttc / msyhbd.ttc / consola.ttf / segoeui.ttf /
       segoeuib.ttf (a CJK font is mandatory: Chinese must never render as
       tofu boxes).
"""
from __future__ import annotations

import os
from html import escape as esc

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs', 'assets')

FONT_CJK = r'C:\Windows\Fonts\msyh.ttc'
FONT_CJK_BOLD = r'C:\Windows\Fonts\msyhbd.ttc'
FONT_MONO = r'C:\Windows\Fonts\consola.ttf'
FONT_EN = r'C:\Windows\Fonts\segoeui.ttf'
FONT_EN_BOLD = r'C:\Windows\Fonts\segoeuib.ttf'
for _p in (FONT_CJK, FONT_CJK_BOLD, FONT_MONO, FONT_EN, FONT_EN_BOLD):
    if not os.path.exists(_p):
        raise SystemExit(f'FATAL: font missing: {_p}  (CJK must never render '
                         f'as tofu boxes; install the font and re-run)')

KIND = {'cjk': FONT_CJK, 'cjk_bold': FONT_CJK_BOLD, 'mono': FONT_MONO,
        'en': FONT_EN, 'en_bold': FONT_EN_BOLD}

# --- palette: family accent + the two mandated page gradients ---------------
SKIN = {
    'light': dict(bg_from='#f9f6fd', bg_to='#e4eaf8', card='#ffffff',
                  card_edge='#e4e1ee', zone='#f7f5fc', text='#141419',
                  sub='#4d5261', faint='#8f94a4', accent='#4B67B4',
                  accent2='#6d80c4', ok='#16a34a', fail='#cf222e',
                  pill='#ece7f9', grid='#e7e4f0', shadow=(32, 26, 64)),
    'dark': dict(bg_from='#131a2a', bg_to='#0c1016', card='#1b2231',
                 card_edge='#2e374b', zone='#202839', text='#f0f3f9',
                 sub='#a8b1c4', faint='#737b8d', accent='#8496f5',
                 accent2='#a9b7f8', ok='#3fb950', fail='#f85149',
                 pill='#242d42', grid='#2a3348', shadow=(0, 0, 0)),
}


def font(size: float, kind: str = 'cjk_bold') -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(KIND[kind], int(round(size)))


def hx(s: str) -> tuple[int, int, int]:
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def gradient(w: int, h: int, c1: str, c2: str) -> Image.Image:
    img = Image.new('RGB', (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = 0.2 * (y / h) + 0.8 * (y / h) ** 1.5
        d.line([(0, y), (w, y)],
               fill=tuple(int(p + (q - p) * t) for p, q in zip(hx(c1), hx(c2))))
    return img


def glow(img: Image.Image, cx: int, cy: int, r: int, color, alpha: int = 30):
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(10, 0, -1):
        rr = r * i / 10
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=color + (int(alpha * (1 - i / 11)),))
    # blur the rings away: concentric ellipses on a near-black page band
    layer = layer.filter(ImageFilter.GaussianBlur(r / 7))
    return Image.alpha_composite(img.convert('RGBA'),
                                 layer).convert('RGB')


def card(img, box, skin, radius=20, shadow=16, fill=None, edge=None, width=2):
    """Rounded card with a soft, offset shadow."""
    x0, y0, x1, y1 = box
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for i in range(shadow, 0, -2):
        sd.rounded_rectangle([x0 - i // 5, y0 + i // 2, x1 + i // 5, y1 + i],
                             radius=radius + i // 4,
                             fill=skin['shadow'] + (int(7 * (1 - i / shadow)),))
    base = Image.alpha_composite(img.convert('RGBA'),
                                 sh.filter(ImageFilter.GaussianBlur(9)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=hx(fill or skin['card']),
                        outline=hx(edge or skin['card_edge']), width=2)
    return base.convert('RGB')


def pill(img, xy, text, skin, size=17, fg=None, bg=None, kind='cjk_bold'):
    d = ImageDraw.Draw(img)
    f = font(size, kind)
    tw = d.textlength(text, font=f)
    x, y = xy
    h = size + 16
    d.rounded_rectangle([x, y, x + tw + 28, y + h], radius=h // 2,
                        fill=hx(bg or skin['pill']))
    d.text((x + 14, y + 7), text, font=f, fill=hx(fg or skin['accent']))
    return tw + 28


def tracked_len(d, text, f, tracking=0.0):
    return (sum(d.textlength(c, font=f) for c in text)
            + tracking * max(0, len(text) - 1))


def tracked(d, xy, text, f, fill, tracking=0.0):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + tracking


def fit(what, width, limit, extra=''):
    if width > limit:
        raise SystemExit(f'FATAL: {what} is {width:.1f}px wide, limit {limit}px '
                         f'({extra}); refusing to draw an overlap')


# ---------------------------------------------------------------------------
# hero copy — only prose is localised; the right-hand tree labels are tokens
# ---------------------------------------------------------------------------
HERO = {
    'zh': dict(
        kicker='DeepSeek Harness · 插件骨架生成器',
        title='dsh-plugin-start',
        value=['一条命令，写出合规骨架', '清单字段一次到位'],
        sub=['给一个包名，按当前规范把 package.json、',
             'cordis.patch.yml、index.js 与可选 client.js',
             '写进目标目录；不装依赖、不跑宿主、不发布。'],
        meta='零依赖 · 无网络 · 无交互 · Node ≥20 · exit 0 / 1',
        foot='Apache-2.0 · 社区工具，与 DeepSeek 官方无关',
        prompt='$ npx dsh-plugin-start new my-plugin',
        right_tag='--dir · --client · --yes',
        tree_head='my-plugin/',
        tree_badge='created',
        notes=[('manifestVersion 1', 'mono'),
               ('insert: ./index.js', 'mono'),
               ('apply(ctx) · ctx.effect', 'mono'),
               ('声明说明 + 下一步三步', 'sans'),
               ('node_modules/ · dist/', 'mono'),
               ('Apache-2.0 全文复制', 'sans'),
               ('仅 --client', 'sans')],
        receipt='created /abs/path/my-plugin',
        files='6 files',
        nextline='Next:   dsh-dev check .   →   dsh-dev test .   →   dsh-dev submit .',
    ),
    'en': dict(
        kicker='DeepSeek Harness · plugin scaffold generator',
        title='dsh-plugin-start',
        value=['One command, a spec-correct', 'plugin skeleton, field by field'],
        sub=['Give it a package name and it writes',
             'package.json, cordis.patch.yml, index.js and an',
             'optional client.js — no install, no host, no publish.'],
        meta='zero-dep · offline · Node >=20 · exit 0/1',
        foot='Apache-2.0 · community tool, not affiliated with DeepSeek',
        prompt='$ npx dsh-plugin-start new my-plugin',
        right_tag='--dir · --client · --yes',
        tree_head='my-plugin/',
        tree_badge='created',
        notes=[('manifestVersion 1', 'mono'),
               ('insert: ./index.js', 'mono'),
               ('apply(ctx) · ctx.effect', 'mono'),
               ('declarations + next steps', 'sans'),
               ('node_modules/ · dist/', 'mono'),
               ('Apache-2.0 text copied', 'sans'),
               ('--client only', 'sans')],
        receipt='created /abs/path/my-plugin',
        files='6 files',
        nextline='Next:   dsh-dev check .   →   dsh-dev test .   →   dsh-dev submit .',
    ),
}

# The generated file set, straight from create(): five writeFileSync calls plus
# the copied LICENSE; client.js appears only under --client.
FILES = ['package.json', 'cordis.patch.yml', 'index.js', 'README.md',
         '.gitignore', 'LICENSE', 'client.js']
OPTIONAL = len(FILES) - 1     # client.js


def hero(lang: str, skin: str) -> None:
    s = SKIN[skin]
    H_ = HERO[lang]
    W, H = 1440, 576
    img = gradient(W, H, s['bg_from'], s['bg_to'])
    img = glow(img, 1240, 48, 380, hx(s['accent']),
               24 if skin == 'light' else 38)
    img = glow(img, 90, 570, 260, hx(s['accent']),
               8 if skin == 'light' else 14)
    m = 60
    d = ImageDraw.Draw(img)

    # ---- left column: kicker / title / two value lines / sub / meta / foot --
    pw = pill(img, (m, 52), H_['kicker'], s, size=17)
    fit(f'{lang} kicker pill', m + pw, 740)
    d = ImageDraw.Draw(img)

    tsize, tracking = 78, -1.6
    ft = font(tsize, 'mono')
    tw = tracked_len(d, H_['title'], ft, tracking)
    while tw > 718 and tsize > 64:
        tsize -= 2
        ft = font(tsize, 'mono')
        tw = tracked_len(d, H_['title'], ft, tracking)
    fit(f'{lang} title', tw, 718)
    tracked(d, (m - 2, 102), H_['title'], ft, hx(s['text']), tracking)

    vkind = 'en_bold' if lang == 'en' else 'cjk_bold'
    vy = 238
    for line in H_['value']:
        fv = font(38, vkind)
        fit(f'{lang} value line', d.textlength(line, font=fv), 700, line)
        d.text((m, vy), line, font=fv, fill=hx(s['text']))
        vy += 54

    skind = 'en' if lang == 'en' else 'cjk'
    fsub = font(25, skind)
    for i, line in enumerate(H_['sub']):
        fit(f'{lang} sub line {i + 1}', d.textlength(line, font=fsub), 706,
            line)
        d.text((m + 1, 358 + i * 34), line, font=fsub, fill=hx(s['sub']))

    fm = font(20, 'mono' if lang == 'en' else 'cjk')
    fit(f'{lang} meta', d.textlength(H_['meta'], font=fm), 566, H_['meta'])
    d.text((m + 1, 478), H_['meta'], font=fm, fill=hx(s['faint']))
    d.line([m + 1, 514, m + 566, 514], fill=hx(s['grid']), width=2)
    ff = font(18, skind)
    fit(f'{lang} foot', d.textlength(H_['foot'], font=ff), 620, H_['foot'])
    d.text((m + 1, 530), H_['foot'], font=ff, fill=hx(s['faint']))

    # ---- right panel: prompt -> generated tree -> receipt ------------------
    PX0, PX1 = 792, 1390

    img = card(img, (PX0, 84, PX1, 130), s, radius=18)
    d = ImageDraw.Draw(img)
    fpr = font(17, 'mono')
    d.text((PX0 + 20, 99), H_['prompt'], font=fpr, fill=hx(s['text']))
    ftag = font(11, 'mono')
    tagw = d.textlength(H_['right_tag'], font=ftag)
    fit(f'{lang} prompt', PX0 + 20 + d.textlength(H_['prompt'], font=fpr),
        PX1 - 18 - tagw - 18)
    d.text((PX1 - 18, 99), H_['right_tag'], font=ftag, anchor='ra',
           fill=hx(s['faint']))

    # prompt -> tree: a small accent chevron, not a long arrow
    cx, cy = (PX0 + PX1) // 2, 130
    d.line([cx, cy, cx, cy + 4], fill=hx(s['accent']), width=2)
    d.polygon([(cx, cy + 10), (cx - 5, cy + 3), (cx + 5, cy + 3)],
              fill=hx(s['accent']))

    TY0, TY1 = 140, 470
    img = card(img, (PX0, TY0, PX1, TY1), s, radius=20)
    d = ImageDraw.Draw(img)
    ftree = font(17, 'mono')
    d.text((PX0 + 20, TY0 + 16), H_['tree_head'], font=ftree, fill=hx(s['text']))
    d.text((PX1 - 20, TY0 + 18), H_['tree_badge'], font=ftag, anchor='ra',
           fill=hx(s['ok']))
    d.line([PX0 + 20, TY0 + 48, PX1 - 20, TY0 + 48], fill=hx(s['grid']), width=2)

    fm_name = font(17, 'mono')
    fm_note_mono = font(12, 'mono')
    fm_note_sans = font(12, skind)
    for i, (fname, (note, nkind)) in enumerate(zip(FILES, H_['notes'])):
        y = TY0 + 58 + i * 38
        optional = i == OPTIONAL
        # marker: filled square when always written, hollow when --client only
        if optional:
            d.rounded_rectangle([PX0 + 24, y + 9, PX0 + 34, y + 19], radius=3,
                                outline=hx(s['accent']), width=2)
        else:
            d.rounded_rectangle([PX0 + 24, y + 9, PX0 + 34, y + 19], radius=3,
                                fill=hx(s['accent2']))
        fname_col = s['faint'] if optional else s['text']
        d.text((PX0 + 48, y + 3), fname, font=fm_name, fill=hx(fname_col))

        note_col = s['accent'] if optional else s['faint']
        fnote = fm_note_sans if nkind == 'sans' else fm_note_mono
        nx = PX1 - 20 - d.textlength(note, font=fnote)
        need = PX0 + 48 + d.textlength(fname, font=fm_name) + 24
        if nx < need:
            raise SystemExit(f'FATAL: {lang} tree note "{note}" would start at '
                             f'{nx:.0f}px but {fname} ends at {need:.0f}px; '
                             f'refusing to draw an overlap')
        d.text((nx, y + 8), note, font=fnote, fill=hx(note_col))

    RY0, RY1 = 480, 536
    img = card(img, (PX0, RY0, PX1, RY1), s, radius=18, edge=s['accent'])
    d = ImageDraw.Draw(img)
    d.ellipse([PX0 + 22, RY0 + 23, PX0 + 30, RY0 + 31], fill=hx(s['ok']))
    frec = font(14, 'mono')
    d.text((PX0 + 42, RY0 + 16), H_['receipt'], font=frec, fill=hx(s['text']))
    fit(f'{lang} receipt path',
        PX0 + 42 + d.textlength(H_['receipt'], font=frec), PX0 + 300)
    d.text((PX1 - 132, RY0 + 19), H_['files'], font=ftag, anchor='ra',
           fill=hx(s['faint']))
    # exit pill: the one number this generator ever returns on success
    px1, px0 = PX1 - 24, PX1 - 92
    d.rounded_rectangle([px0, RY0 + 11, px1, RY0 + 37], radius=13,
                        fill=hx(s['card']), outline=hx(s['ok']), width=2)
    d.text(((px0 + px1) / 2, RY0 + 24), 'exit 0', font=font(12, 'mono'),
           anchor='mm', fill=hx(s['ok']))

    fn = font(12, 'mono')
    d.text((PX0, 552), H_['nextline'], font=fn, fill=hx(s['faint']))
    fit(f'{lang} next line', d.textlength(H_['nextline'], font=fn), PX1 - PX0)

    img.save(os.path.join(OUT, f'dsh-plugin-start-hero-{lang}-{skin}.webp'),
             'WEBP', quality=92, method=6)
    print(f'dsh-plugin-start-hero-{lang}-{skin}.webp')


# ---------------------------------------------------------------------------
# flow (hand-written SVG): the hopper with its admission gate ladder
# ---------------------------------------------------------------------------
FLOW = {
    'light': dict(bg='#f9f6fd', bg2='#e4eaf8', dots='#ece7f7', card='#ffffff',
                  zone='#f6f2fc', edge='#e4e1ee', grid='#eae6f3',
                  text='#141419', sub='#4d5261', faint='#8f94a4',
                  accent='#4B67B4', accent2='#6d80c4', ok='#16a34a',
                  fail='#cf222e', hopper='0.05', solid='0.10'),
    'dark': dict(bg='#131a2a', bg2='#0c1016', dots='#1b2231', card='#161b26',
                 zone='#1c2333', edge='#2a3142', grid='#222a3b',
                 text='#f0f3f9', sub='#a8b1c4', faint='#737b8d',
                 accent='#8496f5', accent2='#a9b7f8', ok='#3fb950',
                 fail='#f85149', hopper='0.08', solid='0.55'),
}
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
SANS = "ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"

# the four gates, narrowing toward the hopper mouth: (x0, x1, y, index, title,
# code symbol, second line, second-line colour)
GATES = [
    (260, 780, 152, '01', '参数解析', 'parse(argv)',
     'unknown option: --foo · unexpected argument: x', 'fail', 'exit 1'),
    (300, 740, 220, '02', '包名规则', 'NAME_RE',
     'invalid package name: My_Plugin', 'fail', 'exit 1'),
    (340, 700, 288, '03', '目标目录', 'create()',
     'target directory is not empty: /a/b', 'fail', 'exit 1'),
    (370, 670, 356, '04', '落地写入', 'writeFileSync',
     'created &lt;abs&gt; · 6 / 7 files', 'ok', 'exit 0'),
]

BASE_FILES = [('package.json', 'write'), ('cordis.patch.yml', 'write'),
              ('index.js', 'write'), ('README.md', 'write'),
              ('.gitignore', 'write'), ('LICENSE', 'copy')]
CLIENT_DELTA = ['exports["./client"] → ./client.js',
                'files[] += "client.js"',
                'dsh.client.platform = "web"']
NOT_DO = ['不装依赖、不启宿主', '不访问 registry', '不写全局配置',
          '无配置文件 / 无环境变量', '不生成测试 / CI', '同步写完即退出']
NEXT_CMDS = ['dsh-dev check .', 'dsh-dev test .', 'dsh-dev submit .']


def t(x, y, txt, size, fill, fam=MONO, weight=None, anchor=None,
      spacing=None, opacity=None):
    a = [f'<text x="{x}" y="{y}" fill="{fill}" font-family="{fam}"',
         f'font-size="{size}"']
    if weight:
        a.append(f'font-weight="{weight}"')
    if anchor:
        a.append(f'text-anchor="{anchor}"')
    if opacity:
        a.append(f'opacity="{opacity}"')
    if spacing:
        a.append(f'letter-spacing="{spacing}"')
    a.append(f'>{txt}</text>')
    return ' '.join(a)


_FIT_CACHE: dict = {}


def measure(txt: str, size: float, fam: str) -> float:
    """Conservative width estimate: max(mono face, CJK face) in px."""
    plain = (txt.replace('&lt;', '<').replace('&gt;', '>')
             .replace('&amp;', '&').replace('&#183;', '·'))
    key = (size, plain)
    if key in _FIT_CACHE:
        return _FIT_CACHE[key]
    w = 0.0
    for path in (FONT_MONO, FONT_CJK, FONT_EN):
        f = ImageFont.truetype(path, int(round(size)))
        w = max(w, f.getlength(plain))
    _FIT_CACHE[key] = w
    return w


def fit_svg(what, txt, size, limit):
    w = measure(txt, size, MONO)
    if w > limit:
        raise SystemExit(f'FATAL: {what} "{txt}" needs {w:.1f}px at {size}px, '
                         f'only {limit:.0f}px available; refusing to draw an '
                         f'overlap')


def flow_svg(skin: str) -> None:
    s = FLOW[skin]
    W, H = 1100, 660
    p = [f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="dsh-plugin-start hopper: a dsh-start argv bar feeds an admission gate ladder (argv, package name, target directory) that narrows into one write step; the mouth forks into two lanes — the six files always written and the --client delta of client.js plus three package.json rewrites — and both lanes converge on one receipt rail. Each of the first three gates can reject with its own message and exit 1.">
<title>dsh-plugin-start — admission hopper and template confluence</title>
<defs>
  <filter id="soft" x="-40%" y="-40%" width="180%" height="200%">
    <feDropShadow dx="0" dy="9" stdDeviation="12" flood-color="#241d4a" flood-opacity="{s['solid']}"/>
  </filter>
  <pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse">
    <circle cx="1.3" cy="1.3" r="1.3" fill="{s['dots']}"/>
  </pattern>
  <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M0 0 L10 5 L0 10 z" fill="{s['accent']}"/>
  </marker>
  <marker id="arrFaint" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M0 0 L10 5 L0 10 z" fill="{s['faint']}"/>
  </marker>
  <linearGradient id="page" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{s['bg']}"/>
    <stop offset="1" stop-color="{s['bg2']}"/>
  </linearGradient>
</defs>
<rect width="{W}" height="{H}" fill="url(#page)"/>
<rect width="{W}" height="{H}" fill="url(#dots)" opacity=".6"/>
''']

    # ---- header ----------------------------------------------------------
    p.append(t(44, 48, 'dsh-plugin-start', 30, s['text'], weight='700'))
    sub = ('new &lt;name&gt; → 三道准入闸 → 基础 6 件 ∪ --client 增量 → '
           '一张回执 · 统一 exit 0 / 1')
    fit_svg('header subtitle', sub, 15, 640)
    p.append(t(44, 76, sub, 15, s['sub'], fam=SANS))
    p.append(t(1056, 46, 'src/start.js · create(name, target, {client})', 12,
               s['faint'], anchor='end'))
    p.append(t(1056, 66, 'bin/dsh-start.js → main(argv)', 11, s['faint'],
               anchor='end'))

    # ---- legend ----------------------------------------------------------
    p.append(f'<circle cx="962" cy="99" r="4" fill="{s["ok"]}"/>')
    p.append(t(974, 103, 'exit 0 · 照单出货', 11, s['ok'], fam=SANS))
    p.append(f'<circle cx="962" cy="119" r="4" fill="{s["fail"]}"/>')
    p.append(t(974, 123, 'exit 1 · 一票否决', 11, s['fail'], fam=SANS))

    # ---- hopper body (behind the gates) ---------------------------------
    p.append(f'<path d="M246 148H794L684 352H356Z" fill="{s["accent"]}" '
             f'opacity="{s["hopper"]}"/>')
    p.append(f'<path d="M246 148L286 216L326 284L356 352" fill="none" '
             f'stroke="{s["accent"]}" stroke-width="1.6" opacity=".45"/>')
    p.append(f'<path d="M794 148L754 216L714 284L684 352" fill="none" '
             f'stroke="{s["accent"]}" stroke-width="1.6" opacity=".45"/>')

    # ---- argv bar --------------------------------------------------------
    p.append(f'<rect x="260" y="92" width="520" height="48" rx="16" '
             f'fill="{s["card"]}" stroke="{s["accent"]}" stroke-width="1.8" '
             f'filter="url(#soft)"/>')
    p.append(t(280, 122, '$ dsh-start new &lt;name&gt;', 15, s['text'],
               weight='700'))
    flags = '[--dir &lt;dir&gt;] [--client] [--yes]'
    fit_svg('argv flags', flags, 11, 300)
    p.append(t(762, 121, flags, 11, s['faint'], anchor='end'))
    p.append(f'<path d="M520 140V148" stroke="{s["accent"]}" stroke-width="2" '
             f'marker-end="url(#arr)"/>')

    # ---- the four gates --------------------------------------------------
    for (x0, x1, y, idx, title, sym, line2, ckey, tagline) in GATES:
        last = idx == '04'
        stroke = s['accent'] if last else s['edge']
        fill = s['zone'] if last else s['card']
        p.append(f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="56" '
                 f'rx="16" fill="{fill}" stroke="{stroke}" stroke-width="'
                 f'{"1.8" if last else "1.4"}" filter="url(#soft)"/>')
        p.append(f'<rect x="{x0 + 14}" y="{y + 15}" width="26" height="18" '
                 f'rx="6" fill="{s["accent"]}" opacity=".14"/>')
        p.append(t(x0 + 18, y + 28, idx, 11, s['accent'], weight='700',
                   spacing='0.6'))
        p.append(t(x0 + 48, y + 24, title, 14, s['text'], fam=SANS,
                   weight='700'))
        tw = measure(title, 14, SANS)
        fit_svg('gate symbol', sym, 11,
                (x1 - 16 - 40) - (x0 + 48 + tw + 10))
        p.append(t(x0 + 58 + tw, y + 23, sym, 11, s['faint']))
        fit_svg('gate rejection line', line2, 11.5, x1 - 108 - x0)
        p.append(t(x0 + 48, y + 44, line2, 11.5,
                   s[ckey] if ckey == 'ok' else s['fail']))
        p.append(t(x1 - 16, y + 24, tagline, 11,
                   s['ok'] if ckey == 'ok' else s['fail'], anchor='end'))
        if not last:
            p.append(f'<path d="M520 {y + 56}V{y + 64}" stroke="{s["accent"]}" '
                     f'stroke-width="2" marker-end="url(#arr)"/>')

    # ---- left boundary card: what the tool refuses to do -----------------
    p.append(f'<rect x="44" y="196" width="196" height="170" rx="18" '
             f'fill="{s["zone"]}" stroke="{s["edge"]}" stroke-width="1.4" '
             f'stroke-dasharray="6 6"/>')
    p.append(t(60, 220, '它不做什么', 12, s['accent'], fam=SANS, weight='700'))
    for i, note in enumerate(NOT_DO):
        fit_svg('left note', note, 11, 168)
        p.append(t(60, 244 + i * 21, note, 11, s['sub'], fam=SANS))

    # ---- right boundary card: the commands it prints but never runs ------
    p.append(f'<rect x="820" y="196" width="236" height="170" rx="18" '
             f'fill="{s["zone"]}" stroke="{s["edge"]}" stroke-width="1.4" '
             f'stroke-dasharray="7 5"/>')
    p.append(t(836, 220, '生成之后由你跑', 12, s['accent'], fam=SANS,
               weight='700'))
    for i, cmd in enumerate(NEXT_CMDS):
        p.append(f'<circle cx="840" cy="{245 + i * 22}" r="2.6" '
                 f'fill="{s["accent"]}"/>')
        p.append(t(850, 249 + i * 22, cmd, 11, s['text']))
    p.append(t(836, 326, '本仓不执行这三步', 11, s['faint'], fam=SANS))
    p.append(t(836, 344, '骨架是起点，不是认证', 11, s['faint'], fam=SANS))

    # ---- fork from the hopper mouth into the two lanes ------------------
    p.append(f'<path d="M520 412V424" stroke="{s["accent"]}" stroke-width="2"/>')
    p.append(f'<path d="M288 424H812" stroke="{s["accent"]}" stroke-width="2" '
             f'fill="none"/>')
    p.append(t(550, 417, '并集写进同一个目标目录', 11, s['sub'], fam=SANS))
    p.append(f'<path d="M288 424V434" stroke="{s["accent"]}" stroke-width="2" '
             f'marker-end="url(#arr)"/>')
    p.append(f'<path d="M812 424V434" stroke="{s["accent"]}" stroke-width="2" '
             f'marker-end="url(#arr)"/>')

    # ---- lane A: the six files written every run ------------------------
    p.append(f'<rect x="44" y="438" width="488" height="132" rx="18" '
             f'fill="{s["card"]}" stroke="{s["edge"]}" filter="url(#soft)"/>')
    p.append(t(62, 462, '基础 · 每次 6 件', 13, s['accent'], fam=SANS,
               weight='700'))
    p.append(t(514, 462, 'writeFileSync ×5 · copyFileSync ×1', 11, s['faint'],
               anchor='end'))
    for i, (fname, tag) in enumerate(BASE_FILES):
        cx = 62 + (i % 2) * 228
        cy = 470 + (i // 2) * 30
        p.append(f'<rect x="{cx}" y="{cy}" width="216" height="26" rx="9" '
                 f'fill="{s["zone"]}" stroke="{s["grid"]}"/>')
        fit_svg('base file chip', fname, 13, 216 - 44)
        p.append(t(cx + 11, cy + 18, fname, 13, s['text']))
        p.append(t(cx + 205, cy + 17, tag, 11,
                   s['accent'] if tag == 'copy' else s['faint'], anchor='end'))

    # ---- lane B: the --client delta (conditional, dashed) --------------
    p.append(f'<rect x="568" y="438" width="488" height="132" rx="18" '
             f'fill="{s["card"]}" stroke="{s["accent"]}" stroke-width="1.6" '
             f'stroke-dasharray="8 5"/>')
    p.append(t(586, 462, '--client · 再 +1 件 + 3 处改写', 13, s['accent'],
               fam=SANS, weight='700'))
    p.append(t(1038, 462, 'if (client)', 11, s['faint'], anchor='end'))
    p.append(f'<rect x="586" y="472" width="164" height="26" rx="9" '
             f'fill="{s["zone"]}" stroke="{s["accent"]}" stroke-width="1"/>')
    p.append(t(597, 490, 'client.js', 13, s['text']))
    p.append(t(739, 489, 'add', 11, s['accent'], anchor='end'))
    p.append(t(766, 490, '新增文件', 11, s['faint'], fam=SANS))
    for i, row in enumerate(CLIENT_DELTA):
        by = 518 + i * 20
        p.append(t(586, by, '+', 12, s['accent'], weight='700'))
        fit_svg('client delta row', row, 11, 440)
        p.append(t(600, by, row, 11, s['sub']))

    # ---- confluence: both lanes land on one receipt rail ----------------
    p.append(f'<path d="M288 570V576" stroke="{s["faint"]}" stroke-width="1.6" '
             f'stroke-dasharray="4 4" marker-end="url(#arrFaint)"/>')
    p.append(f'<path d="M812 570V576" stroke="{s["faint"]}" stroke-width="1.6" '
             f'stroke-dasharray="4 4" marker-end="url(#arrFaint)"/>')
    p.append(f'<rect x="44" y="580" width="1012" height="48" rx="18" '
             f'fill="{s["zone"]}" stroke="{s["accent"]}" stroke-width="1.6"/>')
    p.append(f'<circle cx="70" cy="604" r="4.5" fill="{s["ok"]}"/>')
    p.append(t(82, 609, 'created /abs/my-plugin', 13, s['text'],
               weight='700'))
    p.append(t(272, 608, '6 / 7 files', 11, s['faint']))
    p.append(t(376, 608, 'Next', 11, s['accent'], fam=SANS, weight='700'))
    nxt = 'dsh-dev check .  →  dsh-dev test .  →  dsh-dev submit .'
    fit_svg('receipt next', nxt, 11, 560)
    p.append(t(412, 608, nxt, 11, s['sub']))
    p.append(f'<rect x="964" y="590" width="74" height="28" rx="14" '
             f'fill="{s["card"]}" stroke="{s["ok"]}" stroke-width="1.6"/>')
    p.append(t(1001, 609, 'exit 0', 11.5, s['ok'], anchor='middle',
               weight='700'))

    # ---- footer ----------------------------------------------------------
    foot = '任一闸不过：只打印一行原因并 exit 1，目标目录保持原样'
    fit_svg('footer', foot, 11, 620)
    p.append(t(44, 650, foot, 11, s['faint'], fam=SANS))
    p.append(t(1056, 650, '零依赖 · 无网络 · 无交互 · 同步写盘', 11, s['faint'],
               fam=SANS, anchor='end'))
    p.append('</svg>')

    path = os.path.join(OUT, f'dsh-plugin-start-flow-v5-{skin}.svg')
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(p) + '\n')
    print(f'dsh-plugin-start-flow-v5-{skin}.svg')


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for skin in ('light', 'dark'):
        for lang in ('zh', 'en'):
            hero(lang, skin)
    for skin in ('light', 'dark'):
        flow_svg(skin)


if __name__ == '__main__':
    main()
