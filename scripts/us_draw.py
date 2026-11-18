#!/usr/bin/env python3
"""us_draw.py - turn about ten lines of plain text into a finished SVG figure.

  us_draw.py a.fig [b.fig ...]     render each to a.svg beside it
  us_draw.py --chapter FILE.md     render every <!-- fig: --> comment, refresh image lines
  us_draw.py --all DIR             every .fig and chapter .md under DIR
  us_draw.py --check x.svg         run the checks on an SVG made by this script
  us_draw.py --format              print the description cheat sheet
  options: --png (also x.png, x-dark.png)   --style PATH

Python 3 standard library only. The same description always gives the same bytes.
"""
import difflib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
KINDS = ('flow', 'layers', 'tree', 'sequence', 'memory')

FORMAT = """\
FIGURE FORMAT  (one statement per line; '# ' starts a comment)
title: Text                 optional, drawn top left
kind: flow|tree|layers|sequence|memory   may be left out: inferred from statements
dir: down|right             flow/tree; default down
Labels: an id is its own label; `code` is monospace; \\n breaks a line; long labels wrap.
hot: a b    shade: c        yellow + heavy border / grey + dashed border (any kind)

flow    box id: label   round id: label   diamond id: label?   store id: label   note id: text
        a -> b: label   a ..> b (dashed blue)   a => b (red, the path taken)   a -- b   a <-> b
        a -> b -> c     chains; a name used only in an arrow becomes a plain box
  e.g.  round go: start
        diamond q: built in?
        go -> q
        q -> run: yes
        q -> fork: no
        fork ..> q: retry
tree    same statements; each box has one parent; kind: tree (or inferred)
  e.g.  kind: tree
        root -> left: < 5
        root -> right: >= 5
layers  layer id: Band label @ side note      bands stack in the order written
        in id: a = item text; b = item text     items in that band; a -> b joins neighbours
  e.g.  layer user: User space @ high addresses
        in user: sh = bash; ps = `ps -e`
        layer kern: Kernel
        in kern: tbl = process table
sequence actor id: label     then messages in time order
        a -> b: call   b ..> a: reply   a -> a: self   note over a: text   note over a,b: text
  e.g.  actor sh: shell
        sh -> k: `fork()`
        k ..> sh: child pid
memory  vars: p=1000@2000 x=5@1000 | hot=x shade=p     one row of named cells; @ address
        row arr: 10 20 30 40 | at=1000 step=4 | hot=1 shade=2-3 lo=0 hi=3
                                 array row: index numbers, addresses, k=i markers under cells
        index: 1 | off              start index numbers at 1, or hide them
        frame main: main's frame    rows that follow sit in this labelled box, until next frame
        ptr p -> x: label    dashed curved pointer arrow   ptr p -> arr[2]   ptr q -> null
  e.g.  frame swap: swap's frame
        vars: a=1000@3000 b=1004@3008
        frame main: main's frame
        vars: x=3@1000 y=7@1004
        ptr a -> x
        ptr b -> y
Limits: 12 boxes (24 cells), width 640 by default, refused over 760 (a dir: right flow that is too wide is
drawn top to bottom instead)."""


class Problem(Exception):
    """A refusal: the description line it belongs to and one sentence ending in its fix."""

    def __init__(self, line, msg):
        super().__init__(msg)
        self.line, self.msg = line, msg


# ---------------------------------------------------------------- style and contrast

TEXT_PAIRS = [('ink', 'box'), ('ink', 'ground'), ('ink', 'band'), ('ink', 'muted'),
              ('hot_ink', 'hot'), ('soft', 'ground'), ('soft', 'band'), ('soft', 'box')]
LINE_PAIRS = [('ink', 'ground'), ('ink', 'band'), ('red', 'ground'), ('red', 'band'),
              ('red', 'box'), ('blue', 'ground'), ('blue', 'band'), ('blue', 'box'),
              ('soft', 'ground')]


def luminance(hexc):
    h = hexc.lstrip('#')
    chans = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in chans]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def style_problems(st):
    out = []
    for theme in ('light', 'dark'):
        pal = st[theme]
        for pairs, need, what in ((TEXT_PAIRS, 4.5, 'text'), (LINE_PAIRS, 3.0, 'line')):
            for fg, bg in pairs:
                r = contrast(pal[fg], pal[bg])
                if r < need:
                    out.append('%s %s %s %s on %s %s is %.2f:1, needs %.1f:1: change one of them'
                               % (theme, what, fg, pal[fg], bg, pal[bg], r, need))
    return out


def load_style(path):
    try:
        with open(path, encoding='utf-8') as f:
            st = json.load(f)
        bad = style_problems(st)
    except (OSError, ValueError, KeyError) as e:
        bad = ['cannot use this style file (%s): restore scripts/fig-style.json' % e]
    if bad:
        for b in bad:
            print('%s: %s' % (path, b))
        sys.exit(1)
    return st


# ---------------------------------------------------------------- text measure and wrap

# Advance widths (1/100 em) of ASCII 32..126: the widest of Inter SemiBold/Bold and
# Arial Bold. Multiplied by the style's pessimism (1.15) this also covers DejaVu Sans Bold.
_W = [int(v) for v in (
    '28 34 55 65 65 102 72 34 38 38 56 68 33 47 33 39 67 56 63 65 68 64 65 58 65 65 33 34 68 '
    '68 68 61 102 75 72 74 72 67 61 78 75 28 58 72 61 93 76 78 67 78 72 67 67 74 75 104 74 '
    '73 66 38 39 38 58 56 37 58 63 59 63 60 40 63 62 28 28 58 28 91 62 61 63 63 41 56 37 62 '
    '60 85 58 60 57 47 37 47 68').split()]


class Text:
    """Measures and wraps labels. A run is (text, mono); a line is a list of runs."""

    def __init__(self, st):
        f = st['font']
        self.k, self.mono_em, self.lh = f['pessimism'], f['mono_em'], f['line_height']
        self.px = {'t': f['body'], 's': f['small'], 'tt': f['title']}

    def run_w(self, s, size, mono):
        px = self.px[size] * self.k
        if mono:
            return len(s) * self.mono_em * px
        return sum(_W[ord(c) - 32] if 32 <= ord(c) < 127 else 80 for c in s) / 100 * px

    def line_w(self, line, size):
        return sum(self.run_w(t, size, m) for t, m in line)

    def block(self, lines, size):
        """(width, height) of a block of lines."""
        w = max([self.line_w(l, size) for l in lines] or [0])
        return w, len(lines) * self.px[size] * self.lh

    @staticmethod
    def words(label, all_mono=False):
        """Split a label into words [(word, mono, glued to the previous word)], None = break."""
        out, prev = [], ' '
        for i, seg in enumerate(label.split('`')):
            mono = all_mono or i % 2 == 1
            for j, part in enumerate(seg.split('\\n')):
                if j:
                    out.append(None)
                for k, w in enumerate(part.split()):
                    glue = k == 0 and j == 0 and not part[:1].isspace() and \
                        not prev[-1:].isspace() and bool(out) and out[-1] is not None
                    out.append((w, mono, glue))
            prev = seg or ' '
        return out

    def wrap(self, label, maxw, size='t', all_mono=False):
        lines, cur = [], []
        for wd in self.words(label, all_mono) + [None]:
            if wd is None:
                if cur:
                    lines.append(cur)
                cur = []
                continue
            trial = _append(cur, wd)
            if cur and self.line_w(trial, size) > maxw:
                lines.append(cur)
                cur = _append([], wd)
            else:
                cur = trial
        return lines or [[('', False)]]


def _append(line, word):
    """Add a word to a line of runs, merging runs of the same font."""
    w, mono, glue = word
    line = [list(r) for r in line]
    if line and glue:
        if line[-1][1] == mono:
            line[-1][0] += w
        else:
            line.append([w, mono])
    elif line and line[-1][1] == mono:
        line[-1][0] += ' ' + w
    elif line and mono:         # keep the space in the sans run: SVG drops it after a tspan
        line[-1][0] += ' '
        line.append([w, mono])
    elif line:
        line.append([' ' + w, mono])
    else:
        line.append([w, mono])
    return [tuple(r) for r in line]


def plain(label):
    """A label as plain reading text."""
    return ' '.join(label.replace('`', '').replace('\\n', ' ').split())


# ---------------------------------------------------------------- parsing

TEMPLATES = {
    'title': 'title: text', 'kind': 'kind: flow', 'dir': 'dir: right', 'index': 'index: 0',
    'hot': 'hot: id', 'shade': 'shade: id', 'box': 'box id: label', 'round': 'round id: label',
    'diamond': 'diamond id: label?', 'store': 'store id: label', 'note': 'note id: text',
    'layer': 'layer id: label', 'in': 'in id: a = text; b = text', 'actor': 'actor id: label',
    'frame': 'frame id: label', 'vars': 'vars: x=5@1000', 'row': 'row arr: 1 2 3',
    'ptr': 'ptr p -> x', 'a': 'a -> b: label'}
SHAPES = ('box', 'round', 'diamond', 'store', 'note')
ARROW = re.compile(r'\s*(<->|\.\.>|->|=>|--)\s*')
ID_RE = re.compile(r'^[A-Za-z0-9_][\w.\-]*$')
OWNER = {'layer': 'layers', 'in': 'layers', 'actor': 'sequence', 'note over': 'sequence',
         'frame': 'memory', 'vars': 'memory', 'row': 'memory', 'ptr': 'memory', 'index': 'memory'}


class Fig:
    def __init__(self):
        self.title = self.kind = self.dir = None
        self.kind_line = self.dir_line = self.first = 0
        self.index = 0
        self.nodes = {}          # id -> node dict, in order of first mention
        self.edges = []          # dicts: a, b, op, label, line
        self.hot, self.shade = {}, {}   # id -> line
        self.layers = []         # dicts: id, label, side, items[], line
        self.blocks = []         # memory: [frame or None, [rows]]
        self.ptrs = []
        self.owned = []          # (statement owner kind, line) to check against the kind


def clean(raw):
    """Drop a '# ' comment, keep '#include' and the like."""
    return re.split(r'(?:^|\s)#(?=\s|$)', raw, maxsplit=1)[0].strip()


def parse(text, first_line=1):
    """Parse a description. Returns (Fig, [Problem])."""
    fig, probs = Fig(), []
    for n, raw in enumerate(text.splitlines(), first_line):
        s = clean(raw)
        if not s:
            continue
        fig.first = fig.first or n
        try:
            statement(fig, s, n)
        except Problem as p:
            probs.append(p)
    try:
        finish(fig)
    except Problem as p:
        probs.append(p)
    return fig, probs


def need_id(i, n):
    if not ID_RE.match(i):
        raise Problem(n, "'%s' is not a usable id: use letters, digits, _ . - only" % i)
    return i


def node(fig, i, n, label=None, shape='box'):
    need_id(i, n)
    nd = fig.nodes.get(i)
    if nd is None:
        nd = fig.nodes[i] = {'id': i, 'label': i, 'shape': 'box', 'line': n, 'auto': True}
    if label is not None or shape != 'box':
        nd.update(label=label if label else i, shape=shape, line=n, auto=False)
    return nd


def statement(fig, s, n):
    m = re.match(r'(title|kind|dir|index|hot|shade|vars)\s*:\s*(.*)$', s)
    if m:
        return keyed(fig, m.group(1), m.group(2).strip(), n)
    m = re.match(r'(\w+)\s+(.*)$', s)
    word = m.group(1) if m else s
    if m and word in SHAPES and not (word == 'note' and m.group(2).startswith('over ')):
        i, _, label = m.group(2).partition(':')
        node(fig, i.strip(), n, label.strip() or None, word)
        return
    if m and word in ('layer', 'in', 'actor', 'frame', 'row', 'ptr', 'note'):
        return globals()['st_' + word](fig, m.group(2).strip(), n)
    if ARROW.search(s):
        return st_edge(fig, s, n)
    near = difflib.get_close_matches(word.rstrip(':'), list(TEMPLATES), n=1, cutoff=0.5)
    hint = TEMPLATES[near[0]] if near else ('a -> b' if '>' in s else 'box id: label')
    raise Problem(n, "unknown statement '%s': did you mean '%s'?" % (s[:40], hint))


def keyed(fig, key, val, n):
    if key == 'title':
        fig.title = val
    elif key == 'kind':
        if val not in KINDS:
            near = difflib.get_close_matches(val, KINDS, n=1, cutoff=0.3)
            raise Problem(n, "unknown kind '%s': use %s" % (val, near[0] if near else 'flow')
                          + ' (kinds: ' + ', '.join(KINDS) + ')')
        fig.kind, fig.kind_line = val, n
    elif key == 'dir':
        if val not in ('down', 'right'):
            raise Problem(n, "dir must be down or right, not '%s': write dir: right" % val)
        fig.dir, fig.dir_line = val, n
    elif key == 'index':
        if val != 'off' and not val.isdigit():
            raise Problem(n, "index must be a number or off, not '%s': write index: 0" % val)
        fig.index = None if val == 'off' else int(val)
        fig.owned.append(('memory', n))
    elif key in ('hot', 'shade'):
        for i in re.split(r'[\s,]+', val):
            if i:
                getattr(fig, key)[i] = n
    else:
        st_vars(fig, val, n)


def st_edge(fig, s, n):
    body, _, label = s.partition(': ')
    if label == '' and body.endswith(':'):
        body = body[:-1]
    parts = ARROW.split(' ' + body.strip() + ' ')
    parts = [p.strip() for p in parts]
    ids, ops = parts[0::2], parts[1::2]
    if len(ids) < 2 or not ids[0] or not ids[-1]:
        raise Problem(n, "arrow needs a box at each end: write 'a -> b: label'")
    for k, op in enumerate(ops):
        a, b = ids[k], ids[k + 1]
        lab = label.strip() if k == len(ops) - 1 else ''
        fig.edges.append({'a': need_id(a, n), 'b': need_id(b, n), 'op': op, 'label': lab,
                          'line': n})


