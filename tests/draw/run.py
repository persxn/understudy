#!/usr/bin/env python3
"""Tests for scripts/us_draw.py. One line per test, then 'N passed, M failed'; exit 1 on failure."""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DRAW = os.path.join(ROOT, 'scripts', 'us_draw.py')
EX = os.path.join(HERE, 'examples')
FAIL = os.path.join(HERE, 'must-fail')
NS = '{http://www.w3.org/2000/svg}'
results = []


def run(*args):
    r = subprocess.run([sys.executable, DRAW] + list(args), capture_output=True, text=True)
    return r.returncode, r.stdout.strip().splitlines()


def test(name, ok, why=''):
    results.append(ok)
    print('%s  %s%s' % ('PASS' if ok else 'FAIL', name, '' if ok else ': ' + why))


def read(path, mode='rb'):
    with open(path, mode) as f:
        return f.read()


def boxes_of(root, role):
    """{data-id: (x0, y0, x1, y1)} of the rects with this data-role, shadow included."""
    shadow = {e.get('data-for') for e in root.iter() if e.get('data-role') == 'shadow'}
    out = {}
    for e in root.iter(NS + 'rect'):
        if e.get('data-role') == role:
            x, y = float(e.get('x')), float(e.get('y'))
            s = 4 if e.get('data-id') in shadow else 0
            out[e.get('data-id')] = (x, y, x + float(e.get('width')) + s,
                                     y + float(e.get('height')) + s)
    for e in root.iter(NS + 'polygon'):
        if e.get('data-role') == role:
            pts = [tuple(map(float, p.split(','))) for p in e.get('points').split()]
            out[e.get('data-id')] = (min(p[0] for p in pts), min(p[1] for p in pts),
                                     max(p[0] for p in pts), max(p[1] for p in pts))
    return out


def curve_points(d):
    nums = [float(v) for v in re.findall(r'-?[\d.]+', d)]
    p = list(zip(nums[0::2], nums[1::2]))
    if 'C' not in d:
        return p
    a, b, c, e = p[:4]
    out = []
    for k in range(61):
        t = k / 60
        m = 1 - t
        out.append(tuple(m ** 3 * a[i] + 3 * m * m * t * b[i] + 3 * m * t * t * c[i] +
                         t ** 3 * e[i] for i in (0, 1)))
    return out


