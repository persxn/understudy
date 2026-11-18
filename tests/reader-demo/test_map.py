#!/usr/bin/env python3
"""Checks for reader/demo/map-demo.html (the skill map demo).

Run:  python3 tests/reader-demo/test_map.py          (checks only)
      python3 tests/reader-demo/test_map.py --shots  (checks, then screenshots)

Prints one line per check and "N passed, M failed"; exits 1 on any failure.
Uses the installed Chrome; no network.
"""
import os
import re
import sys
import traceback

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.normpath(os.path.join(HERE, '..', '..', 'reader', 'demo', 'map-demo.html'))
URL = 'file://' + HTML
SHOTS = os.path.join(HERE, 'shots')

RESULTS = []
CONSOLE = []  # every console error or warning and page error, from every page


def check(name):
    def deco(fn):
        def run(*a, **k):
            try:
                detail = fn(*a, **k)
                RESULTS.append((name, True))
                print(f'PASS  {name}' + (f'  ({detail})' if detail else ''))
            except Exception as e:  # noqa: BLE001 - report every failure and carry on
                RESULTS.append((name, False))
                msg = str(e) or e.__class__.__name__
                print(f'FAIL  {name}: {msg}')
                if os.environ.get('VERBOSE'):
                    traceback.print_exc()
        return run
    return deco