def st_layer(fig, rest, n):
    i, _, label = rest.partition(':')
    label, _, side = label.partition('@')
    fig.layers.append({'id': need_id(i.strip(), n), 'label': label.strip() or i.strip(),
                       'side': side.strip(), 'items': [], 'line': n})
    fig.owned.append(('layers', n))


def st_in(fig, rest, n):
    i, _, items = rest.partition(':')
    lay = [l for l in fig.layers if l['id'] == i.strip()]
    if not lay:
        raise Problem(n, "no layer '%s' above this line: add 'layer %s: label' first"
                      % (i.strip(), i.strip()))
    for it in items.split(';'):
        if it.strip():
            k, eq, v = it.partition('=')
            nd = node(fig, k.strip(), n, v.strip() if eq else None)
            lay[0]['items'].append(nd['id'])
    fig.owned.append(('layers', n))


def st_actor(fig, rest, n):
    i, _, label = rest.partition(':')
    node(fig, i.strip(), n, label.strip() or None)
    fig.nodes[i.strip()]['actor'] = True
    fig.owned.append(('sequence', n))


def st_note(fig, rest, n):
    who, _, text = rest[5:].partition(':')
    ids = [need_id(w.strip(), n) for w in who.split(',') if w.strip()]
    if not ids or len(ids) > 2 or not text.strip():
        raise Problem(n, "write 'note over a: text' or 'note over a,b: text'")
    fig.edges.append({'a': ids[0], 'b': ids[-1], 'op': 'note', 'label': text.strip(), 'line': n})
    fig.owned.append(('sequence', n))


def st_frame(fig, rest, n):
    i, _, label = rest.partition(':')
    fig.blocks.append([{'id': i.strip(), 'label': label.strip() or i.strip(), 'line': n}, []])
    fig.owned.append(('memory', n))


def marks(text, n, names=None):
    """Parse 'hot=1 shade=2-3 at=1000 step=4 lo=0' into a dict of lists/values."""
    out = {'hot': [], 'shade': [], 'markers': []}
    for tok in text.split():
        k, eq, v = tok.partition('=')
        if not eq or not v:
            raise Problem(n, "mark '%s' needs a value: write hot=1 or at=1000" % tok)
        if k in ('at', 'step'):
            if not re.match(r'^(0x)?[0-9A-Fa-f]+$', v):
                raise Problem(n, "%s=%s is not a number: write %s=1000" % (k, v, k))
            out[k] = v
            continue
        for part in v.split(','):
            if names is None and re.match(r'^\d+-\d+$', part):
                lo, hi = map(int, part.split('-'))
                vals = list(range(lo, hi + 1))
            elif names is None and not part.isdigit():
                raise Problem(n, "%s=%s: give a cell number, like %s=2" % (k, part, k))
            else:
                vals = [int(part) if names is None else part]
            for v2 in vals:
                if k in ('hot', 'shade'):
                    out[k].append(v2)
                else:
                    out['markers'].append((v2, k))
    return out


def current_rows(fig):
    if not fig.blocks:
        fig.blocks.append([None, []])
    return fig.blocks[-1][1]


VAR_RE = re.compile(r'([^\s=]+)=(`[^`]*`|"[^"]*"|[^\s@]*)(?:@(\S+))?')


def st_vars(fig, val, n):
    body, _, mk = val.partition('|')
    cells = []
    for m in VAR_RE.finditer(body):
        cells.append({'name': m.group(1), 'value': m.group(2).strip('`"'), 'addr': m.group(3)})
    rest = VAR_RE.sub('', body).strip()
    if rest or not cells:
        raise Problem(n, "cannot read '%s' in vars: write vars: x=5@1000 p=1000" % (rest or val))
    current_rows(fig).append({'type': 'vars', 'cells': cells, 'line': n,
                              'marks': marks(mk.replace('|', ' '), n, names=True)})
    fig.owned.append(('memory', n))


def st_row(fig, rest, n):
    name, colon, body = rest.partition(':')
    if not colon:
        raise Problem(n, "write 'row name: 1 2 3' (a colon after the row name)")
    vals, _, mk = body.partition('|')
    values = re.findall(r'`[^`]*`|"[^"]*"|\S+', vals)
    if not values:
        raise Problem(n, "row '%s' has no values: write row %s: 1 2 3" % (name, name))
    m = marks(mk.replace('|', ' '), n)
    cells = [{'name': '%s[%d]' % (name.strip(), k), 'value': v.strip('`"'), 'addr': None}
             for k, v in enumerate(values)]
    current_rows(fig).append({'type': 'row', 'name': name.strip(), 'cells': cells,
                              'marks': m, 'line': n})
    fig.owned.append(('memory', n))


def st_ptr(fig, rest, n):
    body, _, label = rest.partition(':')
    m = re.match(r'^(\S+)\s*->\s*(\S+)$', body.strip())
    if not m:
        raise Problem(n, "write 'ptr p -> x' (or 'ptr p -> null')")
    fig.ptrs.append({'a': m.group(1), 'b': m.group(2), 'label': label.strip(), 'line': n})
    fig.owned.append(('memory', n))


def finish(fig):
    """Infer the kind, check statements belong to it, create boxes named only in arrows."""
    owners = [o for o, _ in fig.owned]
    if fig.kind is None:
        for k in ('memory', 'sequence', 'layers'):
            if k in owners:
                fig.kind = k
                break
        else:
            fig.kind = 'tree' if looks_like_tree(fig) else 'flow'
    for o, n in fig.owned:
        if o != fig.kind:
            raise Problem(n, 'this statement belongs to kind: %s, not %s: remove it or change '
                             'the kind' % (o, fig.kind))
    if fig.kind == 'memory' and (fig.nodes or fig.edges):
        e = (fig.edges or [{'line': fig.kind_line}])[0]
        raise Problem(e['line'], "memory figures join cells with 'ptr p -> x', not boxes and "
                                 "arrows: rewrite it as ptr")
    for e in fig.edges:
        for i in (e['a'], e['b']):
            node(fig, i, e['line'])
            if fig.kind == 'sequence':
                fig.nodes[i]['actor'] = True
    for which in (fig.hot, fig.shade):
        for i, n in which.items():
            if fig.kind != 'memory' and i not in fig.nodes:
                raise Problem(n, "hot/shade names '%s', which is not a box: use one of %s"
                              % (i, ', '.join(list(fig.nodes)[:6])))


def looks_like_tree(fig):
    if len(fig.edges) < 2 or any(e['op'] not in ('->', '--') for e in fig.edges):
        return False
    if any(nd['shape'] != 'box' for nd in fig.nodes.values()):
        return False
    parents = {}
    for e in fig.edges:
        if e['b'] in parents or e['a'] == e['b']:
            return False
        parents[e['b']] = e['a']
    roots = {e['a'] for e in fig.edges} - set(parents)
    return len(roots) == 1 and max(list(parents.values()).count(p) for p in parents.values()) > 1

# ---------------------------------------------------------------- scene

def up(v, g=8):
    return int(math.ceil(v / g - 1e-9) * g)


def bezier(p, t):
    a, b, c, d = p
    m = 1 - t
    return (m ** 3 * a[0] + 3 * m * m * t * b[0] + 3 * m * t * t * c[0] + t ** 3 * d[0],
            m ** 3 * a[1] + 3 * m * m * t * b[1] + 3 * m * t * t * c[1] + t ** 3 * d[1])