def main():
    figs = sorted(glob.glob(os.path.join(EX, '*.fig')))
    kinds = set()
    bad = {k: [] for k in ('render', 'bytes', 'refuse', 'check', 'xml', 'a11y', 'themes', 'width',
                           'overlap', 'pointers')}
    for f in figs:      # every example renders with no problem, then again to the same bytes
        name = os.path.basename(f)
        code, out = run(f)
        if code or len(out) != 2 or not out[0].startswith('ok  ') or \
                not out[1].startswith('reads: '):
            bad['render'].append('%s: %s' % (name, ' / '.join(out)[:160]))
        svg = f[:-4] + '.svg'
        first = read(svg) if os.path.exists(svg) else b''
        run(f)
        if not first or read(svg) != first:
            bad['bytes'].append(name)
    fails = sorted(glob.glob(os.path.join(FAIL, '*.fig')))
    for f in fails:     # must-fail descriptions: exit 1, one line naming a line and a fix
        code, out = run(f)
        if code != 1 or len(out) != 1 or not re.search(r': line \d+: .+: .+', out[0]) or \
                os.path.exists(f[:-4] + '.svg'):
            bad['refuse'].append('%s: %s' % (os.path.basename(f), ' / '.join(out)[:160]))
    for f in figs:
        svg = f[:-4] + '.svg'
        name = os.path.basename(svg)
        code, out = run('--check', svg)
        if code:
            bad['check'].append('%s: %s' % (name, ' / '.join(out)[:160]))
        try:
            root = ET.fromstring(read(svg, 'r'))
        except ET.ParseError as e:
            bad['xml'].append('%s: %s' % (name, e))
            continue
        kinds.add(root.get('data-kind'))
        style = ''.join(e.text for e in root.iter(NS + 'style'))
        desc = root.find(NS + 'desc')
        if root.get('role') != 'img' or root.find(NS + 'title') is None or desc is None or \
                len(desc.text or '') < 20:
            bad['a11y'].append(name)
        text = read(svg, 'r')
        if '@media (prefers-color-scheme:dark){svg:not([data-theme="light"])' not in style or \
                'svg[data-theme="dark"]' not in style or 'gradient' in text or 'filter' in text \
                or 'opacity' in text:
            bad['themes'].append(name)
        w = float(root.get('viewBox').split()[2])
        if w > 760:
            bad['width'].append('%s %d px' % (name, w))
        for group in (boxes_of(root, 'node'), boxes_of(root, 'cell')):
            for a in group:
                for b in group:
                    if a < b and min(group[a][2], group[b][2]) - max(group[a][0], group[b][0]) > 5 \
                            and min(group[a][3], group[b][3]) - max(group[a][1], group[b][1]) > 5:
                        bad['overlap'].append('%s: %s/%s' % (name, a, b))
        if root.get('data-kind') == 'memory':
            cells = boxes_of(root, 'cell')
            for e in root.iter(NS + 'path'):
                if e.get('data-role') == 'edge' and 'ep' in e.get('class', ''):
                    pts = curve_points(e.get('d'))
                    for cid, r in cells.items():
                        if cid not in (e.get('data-from'), e.get('data-to')) and \
                                any(r[0] < x < r[2] and r[1] < y < r[3] for x, y in pts):
                            bad['pointers'].append('%s: %s through %s' % (
                                name, e.get('data-id'), cid))
    n = len(figs)
    test('%d examples render with no problem' % n, not bad['render'], '; '.join(bad['render']))
    test('%d examples render to the same bytes twice' % n, not bad['bytes'],
         ', '.join(bad['bytes']))
    test('%d must-fail cases refused: exit 1, one line' % len(fails),
         len(fails) >= 5 and not bad['refuse'], '; '.join(bad['refuse']))
    test('--check passes on %d SVGs' % n, not bad['check'], '; '.join(bad['check']))
    test('every SVG parses as XML', not bad['xml'], '; '.join(bad['xml']))
    test('role=img, title and desc on every SVG', not bad['a11y'], ', '.join(bad['a11y']))
    test('dark rules twice, no gradient/filter/opacity', not bad['themes'],
         ', '.join(bad['themes']))
    test('no SVG wider than 760', not bad['width'], ', '.join(bad['width']))
    test('no two node boxes or cells overlap', not bad['overlap'], ', '.join(bad['overlap']))
    test('no pointer arrow passes through a third cell', not bad['pointers'],
         ', '.join(bad['pointers']))
    test('all five kinds rendered', kinds >= {'flow', 'tree', 'layers', 'sequence', 'memory'},
         str(sorted(kinds)))
    # 5. chapter mode: idempotent, only image lines change
    with tempfile.TemporaryDirectory() as tmp:
        ch = os.path.join(tmp, 'chapter.md')
        shutil.copy(os.path.join(EX, 'chapter.md'), ch)
        code1, out1 = run('--chapter', ch)
        once = read(ch)
        code2, out2 = run('--chapter', ch)
        test('chapter renders to fig/<chapter>/<id>.svg',
             code1 == 0 and len(glob.glob(os.path.join(tmp, 'fig', 'chapter', '*.svg'))) == 3
             and not glob.glob(os.path.join(tmp, 'fig', '*.svg')), ' / '.join(out1)[:200])
        test('chapter image lines link fig/<chapter>/<id>.svg',
             re.findall(rb'^!\[.*\]\((fig/[^)]*)\)$', once, re.M) and
             all(p.startswith(b'fig/chapter/') and os.path.exists(os.path.join(tmp, p.decode()))
                 for p in re.findall(rb'^!\[.*\]\((fig/[^)]*)\)$', once, re.M)), 'links')
        test('chapter idempotent', code2 == 0 and read(ch) == once, 'second run changed it')
        orig = read(os.path.join(EX, 'chapter.md'), 'r').splitlines()
        new = once.decode('utf-8').splitlines()
        extra = [l for l in new if l not in orig]
        gone = [l for l in orig if l not in new]
        test('chapter only image lines differ', all(l.startswith('![') for l in extra + gone)
             and len(extra) == 3 and any('*Figure 8.1' in l for l in new),
             'changed: %s' % (extra + gone)[:3])
        two = []
        for name in ('01-one.md', '02-two.md'):
            two.append(os.path.join(tmp, name))
            with open(two[-1], 'w') as f:
                f.write('<!-- fig: id=overview\n%s -> b\n-->\n' % name[3:6])
        code, out = run('--chapter', *two)
        test('two chapters in one folder each keep their own figure "overview"', code == 0 and
             b'one' in read(os.path.join(tmp, 'fig', '01-one', 'overview.svg')) and
             b'two' in read(os.path.join(tmp, 'fig', '02-two', 'overview.svg')) and
             '](fig/02-two/overview.svg)' in read(two[1], 'r'), ' / '.join(out))
        with open(two[0], 'w') as f:
            f.write('<!-- fig: id=overview\none -> b\n-->\n![old](fig/overview.svg)\n')
        run('--chapter', two[0])
        lines = read(two[0], 'r').splitlines()
        test('an old fig/<id>.svg image line is moved to the new path',
             len(lines) == 4 and lines[3].endswith('](fig/01-one/overview.svg)'), str(lines))
        dup = os.path.join(tmp, 'dup.md')
        with open(dup, 'w') as f:
            f.write('<!-- fig: id=a\na -> b\n-->\n\n<!-- fig: id=a\nc -> d\n-->\n')
        code, out = run('--chapter', dup)
        test('chapter refuses duplicate ids', code == 1 and any(
            'line 5' in l and 'already used' in l for l in out), ' / '.join(out))
        bad = os.path.join(tmp, 'bad.md')
        with open(bad, 'w') as f:
            f.write('intro\n\n<!-- fig: id=b\nbox a: x\nboks c: y\n-->\n')
        code, out = run('--chapter', bad)
        test('chapter reports its own line numbers', code == 1 and any(
            'line 5:' in l and "did you mean" in l for l in out), ' / '.join(out))
    # 6. a style with poor contrast is refused, naming the pair
    with tempfile.TemporaryDirectory() as tmp:
        st = json.loads(read(os.path.join(ROOT, 'scripts', 'fig-style.json'), 'r'))
        st['light']['soft'] = '#A9B3BD'
        bad = os.path.join(tmp, 'bad-style.json')
        with open(bad, 'w') as f:
            json.dump(st, f)
        code, out = run('--style', bad, figs[0])
        test('bad style refused', code == 1 and any('soft #A9B3BD on ground' in l for l in out),
             ' / '.join(out)[:200])
        # 7. PNG export through the first exporter found
        src = os.path.join(tmp, 'x.fig')
        shutil.copy(os.path.join(EX, 'pointer-box-and-arrow.fig'), src)
        code, out = run('--png', src)
        test('png export', code == 0 and os.path.exists(src[:-4] + '.png') and
             os.path.exists(src[:-4] + '-dark.png') and 'png via' in out[0], ' / '.join(out))
    # 8. the cheat sheet is short and covers every kind
    code, out = run('--format')
    text = '\n'.join(out)
    test('format sheet', len(out) <= 45 and all(k in text for k in (
        'flow', 'tree', 'layers', 'sequence', 'memory', 'ptr', 'frame')), '%d lines' % len(out))
    passed = sum(results)
    print('%d passed, %d failed' % (passed, len(results) - passed))
    return 0 if passed == len(results) else 1


if __name__ == '__main__':
    sys.exit(main())