def new_page(browser, w=1440, h=900, scheme='light', reduced=None, hash_='', dsf=1, touch=False, settle=0):
    ctx = browser.new_context(viewport={'width': w, 'height': h}, color_scheme=scheme, device_scale_factor=dsf,
                              has_touch=touch, is_mobile=touch, reduced_motion=reduced or 'no-preference')
    page = ctx.new_page()
    page.on('console', lambda m: CONSOLE.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
    page.on('pageerror', lambda e: CONSOLE.append(f'pageerror: {e}'))
    page.goto(URL + hash_)
    page.wait_for_function('window.__map && window.__map.S.book')
    page.wait_for_timeout(150 + settle)
    return page


def settle(page, timeout=3000):
    """Wait until no animation or transition is running."""
    page.wait_for_function("document.getAnimations().every(a => a.playState !== 'running')", timeout=timeout)


def focused_id(page):
    return page.evaluate('document.activeElement && document.activeElement.id')


def expanded(page, id_):
    return page.get_attribute(f'#ti-{id_}', 'aria-expanded')


def rows(page):
    return page.evaluate("[...document.querySelectorAll('#tree [role=treeitem]')].map(li => li.dataset.id)")


def book_data(page):
    return page.evaluate("""() => { const b = __map.S.book; return {
        root: b.root.id,
        nodes: b.order.map(n => ({ id: n.id, kind: n.kind, parent: n.parent ? n.parent.id : null, depth: n.depth,
            children: n.children.map(c => c.id), needs: n.needs, status: n.status, title: n.title, route: n.routeStep })),
        subjects: b.subjects.map(s => s.id), route: b.route }; }""")


def anc_desc(data, cid):
    by = {n['id']: n for n in data['nodes']}
    unlocks = {}
    for n in data['nodes']:
        for m in n['needs']:
            unlocks.setdefault(m, []).append(n['id'])
    anc, stack = set(), [cid]
    while stack:
        for m in by[stack.pop()]['needs']:
            if m not in anc:
                anc.add(m)
                stack.append(m)
    desc, stack = set(), [cid]
    while stack:
        for m in unlocks.get(stack.pop(), []):
            if m not in desc:
                desc.add(m)
                stack.append(m)
    return anc, desc


def type_and_settle(page, key, wait=60):
    page.keyboard.press(key)
    page.wait_for_timeout(wait)


# ---------------------------------------------------------------- checks
@check('1. lazy tree: only open folders have rows; expanding adds exactly the direct children')
def t_lazy(browser):
    page = new_page(browser)
    bad = page.evaluate("""() => {
        const errs = [];
        for (const li of document.querySelectorAll('#tree [role=treeitem]')) {
            const n = __map.S.book.byId.get(li.dataset.id);
            const g = li.querySelector(':scope > [role=group]');
            const open = li.getAttribute('aria-expanded') === 'true';
            if (n.kind === 'folder' && open && (!g || g.children.length !== n.children.length)) errs.push('open without all children: ' + n.id);
            if (n.kind === 'folder' && !open && g) errs.push('closed but has rows: ' + n.id);
        }
        return errs; }""")
    assert not bad, bad
    data = book_data(page)
    before = set(rows(page))
    assert 'bsearch-find' not in before, 'a chapter of a closed folder is in the DOM'
    page.click('#ti-bsearch > .row')
    after = set(rows(page))
    added = after - before
    kids = set(next(n for n in data['nodes'] if n['id'] == 'bsearch')['children'])
    assert added == kids, f'added {len(added)} rows, expected {len(kids)}'
    page.click('#ti-bsearch > .row')
    assert set(rows(page)) == before, 'closing did not remove the rows'
    page.context.close()
    return f'{len(before)} rows at load, +{len(kids)} on expand'


@check('2. tree keys: arrows, Home/End, Enter/Space, *, type-ahead')
def t_keys(browser):
    page = new_page(browser)
    page.evaluate("document.getElementById('ti-archive').focus()")
    steps = [
        ('ArrowDown', 'ti-core-cs', None),
        ('ArrowDown', 'ti-algorithms-and-data-structures', None),
        ('ArrowDown', 'ti-bsearch', ('bsearch', 'false')),
        ('ArrowRight', 'ti-bsearch', ('bsearch', 'true')),
        ('ArrowRight', 'ti-bsearch-find', None),
        ('ArrowLeft', 'ti-bsearch', ('bsearch', 'true')),
        ('ArrowLeft', 'ti-bsearch', ('bsearch', 'false')),
        ('ArrowLeft', 'ti-algorithms-and-data-structures', None),
        ('ArrowUp', 'ti-core-cs', None),
        ('End', 'ti-py', None),
        ('Home', 'ti-archive', None),
    ]
    for key, want, exp in steps:
        type_and_settle(page, key)
        got = focused_id(page)
        assert got == want, f'after {key}: focus on {got}, expected {want}'
        if exp:
            assert expanded(page, exp[0]) == exp[1], f'after {key}: {exp[0]} aria-expanded={expanded(page, exp[0])}'
    # type-ahead: one letter, then a pause, then two letters quickly
    type_and_settle(page, 'o')
    assert focused_id(page) == 'ti-os', f'type-ahead "o" went to {focused_id(page)}'
    page.wait_for_timeout(600)
    page.keyboard.press('Home')
    page.keyboard.type('ne', delay=40)
    assert focused_id(page) == 'ti-networks', f'type-ahead "ne" went to {focused_id(page)}'
    page.wait_for_timeout(600)
    # * opens every sibling folder
    page.evaluate("document.getElementById('ti-cli').focus()")
    assert expanded(page, 'cli') == 'false' and expanded(page, 'git') == 'false'
    type_and_settle(page, '*')
    assert expanded(page, 'cli') == 'true' and expanded(page, 'git') == 'true', '* did not open the siblings'
    assert focused_id(page) == 'ti-cli'
    # Enter on a folder toggles and selects it
    page.evaluate("document.getElementById('ti-git').focus()")
    type_and_settle(page, 'Enter')
    assert expanded(page, 'git') == 'false' and page.get_attribute('#ti-git', 'aria-selected') == 'true'
    # Space on a chapter selects it
    page.evaluate("document.getElementById('ti-cli-pipes').focus()")
    type_and_settle(page, ' ')
    assert page.get_attribute('#ti-cli-pipes', 'aria-selected') == 'true'
    assert page.evaluate("document.querySelectorAll('#tree [aria-selected=true]').length") == 1
    assert focused_id(page) == 'ti-cli-pipes', 'focus left the tree'
    page.context.close()


@check('3. aria-level, aria-setsize, aria-posinset; exactly one tabindex=0')
def t_aria(browser):
    page = new_page(browser)
    page.click('#ti-bsearch > .row')
    want = {'archive': (1, 1, 1), 'core-cs': (2, 2, 1), 'programming': (2, 2, 2),
            'algorithms-and-data-structures': (3, 4, 1), 'networks': (3, 4, 4),
            'bsearch-find': (5, 23, 1), 'bsearch-systems': (5, 23, 23), 'cli': (4, 2, 1)}
    for id_, (lv, size, pos) in want.items():
        got = page.evaluate(f"(() => {{ const e = document.getElementById('ti-{id_}'); return [e.getAttribute('aria-level'), e.getAttribute('aria-setsize'), e.getAttribute('aria-posinset')].map(Number); }})()")
        assert got == [lv, size, pos], f'{id_}: {got}, expected {[lv, size, pos]}'
    n0 = page.evaluate("document.querySelectorAll('#tree [role=treeitem][tabindex=\"0\"]').length")
    assert n0 == 1, f'{n0} rows with tabindex=0'
    page.keyboard.press('Tab')  # from the clicked row, Tab leaves the tree
    n0 = page.evaluate("document.querySelectorAll('#tree [role=treeitem][tabindex=\"0\"]').length")
    assert n0 == 1, f'{n0} rows with tabindex=0 after Tab'
    roles = page.evaluate("[document.getElementById('tree').getAttribute('role'), document.querySelector('#ti-bsearch > ul').getAttribute('role')]")
    assert roles == ['tree', 'group'], roles
    page.context.close()


@check('4. filter: matches marked, ancestors opened, count announced, state restored on Esc')
def t_filter(browser):
    page = new_page(browser)
    page.click('#ti-cli > .row')
    open_before = page.evaluate("[...document.querySelectorAll('#tree [aria-expanded=true]')].map(e => e.dataset.id).sort()")
    data = book_data(page)
    want = sorted(n['id'] for n in data['nodes'] if n['kind'] == 'chapter' and 'search' in n['title'].lower())
    page.press('body', '/')
    assert focused_id(page) == 'q', '/ did not focus the search field'
    page.keyboard.type('search')
    page.wait_for_timeout(600)
    shown = page.evaluate("[...document.querySelectorAll('#tree li.chapter')].map(e => e.dataset.id).sort()")
    assert shown == want, f'shown {len(shown)} chapters, expected {len(want)}'
    marks = page.evaluate("[...document.querySelectorAll('#tree mark')].map(m => m.textContent.toLowerCase())")
    assert marks and all(m == 'search' for m in marks), marks[:5]
    assert all(page.evaluate(f"!!document.querySelector('#ti-{c} mark')") for c in want), 'a match is not marked'
    for c in want:
        anc = page.evaluate(f"(() => {{ const r = []; for (let p = __map.S.book.byId.get('{c}').parent; p; p = p.parent) r.push(p.id); return r; }})()")
        for a in anc:
            assert expanded(page, a) == 'true', f'ancestor {a} of {c} not open'
    livetext = page.text_content('#live')
    assert str(len(want)) in livetext and 'match' in livetext, f'live region said "{livetext}"'
    assert '| grep -i "search"' in page.text_content('#cmd')
    page.keyboard.press('Escape')
    page.wait_for_timeout(100)
    open_after = page.evaluate("[...document.querySelectorAll('#tree [aria-expanded=true]')].map(e => e.dataset.id).sort()")
    assert open_after == open_before, 'open/closed state not restored'
    assert page.evaluate("document.querySelectorAll('#tree mark').length") == 0
    # a chip on its own also filters
    page.click('[data-chip=route]')
    shown = page.evaluate("[...document.querySelectorAll('#tree li.chapter')].map(e => e.dataset.id)")
    assert sorted(shown) == sorted(data['route']), 'route chip shows the wrong chapters'
    page.click('[data-chip=all]')
    page.context.close()
    return f'{len(want)} matches for "search"'


@check('5. depth buttons, open to my route, Shift+Enter opens a subtree')
def t_depth(browser):
    page = new_page(browser)
    data = book_data(page)
    nodes = data['nodes']
    for L in (1, 2, 3):
        page.click(f'[data-depth="{L}"]')
        got = sorted(rows(page))
        want = sorted(n['id'] for n in nodes if n['depth'] <= L)
        assert got == want, f'-L {L}: {len(got)} rows, expected {len(want)}'
        assert page.text_content('#cmd') == f'tree book/ -L {L}', page.text_content('#cmd')
        assert page.get_attribute(f'[data-depth="{L}"]', 'aria-pressed') == 'true'
    page.click('[data-depth="all"]')
    assert len(rows(page)) == len(nodes) and page.text_content('#cmd') == 'tree book/'
    page.click('#open-route')
    opened = set(page.evaluate("[...document.querySelectorAll('#tree [aria-expanded=true]')].map(e => e.dataset.id)"))
    by = {n['id']: n for n in nodes}
    need = set()
    for r in data['route']:
        p = by[r]['parent']
        while p:
            need.add(p)
            p = by[p]['parent']
    assert opened == need, f'opened {sorted(opened ^ need)} differ'
    assert all(page.query_selector(f'#ti-{r}') for r in data['route'])
    page.click('#collapse-all')
    assert rows(page) == ['archive']
    page.evaluate("document.getElementById('ti-archive').focus()")
    page.keyboard.press('ArrowRight')
    page.keyboard.press('ArrowDown')
    assert focused_id(page) == 'ti-core-cs'
    page.keyboard.press('Shift+Enter')
    under = []
    for n in nodes:
        p = n['id']
        while p:
            if p == 'core-cs':
                under.append(n['id'])
                break
            p = by[p]['parent']
    got = set(rows(page))
    assert set(under) <= got, f'{len(set(under) - got)} rows under core-cs missing'
    assert 'languages' not in got, 'Shift+Enter opened more than the subtree'
    page.context.close()


@check('6. hash: #bsearch-find opens and selects; a new selection writes a plain name')
def t_hash(browser):
    page = new_page(browser, hash_='#bsearch-find')
    assert page.get_attribute('#ti-bsearch-find', 'aria-selected') == 'true'
    assert page.text_content('#detail-h') == 'Binary search: find a value in a sorted list'
    page.click('#ti-bsearch-bounds > .row')
    h = page.evaluate('location.hash')
    assert h == '#bsearch-bounds' and re.fullmatch(r'#[A-Za-z0-9-]+', h), h
    page.evaluate("location.hash = 'os-signals'")
    page.wait_for_timeout(100)
    assert page.get_attribute('#ti-os-signals', 'aria-selected') == 'true', 'hashchange did not select'
    assert page.evaluate("location.search") == ''
    page.reload()
    page.wait_for_function('window.__map && window.__map.S.book')
    assert page.get_attribute('#ti-os-signals', 'aria-selected') == 'true', 'selection did not survive a reload'
    page.context.close()


OVERLAP_JS = """(boxes) => { let bad = 0; for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
    const a = boxes[i], b = boxes[j];
    if (a.x < b.x + b.w - 0.5 && b.x < a.x + a.w - 0.5 && a.y < b.y + b.h - 0.5 && b.y < a.y + a.h - 0.5) bad++; } return bad; }"""

SCREEN_BOXES_JS = """() => [...document.querySelectorAll('#g-nodes .node > .box')].map(r => { const b = r.getBoundingClientRect(); return { x: b.x, y: b.y, w: b.width, h: b.height }; })"""

LAYOUT_CHECK_JS = """([ds, mode]) => {
    const m = __map, book = m.getBook(ds);
    const exp = new Set(mode === 'all' ? book.subjects.map(s => s.id) : mode === 'none' ? [] : mode.split(','));
    const t0 = performance.now();
    const model = m.buildGraphModel(book, exp);
    const L = m.layoutGraph(model, m.measure);
    const ms = performance.now() - t0;
    const boxes = [...L.units.values()].map(u => ({ x: u.x, y: u.y, w: u.w, h: u.h, id: u.id }));
    for (const b of L.bands) boxes.push({ x: b.x, y: b.y, w: m.GL.W + m.GL.BPAD, h: b.headH, id: 'band:' + b.id });
    let overlaps = 0;
    for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
        const a = boxes[i], b = boxes[j];
        if (a.id.startsWith('band:') && b.id.startsWith('band:')) continue;
        if (a.x < b.x + b.w - 0.5 && b.x < a.x + a.w - 0.5 && a.y < b.y + b.h - 0.5 && b.y < a.y + a.h - 0.5) overlaps++;
    }
    // no edge segment may pass through a box other than its own two ends
    let through = 0;
    for (const e of L.edges) {
        for (let k = 0; k < e.points.length - 1; k++) {
            const [x1, y1] = e.points[k], [x2, y2] = e.points[k + 1];
            for (const b of boxes) {
                if (b.id === e.from || b.id === e.to) continue;
                const lx = Math.min(x1, x2), hx = Math.max(x1, x2), ly = Math.min(y1, y2), hy = Math.max(y1, y2);
                if (hx > b.x + 1 && lx < b.x + b.w - 1 && hy > b.y + 1 && ly < b.y + b.h - 1) through++;
            }
        }
    }
    // band rectangles may not overlap each other or any box outside them
    let bandHits = 0;
    for (const b of L.bands) for (const u of L.units.values()) {
        if (u.group === b.id) continue;
        if (u.x < b.x + b.w && b.x < u.x + u.w && u.y < b.y + b.h && b.y < u.y + u.h) bandHits++;
    }
    return { overlaps, through, bandHits, ms, units: L.units.size, edges: L.edges.length };
}"""


@check('7. graph: clusters at root, chapters on activation, needs/unlocks marks, no overlaps or edges through boxes')
def t_graph(browser):
    page = new_page(browser, settle=500)
    data = book_data(page)
    keys = page.evaluate("[...document.querySelectorAll('#g-nodes .node')].map(e => e.dataset.key)")
    assert sorted(keys) == sorted(data['subjects']), f'root scope shows {keys}'
    assert page.evaluate("document.querySelectorAll('#g-nodes .node.chapter').length") == 0
    assert page.evaluate(OVERLAP_JS, page.evaluate(SCREEN_BOXES_JS)) == 0, 'boxes overlap in root scope'
    k = page.evaluate('__map.G.k')
    assert k >= 11 / 15 - 1e-6 and not page.evaluate("document.getElementById('graph').classList.contains('overview')"), f'fit all at root is {k:.2f}: labels would be under 11 px'
    page.locator('#g-nodes .node[data-key="bsearch"]').dispatch_event('click')
    ch = page.evaluate("[...document.querySelectorAll('#g-nodes .node.chapter')].map(e => e.dataset.key)")
    kids = [n['id'] for n in data['nodes'] if n['parent'] == 'bsearch']
    assert sorted(ch) == sorted(kids), 'activating the cluster did not show its chapters'
    assert page.query_selector('#g-nodes .node[data-key="band:bsearch"]'), 'no band header'
    page.locator('#g-nodes .node[data-key="bsearch-bounds"]').dispatch_event('click')
    assert page.get_attribute('#ti-bsearch-bounds', 'aria-selected') == 'true', 'graph selection did not reach the tree'
    settle(page)
    anc, desc = anc_desc(data, 'bsearch-bounds')
    cls = page.evaluate("Object.fromEntries([...document.querySelectorAll('#g-nodes .node')].map(e => [e.dataset.key, e.getAttribute('class')]))")
    by = {n['id']: n for n in data['nodes']}
    for key, c in cls.items():
        if key.startswith('band:'):
            continue
        if by[key]['kind'] == 'chapter':
            want = 'sel' if key == 'bsearch-bounds' else 'needs' if key in anc else 'unlocks' if key in desc else 'quiet'
        else:
            kidsk = by[key]['children']
            want = 'needs' if any(x in anc for x in kidsk) else 'unlocks' if any(x in desc for x in kidsk) else 'quiet'
        assert want in c.split(), f'{key}: class "{c}", expected {want}'
    assert page.evaluate(OVERLAP_JS, page.evaluate(SCREEN_BOXES_JS)) == 0, 'boxes overlap with a subject open'
    assert page.evaluate("document.querySelectorAll('#g-edges path.needs').length") > 0
    assert page.evaluate("document.querySelectorAll('#g-edges path.unlocks').length") > 0
    out = []
    for ds, mode in [('example', 'none'), ('example', 'bsearch'), ('example', 'bsearch,os,py'), ('example', 'all'),
                     ('large', 'none'), ('large', 'all')]:
        r = page.evaluate(LAYOUT_CHECK_JS, [ds, mode])
        assert r['overlaps'] == 0, f'{ds}/{mode}: {r["overlaps"]} overlapping boxes'
        assert r['through'] == 0, f'{ds}/{mode}: {r["through"]} edge segments through boxes'
        assert r['bandHits'] == 0, f'{ds}/{mode}: {r["bandHits"]} boxes inside a foreign band'
        out.append(f'{ds}/{mode} {r["units"]}u {r["edges"]}e')
    # collapse again
    page.locator('#g-nodes .node[data-key="band:bsearch"]').dispatch_event('click')
    assert page.query_selector('#g-nodes .node[data-key="bsearch"]'), 'band did not close back to a cluster'
    page.context.close()
    return '; '.join(out)


@check('8. graph keys: Right/Left follow edges, Enter selects, Esc returns to the tree row')
def t_graph_keys(browser):
    page = new_page(browser, hash_='#bsearch-loop-invariants')
    page.evaluate("document.querySelector('#g-nodes .node[data-key=\"bsearch-loop-invariants\"]').focus()")
    assert page.evaluate("document.activeElement.dataset.key") == 'bsearch-loop-invariants'
    n0 = page.evaluate("document.querySelectorAll('#g-nodes .node[tabindex=\"0\"]').length")
    assert n0 == 1, f'{n0} graph nodes with tabindex=0'
    succ = page.evaluate("__map.G.layout.succ.get('bsearch-loop-invariants')")
    page.keyboard.press('ArrowRight')
    k1 = page.evaluate("document.activeElement.dataset.key")
    assert k1 in succ, f'Right went to {k1}, not one of {succ}'
    pred = page.evaluate(f"__map.G.layout.pred.get('{k1}')")
    page.keyboard.press('ArrowLeft')
    k2 = page.evaluate("document.activeElement.dataset.key")
    assert k2 in pred, f'Left went to {k2}, not one of {pred}'
    page.keyboard.press('ArrowRight')
    page.keyboard.press('ArrowDown')
    k3 = page.evaluate("document.activeElement.dataset.key")
    col = page.evaluate(f"[__map.G.layout.units.get('{k1}').rank, __map.G.layout.units.get('{k3}').rank]")
    assert col[0] == col[1] and k3 != k1, f'Down left the column ({k1} -> {k3})'
    page.keyboard.press('Enter')
    assert page.evaluate('__map.S.sel') == k3, 'Enter did not select'
    assert page.evaluate("document.activeElement.dataset.key") == k3, 'Enter moved focus out of the graph'
    page.keyboard.press('Escape')
    assert focused_id(page) == f'ti-{k3}', f'Esc focused {focused_id(page)}'
    page.context.close()


@check('9. detail: learning path is a topological order of the unwritten prerequisites only')
def t_detail(browser):
    page = new_page(browser)
    data = book_data(page)
    by = {n['id']: n for n in data['nodes']}
    tried = 0
    for cid in ['bsearch-interview', 'bsearch-systems', 'git-bisect', 'os-history-and-lineage', 'net-debug']:
        page.evaluate(f"__map.select('{cid}', {{ from: 'test' }})")
        got = page.evaluate("[...document.querySelectorAll('#learning-path [data-goto]')].map(b => b.dataset.goto)")
        anc, _ = anc_desc(data, cid)
        want = {a for a in anc if by[a]['status'] != 'written'}
        assert set(got) == want and len(got) == len(want), f'{cid}: path has {len(got)} items, expected {len(want)}'
        for i, x in enumerate(got):
            ax, _ = anc_desc(data, x)
            later = set(got[i + 1:])
            assert not (ax & later), f'{cid}: {x} comes before something it needs'
        tried += 1
    # needs-first buttons select that chapter, and focus stays in the panel
    page.evaluate("__map.select('bsearch-bounds', { from: 'test' })")
    page.click('#detail-body [data-goto="bsearch-intervals"]')
    assert page.evaluate('__map.S.sel') == 'bsearch-intervals'
    assert page.evaluate("document.getElementById('detail').contains(document.activeElement)"), 'focus left the detail panel'
    page.click('#primary')
    page.wait_for_timeout(200)
    assert page.text_content('#confirm').strip(), 'no confirmation after the primary action'
    page.context.close()
    return f'{tried} chapters'


CONTRAST_JS = r"""() => {
    const parse = c => { const m = c && c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; };
    const hex = h => ({ r: parseInt(h.slice(1, 3), 16), g: parseInt(h.slice(3, 5), 16), b: parseInt(h.slice(5, 7), 16), a: 1 });
    const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
    const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
    // the fill an element shows: its own background, or the paper of a surface drawn by a pseudo-element
    const own = e => {
        if (e.matches('.btn, .panel')) { const c = parse(getComputedStyle(e, '::after').backgroundColor); if (c && c.a > 0) return c; }
        if (e.matches('mark.fresh')) { const c = parse(getComputedStyle(e, '::before').backgroundColor); if (c && c.a > 0) return c; }
        const c = parse(getComputedStyle(e).backgroundColor); return c && c.a > 0 ? c : null; };
    const bgOf = el => { for (let e = el; e && e.nodeType === 1; e = e.parentElement) { const c = own(e); if (c) return c; } return parse(getComputedStyle(document.documentElement).backgroundColor) || { r: 255, g: 255, b: 255, a: 1 }; };
    const visible = el => { if (!el.getClientRects().length) return false; const cs = getComputedStyle(el); if (cs.visibility === 'hidden') return false; if (el.closest('.sr-only, [aria-hidden=true].ghost, .ghost')) return false; const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
    const stageBg = bgOf(document.getElementById('stage'));
    const svgBg = el => { const node = el.closest('.node'); if (node) { const box = node.querySelector('.box'); const f = parse(getComputedStyle(box).fill); if (f && f.a > 0) return f; }
        return stageBg; };
    const BODY = '.desc, .tree .ti > .row .name, #detail-h, .links .bt > span:first-child, .levels li, .about, #graph text.t, #graph text.tc, .brand h1, .panel-head h2';
    const fails = [], seen = { text: 0, body: 0, border: 0, edge: 0 };
    let minText = 99, minBody = 99, minBorder = 99, minEdge = 99;
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const els = new Set();
    for (let t = walker.nextNode(); t; t = walker.nextNode()) if (t.textContent.trim() && t.parentElement) els.add(t.parentElement);
    for (const el of els) {
        if (el.closest('script, style, .skip') || !visible(el)) continue;
        const inSvg = el instanceof SVGElement;
        if (inSvg && el.closest('#graph.overview')) continue;
        const fg = parse(inSvg ? getComputedStyle(el).fill : getComputedStyle(el).color);
        let bg = inSvg ? svgBg(el) : bgOf(el);
        if (inSvg) { const b = el.closest('.node') && el.closest('.node').querySelector('.bdg'); if (el.classList.contains('bdgt') && b) bg = parse(getComputedStyle(b).fill); }
        const r = ratio(fg, bg); seen.text++; minText = Math.min(minText, r);
        const body = el.matches(BODY) || !!el.closest('.desc, .about');
        if (body) { seen.body++; minBody = Math.min(minBody, r); if (r < 7) fails.push(`body text ${r.toFixed(2)} "${el.textContent.trim().slice(0, 30)}"`); }
        else if (r < 4.5) fails.push(`text ${r.toFixed(2)} "${el.textContent.trim().slice(0, 30)}"`);
    }
    // borders of every control (every state, disabled included) and panel, against what is around them
    for (const el of document.querySelectorAll('.btn, input[type=search], .panel, .tree [aria-selected=true] > .row, .menu:not([hidden]), .minimap')) {
        if (!visible(el)) continue;
        const surf = el.matches('.btn, .panel');
        const cs = getComputedStyle(el, surf ? '::after' : null);
        if (parseFloat(cs.borderTopWidth) < 1) continue;
        const fg = parse(cs.borderTopColor); if (!fg || fg.a === 0) continue;
        const bg = bgOf(el.parentElement);
        // a filled selection's boundary is its fill edge (yellow on the surface) or its border, whichever is stronger
        const fill = el.matches('[aria-selected=true] > .row') ? parse(cs.backgroundColor) : null;
        const r = Math.max(ratio(fg, bg), fill ? ratio(fill, bg) : 0); seen.border++; minBorder = Math.min(minBorder, r);
        if (r < 3) fails.push(`border ${r.toFixed(2)} ${el.id || el.className}`);
    }
    // tree guide lines (pseudo-elements)
    const li = document.querySelector('#tree .grp > .ti');
    if (li) { const g = parse(getComputedStyle(li, '::before').borderLeftColor), r = ratio(g, bgOf(li)); seen.border++; minBorder = Math.min(minBorder, r); if (r < 3) fails.push('tree guide ' + r.toFixed(2)); }
    // graph box borders, corner tabs and edges against the canvas
    for (const box of document.querySelectorAll('#g-nodes .node .box, #g-bands .bandbox, #g-nodes .node .tab')) {
        const cs = getComputedStyle(box); if (cs.display === 'none') continue;
        const col = box.classList.contains('tab') ? cs.fill : cs.stroke;
        if (col === 'none' || (!box.classList.contains('tab') && parseFloat(cs.strokeWidth) === 0)) continue;
        const sel = box.closest('.node.sel') && box.classList.contains('box');
        const r = Math.max(ratio(parse(col), stageBg), sel ? ratio(parse(cs.fill), stageBg) : 0); seen.border++; minBorder = Math.min(minBorder, r);
        if (r < 3) fails.push(`graph ${box.getAttribute('class')} ${r.toFixed(2)} ${box.parentElement.getAttribute('class')}`);
    }
    for (const p of document.querySelectorAll('#g-edges path')) {
        const r = ratio(parse(getComputedStyle(p).stroke), stageBg); seen.edge++; minEdge = Math.min(minEdge, r);
        if (r < 3) fails.push(`edge ${r.toFixed(2)} ${p.getAttribute('class')}`);
    }
    // the focus ring against every surface it can sit on (it keeps a 2 px gap, so never on yellow)
    const ring = hex(getComputedStyle(document.documentElement).getPropertyValue('--blue').trim());
    const probe = document.querySelector('#tree [role=treeitem]');
    if (probe) { probe.focus({ preventScroll: true });
        const o = parseFloat(getComputedStyle(probe.firstElementChild).outlineOffset);
        if (probe.matches(':focus-visible') && o < 2) fails.push('tree focus ring offset ' + o);
        probe.blur(); }
    for (const v of ['--paper', '--ground', '--sunken', '--band']) {
        const r = ratio(ring, hex(getComputedStyle(document.documentElement).getPropertyValue(v).trim())); minBorder = Math.min(minBorder, r);
        if (r < 3) fails.push(`focus ring on ${v} ${r.toFixed(2)}`);
    }
    return { fails, seen, minText, minBody, minBorder, minEdge };
}"""


@check('10. contrast: body text 7:1, other text 4.5:1, borders, rings, edges and marks 3:1, every state, light and dark')
def t_contrast(browser):
    notes = []
    for scheme in ('light', 'dark'):
        for w, h in ((1440, 900), (390, 844)):
            page = new_page(browser, w=w, h=h, scheme=scheme, hash_='#bsearch-loop-invariants', settle=450)
            assert page.evaluate('document.documentElement.dataset.theme') == scheme
            states = [('default: selected, needs, unlocks, quiet', None)]
            if w > 700:
                states += [
                    ('hover', lambda p: p.hover('#fit-all')),
                    ('pressed', lambda p: (p.hover('#collapse-all'), p.mouse.down())),
                    ('released', lambda p: p.mouse.up()),
                    ('keys open', lambda p: p.click('#keys-btn')),
                    ('disabled', lambda p: [p.click('#z-in') for _ in range(8) if p.is_enabled('#z-in')]),
                    ('filter match', lambda p: (p.fill('#q', 'loop'), p.wait_for_timeout(100))),
                    ('menu', lambda p: p.click('#ds-btn')),
                ]
            else:
                states.append(('graph tab', lambda p: p.click('.tabs [data-tab=graph]')))
                states.append(('detail tab', lambda p: p.click('.tabs [data-tab=detail]')))
            for label, act in states:
                if act:
                    act(page)
                if label not in ('hover', 'pressed'):
                    page.mouse.move(0, 0)
                page.wait_for_timeout(300)  # let the 120 ms colour transitions finish
                r = page.evaluate(CONTRAST_JS)
                assert not r['fails'], f'{scheme} {w}px {label}: ' + '; '.join(r['fails'][:6])
                notes.append(f"{scheme}/{w}/{label} body>={r['minBody']:.1f} text>={r['minText']:.1f} ui>={r['minBorder']:.1f}")
            if w > 700:
                page.mouse.up()
            page.context.close()
    if os.environ.get('VERBOSE'):
        print('\n'.join(notes))
    mins = lambda i: min(float(n.split()[i].split('>=')[1]) for n in notes)
    return f'{len(notes)} states measured; minimum body {mins(-3):.1f}, text {mins(-2):.1f}, ui {mins(-1):.1f}'


@check('11. no horizontal page scroll at 390 and 320; targets >= 24 px (44 on the phone)')
def t_size(browser):
    out = []
    for w, h in ((390, 844), (320, 640)):
        page = new_page(browser, w=w, h=h, hash_='#bsearch-bounds')
        for tab in ('tree', 'graph', 'detail'):
            page.click(f'.tabs [data-tab={tab}]')
            sw = page.evaluate('[document.documentElement.scrollWidth, document.documentElement.clientWidth]')
            assert sw[0] <= sw[1], f'{w}px {tab}: page scrolls sideways ({sw[0]} > {sw[1]})'
            small = page.evaluate("""() => [...document.querySelectorAll('button, input[type=search], .tree .row')]
                .filter(e => e.getClientRects().length && !e.closest('[hidden]'))
                .map(e => { const r = e.getBoundingClientRect(); return [e.textContent.trim().slice(0, 20) || e.getAttribute('aria-label'), r.width, r.height]; })
                .filter(([, w, h]) => w < 43.5 || h < 43.5)""")
            assert not small, f'{w}px {tab}: under 44 px: {small[:4]}'
        out.append(f'{w}px ok')
        page.context.close()
    page = new_page(browser)
    small = page.evaluate("""() => [...document.querySelectorAll('button, input, .tree .row, #g-nodes .node')]
        .filter(e => e.getClientRects().length && !e.closest('[hidden]') && !e.closest('.sr-only'))
        .map(e => { const r = e.getBoundingClientRect(); return [e.textContent.trim().slice(0, 20), r.width, r.height]; })
        .filter(([, w, h]) => w < 24 || h < 24)""")
    assert not small, f'desktop under 24 px: {small[:4]}'
    page.context.close()
    return ', '.join(out)


@check('12. large book: switch without reload, expand-all and layout under 800 ms')
def t_large(browser):
    page = new_page(browser)
    page.evaluate('window.__marker = 1')
    page.click('#ds-btn')
    page.check('input[name=ds][value=large]')
    page.wait_for_timeout(100)
    assert page.evaluate('window.__marker') == 1, 'switching datasets reloaded the page'
    n = page.evaluate('__map.S.book.chapters.length')
    assert n == 300, f'{n} chapters'
    assert len(page.evaluate('__map.S.book.subjects')) >= 28
    page.keyboard.press('Escape')
    t_expand = page.evaluate("(() => { const t = performance.now(); document.querySelector('[data-depth=all]').click(); return performance.now() - t; })()")
    total = page.evaluate('__map.S.book.order.length')
    assert len(rows(page)) == total, 'expand all did not show every row'
    deep = page.evaluate("Math.max(...[...document.querySelectorAll('#tree [role=treeitem]')].map(e => +e.getAttribute('aria-level')))")
    assert deep >= 11, f'deepest row is level {deep}'
    t_layout = page.evaluate("""(() => { const S = __map.S; const t = performance.now();
        const model = __map.buildGraphModel(S.book, new Set(S.book.subjects.map(s => s.id))); __map.layoutGraph(model, __map.measure);
        return performance.now() - t; })()""")
    t_root = page.evaluate("""(() => { const S = __map.S; const t = performance.now();
        __map.layoutGraph(__map.buildGraphModel(S.book, new Set()), __map.measure); return performance.now() - t; })()""")
    # a real selection: tree to graph to detail, timed end to end
    t_sel = page.evaluate("(() => { const t = performance.now(); __map.select(__map.S.book.route[7], { from: 'test' }); return performance.now() - t; })()")
    assert t_expand < 800, f'expand all took {t_expand:.0f} ms'
    assert t_layout < 800, f'layout with every subject open took {t_layout:.0f} ms'
    assert t_sel < 800, f'selecting took {t_sel:.0f} ms'
    page.click('#ds-btn')
    page.check('input[name=ds][value=example]')
    assert page.evaluate('__map.S.book.chapters.length') == 83
    page.context.close()
    assert not CONSOLE, 'console: ' + ' | '.join(CONSOLE[:5])
    return f'expand all {t_expand:.0f} ms ({total} rows), layout all open {t_layout:.0f} ms, root {t_root:.0f} ms, select {t_sel:.0f} ms'


ANIMS_JS = """() => document.getAnimations().filter(a => a.playState !== 'finished').map(a => {
    const e = a.effect, props = new Set();
    if (e && e.getKeyframes) for (const k of e.getKeyframes()) for (const p in k) if (!['offset', 'easing', 'composite', 'computedOffset'].includes(p)) props.add(p);
    if (a.transitionProperty) props.add(a.transitionProperty);
    const t = e ? e.getTiming() : {};
    return { props: [...props], dur: typeof t.duration === 'number' ? t.duration : 0, delay: t.delay || 0,
             on: e && e.target ? (e.target.id || e.target.getAttribute('class') || e.target.tagName) + (e.pseudoElement || '') : '' }; })"""

TRANSITIONS_JS = """(limit) => { const bad = [];
    for (const el of document.querySelectorAll('*')) for (const ps of [null, '::before', '::after']) {
        const cs = getComputedStyle(el, ps), props = cs.transitionProperty.split(',').map(x => x.trim()), durs = cs.transitionDuration.split(',').map(parseFloat);
        props.forEach((p, i) => { const d = durs[i % durs.length]; if (p !== 'none' && d > 0 && (d > limit.max || !limit.props.includes(p))) bad.push(`${el.id || el.className || el.tagName}${ps || ''}: ${p} ${d}s`); });
        if (cs.animationName !== 'none') { const d = cs.animationDuration.split(',').map(parseFloat); if (d.some(x => x > limit.max)) bad.push(`${el.id || el.className}${ps || ''}: animation ${cs.animationDuration}`); }
    } return [...new Set(bad)]; }"""

def click_visible_cluster(page):
    """A real pointer click on a closed subject that is inside the visible canvas."""
    key = page.evaluate("""() => { const s = document.getElementById('stage').getBoundingClientRect();
        for (const n of document.querySelectorAll('#g-nodes .node.cluster')) { const r = n.querySelector('.box').getBoundingClientRect();
            if (r.left >= s.left && r.top >= s.top && r.right <= s.right && r.bottom <= s.bottom) return n.dataset.key; } return null; }""")
    assert key, 'no closed subject in view'
    page.locator(f'#g-nodes .node[data-key="{key}"]').click()
    return key


COLOUR = ['color', 'background-color', 'border-color', 'border-top-color', 'border-right-color', 'border-bottom-color', 'border-left-color', 'fill', 'stroke', 'outline-color']


@check('13. reduced motion: nothing travels, scales or wipes; colour and opacity changes stay at 120 ms or less')
def t_motion(browser):
    page = new_page(browser, reduced='reduce', settle=300)
    bad = page.evaluate(TRANSITIONS_JS, {'max': 0.12, 'props': COLOUR + ['opacity']})
    assert not bad, f'{len(bad)} transitions break the rule: {bad[:3]}'
    seen = []

    def act(label, fn):
        fn()
        anims = page.evaluate(ANIMS_JS)
        for a in anims:
            moving = [p for p in a['props'] if p in ('transform', 'strokeDashoffset', 'stroke-dashoffset', 'clipPath', 'translate', 'scale')]
            assert not moving, f'{label}: {a["on"]} animates {moving}'
            assert a['dur'] <= 120, f'{label}: {a["on"]} runs {a["dur"]} ms'
        seen.append(f'{label}:{len(anims)}')
        page.wait_for_timeout(200)
    act('open folder', lambda: page.click('#ti-bsearch > .row'))
    act('close folder', lambda: page.click('#ti-bsearch > .row'))
    act('select chapter', lambda: (page.click('#ti-os > .row'), page.click('#ti-os-processes > .row')))
    act('fit all', lambda: page.click('#fit-all'))
    act('open subject in graph', lambda: click_visible_cluster(page))
    act('filter', lambda: page.fill('#q', 'git'))
    act('theme', lambda: page.click('#theme-btn'))
    k = page.evaluate('__map.G.k')
    page.context.close()
    page = new_page(browser, w=390, h=844, reduced='reduce', settle=300)
    act = act  # same rules on the phone
    page.click('.tabs [data-tab=graph]')
    anims = page.evaluate(ANIMS_JS)
    assert all(not [p for p in a['props'] if p == 'transform'] and a['dur'] <= 120 for a in anims), f'phone tab: {anims[:2]}'
    page.context.close()
    # with motion allowed, the press and the colour changes are on
    page = new_page(browser)
    d = page.evaluate("[getComputedStyle(document.querySelector('#fit-all')).transitionProperty, getComputedStyle(document.querySelector('#fit-all')).transitionDuration]")
    assert 'transform' in d[0] and '0.14s' in d[1], f'normal motion is {d}'
    page.context.close()
    return ', '.join(seen) + f'; camera at k={k:.2f}'


@check('14. motion rules: no "transition: all"; only transform, opacity, stroke-dashoffset or colour; nothing over 300 ms')
def t_motion_rules(browser):
    page = new_page(browser, settle=600)
    css = page.evaluate("""() => { const out = { all: [], kf: [] };
        const walk = rules => { for (const r of rules) {
            if (r.cssRules && !(r instanceof CSSKeyframesRule)) walk(r.cssRules);
            if (r.style) { const t = (r.style.getPropertyValue('transition') + ' ' + r.style.getPropertyValue('transition-property')).toLowerCase();
                if (/(^|[\\s,])all([\\s,]|$)/.test(t)) out.all.push(r.selectorText); }
            if (r instanceof CSSKeyframesRule) for (const k of r.cssRules) for (let i = 0; i < k.style.length; i++) {
                const p = k.style[i]; if (!['transform', 'opacity', 'stroke-dashoffset', 'color'].includes(p)) out.kf.push(r.name + ': ' + p); }
        } };
        for (const sh of document.styleSheets) walk(sh.cssRules);
        return out; }""")
    assert not css['all'], f'transition: all in {css["all"]}'
    assert not css['kf'], f'keyframes animate {css["kf"]}'
    bad = page.evaluate(TRANSITIONS_JS, {'max': 0.3, 'props': COLOUR + ['opacity', 'transform', 'stroke-dashoffset']})
    assert not bad, f'{len(bad)} transitions break the rule: {bad[:3]}'
    # and what runs during real use
    acts = [('press', lambda: (page.hover('#fit-all'), page.mouse.down())), ('release', lambda: page.mouse.up()),
            ('open subject', lambda: click_visible_cluster(page)), ('open folder', lambda: page.click('#ti-bsearch > .row')),
            ('select', lambda: page.click('#ti-bsearch-bounds > .row')), ('fit all', lambda: page.click('#fit-all')),
            ('filter', lambda: page.fill('#q', 'search')), ('copy', lambda: page.click('#copy-path'))]
    n = 0
    for label, fn in acts:
        fn()
        page.wait_for_timeout(30)
        for a in page.evaluate(ANIMS_JS):
            n += 1
            odd = [p for p in a['props'] if p not in ('transform', 'opacity', 'strokeDashoffset', 'color', 'backgroundColor', 'borderColor', 'borderTopColor', 'borderRightColor', 'borderBottomColor', 'borderLeftColor', 'fill', 'stroke', 'stroke-dashoffset', *COLOUR)]
            assert not odd, f'{label}: {a["on"]} animates {odd}'
            assert a['dur'] <= 300, f'{label}: {a["on"]} runs {a["dur"]} ms'
        page.wait_for_timeout(400)
    page.context.close()
    return f'{n} running animations inspected during 8 actions'


@check('15. keyboard expand never animates; pointer expand does (rows rise, guide draws, close fades in 110 ms)')
def t_kbd_vs_pointer(browser):
    page = new_page(browser, settle=600)
    settle(page)
    page.evaluate("document.getElementById('ti-bsearch').focus()")
    page.keyboard.press('ArrowRight')
    assert expanded(page, 'bsearch') == 'true'
    running = page.evaluate(ANIMS_JS)
    assert not running, f'keyboard expand animates: {running[:3]}'
    page.keyboard.press('ArrowLeft')
    assert not page.evaluate(ANIMS_JS) and not page.query_selector('#tree .leaving'), 'keyboard collapse animates'
    # keyboard selection in the graph changes colour only
    page.keyboard.press('ArrowDown')
    page.keyboard.press('Enter')
    moving = [a for a in page.evaluate(ANIMS_JS) if 'transform' in a['props'] or 'strokeDashoffset' in a['props']]
    assert not moving, f'keyboard select moves: {moving[:2]}'
    settle(page)
    page.click('#ti-bsearch > .row')
    anims = page.evaluate(ANIMS_JS)
    rows_ = [a for a in anims if 'transform' in a['props'] and 'row' in a['on']]
    guides = [a for a in anims if a['on'].endswith('::before')]
    assert rows_ and guides, f'pointer expand: {len(rows_)} row and {len(guides)} guide animations'
    last = max(a['delay'] for a in rows_)
    assert last <= 160, f'stagger runs to {last} ms'
    settle(page)
    page.click('#ti-bsearch > .row')
    assert 'bsearch-find' not in rows(page), 'closed rows are still in the tree'
    ghost = page.evaluate("(() => { const g = document.querySelector('#tree .leaving'); return g && [g.getAttribute('aria-hidden'), g.inert, g.querySelectorAll('[role], [id]').length]; })()")
    assert ghost and ghost[0] == 'true' and ghost[1] and ghost[2] == 0, f'the closing rows are not out of the tree: {ghost}'
    page.wait_for_timeout(250)
    assert not page.query_selector('#tree .leaving'), 'closing rows never left'
    page.context.close()
    return f'{len(rows_)} rows rise, last delay {last:.0f} ms'


FLIP_JS = """() => { const m = __map, G = m.G, r = document.getElementById('graph').getBoundingClientRect(); const out = [];
    for (const el of document.querySelectorAll('#g-nodes .node')) { const b = m.boxOf(el.dataset.key), q = el.querySelector('.box').getBoundingClientRect();
        const ex = r.left + G.tx + b.x * G.k, ey = r.top + G.ty + b.y * G.k;
        if (Math.abs(q.left - ex) > 0.75 || Math.abs(q.top - ey) > 0.75) out.push(`${el.dataset.key}: ${(q.left - ex).toFixed(1)},${(q.top - ey).toFixed(1)}`); }
    return { off: out, n: document.querySelectorAll('#g-nodes .node').length, ghosts: document.querySelectorAll('#g-ghost *').length }; }"""


@check('16. FLIP: opening and closing a subject glides the boxes, and every box ends exactly at its laid-out place')
def t_flip(browser):
    page = new_page(browser, settle=600)
    settle(page)
    out = []
    for key, what in (('os', 'open'), ('band:os', 'close'), ('bsearch', 'open')):
        page.locator(f'#g-nodes .node[data-key="{key}"]').click()
        moving = [a for a in page.evaluate(ANIMS_JS) if 'transform' in a['props'] and 'node' in a['on']]
        assert moving, f'{what} {key}: no box moved'
        assert all(a['dur'] <= 260 for a in moving), 'a box moves for more than 260 ms'
        settle(page)
        r = page.evaluate(FLIP_JS)
        assert not r['off'], f'{what} {key}: {len(r["off"])} boxes off their place: {r["off"][:3]}'
        assert r['ghosts'] == 0, f'{what} {key}: {r["ghosts"]} ghost elements left behind'
        assert page.evaluate("getComputedStyle(document.getElementById('g-edges')).opacity") == '1'
        out.append(f'{what} {key}: {len(moving)} glide')
    page.context.close()
    return '; '.join(out)


@check('17. camera: Fit all glides (pointer) and a drag cancels it at once')
def t_camera(browser):
    page = new_page(browser, settle=600)
    settle(page)
    for _ in range(3):
        page.click('#z-in')
    k0 = page.evaluate('__map.G.k')
    fit = page.evaluate("(() => { const G = __map.G, s = [G.k, G.tx, G.ty]; __map.fitAll(); const f = [G.k, G.tx, G.ty]; [G.k, G.tx, G.ty] = s; __map.fitAll; return f; })()")
    page.evaluate("(() => { const G = __map.G; })()")
    page.click('#fit-all')
    page.wait_for_timeout(90)
    mid = page.evaluate('__map.G.k')
    assert min(k0, fit[0]) - 1e-3 < mid < max(k0, fit[0]) + 1e-3 and abs(mid - fit[0]) > 1e-3, f'no glide: k {k0:.2f} -> {mid:.2f} -> {fit[0]:.2f}'
    page.wait_for_timeout(400)
    end = page.evaluate('[__map.G.k, __map.G.tx, __map.G.ty]')
    assert abs(end[0] - fit[0]) < 1e-3 and abs(end[1] - fit[1]) < 1, f'glide ended at {end}, expected {fit}'
    # again, but drag at once: the view stops where the drag left it and follows the pointer only
    for _ in range(3):
        page.click('#z-in')
    page.click('#fit-all')
    page.wait_for_timeout(40)
    r = page.evaluate("(() => { const b = document.getElementById('stage').getBoundingClientRect(); return [b.left + b.width / 2, b.top + b.height / 2]; })()")
    page.mouse.move(r[0], r[1])
    page.mouse.down()
    at = page.evaluate('[__map.G.k, __map.G.tx, __map.G.ty]')
    page.mouse.move(r[0] + 60, r[1] + 40, steps=5)
    page.mouse.up()
    page.wait_for_timeout(400)
    after = page.evaluate('[__map.G.k, __map.G.tx, __map.G.ty]')
    assert abs(after[0] - at[0]) < 1e-6, f'zoom kept moving after the drag: {at[0]:.3f} -> {after[0]:.3f}'
    assert abs(after[1] - at[1] - 60) < 1.5 and abs(after[2] - at[2] - 40) < 1.5, f'the view did not follow the drag only: {at} -> {after}'
    page.context.close()
    return f'k {k0:.2f} -> {mid:.2f} at 90 ms -> {fit[0]:.2f}; drag froze it at {at[0]:.2f}'


@check('18. dividers: role=separator with values; arrows, Shift, Home/End, double-click, drag; widths remembered')
def t_separators(browser):
    page = new_page(browser, settle=600)
    out = []
    for sel, panel, grow in (('#sep-tree', '#treepanel', 'ArrowRight'), ('#sep-detail', '#detail', 'ArrowLeft')):
        attrs = page.evaluate(f"(() => {{ const e = document.querySelector('{sel}'); return ['role', 'aria-orientation', 'aria-valuenow', 'aria-valuemin', 'aria-valuemax', 'tabindex', 'aria-label'].map(a => e.getAttribute(a)); }})()")
        assert attrs[0] == 'separator' and attrs[1] == 'vertical' and attrs[5] == '0' and attrs[6], attrs
        width = lambda: round(page.evaluate(f"document.querySelector('{panel}').getBoundingClientRect().width"))
        now = lambda: int(page.get_attribute(sel, 'aria-valuenow'))
        page.focus(sel)
        v0, w0 = now(), width()
        page.keyboard.press(grow)
        assert now() == v0 + 16 and width() == w0 + 16, f'{sel}: {grow} gave {now()} / {width()} from {v0} / {w0}'
        page.keyboard.press('Shift+' + ('ArrowLeft' if grow == 'ArrowRight' else 'ArrowRight'))
        assert now() == v0 + 16 - 64, f'{sel}: Shift step gave {now()}'
        page.keyboard.press('Home')
        assert now() == int(attrs[3]), f'{sel}: Home gave {now()}'
        page.keyboard.press('End')
        assert now() == int(page.get_attribute(sel, 'aria-valuemax')), f'{sel}: End gave {now()}'
        page.dblclick(sel)
        assert now() == v0, f'{sel}: double-click reset to {now()}, not {v0}'
        b = page.evaluate(f"(() => {{ const r = document.querySelector('{sel}').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }})()")
        page.mouse.move(*b)
        page.mouse.down()
        page.mouse.move(b[0] + (40 if grow == 'ArrowRight' else -40), b[1], steps=4)
        page.mouse.up()
        assert now() == v0 + 40, f'{sel}: drag gave {now()}, expected {v0 + 40}'
        out.append(f'{sel} {v0}->{v0 + 40}')
    page.reload()
    page.wait_for_function('window.__map && window.__map.S.book')
    assert int(page.get_attribute('#sep-tree', 'aria-valuenow')) == int(out[0].split('->')[1]), 'width not remembered'
    page.context.close()
    return '; '.join(out)


MATRIX = [  # w, h, device scale, touch
    (320, 568, 2, True), (360, 800, 2, True), (390, 844, 3, True), (430, 932, 3, True), (844, 390, 3, True),
    (768, 1024, 2, True), (1024, 768, 1, False), (1280, 720, 1, False), (1366, 768, 1, False), (1440, 900, 1, False),
    (1920, 1080, 1, False), (2560, 1440, 1, False), (720, 450, 2, False),  # the last is 1440x900 at 200% zoom
]

GEOMETRY_JS = """([w, h, touch]) => {
    const vis = e => { if (!e.getClientRects().length) return false; const cs = getComputedStyle(e); if (cs.visibility === 'hidden' || e.closest('[hidden], .sr-only, .ghost')) return false; const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
    const ctrls = [...document.querySelectorAll('button, input[type=search], [role=separator]')].filter(vis).filter(e => !e.closest('.tree-scroll, .detail-body, #ds-menu'));
    const R = e => e.getBoundingClientRect();
    const out = { outside: [], overlap: [], small: [], tiny: [], sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth };
    for (const e of ctrls) { const r = R(e); if (r.left < -0.5 || r.top < -0.5 || r.right > w + 0.5 || r.bottom > h + 0.5) out.outside.push((e.id || e.textContent.trim().slice(0, 14) || e.getAttribute('aria-label')) + ` ${Math.round(r.left)},${Math.round(r.top)},${Math.round(r.right)},${Math.round(r.bottom)}`); }
    for (let i = 0; i < ctrls.length; i++) for (let j = i + 1; j < ctrls.length; j++) {
        const a = R(ctrls[i]), b = R(ctrls[j]); const ix = Math.min(a.right, b.right) - Math.max(a.left, b.left), iy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        if (ix > 3 && iy > 3) out.overlap.push([ctrls[i], ctrls[j]].map(e => e.id || e.textContent.trim().slice(0, 12) || e.getAttribute('aria-label')).join(' / ')); }
    const targets = [...document.querySelectorAll('button, input[type=search], .tree .row')].filter(vis);
    if (touch) for (const e of targets) { const r = R(e); if (r.width < 43.5 || r.height < 43.5) out.small.push((e.textContent.trim().slice(0, 14) || e.getAttribute('aria-label')) + ` ${Math.round(r.width)}x${Math.round(r.height)}`); }
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let t = walker.nextNode(); t; t = walker.nextNode()) { const el = t.parentElement; if (!t.textContent.trim() || !el || el.closest('svg, script, style, .sr-only, .skip') || !vis(el)) continue;
        const fs = parseFloat(getComputedStyle(el).fontSize); if (fs < 13) out.tiny.push(`${fs}px "${t.textContent.trim().slice(0, 16)}"`); }
    const shown = q => { const e = document.querySelector(q); return !!e && vis(e); };
    out.layout = { tabs: shown('.tabs'), tree: shown('#treepanel .tree-wrap'), graph: shown('#stage'), detail: shown('#detail-body'), detailRail: shown('#detail .rail-btn'),
                   seps: shown('#sep-tree'), status: shown('#status'), cols: R(document.getElementById('cols')).height };
    return out; }"""


@check('19. viewport matrix: no sideways scroll, controls inside the window and apart, text >= 13 px, 44 px on touch, forks as designed')
def t_matrix(browser):
    done = []
    for w, h, dsf, touch in MATRIX:
        for scheme in ('light',):
            page = new_page(browser, w=w, h=h, dsf=dsf, touch=touch, scheme=scheme, hash_='#bsearch-bounds', settle=600)
            states = ['tree', 'graph', 'detail'] if w < 768 else ['open']
            for st in states:
                if w < 768:
                    page.click(f'.tabs [data-tab={st}]')
                    page.wait_for_timeout(300)
                g = page.evaluate(GEOMETRY_JS, [w, h, touch])
                tag = f'{w}x{h}{" touch" if touch else ""} {st}'
                assert g['sw'] <= g['cw'], f'{tag}: page scrolls sideways ({g["sw"]} > {g["cw"]})'
                assert not g['outside'], f'{tag}: controls outside the window: {g["outside"][:3]}'
                assert not g['overlap'], f'{tag}: controls overlap: {g["overlap"][:3]}'
                assert not g['tiny'], f'{tag}: text under 13 px: {g["tiny"][:3]}'
                assert not g['small'], f'{tag}: targets under 44 px: {g["small"][:4]}'
                L = g['layout']
                if w < 768:
                    assert L['tabs'] and L[st], f'{tag}: tabs or the {st} panel missing: {L}'
                elif w < 1280:
                    assert L['tree'] and L['graph'] and L['detailRail'] and not L['tabs'], f'{tag}: expected tree, graph and a detail rail: {L}'
                else:
                    assert L['tree'] and L['graph'] and L['detail'] and L['seps'], f'{tag}: expected three panels and dividers: {L}'
                if h < 500:
                    assert not L['status'] and L['cols'] >= h * 2 / 3 - 1, f'{tag}: work area {L["cols"]:.0f} of {h}'
            if w >= 768 and w < 1280:  # the rail opens on demand and folds again
                page.click('#detail .rail-btn')
                page.wait_for_timeout(100)
                g = page.evaluate(GEOMETRY_JS, [w, h, touch])
                assert g['layout']['detail'] and not g['outside'] and not g['overlap'] and g['sw'] <= g['cw'], f'{w}x{h} detail opened: {g["outside"][:2]} {g["overlap"][:2]}'
                if w < 1024:
                    assert not g['layout']['tree'], f'{w}x{h}: the tree should fold when the detail opens'
            done.append(f'{w}x{h}')
            page.context.close()
    return f'{len(done)} sizes'


@check('20. no console errors or warnings anywhere in the run')
def t_console(browser):
    assert not CONSOLE, ' | '.join(CONSOLE[:5])


CHECKS = [t_lazy, t_keys, t_aria, t_filter, t_depth, t_hash, t_graph, t_graph_keys, t_detail,
          t_contrast, t_size, t_large, t_motion, t_motion_rules, t_kbd_vs_pointer, t_flip, t_camera, t_separators,
          t_matrix, t_console]


# ---------------------------------------------------------------- screenshots
def sheet(paths, out, cols, scale):
    """Contact sheet of screenshots (for review), with a label above each."""
    from PIL import Image, ImageDraw
    ims = [Image.open(p_) for p_ in paths]
    ims = [im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale)))) for im in ims]
    cw, ch = max(i.width for i in ims), max(i.height for i in ims) + 18
    rows_ = (len(ims) + cols - 1) // cols
    canvas = Image.new('RGB', (cw * cols + 8 * (cols - 1), ch * rows_ + 8 * (rows_ - 1)), (128, 128, 128))
    d = ImageDraw.Draw(canvas)
    for k, (im, p_) in enumerate(zip(ims, paths)):
        x, y = (k % cols) * (cw + 8), (k // cols) * (ch + 8)
        d.text((x + 2, y + 2), os.path.basename(p_)[:-4], fill=(255, 255, 255))
        canvas.paste(im, (x, y + 18))
    canvas.save(out)


def shots(browser):
    os.makedirs(SHOTS, exist_ok=True)
    made = []

    def snap(page, name, clip=None):
        path = os.path.join(SHOTS, name + '.png')
        page.screenshot(path=path, clip=clip)
        made.append(path)
        return path

    want = os.environ.get('SHOTS', 'matrix,strips')
    # the viewport matrix, light and dark
    for scheme in (('light', 'dark') if 'matrix' in want else ()):
        groups = {'phone': [], 'mid': [], 'wide': []}
        for w, h, dsf, touch in MATRIX:
            page = new_page(browser, w=w, h=h, dsf=1, touch=touch, scheme=scheme, hash_='#bsearch-loop-invariants', settle=700)
            tabs = ['tree', 'graph', 'detail'] if w < 768 and w in (390, 720) else ['tree'] if w < 768 else [None]
            for tab in tabs:
                if tab:
                    page.click(f'.tabs [data-tab={tab}]')
                    page.wait_for_timeout(400)
                name = f'm-{scheme}-{w}x{h}' + (f'-{tab}' if tab and len(tabs) > 1 else '')
                groups['phone' if w < 768 else 'mid' if w < 1280 else 'wide'].append(snap(page, name))
            page.context.close()
        sheet(groups['phone'], os.path.join(SHOTS, f'sheet-{scheme}-phone.png'), 5, 0.5)
        sheet(groups['mid'], os.path.join(SHOTS, f'sheet-{scheme}-mid.png'), 3, 0.42)
        sheet(groups['wide'], os.path.join(SHOTS, f'sheet-{scheme}-wide.png'), 2, 0.32)
    if 'strips' not in want:
        print(f'screenshots: {len(made)} in {SHOTS}')
        return
    # the large book
    page = new_page(browser, scheme='dark')
    page.click('#ds-btn')
    page.check('input[name=ds][value=large]')
    page.keyboard.press('Escape')
    page.click('[data-depth="all"]')
    page.evaluate("__map.select('entry-bits-5', { from: 'tree' })")
    page.wait_for_timeout(400)
    snap(page, 'large-dark-deep')
    page.context.close()

    # filmstrips: five frames of each animation. Animations driven by WAAPI or CSS are
    # paused and sought to exact times; the rAF camera and the theme wipe run at 10% speed.
    def strip(name, setup, act, clip, total, w=1440, h=900, scheme='light', touch=False, real=False):
        page = new_page(browser, w=w, h=h, scheme=scheme, touch=touch, hash_=setup.get('hash', ''), settle=700)
        page.context.grant_permissions(['clipboard-read', 'clipboard-write'])
        for f in setup.get('pre', []):
            f(page)
        settle(page)
        page.mouse.move(0, 0)
        page.wait_for_timeout(200)
        c = clip(page) if callable(clip) else clip
        frames = []
        import time
        if real:
            page.evaluate('window.__motionScale = 10')
            t0 = time.time()
            act(page)
            for k in range(5):
                dt = total * 10 * (k + 0.5) / 5 / 1000 - (time.time() - t0)
                if dt > 0:
                    time.sleep(dt)
                frames.append(snap(page, f'f-{name}-{k}', c))
            page.evaluate('window.__motionScale = 1')
        else:
            act(page)
            page.evaluate("document.getAnimations().forEach(a => a.pause())")
            for k in range(5):
                t = total * k / 4
                page.evaluate(f"document.getAnimations().forEach(a => {{ a.currentTime = {t}; }})")
                frames.append(snap(page, f'f-{name}-{k}', c))
        sheet(frames, os.path.join(SHOTS, f'strip-{name}.png'), 5, 1 if c and c['width'] < 400 else 0.6)
        for f_ in frames:
            os.remove(f_)
            made.remove(f_)
        page.context.close()

    def rect(q, pad=8):
        return lambda page: page.evaluate(f"(() => {{ const r = document.querySelector('{q}').getBoundingClientRect(); return {{ x: Math.max(0, r.left - {pad}), y: Math.max(0, r.top - {pad}), width: r.width + 2 * {pad}, height: r.height + 2 * {pad} }}; }})()")

    def press(page):
        page.hover('#collapse-all')
        page.mouse.down()
        page.wait_for_timeout(450)
        page.mouse.up()
    strip('press', {}, press, rect('#treepanel .head-line', 4), 140 + 50)
    strip('tree-open', {}, lambda p: p.click('#ti-bsearch > .row'), {'x': 16, 'y': 330, 'width': 350, 'height': 400}, 320)
    strip('tree-close', {'pre': [lambda p: p.click('#ti-bsearch > .row')]}, lambda p: p.click('#ti-bsearch > .row'), {'x': 16, 'y': 330, 'width': 350, 'height': 400}, 140)
    strip('graph-open', {}, lambda p: click_visible_cluster(p), rect('#stage', 0), 420)
    strip('graph-close', {'hash': '#os-signals'}, lambda p: p.locator('#g-nodes .node[data-key="band:os"]').click(), rect('#stage', 0), 420)
    strip('edges-draw', {'hash': '#bsearch-find', 'pre': [lambda p: p.click('#fit-all'), lambda p: p.wait_for_timeout(500)]},
          lambda p: p.locator('#g-nodes .node[data-key="bsearch-bounds"]').click(), rect('#stage', 0), 300)
    strip('camera', {'hash': '#bsearch-find'}, lambda p: p.click('#fit-all'), rect('#stage', 0), 260, real=True)
    strip('detail-swap', {'hash': '#bsearch-find'}, lambda p: p.click('#ti-bsearch-bounds > .row'), rect('#detail', 0), 210)
    strip('phone-tab', {'hash': '#bsearch-find'}, lambda p: p.click('.tabs [data-tab=graph]'), None, 220, w=390, h=844, touch=True)
    strip('filter-marks', {}, lambda p: p.fill('#q', 'process'), rect('#treepanel', 0), 140)
    strip('copy', {'hash': '#bsearch-find'}, lambda p: p.click('#copy-path'), rect('#detail .path-line', 6), 200)
    strip('theme-wipe', {}, lambda p: p.click('#theme-btn'), None, 380, scheme='light', real=True)
    strip('first-load', {}, lambda p: (p.evaluate("localStorage.clear()"), p.reload(), p.wait_for_function('window.__map && window.__map.S.book')), None, 420)
    strip('phone-landscape-open', {}, lambda p: click_visible_cluster(p), None, 420, w=844, h=390, touch=True)
    print(f'screenshots: {len(made)} in {SHOTS}')


def main():
    only = None  # --only 7,10 runs just those checks (for iterating; the full run is the gate)
    if '--only' in sys.argv:
        only = {int(x) for x in sys.argv[sys.argv.index('--only') + 1].split(',')}
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
        for i, t in enumerate(CHECKS, 1):
            if only is None or i in only:
                t(browser)
        if '--shots' in sys.argv:
            shots(browser)
        browser.close()
    passed = sum(1 for _, ok in RESULTS if ok)
    failed = len(RESULTS) - passed
    print(f'{passed} passed, {failed} failed')
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