def samples(pts, curve, step=4):
    """Points every few px along a polyline or one cubic Bezier."""
    if curve:
        return [bezier(pts, k / 48) for k in range(49)]
    out = [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        out += [(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n) for k in range(1, n + 1)]
    return out


class Scene:
    """Everything a figure draws, in draw order, as plain dicts; written out by svg()."""

    def __init__(self, st, tx):
        self.st, self.tx, self.els = st, tx, []
        self.sh = st['size']['shadow']
        self.count, self.noun = 0, 'nodes'

    def box(self, role, i, x, y, w, h, cls='box', shape='rect', shadow=True):
        e = dict(t='box', role=role, id=i, x=x, y=y, w=w, h=h, cls=cls, shape=shape,
                 shadow=shadow)
        self.els.append(e)
        return e

    def text(self, i, cx, cy, lines, size='t', anchor='middle', cls='ink', inn=None,
             plate=None, role='label'):
        w, h = self.tx.block(lines, size)
        x0 = {'middle': cx - w / 2, 'start': cx, 'end': cx - w}[anchor]
        e = dict(t='text', role=role, id=i, x=x0, y=cy - h / 2, w=w, h=h, ax=cx, cy=cy,
                 lines=lines, size=size, anchor=anchor, cls=cls, inn=inn, plate=plate)
        self.els.append(e)
        return e

    def edge(self, i, a, b, pts, kind='k', head='end', curve=False, dot=False):
        e = dict(t='edge', id=i, a=a, b=b, pts=pts, kind=kind, head=head, curve=curve, dot=dot)
        self.els.append(e)
        return e

    def mark(self, cls, pts, role='deco'):
        self.els.append(dict(t='mark', cls=cls, pts=pts, role=role))
        return self.els[-1]

    def bbox(self, e):
        if e['t'] == 'box':
            s = self.sh if e['shadow'] else 0
            return e['x'], e['y'], e['x'] + e['w'] + s, e['y'] + e['h'] + s
        if e['t'] == 'text':
            p = 4 if e['plate'] else 0
            return e['x'] - p, e['y'] - p / 2, e['x'] + e['w'] + p, e['y'] + e['h'] + p / 2
        pts = samples(e['pts'], e.get('curve'))
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        return min(xs) - 6, min(ys) - 6, max(xs) + 6, max(ys) + 6

    def extent(self):
        bs = [self.bbox(e) for e in self.els]
        return (min(b[0] for b in bs), min(b[1] for b in bs),
                max(b[2] for b in bs), max(b[3] for b in bs))

    def shift(self, dx, dy):
        for e in self.els:
            if 'x' in e:
                e['x'] += dx
                e['y'] += dy
            if 'ax' in e:
                e['ax'] += dx
                e['cy'] += dy
            if 'pts' in e:
                e['pts'] = [(x + dx, y + dy) for x, y in e['pts']]

    def finish(self, title):
        """Move content inside the margin, add the title, return (width, height)."""
        S = self.st['size']
        m = S['margin']
        x0, y0, x1, y1 = self.extent()
        top = m
        tl = None
        if title:
            tl = self.tx.wrap(title, S['max_width'] - 2 * m, 'tt')
            top += up(self.tx.block(tl, 'tt')[1] + 12)
        w = max(up(x1 - x0 + 2 * m), up(self.tx.block(tl, 'tt')[0] + 2 * m) if tl else 0)
        dx = up((w - (x1 - x0)) / 2 - x0, 8) if w > up(x1 - x0 + 2 * m) else up(m - x0)
        self.shift(dx, up(top - y0))
        if tl:
            th = self.tx.block(tl, 'tt')[1]
            self.els.insert(0, None)
            self.els[0] = dict(t='text', role='title', id='title', x=m, y=m, w=0, h=th,
                               ax=m, cy=m + th / 2, lines=tl, size='tt', anchor='start',
                               cls='ink', inn=None, plate=None)
            self.els[0]['w'] = self.tx.block(tl, 'tt')[0]
        return w, up(self.extent()[3] + m)


# ---------------------------------------------------------------- flow and tree

EDGE_KIND = {'->': ('k', 'end'), '..>': ('b', 'end'), '=>': ('r', 'end'),
             '--': ('k', 'none'), '<->': ('k', 'both')}


class Graph:
    """Ranked layout in (u, v): u runs across ranks, v along them. dir: right swaps axes."""

    def __init__(self, fig, st, tx, wrapw):
        self.fig, self.st, self.tx, self.S = fig, st, tx, st['size']
        self.down = fig.dir != 'right'
        self.ids = list(fig.nodes)
        self.edges = [e for e in fig.edges]
        self.wrapw = wrapw
        self.size_nodes()
        self.rank_nodes()

    # -- sizes
    def size_nodes(self):
        S, tx = self.S, self.tx
        self.lines, self.wh = {}, {}
        for i in self.ids:
            nd = self.fig.nodes[i]
            size = 's' if nd['shape'] == 'note' else 't'
            ww = min(self.wrapw, S['wrap_narrow']) if nd['shape'] == 'diamond' else self.wrapw
            lines = tx.wrap(nd['label'], ww, size)
            tw, th = tx.block(lines, size)
            if tw > ww + 0.5:
                raise Problem(nd['line'], "label of '%s' is %d px too wide for its box: shorten "
                              "it or break it with \\n" % (i, math.ceil(tw - ww)))
            if len(lines) > 4:
                raise Problem(nd['line'], "label of '%s' wraps to %d lines: shorten it to 4 "
                              "lines or fewer" % (i, len(lines)))
            if nd['shape'] == 'diamond':
                w = up(tw + 2 * th + 48, 16)
                h = up(max(w / 2, th + 40), 16)
            else:
                h = up(max(S['box_min_h'], th + 2 * S['pad_y'] + (8 if nd['shape'] == 'store'
                                                                    else 0)), 16)
                extra = h + 8 if nd['shape'] == 'round' else 2 * S['pad_x']
                w = up(max(S['box_min_w'], tw + extra), 16)
            self.lines[i], self.wh[i] = (lines, size), [w, h]

    def ext(self, i):
        """(cross extent, rank extent)."""
        w, h = self.wh[i]
        return (w, h) if self.down else (h, w)

    # -- ranks and order
    def rank_nodes(self):
        ids, edges = self.ids, self.edges
        outs = {i: [] for i in ids}
        ins = {i: [] for i in ids}
        for k, e in enumerate(edges):
            if e['a'] == e['b']:
                raise Problem(e['line'], "'%s' points to itself: add a second box" % e['a'])
            outs[e['a']].append(k)
            ins[e['b']].append(k)
        if self.fig.kind == 'tree':
            for i in ids:
                if len(ins[i]) > 1:
                    raise Problem(edges[ins[i][1]]['line'], "'%s' has two parents, which a tree "
                                  "cannot draw: use kind: flow" % i)
        back, state = set(), {}

        def dfs(u):
            state[u] = 1
            for k in outs[u]:
                v = edges[k]['b']
                if state.get(v) == 1:
                    back.add(k)
                elif v not in state:
                    dfs(v)
            state[u] = 2
        for i in [i for i in ids if not ins[i]] + ids:
            if i not in state:
                dfs(i)
        if self.fig.kind == 'tree' and back:
            raise Problem(edges[min(back)]['line'], 'a tree cannot loop back: use kind: flow')
        rank = {i: 0 for i in ids}
        for _ in ids:
            for k, e in enumerate(edges):
                if k not in back:
                    rank[e['b']] = max(rank[e['b']], rank[e['a']] + 1)
        self.back, self.rank, self.outs, self.ins = back, rank, outs, ins
        self.R = max(rank.values()) + 1
        self.byr = [[i for i in ids if rank[i] == r] for r in range(self.R)]
        if self.fig.kind != 'tree':
            self.order()

    def order(self):
        """Barycentre sweeps: sort each rank by the mean place of its neighbours."""
        fwd = [e for k, e in enumerate(self.edges) if k not in self.back]
        for sweep in range(4):
            rs = range(1, self.R) if sweep % 2 == 0 else range(self.R - 2, -1, -1)
            for r in rs:
                ref = self.byr[r - 1] if sweep % 2 == 0 else self.byr[r + 1]
                pos = {i: p for p, i in enumerate(ref)}
                cur = self.byr[r]

                def key(i):
                    nb = [pos[e['a']] for e in fwd if e['b'] == i and e['a'] in pos] + \
                         [pos[e['b']] for e in fwd if e['a'] == i and e['b'] in pos]
                    return (sum(nb) / len(nb) if nb else cur.index(i), self.ids.index(i))
                self.byr[r] = sorted(cur, key=key)

    # -- cross positions
    def place_cross(self):
        gap = self.S['node_gap']
        self.u = {}
        if self.fig.kind == 'tree':
            kids = {i: [self.edges[k]['b'] for k in self.outs[i]] for i in self.ids}
            width = {}

            def span(i):
                for c in kids[i]:
                    span(c)
                s = sum(width[c] for c in kids[i]) + gap * (len(kids[i]) - 1)
                width[i] = max(self.ext(i)[0], s)

            def put(i, left):
                ks = kids[i]
                s = sum(width[c] for c in ks) + gap * (len(ks) - 1)
                x = left + (width[i] - s) / 2
                for c in ks:
                    put(c, x)
                    x += width[c] + gap
                self.u[i] = (self.u[ks[0]] + self.u[ks[-1]]) / 2 if ks else left + width[i] / 2
            left = 0
            for root in self.byr[0]:
                span(root)
                put(root, left)
                left += width[root] + gap
            for i in self.ids:
                self.u[i] -= left / 2
            return
        # Each box goes under the mean of its parents; overlaps are resolved by averaging a
        # push-right and a push-left pass (both keep the order and the gaps, so the mean does).
        fwd = [e for k, e in enumerate(self.edges) if k not in self.back]
        for r, row in enumerate(self.byr):
            total = sum(self.ext(i)[0] for i in row) + gap * (len(row) - 1)
            x, want = -total / 2, []
            for i in row:
                par = [self.u[e['a']] for e in fwd if e['b'] == i]
                want.append(sum(par) / len(par) if par and r else x + self.ext(i)[0] / 2)
                x += self.ext(i)[0] + gap
            sep = [(self.ext(a)[0] + self.ext(b)[0]) / 2 + gap for a, b in zip(row, row[1:])]
            lft, rgt = want[:], want[:]
            for k in range(1, len(row)):
                lft[k] = max(lft[k], lft[k - 1] + sep[k - 1])
            for k in range(len(row) - 2, -1, -1):
                rgt[k] = min(rgt[k], rgt[k + 1] - sep[k])
            for k, i in enumerate(row):
                self.u[i] = round((lft[k] + rgt[k]) / 2 / 8) * 8
            for k in range(1, len(row)):
                self.u[row[k]] = max(self.u[row[k]], self.u[row[k - 1]] + up(sep[k - 1]))

    def push(self, i, axis):
        """How far the shadow sticks out past the + side of node i on 'u' or 'v' axis."""
        sh = self.S['shadow']
        if self.fig.nodes[i]['shape'] != 'diamond':
            return sh
        bottom = (axis == 'v') == self.down
        return sh / 2 if bottom else 0

    def label_lines(self, e):
        return self.tx.wrap(e['label'], 120, 's') if e['label'] else None

    def lab_ext(self, e):
        """(cross extent, rank extent) of an edge label with its plate."""
        if not e['label']:
            return 0, 0
        w, h = self.tx.block(self.label_lines(e), 's')
        w, h = w + 8, h + 4
        return (w, h) if self.down else (h, w)

    # -- routing plan
    def plan(self):
        """Decide each edge's path in abstract terms and the tracks each gap needs."""
        S = self.S
        half = {i: (self.ext(i)[0] / 2, self.ext(i)[1] / 2) for i in self.ids}
        self.half = half
        segs = {r: [] for r in range(-1, self.R)}   # gap r lies below rank r
        self.paths = []
        self.ports()
        nback = 0
        for k, e in enumerate(self.edges):
            a, b = e['a'], e['b']
            ra, rb = self.rank[a], self.rank[b]
            ua, ub = self.u[a] + self.po[k][0], self.u[b] + self.po[k][1]
            # a fan-out shares one track (a bus) from its source; a lone edge shares the
            # track of its target, so edges merging into one box meet on one line
            fan = sum(1 for kk, f in enumerate(self.edges) if kk not in self.back and
                      f['a'] == a and f['op'] == e['op']) > 1
            k1 = ('s', a, e['op']) if fan else ('t', b, e['op'])
            if k not in self.back and rb == ra + 1:
                if ua != ub:
                    segs[ra].append([k1, min(ua, ub), max(ua, ub)])
                self.paths.append(('fwd', k, (None, k1, None)))
                continue
            if k not in self.back:
                uc = self.column(ra, rb, ua, ub)
                k1 = ('s', a, e['op']) if fan else ('l', k)
                k2 = ('t', b, e['op'])
                if uc != ua:
                    segs[ra].append([k1, min(ua, uc), max(ua, uc)])
                if uc != ub:
                    segs[rb - 1].append([k2, min(uc, ub), max(uc, ub)])
                self.paths.append(('fwd', k, (uc, k1, k2)))
                continue
            span = [i for i in self.ids if rb <= self.rank[i] <= ra]
            side = 1 if self.u[a] == max(self.u[i] for i in self.byr[ra]) and \
                self.u[b] == max(self.u[i] for i in self.byr[rb]) else \
                -1 if self.u[a] == min(self.u[i] for i in self.byr[ra]) and \
                self.u[b] == min(self.u[i] for i in self.byr[rb]) else 0
            reach = max(self.u[i] + half[i][0] + S['shadow'] for i in span) if side >= 0 else \
                min(self.u[i] - half[i][0] for i in span)
            out = reach + (1 if side >= 0 else -1) * (24 + self.lab_ext(e)[0] / 2 + 16 * nback)
            nback += 1
            if side == 0:
                segs[ra].append([('b', k), min(ua, out), max(ua, out)])
                segs[rb - 1].append([('B', k), min(ub, out), max(ub, out)])
            self.paths.append(('back', k, (side, up(out) if side >= 0 else -up(-out))))
        return segs

    def ports(self):
        """Edges of different kinds leaving (or entering) one side get ports 16 px apart."""
        self.po = {k: [0, 0] for k in range(len(self.edges))}
        for i in self.ids:
            for end, other in ((0, 'b'), (1, 'a')):
                ks = [k for k, e in enumerate(self.edges) if k not in self.back and
                      e['ab'[end]] == i]
                ops = sorted({self.edges[k]['op'] for k in ks}, key=lambda op: (min(
                    self.u[self.edges[k][other]] for k in ks if self.edges[k]['op'] == op), op))
                for k in ks:
                    if len(ops) > 1:
                        self.po[k][end] = (ops.index(self.edges[k]['op']) - (len(ops) - 1) / 2) * 16

    def column(self, ra, rb, ua, ub):
        """A cross position free of boxes in the ranks a long edge passes."""
        blocked = []
        for r in range(ra + 1, rb):
            for i in self.byr[r]:
                blocked.append((self.u[i] - self.half[i][0] - 16,
                                self.u[i] + self.half[i][0] + self.S['shadow'] + 16))
        cands = [ua, ub] + [up(lo) - 8 for lo, _ in blocked] + [up(hi) + 8 for _, hi in blocked]
        free = [c for c in cands if not any(lo < c < hi for lo, hi in blocked)]
        return min(free, key=lambda c: (abs(ua - c) + abs(c - ub), c))

    def tracks(self, segs):
        """Give overlapping horizontal runs in one gap different tracks."""
        self.track = {}
        n = {}
        for r, lst in segs.items():
            merged = {}
            for key, lo, hi in lst:
                if key in merged:
                    merged[key] = [min(merged[key][0], lo), max(merged[key][1], hi)]
                else:
                    merged[key] = [lo, hi]
            used = []
            for key, (lo, hi) in sorted(merged.items(), key=lambda kv: (kv[1], str(kv[0]))):
                t = 0
                while any(t == tt and lo < h2 + 16 and l2 - 16 < hi for tt, l2, h2 in used):
                    t += 1
                used.append((t, lo, hi))
                self.track[(r, key)] = t
            n[r] = 1 + max([t for t, _, _ in used] or [-1])
        return n

    def place_ranks(self, ntr):
        S = self.S
        tg = S['track_gap']
        thick = [max(self.ext(i)[1] for i in row) for row in self.byr]
        labz = {r: 0 for r in range(-1, self.R)}
        for k, e in enumerate(self.edges):
            if k not in self.back:
                labz[self.rank[e['b']] - 1] = max(labz[self.rank[e['b']] - 1], self.lab_ext(e)[1])
        self.gap, self.vtop, self.labz = {}, [], labz
        v = 0
        for r in range(self.R):
            self.vtop.append(v)
            g = 20 + tg * max(0, ntr[r] - 1) + (labz[r] + 16 if labz[r] else 0) + 20
            self.gap[r] = up(max(S['rank_gap'], g))
            v += thick[r] + self.gap[r]
        self.thick = thick
        self.v = {i: self.vtop[self.rank[i]] + thick[self.rank[i]] / 2 for i in self.ids}
        # boxes in a rank share the rank extent, diamonds keep their own
        for i in self.ids:
            if self.fig.nodes[i]['shape'] != 'diamond':
                same = [self.ext(j)[1] for j in self.byr[self.rank[i]]
                        if self.fig.nodes[j]['shape'] != 'diamond']
                self.wh[i][1 if self.down else 0] = max(same)
        self.half = {i: (self.ext(i)[0] / 2, self.ext(i)[1] / 2) for i in self.ids}

    def gap_v(self, r, t, ntr):
        """v of track t in the gap below rank r (r = -1: above rank 0, r = R-1: below all)."""
        tg = self.S['track_gap']
        if r < 0:
            return -24 - tg * t
        start = self.vtop[r] + self.thick[r]
        if r == self.R - 1:
            return start + 24 + tg * t
        if not self.labz[r]:
            return start + self.gap[r] / 2 + tg * (t - (ntr[r] - 1) / 2)
        return start + 20 + tg * t

    def label_v(self, r, ntr):
        lo = self.gap_v(r, max(0, ntr[r] - 1), ntr) + 8 if ntr[r] else self.vtop[r] + \
            self.thick[r] + 12
        return (lo + self.vtop[r + 1] - 12) / 2

    def P(self, u, v):
        return (u, v) if self.down else (v, u)

    def layout(self):
        self.place_cross()
        self.half = {i: (self.ext(i)[0] / 2, self.ext(i)[1] / 2) for i in self.ids}
        segs = self.plan()
        ntr = self.tracks(segs)
        self.place_ranks(ntr)
        sc = Scene(self.st, self.tx)
        sc.count, sc.graph = len(self.ids), self
        for i in self.ids:
            self.draw_node(sc, i)
        for kind, k, extra in self.paths:
            self.draw_edge(sc, kind, k, extra, ntr)
        return sc

    def draw_node(self, sc, i):
        nd = self.fig.nodes[i]
        (cu, cv), u, v = self.half[i], self.u[i], self.v[i]
        x, y = self.P(u - cu, v - cv)
        w, h = self.P(2 * cu, 2 * cv)
        cls = 'hot' if i in self.fig.hot else 'mut' if i in self.fig.shade else \
            'note' if nd['shape'] == 'note' else 'box'
        shape = {'round': 'pill'}.get(nd['shape'], nd['shape'])
        sc.box('node', i, x, y, w, h, cls, shape, nd['shape'] != 'note')
        lines, size = self.lines[i]
        cx, cy = self.P(u, v)
        sc.text(i, cx, cy + (4 if nd['shape'] == 'store' else 0), lines, size,
                cls='hink' if cls == 'hot' else 'ink', inn=i)

    def draw_edge(self, sc, kind, k, extra, ntr):
        e = self.edges[k]
        a, b = e['a'], e['b']
        ra, rb = self.rank[a], self.rank[b]
        ua, ub, va, vb = self.u[a], self.u[b], self.v[a], self.v[b]
        if kind == 'fwd':
            ua, ub = ua + self.po[k][0], ub + self.po[k][1]
        ha, hb = self.half[a], self.half[b]
        start = (ua, va + ha[1] + self.push(a, 'v'))
        lab = None
        if kind == 'fwd':
            uc, k1, k2 = extra
            end = (ub, vb - hb[1])
            t1 = self.gap_v(ra, self.track.get((ra, k1), 0), ntr)
            if uc is None:
                pts = [start, (ua, t1), (ub, t1), end]
            else:
                t2 = self.gap_v(rb - 1, self.track.get((rb - 1, k2), 0), ntr)
                pts = [start, (ua, t1), (uc, t1), (uc, t2), (ub, t2), end]
            lab = (ub, self.label_v(rb - 1, ntr))
        else:
            side, out = extra
            if side:
                pa = self.push(a, 'u') if side > 0 else 0
                pb = self.push(b, 'u') if side > 0 else 0
                start = (ua + side * (ha[0] + pa), va)
                end = (ub + side * (hb[0] + pb), vb)
                pts = [start, (out, va), (out, vb), end]
            else:
                t1 = self.gap_v(ra, self.track[(ra, ('b', k))], ntr)
                t2 = self.gap_v(rb - 1, self.track[(rb - 1, ('B', k))], ntr)
                end = (ub, vb - hb[1])
                pts = [start, (ua, t1), (out, t1), (out, t2), (ub, t2), end]
            lab = (out, (va + vb) / 2)
        pts = simplify([self.P(*p) for p in pts])
        ek, head = EDGE_KIND[e['op']]
        eid = 'e%d' % (k + 1)
        sc.edge(eid, a, b, pts, ek, head)
        if e['label']:
            sc.text(eid, *self.P(*lab), self.label_lines(e), 's', plate='plate', inn=None)


def simplify(pts):
    """Drop repeated and collinear points of an orthogonal path."""
    out = []
    for p in pts:
        p = (round(p[0], 2), round(p[1], 2))
        if out and abs(p[0] - out[-1][0]) < 0.01 and abs(p[1] - out[-1][1]) < 0.01:
            continue
        if len(out) >= 2:
            (x0, y0), (x1, y1) = out[-2], out[-1]
            if (abs(x0 - x1) < 0.01 and abs(x1 - p[0]) < 0.01) or \
               (abs(y0 - y1) < 0.01 and abs(y1 - p[1]) < 0.01):
                out[-1] = p
                continue
        out.append(p)
    return out


def layout_graph(fig, st, tx):
    S = st['size']
    if len(fig.nodes) > S['max_boxes']:
        nd = list(fig.nodes.values())[S['max_boxes']]
        raise Problem(nd['line'], '%d boxes, more than %d: split the figure in two'
                      % (len(fig.nodes), S['max_boxes']))
    if not fig.nodes:
        raise Problem(fig.first or 1, "nothing to draw: add boxes and arrows, like 'a -> b'")
    best = None
    for wrapw in (S['wrap'], S['wrap_narrow'], 96):
        try:
            sc = Graph(fig, st, tx, wrapw).layout()
        except Problem:
            if best is None:
                raise
            break
        x0, _, x1, _ = sc.extent()
        width = x1 - x0 + 2 * S['margin']
        if best is None or width < best[0]:
            best = (width, sc)
        if width <= S['max_width']:
            break
    width, sc = best
    if width > S['hard_width'] and fig.dir == 'right' and not getattr(fig, 'turned', False):
        fig.turned, fig.dir = True, 'down'      # a row too wide for the page is drawn top to bottom instead
        return layout_graph(fig, st, tx)
    if width > S['hard_width']:
        fix = 'add dir: right' if fig.dir != 'right' else 'use dir: down'
        first = min([n['line'] for n in fig.nodes.values()] or [1])
        raise Problem(fig.dir_line or fig.kind_line or first, 'figure is %d px wide, more than '
                      '%d: %s, shorten '
                      'labels or split it' % (width, S['hard_width'], fix))
    return sc


# ---------------------------------------------------------------- memory

def addr_at(base, step, k):
    if base.lower().startswith('0x'):
        return '0x%X' % (int(base, 16) + k * int(step or '4', 0))
    return str(int(base) + k * int(step or '4'))


DOTZONE = 32     # room at the right of a pointer cell for its dot or its null slash


class Memory:
    """Rows of cells (named variables or arrays), optional frames, pointer arrows."""

    def __init__(self, fig, st, tx):
        self.fig, self.st, self.tx, self.S = fig, st, tx, st['size']
        self.sc = Scene(st, tx)
        self.sc.noun = 'cells'
        self.cells = {}         # ref -> cell dict (with geometry once placed)
        self.labels = []        # rects that pointer arrows must avoid

    def prepare(self):
        S, tx, fig = self.S, self.tx, self.fig
        n = 0
        for frame, rows in fig.blocks:
            for row in rows:
                mk = row['marks']
                for k, c in enumerate(row['cells']):
                    n += 1
                    key = c['name'] if row['type'] == 'vars' else k
                    c['cls'] = 'hot' if key in mk['hot'] or c['name'] in fig.hot else \
                        'mut' if key in mk['shade'] or c['name'] in fig.shade else 'box'
                    c['row'], c['k'] = row, k
                    if row['type'] == 'row' and 'at' in mk:
                        c['addr'] = addr_at(mk['at'], mk.get('step'), k)
                    if c['name'] in self.cells:
                        raise Problem(row['line'], "cell '%s' is named twice: rename one"
                                      % c['name'])
                    self.cells[c['name']] = c
                    vw = tx.run_w(c['value'], 't', True)
                    if vw > S['cell_max_text']:
                        raise Problem(row['line'], "value '%s' is %d px too wide for its cell: "
                                      "shorten it to %d characters or fewer" % (
                                          c['value'], vw - S['cell_max_text'],
                                          int(S['cell_max_text'] / tx.run_w('0', 't', True))))
                    c['vw'] = vw
                for key in mk['hot'] + mk['shade'] + [i for i, _ in mk['markers']]:
                    if (row['type'] == 'vars' and key not in [c['name'] for c in row['cells']]) \
                            or (row['type'] == 'row' and not 0 <= key < len(row['cells'])):
                        raise Problem(row['line'], "mark names cell %s, which this row does not "
                                      "have: use one of %s" % (key, self.choices(row)))
        if n > S['max_cells']:
            raise Problem(fig.blocks[-1][1][-1]['line'] if fig.blocks[-1][1] else None,
                          '%d cells, more than %d: split the figure in two' % (n, S['max_cells']))
        if not n:
            raise Problem(fig.first or 1, "no cells to draw: add 'vars: x=5' or 'row a: 1 2 3'")
        for i, nm in list(fig.hot.items()) + list(fig.shade.items()):
            if i not in self.cells:
                raise Problem(nm, "hot/shade names '%s', which is not a cell: use one of %s"
                              % (i, ', '.join(list(self.cells)[:6])))
        for p in fig.ptrs:
            p['src'] = self.ref(p['a'], p['line'])
            p['dst'] = None if p['b'].lower() in ('null', 'nullptr') else self.ref(p['b'], p['line'])
            if p['src'].get('ptr'):
                raise Problem(p['line'], "'%s' already has a pointer arrow: draw one arrow per "
                              "cell" % p['a'])
            p['src']['ptr'] = p
            if p['dst'] is p['src']:
                raise Problem(p['line'], "'%s' points to itself: point it at another cell" % p['a'])

    def choices(self, row):
        names = [c['name'] for c in row['cells']]
        return ', '.join(names) if row['type'] == 'vars' else '0 to %d' % (len(names) - 1)

    def ref(self, r, line):
        if r in self.cells:
            return self.cells[r]
        if r + '[0]' in self.cells:
            return self.cells[r + '[0]']
        near = difflib.get_close_matches(r, list(self.cells), n=3, cutoff=0.3)
        raise Problem(line, "'%s' is not a cell: use one of %s" % (
            r, ', '.join(near or list(self.cells)[:4])))

    # -- geometry of one row, relative to its own left edge and its cell top
    def measure_row(self, row):
        S, tx = self.S, self.tx
        arr = row['type'] == 'row'
        src = any(c.get('ptr') for c in row['cells'])
        if arr:
            cw = up(max(S['cell_min_w'], max(c['vw'] for c in row['cells']) + 24 +
                        (DOTZONE if src else 0)), 16)
            for c in row['cells']:
                if c['addr'] and tx.run_w(c['addr'], 's', True) > cw - 4:
                    raise Problem(row['line'], "address %s is too wide for its cell: use "
                                  "shorter addresses, like at=100" % c['addr'])
            lw = up(tx.run_w(row['name'], 't', True) + 16)
            row['lead'] = lw
            x = lw
            for c in row['cells']:
                c['w'], c['dx'] = cw, x
                x += cw
            row['w'] = x + self.S['shadow']
        else:
            x = 0
            row['lead'] = 0
            # room for an arrow between cells of one row that point at each other
            inner = any(c.get('ptr') and c['ptr']['dst'] and c['ptr']['dst']['row'] is row
                        for c in row['cells'])
            gap = 2 * S['var_gap'] + 16 if inner else S['var_gap']
            for c in row['cells']:
                cw = up(max(S['cell_min_w'], c['vw'] + 24 + (DOTZONE if c.get('ptr') else 0)), 16)
                slot = max(cw, tx.run_w(c['name'], 't', True),
                           tx.run_w('at ' + c['addr'], 's', True) if c['addr'] else 0)
                slot = up(slot, 16)
                c['w'], c['dx'] = cw, x + (slot - cw) / 2
                x += slot + gap
            row['w'] = x - gap + S['shadow']
        top = 24 if (not arr or self.fig.index is not None) else 0
        bottom = (20 if any(c['addr'] for c in row['cells']) else 0) + \
            (28 if row['marks']['markers'] else 0)
        row['top'], row['h'] = top, top + S['cell_h'] + S['shadow'] + bottom

    def layout(self):
        S, sc, tx = self.S, self.sc, self.tx
        self.prepare()
        rows = [r for _, rs in self.fig.blocks for r in rs]
        for r in rows:
            self.measure_row(r)
        pad = S['frame_pad']
        framed = any(f for f, _ in self.fig.blocks)
        inner = max(r['w'] for r in rows)
        heads = {}      # frame labels wrap at 280, leaving room on the right for arrows
        for f, rs in self.fig.blocks:
            if f:
                heads[f['id']] = tx.wrap(f['label'], 280, 's')
                inner = max(inner, tx.block(heads[f['id']], 's')[0] + 8)
        limit = S['hard_width'] - 2 * S['margin'] - (2 * pad if framed else 0)
        for r in rows:
            if r['w'] > limit:
                raise Problem(r['line'], 'row is %d px wide, more than %d: split it into two '
                              'rows or shorten its values' % (r['w'], limit))
        fw = up(inner + 2 * pad, 16)
        y = 0
        for f, rs in self.fig.blocks:
            y0 = y
            y += up(tx.block(heads[f['id']], 's')[1] + 12) if f else 0
            for r in rs:
                self.place_row(r, y)
                y += r['h'] + S['row_gap']
            y -= S['row_gap']
            if f:
                y += pad
                sc.box('band', f['id'], -fw / 2, y0, fw, y - y0, 'band')
                sc.els.insert(0, sc.els.pop())
                hh = tx.block(heads[f['id']], 's')[1]
                t = sc.text(f['id'] + ':label', -fw / 2 + 12, y0 + 8 + hh / 2, heads[f['id']],
                            's', anchor='start')
                self.labels.append(t)
            y += (40 if any(p['label'] for p in self.fig.ptrs) else 24) + S['shadow']
        sc.count = len(self.cells)
        self.align(rows)
        self.route()
        return sc

    def align(self, rows):
        """Slide a row whose cells only point elsewhere so its dots sit near their targets."""
        lo = min(min(c['x'] for c in r['cells']) for r in rows)
        hi = max(max(c['x'] + c['w'] for c in r['cells']) for r in rows)
        targets = {id(p['dst']['row']) for p in self.fig.ptrs if p['dst']}
        for r in rows:
            ps = [c['ptr'] for c in r['cells'] if c.get('ptr') and c['ptr']['dst'] and
                  c['ptr']['dst']['row'] is not r]
            if id(r) in targets or not ps or r['type'] != 'vars':
                continue
            want = sum(p['dst']['x'] + p['dst']['w'] * 0.75 - (p['src']['x'] + p['src']['w'] -
                       DOTZONE / 2) for p in ps) / len(ps)
            x0 = min(c['x'] for c in r['cells'])
            x1 = max(c['x'] + c['w'] for c in r['cells'])
            dx = round(max(lo - x0, min(hi - x1, want)) / 8) * 8
            ids = {c['name'] for c in r['cells']}
            for e in self.sc.els:
                if e['t'] != 'mark' and e['id'].split(':')[0] in ids:
                    e['x'] += dx
                    if 'ax' in e:
                        e['ax'] += dx
            for e in r.get('deco', []):
                e['pts'] = [(x + dx, y) for x, y in e['pts']]
            for c in r['cells']:
                c['x'] += dx

    def place_row(self, row, y):
        S, sc, tx = self.S, self.sc, self.tx
        arr = row['type'] == 'row'
        x0 = up(-row['w'] / 2, 8)
        cy = y + row['top']
        h = S['cell_h']
        for c in row['cells']:
            c['x'], c['y'], c['h'] = x0 + c['dx'], cy, h
            sc.box('cell', c['name'], c['x'], cy, c['w'], h, c['cls'], 'rect', True)
            room = c['w'] - (DOTZONE if c.get('ptr') else 0)
            self.labels.append(sc.text(c['name'], c['x'] + room / 2, cy + h / 2,
                                       [[(c['value'], True)]], 't', inn=c['name'],
                                       cls='hink' if c['cls'] == 'hot' else 'ink'))
            mid = c['x'] + c['w'] / 2
            if not arr:
                self.labels.append(sc.text(c['name'] + ':name', mid, cy - 12,
                                           [[(c['name'], True)]], 't'))
            elif self.fig.index is not None:
                self.labels.append(sc.text(c['name'] + ':index', mid, cy - 12,
                                           [[(str(c['k'] + self.fig.index), True)]], 's',
                                           cls='soft'))
            below = cy + h + S['shadow'] + 10
            if c['addr']:       # under the value, so the column below a pointer's dot is free
                txt = c['addr'] if arr else 'at ' + c['addr']
                self.labels.append(sc.text(c['name'] + ':addr', mid if arr else c['x'] + room / 2,
                                           below, [[(txt, True)]], 's', cls='soft'))
                below += 20
            names = [nm for k, nm in row['marks']['markers'] if k == (c['k'] if arr else
                                                                        c['name'])]
            if names:
                sc.mark('tick', [(mid, below - 4), (mid - 6, below + 5), (mid + 6, below + 5)])
                self.labels.append(sc.text(c['name'] + ':mark', mid, below + 15,
                                           [[(', '.join(names), False)]], 's'))
            if c.get('ptr') and c['ptr']['dst'] is None:
                row.setdefault('deco', []).append(sc.mark('deco', [
                    (c['x'] + c['w'] - 25, cy + h - 12), (c['x'] + c['w'] - 9, cy + 12)]))
        if arr:
            self.labels.append(sc.text(row['name'] + ':row', x0 + row['lead'] - 12, cy + h / 2,
                                       [[(row['name'], True)]], 't', anchor='end'))

    # -- pointer arrows
    def route(self):
        S, sc = self.S, self.sc
        sh = S['shadow']
        rects = {c['name']: (c['x'], c['y'], c['x'] + c['w'] + sh, c['y'] + c['h'] + sh)
                 for c in self.cells.values()}
        labs = [(t['x'] - 2, t['y'] - 1, t['x'] + t['w'] + 2, t['y'] + t['h'] + 1)
                for t in self.labels]
        bx = sc.extent()
        ptrs = [p for p in self.fig.ptrs if p['dst']]
        route = {}

        def best(p, others):
            s = p['src']
            dot = (s['x'] + s['w'] - DOTZONE / 2, s['y'] + s['h'] / 2)
            done = [samples(route[id(q)], True) for q in others if id(q) in route]
            key = lambda pts: self.score(pts, s['name'], p['dst']['name'], rects, labs, done, bx)
            pick = min(self.candidates(dot, p['dst']), key=key)
            return pick, key(pick)
        # greedy in order, then one repair pass for any arrow left in a collision
        for k, p in enumerate(ptrs):
            route[id(p)] = best(p, ptrs[:k])[0]
        for p in ptrs:
            others = [q for q in ptrs if q is not p]
            done = [samples(route[id(q)], True) for q in others]
            if self.score(route[id(p)], p['src']['name'], p['dst']['name'], rects, labs, done,
                          bx) >= 1000:
                route[id(p)] = best(p, others)[0]
        for n, p in enumerate(self.fig.ptrs, 1):
            if p['dst']:
                sc.edge('p%d' % n, p['src']['name'], p['dst']['name'], route[id(p)], 'p', 'end',
                        True, True)
                if p['label']:
                    self.ptr_label(p, route[id(p)], rects, labs, 'p%d' % n)

    def candidates(self, dot, t):
        sh = self.S['shadow']
        x, y, w, h = t['x'], t['y'], t['w'], t['h']
        # the middle of a side first; a quarter point on top or bottom when a name or an
        # address sits in the middle
        ends = [((x + w * f, y), (0, -1)) for f in (0.5, 0.25, 0.75)] + \
            [((x + w * f, y + h + sh), (0, 1)) for f in (0.5, 0.25, 0.75)] + \
            [((x, y + h / 2), (-1, 0)), ((x + w + sh, y + h / 2), (1, 0))]
        out = []
        for d in ((1, 0), (0, -1), (0, 1), (0.6, 0.8), (0.6, -0.8), (-0.6, 0.8), (-0.6, -0.8)):
            for end, nrm in ends:
                L = math.hypot(end[0] - dot[0], end[1] - dot[1])
                for f1 in (0.3, 0.5, 0.8):
                    for f2 in (0.3, 0.5, 0.8):
                        k1, k2 = min(max(24, f1 * L), 200), min(max(24, f2 * L), 200)
                        c1 = (dot[0] + d[0] * k1, dot[1] + d[1] * k1)
                        c2 = (end[0] + nrm[0] * k2, end[1] + nrm[1] * k2)
                        out.append([dot, c1, c2, end])
                        if f1 == f2 == 0.5:     # bowed variants, for a gentle curve
                            for b in (-0.18, 0.18):
                                bx, by = -(end[1] - dot[1]) * b, (end[0] - dot[0]) * b
                                out.append([dot, (c1[0] + bx, c1[1] + by),
                                            (c2[0] + bx, c2[1] + by), end])
        return out

    @staticmethod
    def score(pts, src, dst, rects, labs, done, bx):
        pts_s = samples(pts, True)
        inside = lambda p, r, m=3: r[0] - m < p[0] < r[2] + m and r[1] - m < p[1] < r[3] + m
        cost = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts_s, pts_s[1:]))
        r = rects[dst]
        end = pts[-1]
        cost += 0 if abs(end[0] - (r[0] + r[2] - 4) / 2) < 1 or abs(end[1] - (r[1] + r[3] - 4)
                                                                     / 2) < 1 else 24
        cost += 40 if end[0] > r[2] - 2 or end[1] > r[3] - 2 else 0     # shadow side
        for name, r in rects.items():
            if name == src:
                hit = [inside(p, r, -1) for p in pts_s]
                left = hit.index(False) if False in hit else len(hit)
                cost += 1000 if any(hit[left:]) else 0
                step = max(1, sum(math.hypot(b[0] - a[0], b[1] - a[1])
                                  for a, b in zip(pts_s, pts_s[1:])) / 48)
                cost += 25 * max(0, left - 32 / step)   # leave the source cell promptly
                away = [not inside(p, r, 12) for p in pts_s]
                gone = away.index(True) if True in away else len(away)
                cost += 150 if any(inside(p, r, 6) for p in pts_s[gone:]) else 0
            elif name == dst:
                cost += 1000 if any(inside(p, r, -2) for p in pts_s[:-2]) else 0
            elif any(inside(p, r) for p in pts_s):
                cost += 1000
            elif any(inside(p, r, 8) for p in pts_s):
                cost += 150         # too close: keep clear of other cells
        for r in labs:
            cost += 1000 if any(inside(p, r, 2) for p in pts_s[1:]) else \
                150 if any(inside(p, r, 6) for p in pts_s[3:-3]) else 0
        for other in done:
            if any(min(abs(p[0] - q[0]) + abs(p[1] - q[1]) for q in other) < 8
                   for p in pts_s[4:-4:2]):
                cost += 150
            if abs(other[-1][0] - end[0]) + abs(other[-1][1] - end[1]) < 16:
                cost += 1000        # two arrowheads on one spot
        over = max(0, bx[0] - min(p[0] for p in pts_s), max(p[0] for p in pts_s) - bx[2]) + \
            max(0, bx[1] - min(p[1] for p in pts_s), max(p[1] for p in pts_s) - bx[3])
        chord = math.hypot(end[0] - pts[0][0], end[1] - pts[0][1]) or 1
        bow = max(abs((end[0] - pts[0][0]) * (p[1] - pts[0][1]) - (end[1] - pts[0][1]) *
                      (p[0] - pts[0][0])) / chord for p in pts_s)
        cost += 60 if bow < 8 else 0        # the book's pointer arrow is gently curved
        turn = 0
        for a, b, c in zip(pts_s, pts_s[1:], pts_s[2:]):
            a1 = math.atan2(b[1] - a[1], b[0] - a[0])
            a2 = math.atan2(c[1] - b[1], c[0] - b[0])
            turn += abs((a2 - a1 + math.pi) % (2 * math.pi) - math.pi)
        # prefer one smooth arc that leaves the dot forwards; an arch over a sag
        back = 12 if (pts[1][0] - pts[0][0]) < -1 else 0
        sag = 6 if abs(end[1] - pts[0][1]) < 24 and max(p[1] for p in pts_s) > pts[0][1] + 6 else 0
        return cost + 3 * over + max(0, math.degrees(turn) - 120) + 0.3 * math.degrees(turn) + \
            back + sag

    def ptr_label(self, p, pts, rects, labs, eid):
        lines = self.tx.wrap(p['label'], 120, 's')
        w, h = self.tx.block(lines, 's')
        bands = [(e['x'], e['y'], e['x'] + e['w'], e['y'] + e['h']) for e in self.sc.els
                 if e['t'] == 'box' and e['role'] == 'band']
        for t in sorted((k / 50 for k in range(10, 41)), key=lambda t: (abs(t - 0.5), t)):
            cx, cy = bezier(pts, t)
            r = (cx - w / 2 - 6, cy - h / 2 - 4, cx + w / 2 + 6, cy + h / 2 + 4)
            clear = lambda q: q[2] < r[0] or q[0] > r[2] or q[3] < r[1] or q[1] > r[3]
            within = lambda q: q[0] < r[0] and r[2] < q[2] and q[1] < r[1] and r[3] < q[3]
            if all(clear(q) for q in list(rects.values()) + labs) and \
                    all(clear(b) or within(b) for b in bands):
                break
        else:
            cx, cy = bezier(pts, 0.5)
        band = any(e['t'] == 'box' and e['role'] == 'band' and e['x'] < cx < e['x'] + e['w']
                   and e['y'] < cy < e['y'] + e['h'] for e in self.sc.els)
        t = self.sc.text(eid, cx, cy, lines, 's', plate='plateb' if band else 'plate')
        labs.append((t['x'] - 4, t['y'] - 2, t['x'] + t['w'] + 4, t['y'] + t['h'] + 2))


def describe_memory(fig):
    parts = ['Memory']
    for f, rows in fig.blocks:
        if f:
            names = [c['name'] if r['type'] == 'vars' else r['name'] for r in rows
                     for c in (r['cells'] if r['type'] == 'vars' else r['cells'][:1])]
            parts.append('%s. It holds %s' % (plain(f['label']), listing(names)))
        for r in rows:
            cells = r['cells']
            if r['type'] == 'row':
                at = ' at addresses %s to %s' % (cells[0]['addr'], cells[-1]['addr']) \
                    if cells[0]['addr'] else ''
                parts.append('%s holds %s%s' % (r['name'], listing([c['value'] for c in cells]),
                                                at))
                for c in cells:
                    if c.get('ptr'):
                        parts.append(ptr_words(c))
            else:
                for c in cells:
                    at = ' at address %s' % c['addr'] if c['addr'] else ''
                    tail = ' and ' + ptr_words(c, short=True) if c.get('ptr') else ''
                    parts.append('%s holds %s%s%s' % (c['name'], c['value'] or 'nothing', at, tail))
            for c in cells:
                if c['cls'] != 'box':
                    parts.append('%s is %s' % (c['name'], 'highlighted' if c['cls'] == 'hot'
                                               else 'greyed out'))
            for k, nm in r['marks']['markers']:
                c = cells[k] if r['type'] == 'row' else [c for c in cells if c['name'] == k][0]
                parts.append('%s marks %s' % (nm, c['name']))
    return sentences(parts)


def ptr_words(c, short=False):
    p = c['ptr']
    who = '' if short else c['name'] + ' '
    lab = ' (%s)' % plain(p['label']) if p['label'] else ''
    if p['dst'] is None:
        return '%sis null%s' % (who, lab)
    return '%spoints to %s%s' % (who, p['dst']['name'], lab)


# ---------------------------------------------------------------- layers

def item_box(tx, S, label, wrapw=136, line=None):
    lines = tx.wrap(label, wrapw)
    tw, th = tx.block(lines, 't')
    if tw > wrapw + 0.5:
        raise Problem(line, "label '%s' is %d px too wide for its box: shorten it or break it "
                      "with \\n" % (plain(label)[:24], tw - wrapw))
    return lines, up(max(80, tw + 2 * S['pad_x']), 16), up(max(S['box_min_h'], th + 2 *
                                                                 S['pad_y']), 16)


def longest_mid(pts):
    a, b = max(zip(pts, pts[1:]), key=lambda s: abs(s[1][0] - s[0][0]) + abs(s[1][1] - s[0][1]))
    return (a[0] + b[0]) / 2, (a[1] + b[1]) / 2


def layout_layers(fig, st, tx):
    S, sh = st['size'], st['size']['shadow']
    sc = Scene(st, tx)
    items = [i for l in fig.layers for i in l['items']]
    if not fig.layers:
        raise Problem(fig.first or 1, "no layers to draw: add 'layer id: label'")
    if len(items) > S['max_boxes']:
        raise Problem(fig.layers[-1]['line'], '%d boxes, more than %d: split the figure in two'
                      % (len(items), S['max_boxes']))
    loose = [i for i in fig.nodes if i not in items]
    if loose:
        e = [e for e in fig.edges if loose[0] in (e['a'], e['b'])][0]
        raise Problem(e['line'], "'%s' is not an item of any layer: add it with 'in layer: %s = "
                      "text'" % (loose[0], loose[0]))
    box = {i: item_box(tx, S, fig.nodes[i]['label'], line=fig.nodes[i]['line']) for i in items}
    heads = {l['id']: tx.wrap(l['label'], 128) for l in fig.layers}
    lw = up(max(tx.block(h, 't')[0] for h in heads.values()) + 32, 16)
    sides = {l['id']: tx.wrap(l['side'], 120, 's') for l in fig.layers if l['side']}
    sw = max([tx.block(v, 's')[0] for v in sides.values()] or [0])
    rows = {l['id']: sum(box[i][1] for i in l['items']) + S['node_gap'] * max(0, len(
        l['items']) - 1) for l in fig.layers}
    iw = up(max(rows.values()) + 2 * S['frame_pad'] + 8, 16)
    bw = lw + iw
    layer_of = {i: k for k, l in enumerate(fig.layers) for i in l['items']}
    for e in fig.edges:
        if abs(layer_of[e['a']] - layer_of[e['b']]) != 1:
            raise Problem(e['line'], 'arrows in layers join items in neighbouring layers only: '
                          'move %s or %s' % (e['a'], e['b']))
    # bands touch-free by 16 px; a gap that carries arrows opens to make room for them
    gaps = [16] * len(fig.layers)
    for e in fig.edges:
        k = min(layer_of[e['a']], layer_of[e['b']])
        gaps[k] = max(gaps[k], 64 if e['label'] else 48)
    pos, y = {}, 0
    for k, l in enumerate(fig.layers):
        ih = max([box[i][2] for i in l['items']] or [S['box_min_h']])
        bh = max(ih + 2 * S['frame_pad'], up(tx.block(heads[l['id']], 't')[1] + 24, 16))
        sc.box('band', l['id'], 0, y, bw, bh, 'band')
        sc.text(l['id'], 16, y + bh / 2, heads[l['id']], anchor='start', inn=l['id'])
        if l['id'] in sides:
            sc.text(l['id'] + ':side', bw + sh + 12, y + bh / 2, sides[l['id']], 's',
                    anchor='start', cls='soft')
        x = lw + (iw - rows[l['id']]) / 2
        x = up(x, 8)
        for i in l['items']:
            lines, w, _ = box[i]
            cls = 'hot' if i in fig.hot else 'mut' if i in fig.shade else 'box'
            sc.box('node', i, x, y + (bh - ih) / 2 - 2, w, ih, cls)
            sc.text(i, x + w / 2, y + bh / 2 - 2, lines, cls='hink' if cls == 'hot' else 'ink',
                    inn=i)
            pos[i] = (x, y + (bh - ih) / 2 - 2, w, ih, k)
            x += w + S['node_gap']
        y += bh + gaps[k]
    for n, e in enumerate(fig.edges, 1):
        ax, ay, aw, ah, ka = pos[e['a']]
        bx, by, bw2, bh2, kb = pos[e['b']]
        if kb > ka:
            p0, p1 = (ax + aw / 2, ay + ah + sh), (bx + bw2 / 2, by)
        else:
            p0, p1 = (ax + aw / 2, ay), (bx + bw2 / 2, by + bh2 + sh)
        band_edge = [el for el in sc.els if el['t'] == 'box' and el['id'] ==
                     fig.layers[min(ka, kb)]['id']][0]
        mid = band_edge['y'] + band_edge['h'] + sh + (gaps[min(ka, kb)] - sh) / 2
        pts = simplify([p0, (p0[0], mid), (p1[0], mid), p1])
        ek, hd = EDGE_KIND[e['op']]
        sc.edge('e%d' % n, e['a'], e['b'], pts, ek, hd)
        if e['label']:
            ll = tx.wrap(e['label'], 120, 's')
            sc.text('e%d' % n, *longest_mid(pts), ll, 's', plate='plate')
    sc.count = len(items)
    return sc


# ---------------------------------------------------------------- sequence

def layout_sequence(fig, st, tx):
    S, sh = st['size'], st['size']['shadow']
    sc = Scene(st, tx)
    sc.noun = 'boxes'
    actors = list(fig.nodes)
    notes = [e for e in fig.edges if e['op'] == 'note']
    if len(actors) + len(notes) > S['max_boxes']:
        raise Problem(fig.edges[-1]['line'], '%d actors and notes, more than %d: split the '
                      'figure in two' % (len(actors) + len(notes), S['max_boxes']))
    box = {i: item_box(tx, S, fig.nodes[i]['label'], 152, fig.nodes[i]['line']) for i in actors}
    ah = max(b[2] for b in box.values())
    idx = {i: k for k, i in enumerate(actors)}
    gaps = [(box[a][1] + box[b][1]) / 2 + S['node_gap'] for a, b in zip(actors, actors[1:])]
    labels = {}
    for k, e in enumerate(fig.edges):
        ia, ib = sorted((idx[e['a']], idx[e['b']]))
        if e['op'] == 'note':
            labels[k] = tx.wrap(e['label'], 200, 's')
            need = tx.block(labels[k], 's')[0] + 24
        else:
            labels[k] = tx.wrap(e['label'], 200, 's') if e['label'] else []
            need = tx.block(labels[k], 's')[0] + 48 if e['label'] else 48
        if e['op'] != 'note' and ia == ib:      # message to itself: room on the right
            need += 40      # the label of the last actor's loop just widens the figure
            if ia < len(actors) - 1:
                gaps[ia] = max(gaps[ia], need + box[actors[ia + 1]][1] / 2)
        elif e['op'] == 'note' and ia == ib:
            if ia > 0:
                gaps[ia - 1] = max(gaps[ia - 1], need / 2 + box[actors[ia - 1]][1] / 2 + 16)
            if ia < len(actors) - 1:
                gaps[ia] = max(gaps[ia], need / 2 + box[actors[ia + 1]][1] / 2 + 16)
        elif sum(gaps[ia:ib]) < need:
            extra = (need - sum(gaps[ia:ib])) / (ib - ia)
            for g in range(ia, ib):
                gaps[g] += extra
    cx = [0]
    for g in gaps:
        cx.append(cx[-1] + up(g, 16))
    for i in actors:
        lines, w, _ = box[i]
        x = cx[idx[i]] - w / 2
        cls = 'hot' if i in fig.hot else 'mut' if i in fig.shade else 'box'
        sc.box('node', i, x, 0, w, ah, cls)
        sc.text(i, cx[idx[i]], ah / 2, lines, cls='hink' if cls == 'hot' else 'ink', inn=i)
    y = ah + sh + 24
    for k, e in enumerate(fig.edges):
        a, b = cx[idx[e['a']]], cx[idx[e['b']]]
        lab = labels[k]
        lh = tx.block(lab, 's')[1] if lab else 0
        if e['op'] == 'note':
            nw = up(max(tx.block(lab, 's')[0] + 24, abs(b - a) + 48), 16)
            nh = up(lh + 16, 8)
            sc.box('node', 'note%d' % (k + 1), (a + b) / 2 - nw / 2, y, nw, nh, 'note', 'rect',
                   False)
            sc.text('note%d' % (k + 1), (a + b) / 2, y + nh / 2, lab, 's', inn='note%d' % (k + 1))
            y += nh + 20
            continue
        ek, hd = EDGE_KIND[e['op']]
        eid = 'e%d' % (k + 1)
        if a == b:
            sc.edge(eid, e['a'], e['b'], [(a, y), (a + 32, y), (a + 32, y + 20), (a, y + 20)],
                    ek, hd)
            if lab:
                sc.text(eid, a + 40, y + 10, lab, 's', anchor='start', plate='plate')
            y += 20 + max(24, lh - 4) + 12
            continue
        y_line = y + lh + 6
        sc.edge(eid, e['a'], e['b'], [(a, y_line), (b, y_line)], ek, hd)
        if lab:
            sc.text(eid, (a + b) / 2, y + lh / 2, lab, 's', plate='plate')
        y = y_line + 24
    for i in actors:
        sc.mark('life', [(cx[idx[i]], ah + sh + 2), (cx[idx[i]], y)], role='life')
    sc.count = len(actors) + len(notes)
    return sc

# @@CONTINUE@@

# ---------------------------------------------------------------- plain-language reading

def sentences(parts):
    out = []
    for p in parts:
        p = p.strip()
        if p:
            out.append(p if p[-1] in '.?!' else p + '.')
    return ' '.join(out)


def listing(items):
    items = [i for i in items if i]
    if len(items) < 3:
        return ' and '.join(items)
    return ', '.join(items[:-1]) + ' and ' + items[-1]


def marks_text(fig, ids):
    out = []
    hot = [plain(fig.nodes[i]['label']) for i in ids if i in fig.hot]
    shade = [plain(fig.nodes[i]['label']) for i in ids if i in fig.shade]
    if hot:
        out.append('%s %s highlighted' % (listing(hot), 'is' if len(hot) == 1 else 'are'))
    if shade:
        out.append('%s %s greyed out' % (listing(shade), 'is' if len(shade) == 1 else 'are'))
    return out


def edge_words(fig, e, back=False):
    a, b = plain(fig.nodes[e['a']]['label']), plain(fig.nodes[e['b']]['label'])
    how = {'..>': ' by a dashed arrow', '=>': ' by the highlighted path'}.get(e['op'], '')
    lab = plain(e['label'])
    if e['op'] == '--':
        return '%s is joined to %s%s' % (a, b, ' (%s)' % lab if lab else '')
    if e['op'] == '<->':
        return '%s and %s lead to each other%s' % (a, b, ' (%s)' % lab if lab else '')
    if fig.nodes[e['a']]['shape'] == 'diamond' and lab:
        return '%s %s: %s%s' % (a, lab, 'back to ' if back else '', b)
    return '%s leads %sto %s%s%s' % (a, 'back ' if back else '', b, how,
                                     ' (%s)' % lab if lab else '')


def describe(fig, g=None):
    k = fig.kind
    way = 'left to right' if fig.dir == 'right' else 'top to bottom'
    if k in ('flow', 'tree'):
        order = [i for row in g.byr for i in row] if g else list(fig.nodes)
        parts = ['%s, %s' % ('Flow chart' if k == 'flow' else 'Tree', way)]
        for i in order:
            for kk, e in enumerate(fig.edges):
                if e['a'] == i:
                    parts.append(edge_words(fig, e, g is not None and kk in g.back))
        loose = [i for i in order if not any(i in (e['a'], e['b']) for e in fig.edges)]
        parts += ['%s stands alone' % plain(fig.nodes[i]['label']) for i in loose]
        return sentences(parts + marks_text(fig, order))
    if k == 'layers':
        parts = ['Layers, top to bottom']
        for l in fig.layers:
            side = ' (%s)' % plain(l['side']) if l['side'] else ''
            items = [plain(fig.nodes[i]['label']) for i in l['items']]
            parts.append('%s%s%s' % (plain(l['label']), side,
                                     ' holds ' + listing(items) if items else ''))
        parts += [edge_words(fig, e) for e in fig.edges]
        return sentences(parts + marks_text(fig, list(fig.nodes)))
    if k == 'sequence':
        actors = [i for i in fig.nodes]
        parts = ['Sequence between %s, in time order' % listing(
            [plain(fig.nodes[i]['label']) for i in actors])]
        for e in fig.edges:
            a, b, lab = plain(fig.nodes[e['a']]['label']), plain(fig.nodes[e['b']]['label']), \
                plain(e['label'])
            if e['op'] == 'note':
                over = a if e['a'] == e['b'] else a + ' and ' + b
                parts.append('Note over %s: %s' % (over, lab))
            elif e['a'] == e['b']:
                parts.append('%s does %s itself' % (a, lab or 'something'))
            elif e['op'] == '..>':
                parts.append('%s replies to %s%s' % (a, b, ': ' + lab if lab else ''))
            else:
                parts.append('%s sends %s to %s' % (a, lab or 'a message', b))
        return sentences(parts + marks_text(fig, actors))
    return describe_memory(fig)

# ---------------------------------------------------------------- SVG writer

def fmt(v):
    s = '%.1f' % v
    s = s[:-2] if s.endswith('.0') else s
    return '0' if s == '-0' else s


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def css(st):
    """One style block: light colours, then dark under the media query and data-theme."""
    F, S = st['font'], st['size']
    sw = lambda w: 'stroke-width:%s' % fmt(w)
    font = lambda w, px, fam: 'font-family:%s;font-size:%dpx;font-weight:%d' % (fam, px, w)
    # (selector, colour declarations, other declarations); colours are {palette keys}
    rules = [
        ('.bg', 'fill:{ground}', ''), ('.sh', 'fill:{shadow}', ''),
        ('.box', 'fill:{box};stroke:{ink}', sw(S['border'])),
        ('.hot', 'fill:{hot};stroke:{ink}', sw(S['border_hot'])),
        ('.mut', 'fill:{muted};stroke:{ink}', sw(S['border']) + ';stroke-dasharray:' +
         S['mute_dash']),
        ('.band', 'fill:{band};stroke:{ink}', sw(S['border'])),
        ('.note', 'fill:{box};stroke:{ink}', sw(S['border_note'])),
        ('.deco', 'stroke:{ink}', 'fill:none;' + sw(S['line'])),
        ('.ek', 'stroke:{ink}', 'fill:none;' + sw(S['line'])),
        ('.er', 'stroke:{red}', 'fill:none;' + sw(S['line_red'])),
        ('.eb', 'stroke:{blue}', 'fill:none;stroke-dasharray:%s;%s' % (S['dash'], sw(S['line']))),
        ('.ep', 'stroke:{blue}', 'fill:none;stroke-dasharray:%s;%s' % (S['dash'], sw(S['line']))),
        ('.hk', 'fill:{ink}', ''), ('.hr', 'fill:{red}', ''), ('.hb', 'fill:{blue}', ''),
        ('.hp', 'stroke:{blue}', 'fill:none;stroke-linecap:round;stroke-linejoin:round;' +
         sw(S['line'] + 0.5)),
        ('.dot', 'fill:{blue}', ''), ('.tick', 'fill:{ink}', ''),
        ('.life', 'stroke:{soft}', 'fill:none;stroke-dasharray:%s;%s' % (S['life_dash'], sw(1.5))),
        ('.plate', 'fill:{ground}', ''), ('.plateb', 'fill:{band}', ''),
        ('.ink', 'fill:{ink}', ''), ('.soft', 'fill:{soft}', ''), ('.hink', 'fill:{hot_ink}', ''),
        ('.t', '', font(600, F['body'], F['sans'])),
        ('.s', '', font(600, F['small'], F['sans'])),
        ('.tt', '', font(700, F['title'], F['sans'])),
        ('.m', '', 'font-family:%s' % F['mono'])]
    light = ''.join('%s{%s}' % (sel, ';'.join(x for x in (c.format(**st['light']), o) if x))
                    for sel, c, o in rules)
    dark = lambda pre: ''.join('%s %s{%s}' % (pre, sel, c.format(**st['dark']))
                               for sel, c, _ in rules if c)
    return (light + '@media (prefers-color-scheme:dark){%s}' % dark('svg:not([data-theme="light"])')
            + dark('svg[data-theme="dark"]'))


LAYER = {'band': 0, 'life': 1, 'node': 2, 'cell': 2, 'deco': 3, 'edge': 4, 'label': 5,
         'title': 5}


def text_svg(e, tx):
    px = tx.px[e['size']]
    lh = px * tx.lh
    out = []
    if e['plate']:
        out.append('<rect class="%s" data-role="plate" data-for="%s" x="%s" y="%s" width="%s" '
                   'height="%s"/>' % (e['plate'], esc(e['id']), fmt(e['x'] - 4), fmt(e['y'] - 2),
                                      fmt(e['w'] + 8), fmt(e['h'] + 4)))
    attrs = 'class="%s %s" data-role="%s" data-id="%s"' % (e['size'], e['cls'], e['role'],
                                                          esc(e['id']))
    if e['inn']:
        attrs += ' data-in="%s"' % esc(e['inn'])
    if e['anchor'] != 'start':
        attrs += ' text-anchor="%s"' % e['anchor']
    spans = []
    for k, line in enumerate(e['lines']):
        y = e['y'] + lh * (k + 0.5) + 0.35 * px
        runs = ''.join('<tspan class="m">%s</tspan>' % esc(t) if m else esc(t) for t, m in line)
        spans.append('<tspan x="%s" y="%s">%s</tspan>' % (fmt(e['ax']), fmt(y), runs))
    out.append('<text %s>%s</text>' % (attrs, ''.join(spans)))
    return out


def head(tip, frm, kind, st):
    """Arrowhead at tip pointing away from frm. Returns (svg, new end of the shaft)."""
    dx, dy = tip[0] - frm[0], tip[1] - frm[1]
    d = math.hypot(dx, dy) or 1
    ux, uy = dx / d, dy / d
    L = st['size']['head'] + (2 if kind == 'r' else 0)
    if kind == 'p':     # open V for pointers
        a = math.radians(30)
        arms = [(tip[0] - L * (ux * math.cos(s * a) - uy * math.sin(s * a)),
                 tip[1] - L * (uy * math.cos(s * a) + ux * math.sin(s * a))) for s in (1, -1)]
        d = 'M{0} {1}L{2} {3}M{0} {1}L{4} {5}'.format(
            fmt(tip[0]), fmt(tip[1]), fmt(arms[0][0]), fmt(arms[0][1]), fmt(arms[1][0]),
            fmt(arms[1][1]))
        return '<path class="hp" data-role="head" d="%s"/>' % d, tip
    W = L * 0.5
    bx, by = tip[0] - ux * L, tip[1] - uy * L
    pts = [tip, (bx - uy * W, by + ux * W), (bx + uy * W, by - ux * W)]
    cls = {'k': 'hk', 'r': 'hr', 'b': 'hb'}[kind]
    return ('<path class="%s" data-role="head" d="M%sZ"/>' % (
        cls, 'L'.join('%s %s' % (fmt(x), fmt(y)) for x, y in pts)),
        (tip[0] - ux * (L - 1), tip[1] - uy * (L - 1)))


def edge_svg(e, st):
    pts = list(e['pts'])
    out = []
    ends = {'end': [-1], 'both': [-1, 0], 'none': []}[e['head']]
    for idx in ends:
        nb = (pts[-2] if idx == -1 else pts[1])
        h, shaft = head(pts[idx], nb, e['kind'], st)
        out.append(h.replace('data-role="head"', 'data-role="head" data-for="%s"' % esc(e['id'])))
        if not e['curve']:
            pts[idx] = shaft
    if e['curve']:
        d = 'M%s %sC%s' % (fmt(pts[0][0]), fmt(pts[0][1]),
                           ' '.join('%s %s' % (fmt(x), fmt(y)) for x, y in pts[1:]))
    else:
        d = 'M' + 'L'.join('%s %s' % (fmt(x), fmt(y)) for x, y in pts)
    cls = {'k': 'ek', 'r': 'er', 'b': 'eb', 'p': 'ep'}[e['kind']]
    path = '<path class="%s" data-role="edge" data-id="%s" data-from="%s" data-to="%s" d="%s"/>' % (
        cls, esc(e['id']), esc(e['a']), esc(e['b']), d)
    dot = []
    if e['dot']:
        dot = ['<circle class="dot" data-role="deco" cx="%s" cy="%s" r="%s"/>' % (
            fmt(e['pts'][0][0]), fmt(e['pts'][0][1]), fmt(st['size']['dot']))]
    return [path] + dot + out


def box_svg(e, sh):
    x, y, w, h = e['x'], e['y'], e['w'], e['h']
    out = []

    def shape(cls, dx, role, extra):
        if e['shape'] == 'diamond':
            pts = [(x + w / 2, y), (x + w, y + h / 2), (x + w / 2, y + h), (x, y + h / 2)]
            return '<polygon class="%s" %s points="%s"/>' % (cls, extra, ' '.join(
                '%s,%s' % (fmt(px + dx), fmt(py + dx)) for px, py in pts))
        rx = ' rx="%s"' % fmt(h / 2) if e['shape'] == 'pill' else ''
        return '<rect class="%s" %s x="%s" y="%s" width="%s" height="%s"%s/>' % (
            cls, extra, fmt(x + dx), fmt(y + dx), fmt(w), fmt(h), rx)
    if e['shadow']:
        out.append(shape('sh', sh, '', 'data-role="shadow" data-for="%s"' % esc(e['id'])))
    extra = 'data-role="%s" data-id="%s"' % (e['role'], esc(e['id']))
    if e['shape'] != 'rect':
        extra += ' data-shape="%s"' % e['shape']
    out.append(shape(e['cls'], 0, e['role'], extra))
    if e['shape'] == 'store':
        out.append('<path class="deco" data-role="deco" d="M%s %sH%s"/>' % (
            fmt(x), fmt(y + 8), fmt(x + w)))
    return out


def mark_svg(m):
    if m['cls'] in ('tick', 'dot'):
        return ['<path class="%s" data-role="deco" d="M%sZ"/>' % (m['cls'], 'L'.join(
            '%s %s' % (fmt(x), fmt(y)) for x, y in m['pts']))]
    return ['<path class="%s" data-role="%s" d="M%s"/>' % (m['cls'], m['role'], 'L'.join(
        '%s %s' % (fmt(x), fmt(y)) for x, y in m['pts']))]


def svg(sc, w, h, kind, title, desc, fid):
    st, tx = sc.st, sc.tx
    fid = re.sub(r'[^\w-]', '-', fid)
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
           'role="img" aria-labelledby="%s-t %s-d" data-kind="%s" data-count="%d">'
           % (w, h, w, h, fid, fid, kind, sc.count),
           '<title id="%s-t">%s</title>' % (fid, esc(title)),
           '<desc id="%s-d">%s</desc>' % (fid, esc(desc)),
           '<style>%s</style>' % css(st),
           '<rect class="bg" data-role="bg" x="0" y="0" width="%d" height="%d"/>' % (w, h)]
    order = sorted(range(len(sc.els)), key=lambda k: (LAYER.get(
        sc.els[k].get('role') if sc.els[k]['t'] != 'edge' else 'edge', 3), k))
    for k in order:
        e = sc.els[k]
        if e['t'] == 'box':
            out += box_svg(e, sc.sh)
        elif e['t'] == 'text':
            out += text_svg(e, tx)
        elif e['t'] == 'edge':
            out += edge_svg(e, st)
        else:
            out += mark_svg(e)
    out.append('</svg>')
    return '\n'.join(out) + '\n'


# ---------------------------------------------------------------- checks

NS = '{http://www.w3.org/2000/svg}'


def path_points(d):
    """Points of an M/L/H/V/C path, and whether it is a curve."""
    toks = re.findall(r'[MLHVCZ]|-?[\d.]+', d)
    pts, cmd, nums = [], None, []
    for t in toks + ['Z']:
        if t.isalpha():
            if cmd == 'H':
                pts += [(n, pts[-1][1]) for n in nums]
            elif cmd == 'V':
                pts += [(pts[-1][0], n) for n in nums]
            elif cmd:
                pts += list(zip(nums[0::2], nums[1::2]))
            cmd, nums = t, []
        else:
            nums.append(float(t))
    return pts, 'C' in d


def outline(b):
    """Corner points of a box: rect, or diamond when b has a 'diamond' shape."""
    x0, y0, x1, y1 = b['r']
    if b['shape'] == 'diamond':
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        return [(cx, y0), (x1, cy), (cx, y1), (x0, cy)]
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / ((dx * dx + dy * dy) or 1)))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def on_edge(p, b, sh):
    for off in (0, sh):
        pts = [(x + off, y + off) for x, y in outline(b)]
        if min(seg_dist(p, a, c) for a, c in zip(pts, pts[1:] + pts[:1])) <= 3:
            return True
    return False


def inside(p, r, m=0):
    return r[0] + m < p[0] < r[2] - m and r[1] + m < p[1] < r[3] - m


def overlap(a, b, tol=1):
    return min(a[2], b[2]) - max(a[0], b[0]) > tol and min(a[3], b[3]) - max(a[1], b[1]) > tol


def check_svg(text, st, tx):
    """Problems with a finished SVG, one sentence each, ending in the fix."""
    S = st['size']
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        return ['not well-formed XML (%s): re-render it from its description' % e]
    probs = []
    W, H = [float(v) for v in root.get('viewBox', '0 0 0 0').split()[2:]]
    if W > S['hard_width']:
        probs.append('figure is %d px wide, more than %d, too small on a phone: turn it '
                     '(dir: right) or split it' % (W, S['hard_width']))
    style = ''.join(e.text or '' for e in root.iter(NS + 'style'))
    px = {c: int(v) for c, v in re.findall(r'\.(\w+)\{[^}]*font-size:(\d+)px', style)}
    for c, v in px.items():
        if v < st['font']['min']:
            probs.append('text class .%s is %d px, under %d: raise it in the style file'
                         % (c, v, st['font']['min']))
    sh = S['shadow']
    boxes, shadows, labels, edges, heads, plates = {}, {}, [], [], {}, []
    for el in root.iter():
        role, tag = el.get('data-role'), el.tag.replace(NS, '')
        if role in ('node', 'cell', 'band'):
            if tag == 'rect':
                x, y = float(el.get('x')), float(el.get('y'))
                r = (x, y, x + float(el.get('width')), y + float(el.get('height')))
            else:
                pts = [tuple(map(float, q.split(','))) for q in el.get('points').split()]
                r = (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts),
                     max(p[1] for p in pts))
            boxes[el.get('data-id')] = {'role': role, 'r': r, 'shape': el.get('data-shape', 'rect')}
        elif role == 'shadow':
            shadows[el.get('data-for')] = True
        elif role in ('label', 'title'):
            labels.append(text_box(el, px, tx))
        elif role == 'edge':
            pts, curve = path_points(el.get('d'))
            edges.append({'id': el.get('data-id'), 'a': el.get('data-from'), 'cls': el.get('class'),
                          'b': el.get('data-to'), 'pts': pts, 'curve': curve})
        elif role == 'head':
            heads.setdefault(el.get('data-for'), []).append(path_points(el.get('d'))[0][0])
        elif role == 'plate':
            plates.append(el.get('data-for'))
    kind = root.get('data-kind')
    nodes = [b for b in boxes.values() if b['role'] == 'node']
    cells = [b for b in boxes.values() if b['role'] == 'cell']
    if len(nodes) > S['max_boxes']:
        probs.append('%d boxes, more than %d: split the figure' % (len(nodes), S['max_boxes']))
    if len(cells) > S['max_cells']:
        probs.append('%d cells, more than %d: split the figure' % (len(cells), S['max_cells']))
    full = lambda i: (boxes[i]['r'][0], boxes[i]['r'][1], boxes[i]['r'][2] + (sh if i in shadows
                      else 0), boxes[i]['r'][3] + (sh if i in shadows else 0))
    # text inside its box, with room to spare
    for lab in labels:
        b = boxes.get(lab['in'])
        if lab['in'] and b is None:
            probs.append("label '%s' sits in unknown box '%s'" % (lab['text'], lab['in']))
        elif b:
            x0, y0, x1, y1 = b['r']
            w, h = x1 - x0, y1 - y0
            if b['shape'] == 'diamond':
                bad = lab['w'] / w + lab['h'] / h > 1
            elif b['shape'] == 'pill':
                bad = lab['w'] > w - h + 4 or lab['h'] > h - 6
            else:
                bad = not (x0 + 4 <= lab['r'][0] and lab['r'][2] <= x1 - 4 and
                           y0 + 3 <= lab['r'][1] and lab['r'][3] <= y1 - 3)
            if bad:
                probs.append("label '%s' is too wide for its box '%s': shorten it"
                             % (lab['text'], lab['in']))
    ids = sorted(boxes)
    for k, i in enumerate(ids):
        for j in ids[k + 1:]:
            if boxes[i]['role'] == boxes[j]['role'] != 'band' and \
                    overlap(boxes[i]['r'], boxes[j]['r']):
                probs.append("boxes '%s' and '%s' overlap: re-render, or report a layout bug"
                             % (i, j))
    for k, a in enumerate(labels):
        for b in labels[k + 1:]:
            if overlap(a['r'], b['r']):
                probs.append("labels '%s' and '%s' overlap: shorten one" % (a['text'], b['text']))
        for i, b in boxes.items():
            if b['role'] != 'band' and i != a['in'] and overlap(a['r'], full(i)):
                probs.append("label '%s' overlaps box '%s': shorten the label" % (a['text'], i))
    for e in edges:
        probs += check_edge(e, boxes, labels, heads, full, sh, kind)
    for name, r in [(i, full(i)) for i in boxes] + [(l['text'], l['r']) for l in labels] + \
            [(e['id'], bbox_pts(samples(e['pts'], e['curve']))) for e in edges]:
        if r[0] < 8 or r[1] < 8 or r[2] > W - 8 or r[3] > H - 8:
            probs.append("'%s' is within 8 px of the figure edge: re-render it" % name)
    return probs


def bbox_pts(pts):
    return (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts),
            max(p[1] for p in pts))


def text_box(el, px, tx):
    """Measured box of a <text>: lines are tspans with x and y; class m runs are monospace."""
    cls = (el.get('class') or '').split()
    size = next((c for c in cls if c in tx.px), 't')
    lines, ys, words = [], [], []
    for ln in el:
        runs = [(ln.text or '', False)]
        for r in ln:
            runs += [(r.text or '', 'm' in (r.get('class') or '').split()), (r.tail or '', False)]
        lines.append([r for r in runs if r[0]])
        ys.append(float(ln.get('y')))
        words.append(''.join(r[0] for r in runs))
    if not lines:
        return {'r': (0, 0, 0, 0), 'w': 0, 'h': 0, 'text': '', 'in': el.get('data-in'),
                'id': el.get('data-id')}
    tx.px[size] = px.get(size, tx.px[size])
    w, h = tx.block(lines, size)
    x = float(el[0].get('x'))
    x0 = {'middle': x - w / 2, 'end': x - w}.get(el.get('text-anchor'), x)
    top = ys[0] - 0.35 * tx.px[size] - tx.px[size] * tx.lh / 2
    return {'r': (x0, top, x0 + w, top + h), 'w': w, 'h': h, 'text': ' '.join(words)[:30],
            'in': el.get('data-in'), 'id': el.get('data-id')}


def check_edge(e, boxes, labels, heads, full, sh, kind):
    probs = []
    for end in ('a', 'b'):
        if e[end] not in boxes:
            return ["arrow %s names unknown box '%s': declare it" % (e['id'], e[end])]
    pts = samples(e['pts'], e['curve'])
    start = e['pts'][0]
    tips = heads.get(e['id'], [])
    tip = next((t for t in tips if math.hypot(t[0] - start[0], t[1] - start[1]) > 1), e['pts'][-1])
    ptr = e['cls'] == 'ep'
    if kind == 'sequence':
        for end, p in (('a', start), ('b', tip)):
            r = boxes[e[end]]['r']
            if abs(p[0] - (r[0] + r[2]) / 2) > 1 and e['a'] != e['b']:
                probs.append('arrow %s does not end on the line of %s' % (e['id'], e[end]))
        ends = []
    else:
        if not (ptr and inside(start, boxes[e['a']]['r'])) and not on_edge(start, boxes[e['a']], sh):
            probs.append("arrow %s does not start on the edge of '%s'" % (e['id'], e['a']))
        if not on_edge(tip, boxes[e['b']], sh):
            probs.append("arrow %s does not end on the edge of '%s'" % (e['id'], e['b']))
        ends = [e['a'], e['b']]
    body = [p for p in pts if math.hypot(p[0] - start[0], p[1] - start[1]) > 6 and
            math.hypot(p[0] - tip[0], p[1] - tip[1]) > 6]
    for i, b in boxes.items():
        if b['role'] == 'band':
            continue
        if i in ends:
            if not (ptr and i == e['a']) and any(inside(p, b['r'], 2) for p in body):
                probs.append("arrow %s runs through its own box '%s': re-render" % (e['id'], i))
        elif any(inside(p, full(i)) for p in body):
            probs.append("arrow %s crosses box '%s': reorder the boxes or add dir: right"
                         % (e['id'], i))
    for lab in labels:
        if lab['id'] != e['id'] and any(inside(p, lab['r'], 1) for p in body):
            probs.append("arrow %s runs through label '%s': shorten the label" % (e['id'],
                                                                                  lab['text']))
    return probs


# ---------------------------------------------------------------- render, chapter, export

LAYOUTS = {'flow': layout_graph, 'tree': layout_graph, 'memory': lambda f, s, t: Memory(
    f, s, t).layout(), 'layers': lambda f, s, t: layout_layers(f, s, t),
    'sequence': lambda f, s, t: layout_sequence(f, s, t)}


def render(text, st, tx, first_line=1, fid='figure'):
    """Description -> (svg text, info) or (None, [Problem])."""
    fig, probs = parse(text, first_line)
    if probs:
        return None, probs
    try:
        sc = LAYOUTS[fig.kind](fig, st, tx)
        w, h = sc.finish(fig.title)
        if w > st['size']['hard_width']:
            raise Problem(fig.kind_line or fig.first, 'figure is %d px wide, more than %d: shorten '
                          'labels or split it' % (w, st['size']['hard_width']))
    except Problem as p:
        return None, [p]
    desc = describe(fig, getattr(sc, 'graph', None))
    title = plain(fig.title) if fig.title else desc.split('. ')[0]
    out = svg(sc, w, h, fig.kind, title, desc, fid)
    info = {'w': w, 'h': h, 'count': sc.count, 'noun': sc.noun, 'desc': desc, 'turned': getattr(fig, 'turned', False)}
    return out, [Problem(None, m) for m in check_svg(out, st, tx)] + [info]


def write_if_changed(path, data):
    old = None
    if os.path.exists(path):
        with open(path, 'rb') as f:
            old = f.read()
    new = data.encode('utf-8')
    if old != new:
        with open(path, 'wb') as f:
            f.write(new)


def show(path):
    rel = os.path.relpath(path)
    return path if rel.startswith('..') else rel


class Run:
    """One command-line run: prints results, remembers whether anything failed."""

    def __init__(self, st, png):
        self.st, self.tx, self.png, self.failed = st, Text(st), png, False
        self.exporter = None

    def problem(self, where, p):
        self.failed = True
        line = getattr(p, 'line', None)
        print('%s:%s %s' % (where, ' line %d:' % line if line else '', getattr(p, 'msg', p)))

    def figure(self, text, svg_path, where, first_line=1):
        fid = os.path.splitext(os.path.basename(svg_path))[0]
        out, res = render(text, self.st, self.tx, first_line, fid)
        if out is None:
            for p in res:
                self.problem(where, p)
            return None
        info, probs = res[-1], res[:-1]
        for p in probs:
            self.problem(where, p)
        write_if_changed(svg_path, out)     # written anyway, so the problem can be seen
        if probs:
            return None
        extra = ''
        if self.png:
            extra = '  png via %s' % self.export(svg_path, out)
        print('ok  %s  %dx%d  %d %s%s' % (show(svg_path), info['w'], info['h'], info['count'],
                                         info['noun'][:-1] if info['count'] == 1 else
                                         info['noun'], extra))
        print('reads: ' + info['desc'] + (' (Too wide left to right, so drawn top to bottom: the text must '
                                           'not say "left to right".)' if info.get('turned') else ''))
        return info

    def fig_file(self, path):
        with open(path, encoding='utf-8') as f:
            self.figure(f.read(), os.path.splitext(path)[0] + '.svg', show(path))

    def chapter(self, path):
        with open(path, 'rb') as f:
            raw = f.read().decode('utf-8')
        lines = raw.splitlines(keepends=True)
        nl = '\r\n' if '\r\n' in raw else '\n'
        stem = os.path.splitext(os.path.basename(path))[0]   # fig/<chapter>/<id>.svg: ids are per chapter
        figdir = os.path.join(os.path.dirname(path), 'fig', stem)
        seen, out, k = {}, [], 0
        while k < len(lines):
            line = lines[k]
            out.append(line)
            m = re.match(r'\s*<!--\s*fig:(.*)$', line.rstrip('\r\n'))
            if not m:
                k += 1
                continue
            start = k
            body = [m.group(1)]
            while '-->' not in body[-1] and k + 1 < len(lines):
                k += 1
                out.append(lines[k])
                body.append(lines[k].rstrip('\r\n'))
            if '-->' not in body[-1]:
                self.problem(show(path), Problem(start + 1, "fig comment never closes: end it "
                                                 "with -->"))
                break
            body[-1] = body[-1].split('-->')[0]
            idm = re.match(r'\s*id=([\w.\-]+)\s*(.*)$', body[0])
            k += 1
            if not idm:
                self.problem(show(path), Problem(start + 1, "fig comment has no id: write "
                                                 "<!-- fig: id=short-name"))
                continue
            fid = idm.group(1)
            body[0] = idm.group(2)
            if fid in seen:
                self.problem(show(path), Problem(start + 1, "fig id '%s' is already used on line "
                                                 "%d: rename one" % (fid, seen[fid])))
                continue
            seen[fid] = start + 1
            os.makedirs(figdir, exist_ok=True)
            info = self.figure('\n'.join(body), os.path.join(figdir, fid + '.svg'), show(path),
                               start + 1)
            img = re.compile(r'^!\[.*\]\(fig/(?:%s/)?%s\.svg\)\s*$' % (re.escape(stem), re.escape(fid)))
            has = k < len(lines) and img.match(lines[k].rstrip('\r\n'))
            if info is None:
                continue
            alt = info['desc'].replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]')
            new = '![%s](fig/%s/%s.svg)' % (alt, stem, fid)
            if not out[-1].endswith(('\n', '\r')):
                out[-1] += nl
            if has:
                end = lines[k][len(lines[k].rstrip('\r\n')):]
                lines[k] = new + end
            else:
                out.append(new + nl)
        new_raw = ''.join(out)
        if new_raw != raw:
            with open(path, 'wb') as f:
                f.write(new_raw.encode('utf-8'))

    def all(self, top):
        for d, dirs, files in sorted(os.walk(top)):
            dirs[:] = sorted(x for x in dirs if not x.startswith('.'))
            for f in sorted(files):
                p = os.path.join(d, f)
                if f.endswith('.fig'):
                    self.fig_file(p)
                elif f.endswith('.md'):
                    with open(p, encoding='utf-8', errors='replace') as fh:
                        if '<!-- fig:' in fh.read():
                            self.chapter(p)

    def check(self, path):
        with open(path, encoding='utf-8') as f:
            probs = check_svg(f.read(), self.st, self.tx)
        for p in probs:
            self.problem(show(path), p)
        if not probs:
            print('ok  %s  checks pass' % show(path))

    def export(self, svg_path, text):
        base = os.path.splitext(svg_path)[0]
        W, H = re.search(r'viewBox="0 0 (\d+) (\d+)"', text).groups()
        with tempfile.TemporaryDirectory() as tmp:
            for theme, suffix in (('light', ''), ('dark', '-dark')):
                src = os.path.join(tmp, theme + '.svg')
                with open(src, 'w', encoding='utf-8') as f:
                    f.write(text.replace('<svg ', '<svg data-theme="%s" ' % theme, 1))
                dst = os.path.abspath(base + suffix + '.png')
                tools = [self.exporter] if self.exporter else list(EXPORTERS)
                for name in tools:
                    if EXPORTERS[name](src, dst, int(W), int(H), tmp):
                        self.exporter = name
                        break
                else:
                    return 'nothing: install rsvg-convert (librsvg) or Chrome to export PNGs'
        return self.exporter


def _cmd(args):
    if not shutil.which(args[0]):
        return False
    try:
        r = subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return False
    return r.returncode == 0


def _cairo(src, dst):
    try:
        import cairosvg
        cairosvg.svg2png(url=src, write_to=dst, scale=2)
        return True
    except Exception:
        return False


def _chrome(src, dst, w, h, tmp):
    html = os.path.join(tmp, 'page.html')
    with open(src, encoding='utf-8') as f, open(html, 'w', encoding='utf-8') as g:
        g.write('<!DOCTYPE html><html><body style="margin:0">%s</body></html>' % f.read())
    for exe in ('google-chrome', 'chromium', 'chromium-browser'):
        if _cmd([exe, '--headless=new', '--no-sandbox', '--hide-scrollbars', '--disable-gpu',
                 '--force-device-scale-factor=2', '--window-size=%d,%d' % (w, h),
                 '--screenshot=%s' % dst, 'file://' + html]) and os.path.exists(dst):
            return True
    return False


EXPORTERS = {
    'rsvg-convert': lambda s, d, w, h, t: _cmd(['rsvg-convert', '-z', '2', '-o', d, s]),
    'inkscape': lambda s, d, w, h, t: _cmd(['inkscape', s, '--export-type=png',
                                            '--export-filename=' + d, '--export-dpi=192']),
    'magick': lambda s, d, w, h, t: _cmd(['magick', '-density', '192', s, d]),
    'cairosvg': lambda s, d, w, h, t: _cairo(s, d),
    'chrome': _chrome}


def main(argv):
    args = list(argv)
    if '--format' in args:
        print(FORMAT)
        return 0
    style = os.path.join(HERE, 'fig-style.json')
    if '--style' in args:
        k = args.index('--style')
        if k + 1 >= len(args):
            print('--style needs a path: --style my-style.json')
            return 1
        style = args.pop(k + 1)
        args.pop(k)
    png = '--png' in args
    args = [a for a in args if a != '--png']
    run = Run(load_style(style), png)
    if not args:
        print(__doc__.strip())
        return 1
    mode = None
    for a in args:
        if a in ('--chapter', '--all', '--check'):
            mode = a
        elif a.startswith('--'):
            print("unknown option %s: use --chapter, --all, --check, --png, --style or --format" % a)
            return 1
        elif not os.path.exists(a):
            run.problem(a, 'no such file')
        elif mode == '--chapter':
            run.chapter(a)
        elif mode == '--all':
            run.all(a)
        elif mode == '--check':
            run.check(a)
        else:
            run.fig_file(a)
    return 1 if run.failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
