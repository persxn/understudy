#!/usr/bin/env python3
"""Checks for reader/index.html, the reading page, on real books served from a temporary shelf.

Run:  python3 tests/reader/test_reader.py            (checks only)
      python3 tests/reader/test_reader.py --shots    (checks, then screenshots into tests/reader/shots)
      python3 tests/reader/test_reader.py 5 9        (only the checks whose number is given)

Prints one line per check and "N passed, M failed"; exits 1 on any failure.
Uses the installed Chrome and python3 -m http.server on a free port; no network.
"""
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import traceback
import urllib.error
import urllib.request

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from shelf import ROOT, JOJO, make_shelf  # noqa: E402

HTML = os.path.join(ROOT, 'reader', 'index.html')
SHOTS = os.path.join(HERE, 'shots')
HAVE_C = os.path.isdir(os.path.join(JOJO, 'chapters'))                # the owner's 11-chapter book; the checks that need it say so when it is absent
BIG = 'learn-c' if HAVE_C else 'long-read'  # the book used where any real book will do

RESULTS = []
CONSOLE = []   # every console error or warning and page error, from every page
FOREIGN = []   # every request that left the shelf's own address
SERVERS = []
SHELVES = []   # extra shelves made by single checks, removed at the end


def check(name):
    def deco(fn):
        def run(*a, **k):
            try:
                detail = fn(*a, **k)
                RESULTS.append((name, True))
                print(f'PASS  {name}' + (f'  ({detail})' if detail else ''), flush=True)
            except Exception as e:  # noqa: BLE001 - report every failure and carry on
                RESULTS.append((name, False))
                print(f'FAIL  {name}: {str(e) or e.__class__.__name__}'.split('\nCall log')[0], flush=True)
                if os.environ.get('VERBOSE'):
                    traceback.print_exc()
        run.label = name
        return run
    return deco


def serve(folder):
    """python3 -m http.server on a free port; returns the base address."""
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    proc = subprocess.Popen([sys.executable, '-m', 'http.server', str(port), '--bind', '127.0.0.1', '--directory', folder],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    SERVERS.append(proc)
    base = f'http://127.0.0.1:{port}'
    for _ in range(100):
        try:
            urllib.request.urlopen(base + '/index.html', timeout=1).read(1)
            return base
        except urllib.error.HTTPError:      # it answered: a folder without the page is still a running server
            return base
        except OSError:
            time.sleep(0.05)
    raise RuntimeError('the test server did not start')


def new_page(browser, base, hash_='', w=1440, h=900, scheme='light', reduced=None, touch=False, dsf=1, clipboard=False,
             ready='window.__us && __us.S.book', settle=200, init=None, path='/index.html', quiet=False):
    ctx = browser.new_context(viewport={'width': w, 'height': h}, color_scheme=scheme, device_scale_factor=dsf,
                              has_touch=touch, is_mobile=touch, reduced_motion=reduced or 'no-preference')
    if clipboard:
        ctx.grant_permissions(['clipboard-read', 'clipboard-write'])
    if init:
        ctx.add_init_script(init)
    page = ctx.new_page()
    page.set_default_timeout(8000)
    if not quiet:
        page.on('console', lambda m: CONSOLE.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
        page.on('pageerror', lambda e: CONSOLE.append(f'pageerror: {e}'))
    page.on('request', lambda r: FOREIGN.append(r.url) if not r.url.startswith((base, 'file:', 'data:', 'about:')) else None)
    page.goto(base + path + (('#' + hash_) if hash_ else ''))
    if ready:
        page.wait_for_function(ready)
    page.wait_for_timeout(settle)
    return page


def reading(page, sec_id=None):
    """Wait until a section is on the page (the one named, if any)."""
    cond = "document.body.dataset.mode === 'read' && __us.R.sec && document.querySelector('#article h1')"
    if sec_id:
        cond += f" && __us.R.sec.id === '{sec_id}'"
    page.wait_for_function(cond)
    page.wait_for_timeout(120)


def settle(page, timeout=3000):
    page.wait_for_function("document.getAnimations().every(a => a.playState !== 'running')", timeout=timeout)


def manifest(shelf):
    with open(os.path.join(shelf, 'manifest.json'), encoding='utf-8') as f:
        return json.load(f)


# ---------------------------------------------------------------- 1. the map: tree
@check('1. map, tree: book > part > chapter > section from the manifest; lazy rows; ARIA tree; arrows, Home/End, type-ahead')
def t_tree(browser, base, shelf):
    man = manifest(shelf)
    page = new_page(browser, base)
    data = page.evaluate("""() => { const b = __us.S.book; return { books: b.books.map(x => x.name), chapters: b.chapters.length, sections: b.sections.length,
        kinds: [...new Set(b.order.map(n => n.kind))], parts: b.order.filter(n => n.kind === 'part').map(n => n.title) }; }""")
    assert data['books'] == [b['name'] for b in man['books']], data['books']
    assert data['chapters'] == sum(len(p['chapters']) for b in man['books'] for p in b['parts'])
    assert data['sections'] == sum(len(c['sections']) for b in man['books'] for p in b['parts'] for c in p['chapters'])
    assert set(data['kinds']) == {'shelf', 'book', 'part', 'chapter', 'section'}, data['kinds']
    assert 'Part I · Basics' in data['parts'], data['parts']
    # first visit: books and parts open, chapters closed, so no section row exists yet
    assert page.locator('#tree .ti.section').count() == 0 and page.locator('#tree .ti.chapter').count() == data['chapters']
    page.click('#ti-first-steps-c-1 > .row')
    page.wait_for_timeout(300)
    assert page.locator('#ti-first-steps-c-1 > .grp > .ti.section').count() == 4, 'opening a chapter adds exactly its sections'
    # ARIA: levels, set sizes, one tab stop
    bad = page.evaluate("""() => { const out = []; const items = [...document.querySelectorAll('#tree [role=treeitem]')];
        for (const li of items) { const sibs = [...li.parentElement.children].filter(x => x.matches('[role=treeitem]'));
            if (+li.getAttribute('aria-setsize') !== sibs.length || +li.getAttribute('aria-posinset') !== sibs.indexOf(li) + 1) out.push(li.id);
            const up = li.parentElement.closest('[role=treeitem]'); if (up && +li.getAttribute('aria-level') !== +up.getAttribute('aria-level') + 1) out.push('level ' + li.id);
            if (!li.getAttribute('aria-label')) out.push('label ' + li.id); }
        if (items.filter(li => li.tabIndex === 0).length !== 1) out.push('tab stops'); return out; }""")
    assert not bad, bad[:4]
    # keys
    page.focus('#ti-first-steps-c-1')
    page.keyboard.press('ArrowDown')
    assert page.evaluate('document.activeElement.id') == 'ti-first-steps-c-1-1'
    page.keyboard.press('ArrowLeft')
    assert page.evaluate('document.activeElement.id') == 'ti-first-steps-c-1'
    page.keyboard.press('ArrowLeft')
    assert page.get_attribute('#ti-first-steps-c-1', 'aria-expanded') == 'false'
    page.keyboard.press('Home')
    assert page.evaluate('document.activeElement.id') == 'ti-shelf'
    page.keyboard.press('End')
    last = page.evaluate('document.activeElement.id')
    assert last == page.evaluate("[...document.querySelectorAll('#tree [role=treeitem]')].pop().id")
    page.keyboard.press('Home')
    page.keyboard.type('choi')
    assert page.evaluate('document.activeElement.id') == 'ti-first-steps-c-2', 'type-ahead'
    page.keyboard.press('Enter')
    assert page.evaluate('__us.S.sel') == 'first-steps-c-2' and page.evaluate('location.hash') == '#map-first-steps-c-2'
    # filter by typing: matches marked, ancestors opened, restored on Escape
    before = page.evaluate('[...__us.S.open].sort()')
    page.fill('#q', 'variab')
    page.wait_for_timeout(250)
    assert page.locator('#tree mark').count() >= 1 and page.locator('#ti-first-steps-c-1-3').count() == 1
    page.press('#q', 'Escape')
    page.wait_for_timeout(150)
    assert page.evaluate('[...__us.S.open].sort()') == before, 'filter did not restore the tree'
    # depth buttons and the status line
    page.click('[data-depth="1"]')
    assert page.locator('#tree .ti.book').count() == len(man['books']) and page.locator('#tree .ti.chapter').count() == 0
    assert '-L 1' in page.text_content('#cmd')
    page.click('[data-depth="all"]')
    assert page.locator('#tree .ti.section').count() == data['sections']
    page.context.close()
    return f"{len(data['books'])} books, {data['chapters']} chapters, {data['sections']} sections"


# ---------------------------------------------------------------- 2. the map: graph
GRAPH_JS = """() => { const L = __us.G.layout, out = { overlaps: [], through: [], units: L.units.size, rows: L.rows.size, bands: L.bands.length, edges: L.edges.length };
    const boxes = [...L.units.values()].map(u => [u.id, u.x, u.y, u.x + u.w, u.y + u.h]);
    for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) { const a = boxes[i], b = boxes[j];
        if (Math.min(a[3], b[3]) - Math.max(a[1], b[1]) > 0 && Math.min(a[4], b[4]) - Math.max(a[2], b[2]) > 0) out.overlaps.push(a[0] + '/' + b[0]); }
    for (const e of L.edges) for (let k = 0; k + 1 < e.points.length; k++) { const [x1, y1] = e.points[k], [x2, y2] = e.points[k + 1];
        for (const b of boxes) { const lo = [Math.min(x1, x2), Math.min(y1, y2)], hi = [Math.max(x1, x2), Math.max(y1, y2)];
            if (hi[0] > b[1] + 1 && lo[0] < b[3] - 1 && hi[1] > b[2] + 1 && lo[1] < b[4] - 1) out.through.push(e.id + ' through ' + b[0]); } }
    out.arrows = L.edges.every(e => { const p = e.points, n = p.length; return p[n - 1][0] > p[n - 2][0] && p[n - 1][1] === p[n - 2][1]; });
    return out; }"""


@check('2. map, graph: a book is a cluster, open it shows its chapters, a chapter opens into its sections; edges from the manifest; nothing overlaps')
def t_graph(browser, base, shelf):
    man = manifest(shelf)
    page = new_page(browser, base)
    page.evaluate("__us.select('shelf', { from: 'tree' })")
    g = page.evaluate(GRAPH_JS)
    assert g['units'] == len(man['books']) and g['bands'] == 0, f'closed shelf: {g}'
    # open the book: its chapters appear as boxes inside a band
    page.click(f'#g-nodes [data-key="{BIG}"]')
    page.wait_for_timeout(700)
    book = next(b for b in man['books'] if b['name'] == BIG)
    nch = sum(len(p['chapters']) for p in book['parts'])
    g = page.evaluate(GRAPH_JS)
    assert g['bands'] == 1 and g['units'] == len(man['books']) - 1 + nch, g
    assert not g['overlaps'] and not g['through'] and g['arrows'], f"{g['overlaps'][:3]} {g['through'][:3]} arrows={g['arrows']}"
    # every drawn edge is a manifest chapter edge, and the drawing keeps the manifest's reachability
    ok = page.evaluate("""(book) => { const b = __us.S.book, L = __us.G.layout; const real = new Set();
        for (const c of b.chapters) for (const m of c.needs) real.add(m + '>' + c.id);
        const drawn = L.edges.map(e => e.id); if (!drawn.every(id => real.has(id))) return 'an edge is not in the manifest';
        const reach = (start, next) => { const s = new Set(), st = [start]; while (st.length) for (const m of next(st.pop())) if (!s.has(m)) { s.add(m); st.push(m); } return s; };
        for (const c of b.chapters.filter(c => c.book.name === book)) { const a = reach(c.id, id => b.byId.get(id).needs), d = reach(c.id, id => L.pred.get(id) || []);
            if (a.size !== d.size || [...a].some(x => !d.has(x))) return 'chapter ' + c.n + ' lost a prerequisite in the drawing'; }
        return true; }""", BIG)
    assert ok is True, ok
    edges = g['edges']
    # selecting a chapter marks what it needs and what it unlocks
    target = f'{BIG}-8' if HAVE_C else f'{BIG}-1'
    page.evaluate(f"__us.select('{target}', {{ from: 'test' }})")
    marks = page.evaluate("""() => { const b = __us.S.book, sel = b.byId.get(__us.S.sel); const cls = k => { const el = document.querySelector(`#g-nodes [data-key="${k}"]`); return el ? el.getAttribute('class') : ''; };
        const anc = [...__us.ancestorsOf(b, sel.id)], desc = [...__us.descendantsOf(b, sel.id)];
        return { sel: cls(sel.id), anc: anc.map(cls), desc: desc.map(cls) }; }""")
    assert 'sel' in marks['sel'] and all('needs' in c for c in marks['anc']) and all('unlocks' in c for c in marks['desc']), marks
    # a chapter opens into its sections (pointer), and folds again
    page.click(f'#g-nodes [data-key="{target}"]')
    page.wait_for_timeout(700)
    nsec = page.evaluate(f"__us.S.book.byId.get('{target}').children.length")
    g2 = page.evaluate(GRAPH_JS)
    assert g2['rows'] == nsec and not g2['overlaps'] and not g2['through'], f"sections listed: {g2['rows']} of {nsec}; {g2['overlaps'][:2]} {g2['through'][:2]}"
    inside = page.evaluate(f"""() => {{ const L = __us.G.layout, u = L.units.get('{target}'); return [...L.rows.values()].every(r => r.x === u.x && r.y >= u.y + u.headH - 0.5 && r.y + r.h <= u.y + u.h + 0.5); }}""")
    assert inside, 'section rows are not inside their chapter box'
    first = page.evaluate(f"__us.S.book.byId.get('{target}').children[1].id")
    box = page.evaluate(f"document.querySelector('#g-nodes [data-key=\"{first}\"] .rbg').getBoundingClientRect().toJSON()")
    page.mouse.click(box['x'] + box['width'] - 6, box['y'] + box['height'] / 2)     # the empty end of the row, not its letters
    page.wait_for_timeout(300)
    assert page.evaluate('__us.S.sel') == first and 'sel' in page.get_attribute(f'#g-nodes [data-key="{first}"]', 'class')
    # keyboard: one tab stop, Right and Left follow the arrows, Enter selects, Esc returns to the tree
    assert page.locator('#g-nodes [tabindex="0"]').count() == 1
    page.evaluate(f"__us.select('{target}', {{ from: 'test' }})")
    page.focus(f'#g-nodes [data-key="{target}"]')
    succ = page.evaluate(f"__us.G.layout.succ.get('{target}')")
    page.keyboard.press('ArrowRight')
    now = page.evaluate('document.activeElement.dataset.key')
    assert now in succ if succ else True, f'Right went to {now}, not one of {succ}'
    assert succ or not HAVE_C
    page.keyboard.press('Enter')
    assert page.evaluate('__us.S.sel') == now
    page.keyboard.press('Escape')
    assert page.evaluate('document.activeElement.id') == 'ti-' + now, 'Esc should return to the tree row'
    # readable labels, never under 11 px on screen
    k = page.evaluate('__us.G.k')
    assert k >= 0.3
    page.context.close()
    return f'{nch} chapter boxes, {edges} edges drawn, {nsec} section rows'


# ---------------------------------------------------------------- 3. the map: detail
@check('3. map, detail: state, level, needs and unlocks from the manifest; one action: Read when written, Copy a request for Claude when planned')
def t_detail(browser, base, shelf):
    man = manifest(shelf)
    page = new_page(browser, base, clipboard=True)
    # a planned chapter: copies the sentence for the agent
    page.evaluate("__us.select('first-steps-c-2', { from: 'test' })")
    assert 'Planned' in page.text_content('#detail-body .facts')
    assert page.text_content('#primary').strip() == 'Copy a request for Claude'
    page.click('#primary')
    page.wait_for_timeout(250)
    assert page.evaluate('navigator.clipboard.readText()') == 'Write chapter 2 of first-steps-c'
    assert 'Copied' in page.text_content('#primary') and page.text_content('#confirm').strip()
    needs = page.eval_on_selector_all('#detail-body .links.needs [data-goto]', 'els => els.map(e => e.dataset.goto)')
    assert needs == ['first-steps-c-1'], needs
    assert page.locator('#learning-path-none').count() == 1, 'chapter 1 is written, so nothing is left to write first'
    # a planned section: its level and what it needs, from the manifest edges
    page.evaluate("__us.select('first-steps-c-2-2', { from: 'test' })")
    e = [x for x in man['edges'] if x['from'] == 'first-steps-c:2.2']
    want = sorted('first-steps-c-' + x['to'].split(':')[1].replace('.', '-') for x in e)
    got = sorted(page.eval_on_selector_all('#detail-body .links.needs [data-goto]', 'els => els.map(e => e.dataset.goto)'))
    assert got == want and want, f'{got} != {want}'
    lv = page.evaluate("[...document.querySelectorAll('#detail-body .levels li')].map(li => [li.textContent.trim().slice(0, 9), !!li.querySelector('.on')])")
    assert [x[1] for x in lv] == [False, True, False, False, False] and lv[1][0].startswith('2 Explain'), lv
    assert page.text_content('#primary .bl') == 'Copy a request for Claude'
    assert page.get_attribute('#primary', 'data-copy') == 'Write section 2.2 of first-steps-c'
    # a written section: Read is a real link to it; unlocks lists what names it
    page.evaluate("__us.select('first-steps-c-1-3', { from: 'test' })")
    assert page.text_content('#primary').strip() == 'Read' and page.get_attribute('#primary', 'href') == '#first-steps-c-1-3'
    unl = page.eval_on_selector_all('#detail-body .links.unlocks [data-goto]', 'els => els.map(e => e.dataset.goto)')
    assert unl == ['first-steps-c-2-1'], unl
    assert 'Written' in page.text_content('#detail-body .facts')
    # needs buttons move the selection and keep focus in the panel
    page.evaluate("__us.select('first-steps-c-2-1', { from: 'test' })")
    page.click('#detail-body .links.needs [data-goto]')
    assert page.evaluate('__us.S.sel') == 'first-steps-c-1-3'
    assert page.evaluate("document.getElementById('detail').contains(document.activeElement)")
    # a written chapter and a book: Read goes to the first written section
    page.evaluate("__us.select('first-steps-c-1', { from: 'test' })")
    assert page.get_attribute('#primary', 'href') == '#first-steps-c-1-1'
    page.evaluate("__us.select('first-steps-c', { from: 'test' })")
    assert page.get_attribute('#primary', 'href') == '#first-steps-c-1-1' and 'For someone who has never programmed' in page.text_content('#detail-body')
    page.click('#copy-path')
    page.wait_for_timeout(200)
    assert page.evaluate('navigator.clipboard.readText()') == 'book/first-steps-c/'
    page.context.close()
    # on a phone, tapping a section in the tree shows its detail, with the way in
    page = new_page(browser, base, 'map-first-steps-c-1', w=390, h=844, touch=True, settle=500)
    if page.get_attribute('#ti-first-steps-c-1', 'aria-expanded') != 'true':
        page.tap('#ti-first-steps-c-1 > .row')
        page.wait_for_timeout(300)
    page.tap('#ti-first-steps-c-1-2 > .row')
    page.wait_for_timeout(400)
    assert page.evaluate('document.body.dataset.tab') == 'detail' and page.is_visible('#primary')
    page.tap('#primary')
    reading(page, 'first-steps-c-1-2')
    page.context.close()
    return 'planned chapter and section copy a request; written ones link to Read'


# ---------------------------------------------------------------- 4. shelves
@check('4. shelves: several books on one shelf; a brand-new empty shelf invites, with the exact sentence to type; a broken index says how to mend it')
def t_shelves(browser, base, shelf):
    page = new_page(browser, base)
    names = page.evaluate('__us.S.book.books.map(b => b.name)')
    assert len(names) >= 2 and page.locator('#tree .ti.book').count() == len(names)
    assert page.locator('#g-nodes .node').count() >= len(names)
    assert re.match(rf'^{len(names)} books, \d+ chapters$', page.text_content('#shelf-sum').strip())
    page.context.close()
    out = []
    for label, write in (('no manifest.json', None), ('a manifest with no books', '{"schema": 3, "books": [], "edges": [], "chapter_edges": []}')):
        empty = make_shelf(books=())
        if write:
            with open(os.path.join(empty, 'manifest.json'), 'w') as f:
                f.write(write)
        b2 = serve(empty)
        page = new_page(browser, b2, ready="document.body.dataset.mode === 'empty'", clipboard=True, quiet=True)  # the browser itself logs the 404
        assert page.is_visible('#notice h1') and page.text_content('#notice h1') == 'Your shelf is empty'
        assert not page.is_visible('#cols') and not page.is_visible('#q'), 'the empty shelf shows no map and no search'
        said = page.text_content('#n-cmd')
        assert said == 'I want to learn C from scratch', said
        page.click('#n-copy')
        page.wait_for_timeout(250)
        assert page.evaluate('navigator.clipboard.readText()') == said
        errs = page.evaluate('window.__errs || 0')
        assert not errs
        page.click('#theme-btn')  # the theme still works here
        page.wait_for_timeout(500)
        assert page.evaluate('document.documentElement.dataset.theme') == 'dark'
        page.context.close()
        shutil.rmtree(empty, ignore_errors=True)
        out.append(label)
    broken = make_shelf(books=())
    with open(os.path.join(broken, 'manifest.json'), 'w') as f:
        f.write('{"nodes": [], "planned": []}')
    page = new_page(browser, serve(broken), ready="document.body.dataset.mode === 'broken'")
    assert 'python3 scripts/us_index.py' in page.text_content('#notice') and 'older understudy' in page.text_content('#notice')
    page.context.close()
    shutil.rmtree(broken, ignore_errors=True)
    return f'{len(names)} books; empty: ' + ', '.join(out) + '; old index explained'


# ---------------------------------------------------------------- 5. routes
@check('5. reading: a chapter opens at its first section; sections route by a plain hash; previous and next; a heading inside a section; a planned one shows the map')
def t_routes(browser, base, shelf):
    page = new_page(browser, base, 'first-steps-c-1')
    reading(page, 'first-steps-c-1-1')
    assert page.text_content('#article h1').strip().startswith('1.1') and page.is_visible('.ch-title')
    assert not page.is_visible('#cols') and page.is_visible('#sheet')
    assert 'Tiny C' in page.title() and page.title().startswith('1.1 ')
    # contents: every section of the chapter, the current one marked
    toc = page.eval_on_selector_all('.toc-list > li > a', 'els => els.map(a => [a.getAttribute("href"), a.getAttribute("aria-current")])')
    assert [t[0] for t in toc] == ['#first-steps-c-1-1', '#first-steps-c-1-2', '#first-steps-c-1-3', '#first-steps-c-1-4'], toc
    assert [t[1] for t in toc] == ['page', None, None, None]
    # next, next, previous by the links at the end
    assert page.get_attribute('.pager .next', 'href') == '#first-steps-c-1-2'
    page.click('.pager .next')
    reading(page, 'first-steps-c-1-2')
    assert page.evaluate('location.hash') == '#first-steps-c-1-2' and page.evaluate('scrollY') == 0
    assert page.evaluate("document.activeElement === document.querySelector('#article h1')"), 'focus should move to the new heading'
    beats = page.eval_on_selector_all('#otp .beats a', 'els => els.map(a => a.textContent.trim().replace(/\\s+\\d+\\/\\d+$/, ""))')
    assert beats == ['The question', 'The picture', 'The idea', 'The code', 'The trace', 'What goes wrong', 'Remember', 'Check yourself'], beats
    page.click('.pager .prev')
    reading(page, 'first-steps-c-1-1')
    # keys: n and p
    page.keyboard.press('n')
    reading(page, 'first-steps-c-1-2')
    page.keyboard.press('n')
    reading(page, 'first-steps-c-1-3')
    page.keyboard.press('p')
    reading(page, 'first-steps-c-1-2')
    # a beat: the hash names it, the page moves to it, and it is still one plain name
    page.click('#otp .beats a >> nth=3')
    page.wait_for_timeout(700)
    assert page.evaluate('location.hash') == '#first-steps-c-1-2-the-code'
    top = page.evaluate("document.getElementById('first-steps-c-1-2-the-code').getBoundingClientRect().top")
    assert 40 < top < 160, f'the heading is at {top}px, under the bar it should be'
    # the same address opened cold lands on the heading
    p2 = new_page(browser, base, 'first-steps-c-1-2-the-trace')
    reading(p2, 'first-steps-c-1-2')
    top = p2.evaluate("document.getElementById('first-steps-c-1-2-the-trace').getBoundingClientRect().top")
    assert 40 < top < 160, f'cold deep link: heading at {top}px'
    p2.context.close()
    # Back returns to where the reader was, scrolled
    page.evaluate('scrollTo(0, 900)')
    page.wait_for_timeout(100)
    page.keyboard.press('n')
    reading(page, 'first-steps-c-1-3')
    page.go_back()
    reading(page, 'first-steps-c-1-2')
    page.wait_for_timeout(200)
    assert abs(page.evaluate('scrollY') - 900) < 5, f"Back restored scroll to {page.evaluate('scrollY')}"
    # the end of what is written: a request to copy, not a dead end
    page.evaluate("__us.go('first-steps-c-1-4')")
    reading(page, 'first-steps-c-1-4')
    assert page.get_attribute('.pager-end [data-copy]', 'data-copy') == 'Write chapter 2 of first-steps-c'
    # a planned section or chapter is not readable: the map, with it selected
    for h in ('first-steps-c-2-1', 'first-steps-c-2'):
        page.evaluate(f"__us.go('{h}')")
        page.wait_for_function("document.body.dataset.mode === 'map'")
        assert page.evaluate('__us.S.sel') == h
    # across chapters, when the next chapter is written
    if HAVE_C:
        page.evaluate("__us.go('learn-c-8-12')")
        reading(page, 'learn-c-8-12')
        assert page.get_attribute('.pager .next', 'href') == '#learn-c-9-1'
        assert page.get_attribute('.pager .prev', 'href') == '#learn-c-8-11'
    # only plain names ever reach location.hash, and a strange one is ignored
    seen = page.evaluate("""async () => { const out = []; const go = h => new Promise(r => { location.hash = h; setTimeout(r, 250); });
        await go('first-steps-c-1-2'); out.push(location.hash); await go('map-first-steps-c'); out.push(location.hash); await go('no-such-place'); out.push(document.body.dataset.mode); return out; }""")
    assert all(re.match(r'^#?[A-Za-z0-9-]*$', s) for s in seen[:2]) and seen[2] == 'map', seen
    names = page.evaluate("[...__us.S.book.byId.keys()].filter(id => !/^[A-Za-z0-9-]+$/.test(id))")
    assert not names, f'ids that are not plain names: {names[:3]}'
    page.context.close()
    return 'chapter, section, heading, previous/next, n/p, Back, planned, plain names'


# ---------------------------------------------------------------- 6. markdown
@check('6. text: build markers and the generated contents never show; section references are links; tables and long lines scroll inside themselves')
def t_text(browser, base, shelf):
    page = new_page(browser, base, 'first-steps-c-1-2')
    reading(page, 'first-steps-c-1-2')
    src = open(os.path.join(shelf, 'first-steps-c', 'chapters', '01-first-steps.md'), encoding='utf-8').read()
    assert '<!-- teaches:' in src and '<!-- code:' in src and '<!-- fig:' in src and '<!-- contents -->' in src, 'the fixture lost its markers'
    text = page.evaluate('document.getElementById("article").innerText')
    html = page.evaluate('document.getElementById("article").innerHTML')
    for marker in ('teaches:', 'code: id=', 'fig: id=', 'kind: memory', 'ptr p -> x', '<!--', '-->', '/contents'):
        assert marker not in text and marker not in html, f'a build marker shows: {marker}'
    assert page.evaluate("""() => { const w = document.createTreeWalker(document.getElementById('article'), NodeFilter.SHOW_COMMENT); return !w.nextNode(); }"""), 'a comment node is in the page'
    assert '- [1.1 Where C came from]' not in text and 'Chapter 1: First steps' not in page.text_content('.prose')
    # section references
    ref = page.eval_on_selector_all('.prose a.xref', 'els => els.map(a => [a.textContent, a.getAttribute("href")])')
    assert ['§1.1', '#first-steps-c-1-1'] in ref, ref
    page.click('.prose a.xref >> nth=0')
    reading(page, 'first-steps-c-1-1')
    page.go_back()
    reading(page, 'first-steps-c-1-2')
    # a wide table and a long line scroll inside themselves; the page never scrolls sideways
    out = []
    for w in (1440, 768, 390, 320):
        page.set_viewport_size({'width': w, 'height': 800})
        page.wait_for_timeout(200)
        m = page.evaluate("""() => { const tw = [...document.querySelectorAll('.tablewrap')].map(t => [t.scrollWidth, t.clientWidth, t.getBoundingClientRect().right, getComputedStyle(t).overflowX]);
            const pre = [...document.querySelectorAll('.code pre')].map(p => [p.scrollWidth, p.clientWidth, p.getBoundingClientRect().right, getComputedStyle(p).overflowX]);
            return { tw, pre, sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth, sheet: document.getElementById('sheet').getBoundingClientRect().right }; }""")
        assert m['sw'] <= m['cw'], f'{w}px: the page scrolls sideways ({m["sw"]} > {m["cw"]})'
        assert all(x[3] == 'auto' and x[2] <= m['cw'] + 0.5 for x in m['tw'] + m['pre']), f'{w}px: a block leaves the page'
        if w <= 768:
            assert any(x[0] > x[1] for x in m['tw']), f'{w}px: the wide table should scroll inside its frame'
        assert any(x[0] > x[1] for x in m['pre']), f'{w}px: the long line should scroll inside its block'
        out.append(str(w))
    # what scrolls sideways can be reached and scrolled from the keyboard
    assert page.evaluate("[...document.querySelectorAll('.code pre, .tablewrap')].filter(e => e.scrollWidth > e.clientWidth + 1).every(e => e.tabIndex === 0 && e.getAttribute('role') === 'region' && e.getAttribute('aria-label'))")
    # the measure: about 68 characters to a line at reading widths
    page.set_viewport_size({'width': 1440, 'height': 900})
    page.wait_for_timeout(200)
    cpl = page.evaluate("""() => { const ps = [...document.querySelectorAll('.prose > p')].filter(p => p.textContent.length > 300 && !p.querySelector('code'));
        const per = ps.map(p => { const lines = Math.round(p.getBoundingClientRect().height / parseFloat(getComputedStyle(p).lineHeight)); return p.textContent.length / lines; });
        return per.reduce((a, b) => a + b, 0) / per.length; }""")
    assert 60 <= cpl <= 76, f'{cpl:.0f} characters to a line'
    fonts = page.evaluate("[getComputedStyle(document.querySelector('.prose p')).fontFamily, getComputedStyle(document.querySelector('.code pre')).fontFamily, parseFloat(getComputedStyle(document.querySelector('.prose p')).fontSize)]")
    assert 'serif' in fonts[0] and 'monospace' in fonts[1] and fonts[2] >= 17, fonts
    scale = page.evaluate("['#article h1', '.prose h2', '.prose p', '.sec-meta'].map(q => parseFloat(getComputedStyle(document.querySelector(q)).fontSize))")
    assert scale[0] > scale[1] > scale[2] > scale[3] >= 13, f'type scale {scale}'
    page.context.close()
    return f'no markers; § links; inside-scroll at {", ".join(out)} px; {cpl:.0f} characters to a line'


# ---------------------------------------------------------------- 7. code
@check('7. code: highlighted with the vendored highlighter, console and text included; line numbers; the copy button copies the program exactly')
def t_code(browser, base, shelf):
    page = new_page(browser, base, 'first-steps-c-1-2', clipboard=True)
    reading(page, 'first-steps-c-1-2')
    info = page.evaluate("""() => [...document.querySelectorAll('.code')].map(c => ({ cls: c.className, lang: (c.querySelector('.lang') || {}).textContent || '', copy: !!c.querySelector('button.copy'),
        spans: c.querySelectorAll('code [class^="hljs-"]').length, ln: (c.querySelector('.ln') || {}).textContent || '', text: c.querySelector('code').textContent }))""")
    prog = [c for c in info if 'prog' in c['cls']]
    term = [c for c in info if 'term' in c['cls']]
    out = [c for c in info if 'out' in c['cls']]
    assert prog and term and out, [c['cls'] for c in info]
    first = prog[0]
    assert first['lang'] == 'c' and first['spans'] >= 6 and first['copy'], first
    assert first['ln'].split('\n') == [str(i) for i in range(1, first['text'].count('\n') + 2)], 'line numbers do not match the lines'
    kw = page.evaluate("""() => { const k = document.querySelector('.code.prog .hljs-keyword, .code.prog .hljs-type'), s = document.querySelector('.code.prog .hljs-string');
        return [getComputedStyle(k).fontWeight, getComputedStyle(s).color, getComputedStyle(document.querySelector('.code.prog code')).color]; }""")
    assert int(kw[0]) >= 700 and kw[1] != kw[2], f'keywords bold, strings coloured: {kw}'
    # text: no highlighting, no copy button; console: prompt and command told apart, commands copied
    assert all(c['spans'] == 0 and not c['copy'] for c in out), 'a text block should stay plain'
    assert term[0]['lang'] == 'terminal' and term[0]['copy']
    assert page.locator('.code.term .prompt').count() == 2 and page.locator('.code.term .cmd').count() == 2
    page.click('.code.term button.copy')
    page.wait_for_timeout(250)
    assert page.evaluate('navigator.clipboard.readText()') == 'gcc first.c -o first\n./first'
    # the program, copied byte for byte (no line numbers, no markup)
    src = open(os.path.join(shelf, 'first-steps-c', 'chapters', '01-first-steps.md'), encoding='utf-8').read()
    sect = src.split('## 1.2 ')[1]
    want = re.search(r'```c\n(.*?)\n```', sect, re.S).group(1)
    page.click('.code.prog button.copy >> nth=0')
    page.wait_for_timeout(250)
    assert page.evaluate('navigator.clipboard.readText()') == want
    assert page.text_content('.code.prog button.copy >> nth=0').strip() == 'Copied'
    assert page.evaluate("document.querySelector('.code.prog .ln').getAttribute('aria-hidden')") == 'true'
    langs = page.evaluate("['c', 'python', 'bash', 'javascript', 'json', 'sql'].filter(l => !hljs.getLanguage(l))")
    assert not langs, f'languages missing from the highlighter: {langs}'
    page.context.close()
    return f'{len(prog)} programs, {len(term)} terminal, {len(out)} plain; copy is exact'


# ---------------------------------------------------------------- 8. hidden answers
@check('8. Check yourself: an answer is not in the page until its card is turned; keyboard-operable; never shown by search or print unless opened')
def t_answers(browser, base, shelf):
    page = new_page(browser, base, 'long-read-1-3')
    reading(page, 'long-read-1-3')
    cards = page.locator('.prose details.card')
    assert cards.count() == 3
    body = lambda: page.evaluate('document.body.innerHTML')  # noqa: E731
    assert 'zebra-3-1' not in body() and 'zebra' not in page.evaluate('document.body.innerText'), 'a hidden answer is in the page'
    # the keyboard: Tab reaches the summary, Enter turns the card, Enter turns it back
    page.focus('.prose details.card >> nth=0 >> summary')
    assert page.evaluate("document.activeElement.tagName") == 'SUMMARY'
    page.keyboard.press('Enter')
    page.wait_for_timeout(150)
    assert page.evaluate("document.querySelector('.prose details.card').open") and 'zebra-3-1' in page.evaluate('document.body.innerText')
    assert 'zebra-3-2' not in body(), 'turning one card showed another answer'
    assert page.evaluate('document.getAnimations().filter(a => a.playState === "running").length') == 0, 'a keyboard turn should not animate'
    page.keyboard.press('Enter')
    page.wait_for_timeout(150)
    assert 'zebra-3-1' not in body(), 'a card turned back should take its answer out of the page'
    # the pointer: the card turns over (a short transform), then rests
    page.click('.prose details.card >> nth=1 >> summary')
    page.wait_for_function("document.querySelectorAll('.prose details.card')[1].querySelector('.card-body').childNodes.length > 0")
    anim = page.evaluate("document.getAnimations().filter(a => a.playState === 'running').map(a => Object.keys(a.effect.getKeyframes()[0] || {}))")
    assert any('transform' in k for k in anim), f'a pointer turn should move: {anim}'
    settle(page)
    assert 'zebra-3-2' in page.evaluate('document.body.innerText')
    assert page.evaluate("document.querySelector('.prose details.card:nth-of-type(1)') !== null")
    # search: answers are not in search.json, and searching for one finds nothing
    sj = open(os.path.join(shelf, 'search.json'), encoding='utf-8').read()
    assert 'zebra' not in sj
    page.fill('#q', 'zebra')
    page.wait_for_timeout(300)
    assert page.locator('.r-hit').count() == 0 and 'Nothing on your shelf' in page.text_content('#results')
    page.press('#q', 'Escape')
    # print: the whole chapter is laid out; only the card that is open shows its answer
    page.emulate_media(media='print')
    page.evaluate('__us.beforePrint()')
    page.wait_for_timeout(200)
    printed = page.evaluate('document.getElementById("article").innerText')
    assert 'zebra-3-2' in printed and 'zebra-3-1' not in printed and 'zebra-3-3' not in printed and 'zebra-1-1' not in printed and 'zebra-16-3' not in printed
    assert 'Lesson 16 of the long chapter' in printed, 'print should hold the whole chapter'
    page.evaluate('__us.afterPrint()')
    page.emulate_media(media='screen')
    # a practice section lists its exercises; a turned answer fills its square; a program inside an answer is dressed like any other
    page.evaluate("__us.go('first-steps-c-1-4')")
    reading(page, 'first-steps-c-1-4')
    n = page.locator('.prose details.card').count()
    assert page.locator('#otp .qs a').count() == n and n >= 12, f'{n} exercises'
    page.click('#otp .qs a >> nth=4')
    page.wait_for_timeout(500)
    top = page.evaluate("document.querySelectorAll('.prose details.card')[4].getBoundingClientRect().top")
    assert 60 < top < 400, f'exercise 5 is at {top}px'
    page.click('.prose details.card >> nth=4 >> summary')
    page.wait_for_function("document.querySelector('#otp .qs a.on')")
    assert page.eval_on_selector_all('#otp .qs a', 'els => els.map(a => a.classList.contains("on"))').index(True) == 4
    assert page.text_content('#otp .check-count') == f'1/{n}' and 'turned over' in page.get_attribute('#otp .qs a.on', 'aria-label')
    if HAVE_C:
        page.evaluate("__us.go('learn-c-8-12')")
        reading(page, 'learn-c-8-12')
        assert page.locator('.prose .card-body .code').count() == 0, 'answers are out of the page'
        page.click('.prose details.card >> nth=2 >> summary')
        page.wait_for_selector('.prose .card-body .code.prog .hljs-keyword')
        assert page.locator('.prose .card-body .code.prog button.copy').count() == 1 and page.locator('.prose .card-body .ln').count() == 1
    page.context.close()
    return f'3 cards; keyboard and pointer; search and print keep them hidden; {n} exercises listed'


# ---------------------------------------------------------------- 9. figures
@check('9. figures: an SVG is inlined and follows the page theme; its description is kept; tap to enlarge; old PNG figures show too')
def t_figures(browser, base, shelf):
    page = new_page(browser, base, 'first-steps-c-1-2')
    reading(page, 'first-steps-c-1-2')
    page.wait_for_selector('.fig-svg.ready')
    f = page.evaluate("""() => { const h = document.querySelector('.fig-svg.ready'), s = h.shadowRoot.querySelector('svg'); const bg = s.querySelector('.bg');
        return { theme: s.getAttribute('data-theme'), role: s.getAttribute('role'), title: s.querySelector('title').textContent, desc: s.querySelector('desc').textContent,
                 bg: getComputedStyle(bg).fill, w: h.getBoundingClientRect().width, max: h.style.maxWidth, cap: h.closest('figure').querySelector('figcaption').textContent,
                 leak: getComputedStyle(document.querySelector('.prose p')).fill, imgs: document.querySelectorAll('.prose img').length }; }""")
    assert f['theme'] == 'light' and f['role'] == 'img' and 'p holds 1000' in f['title'] and len(f['desc']) > 20, f
    assert f['cap'].startswith('Figure 1.2a') and f['w'] > 200
    style = json.load(open(os.path.join(ROOT, 'scripts', 'fig-style.json')))
    hexrgb = lambda h: 'rgb(%d, %d, %d)' % tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))  # noqa: E731
    assert f['bg'] == hexrgb(style['light']['ground']), f"light figure ground is {f['bg']}"
    # the theme button turns the figure with the page, and the figure's dark colours are the page's
    page.click('#theme-btn')
    page.wait_for_timeout(700)
    d = page.evaluate("""() => { const s = document.querySelector('.fig-svg.ready').shadowRoot.querySelector('svg'); const cs = getComputedStyle(document.documentElement);
        return { theme: s.getAttribute('data-theme'), bg: getComputedStyle(s.querySelector('.bg')).fill, box: getComputedStyle(s.querySelector('.box')).fill, ink: getComputedStyle(s.querySelector('.box')).stroke,
                 page: ['--ground', '--paper', '--ink'].map(v => cs.getPropertyValue(v).trim()) }; }""")
    assert d['theme'] == 'dark' and [d['bg'], d['box'], d['ink']] == [hexrgb(x) for x in d['page']], f'figure and page disagree in dark: {d}'
    assert [style['dark'][k] for k in ('ground', 'box', 'ink')] == d['page'], 'scripts/fig-style.json and the page palette differ'
    # enlarge: by the picture (pointer) and by the button (keyboard); Escape closes and focus returns
    page.click('.fig-svg.ready')
    page.wait_for_timeout(400)
    assert page.evaluate("document.getElementById('lightbox').open")
    big = page.evaluate("document.querySelector('#lightbox-body .fig-svg').getBoundingClientRect().width")
    assert big > f['w'] * 1.3, f'enlarged {big:.0f}px from {f["w"]:.0f}px'
    assert page.evaluate("document.querySelector('#lightbox-body .fig-svg').shadowRoot.querySelector('svg').getAttribute('data-theme')") == 'dark'
    page.keyboard.press('Escape')
    page.wait_for_timeout(200)
    assert not page.evaluate("document.getElementById('lightbox').open")
    page.focus('.fig-zoom')
    page.keyboard.press('Enter')
    page.wait_for_timeout(300)
    assert page.evaluate("document.getElementById('lightbox').open") and page.evaluate("document.getElementById('lightbox').contains(document.activeElement)")
    page.keyboard.press('Escape')
    page.wait_for_timeout(200)
    assert page.evaluate("document.activeElement.className").find('fig-zoom') >= 0, 'focus should return to the button'
    page.context.close()
    if not HAVE_C:
        return 'SVG inlined, themed, enlarged (the PNG book is not on this machine)'
    page = new_page(browser, base, 'learn-c-8-2', scheme='dark')
    reading(page, 'learn-c-8-2')
    page.evaluate("document.querySelector('figure.fig img').scrollIntoView()")
    page.wait_for_function("(() => { const i = document.querySelector('figure.fig img'); return i.complete && i.naturalWidth > 0; })()")
    p = page.evaluate("""() => { const i = document.querySelector('figure.fig img'), r = i.getBoundingClientRect(); return { alt: i.alt, w: r.width, right: r.right, sheet: document.getElementById('sheet').getBoundingClientRect().right,
        bg: getComputedStyle(i).backgroundColor, src: i.getAttribute('src'), cap: (i.closest('figure').querySelector('figcaption') || {}).textContent || '' }; }""")
    assert len(p['alt']) > 40 and p['w'] > 300 and p['right'] <= p['sheet'] and p['bg'] == 'rgb(255, 255, 255)' and '/learn-c/diagrams/08/' in p['src'], p
    assert p['cap'].startswith('Figure 8.2a'), p['cap'][:40]
    page.click('figure.fig img')
    page.wait_for_timeout(400)
    assert page.evaluate("document.getElementById('lightbox').open && document.querySelector('#lightbox-body img').getBoundingClientRect().width") > p['w']
    page.context.close()
    return 'SVG inlined in its own tree, follows the theme, enlarges; PNG figures framed on white'


# ---------------------------------------------------------------- 10. search
@check('10. search: "/" focuses it; results as you type, grouped by book and chapter; arrows and Enter open at the section')
def t_search(browser, base, shelf):
    page = new_page(browser, base)
    page.keyboard.press('/')
    assert page.evaluate('document.activeElement.id') == 'q'
    page.keyboard.type('variab')
    page.wait_for_selector('.r-hit')
    g = page.evaluate("""() => [...document.querySelectorAll('#results [role=group]')].map(g => ({ head: document.getElementById(g.getAttribute('aria-labelledby')).textContent, hits: [...g.querySelectorAll('.r-hit')].map(h => h.textContent.trim().slice(0, 30)) }))""")
    assert any('Tiny C' in x['head'] and 'First steps' in x['head'] and any(h.startswith('1.3') for h in x['hits']) for x in g), g
    assert page.get_attribute('#q', 'aria-expanded') == 'true' and page.get_attribute('#q', 'aria-activedescendant') == 'hit-0'
    assert page.locator('#results mark').count() >= 1
    # every result belongs to the group it is listed under
    ok = page.evaluate("""() => __us.SR.hits.every((n, i) => { const el = document.getElementById('hit-' + i), head = document.getElementById(el.parentElement.getAttribute('aria-labelledby')).textContent; const ch = n.kind === 'chapter' ? n : n.chapter; return head.includes(ch.title) && head.includes(ch.book.title); })""")
    assert ok, 'a result is under the wrong chapter'
    # a key term finds the section that teaches it, even when its title does not say so
    page.fill('#q', 'idea 7')
    page.wait_for_timeout(250)
    assert page.evaluate("__us.SR.hits[0].id") == 'long-read-1-7' and 'teaches' in page.text_content('#hit-0 .r-term'), page.evaluate("__us.SR.hits.map(n => n.id)")
    page.fill('#q', 'string literal')
    page.wait_for_timeout(250)
    assert 'first-steps-c-1-2' in page.evaluate("__us.SR.hits.map(n => n.id)")
    page.evaluate("document.getElementById('hit-' + __us.SR.hits.findIndex(n => n.id === 'first-steps-c-1-2')).dispatchEvent(new MouseEvent('click', { bubbles: true }))")
    reading(page, 'first-steps-c-1-2')
    page.keyboard.press('/')
    page.keyboard.type('where c came')
    page.wait_for_selector('.r-hit')
    first = page.evaluate("__us.SR.hits[0].id")
    hits = page.evaluate('__us.SR.hits.length')
    page.keyboard.press('ArrowDown')
    assert page.get_attribute('#q', 'aria-activedescendant') == ('hit-1' if hits > 1 else 'hit-0') and page.locator('.r-hit[aria-selected="true"]').count() == 1
    page.keyboard.press('ArrowUp')
    page.keyboard.press('Enter')
    reading(page, first)
    assert first == 'first-steps-c-1-1', first
    assert page.evaluate('location.hash') == '#first-steps-c-1-1' and page.evaluate("document.getElementById('q').value") == ''
    assert not page.is_visible('#results')
    # while reading: the same search, a click opens the section; a planned one goes to the map
    page.keyboard.press('/')
    page.keyboard.type('comparing')
    page.wait_for_selector('.r-hit')
    assert 'planned' in page.text_content('.r-hit')
    page.click('.r-hit')
    page.wait_for_function("document.body.dataset.mode === 'map'")
    assert page.evaluate('__us.S.sel') == 'first-steps-c-2-1'
    # Escape clears it and gives the tree back
    page.keyboard.press('/')
    page.keyboard.type('zzzzqq')
    page.wait_for_timeout(250)
    assert 'Nothing on your shelf matches' in page.text_content('#results')
    page.keyboard.press('Escape')
    assert not page.is_visible('#results') and page.evaluate("document.getElementById('q').value") == ''
    # instant: a query over the whole shelf
    ms = page.evaluate("""() => { const t = performance.now(); for (let i = 0; i < 20; i++) __us.search(['pointer', 'loop', 'array', 'memory'][i % 4]); return (performance.now() - t) / 20; }""")
    assert ms < 30, f'{ms:.1f} ms a query'
    n = page.evaluate('__us.SR.index.length')
    page.context.close()
    return f'{n} entries, {ms:.1f} ms a query'


# ---------------------------------------------------------------- 11. progress
NO_STORAGE = "Object.defineProperty(window, 'localStorage', { get() { throw new Error('storage is off'); } });"


@check('11. progress: opened sections and turned answers stay in localStorage, show in the tree and the contents, copy out and paste in; the page works without storage')
def t_progress(browser, base, shelf):
    page = new_page(browser, base, 'long-read-1-2', clipboard=True)
    reading(page, 'long-read-1-2')
    page.click('.prose details.card >> nth=2 >> summary')
    page.keyboard.press('n')
    reading(page, 'long-read-1-3')
    stored = page.evaluate("Object.keys(localStorage).filter(k => k.endsWith('progress')).map(k => JSON.parse(localStorage.getItem(k)))")
    assert len(stored) == 1 and set(stored[0]['opened']) == {'long-read:1.2', 'long-read:1.3'} and stored[0]['answers'] == {'long-read:1.2': [2]}, stored
    assert 'http' not in json.dumps(stored[0]) and len(json.dumps(stored[0])) < 300, 'progress should hold only what was opened'
    # shown quietly in the contents, and said on the page in one line
    ticks = page.eval_on_selector_all('.toc-list > li > a', 'els => els.map(a => !!a.querySelector(".tick"))')
    assert ticks[:4] == [False, True, True, False], ticks
    assert page.text_content('#toc-prog').strip() == '2 of 16 sections opened'
    assert 'Nothing is sent anywhere' in page.text_content('.privacy')
    page.click('#prog-btn')
    assert 'This stays in this browser. Nothing is sent anywhere.' in page.text_content('#prog-menu')
    assert '2 of ' in page.text_content('#prog-sum') and '1 answer turned over' in page.text_content('#prog-sum')
    page.click('#prog-copy')
    page.wait_for_timeout(250)
    text = page.evaluate('navigator.clipboard.readText()')
    assert text.startswith('understudy-progress {') and 'long-read:1.3' in text
    page.keyboard.press('Escape')
    # restored after a reload; the tree shows it too, and "Continue reading" knows the place
    page.reload()
    page.wait_for_function('window.__us && __us.S.book')
    reading(page, 'long-read-1-3')
    page.evaluate("__us.go('long-read-1-2')")
    reading(page, 'long-read-1-2')
    assert page.evaluate("[...document.querySelectorAll('.prose details.card')].map(d => d.classList.contains('seen'))") == [False, False, True]
    page.evaluate("__us.go('map-long-read-1')")
    page.wait_for_function("document.body.dataset.mode === 'map'")
    page.evaluate("document.querySelector('#ti-long-read-1').getAttribute('aria-expanded') === 'true' || document.querySelector('#ti-long-read-1 > .row').click()")
    page.wait_for_timeout(300)
    tree = page.evaluate("['long-read-1-1', 'long-read-1-2', 'long-read-1-3'].map(id => [!!document.querySelector(`#ti-${id} .tick`), document.getElementById('ti-' + id).getAttribute('aria-label').includes('opened')])")
    assert tree == [[False, False], [True, True], [True, True]], tree
    assert '2/16 read' in page.text_content('#ti-long-read-1 > .row')
    assert page.text_content('#primary').strip() == 'Continue reading' and page.get_attribute('#primary', 'href') == '#long-read-1-2'
    # the beat being read is remembered: Continue reading and a reload both return to it
    page.click('#primary')
    reading(page, 'long-read-1-2')
    page.evaluate("document.getElementById('long-read-1-2-the-trace').scrollIntoView()")
    page.wait_for_function("__us.PR.beat === 'the-trace'")
    page.reload()
    page.wait_for_function('window.__us && __us.S.book')
    reading(page, 'long-read-1-2')
    page.wait_for_timeout(200)
    top = page.evaluate("document.getElementById('long-read-1-2-the-trace').getBoundingClientRect().top")
    assert 40 < top < 160, f'after a reload the beat is at {top}px'
    page.evaluate("__us.go('map-long-read')")
    page.wait_for_function("document.body.dataset.mode === 'map'")
    assert page.get_attribute('#primary', 'href') == '#long-read-1-2-the-trace' and 'Where you stopped' in page.text_content('#detail-body .cmdtext')
    page.context.close()
    # another browser: nothing yet; paste the copied text; it is there, and nothing was lost by pasting twice
    page = new_page(browser, base, 'map-long-read-1', clipboard=True)
    assert page.evaluate('Object.keys(__us.PR.opened).length') == 0
    page.evaluate("t => navigator.clipboard.writeText(t)", text)
    page.click('#prog-btn')
    page.click('#prog-paste')
    page.wait_for_timeout(300)
    assert page.is_visible('#prog-text')
    if not page.input_value('#prog-text'):
        page.fill('#prog-text', text)
    page.click('#prog-add')
    assert page.text_content('#prog-note').startswith('Added 2 sections and 1 answer')
    assert page.evaluate('Object.keys(__us.PR.opened).sort()') == ['long-read:1.2', 'long-read:1.3']
    page.click('#prog-paste')
    page.wait_for_timeout(300)
    page.fill('#prog-text', 'this is not progress')
    page.click('#prog-add')
    assert 'not understudy progress' in page.text_content('#prog-note')
    page.fill('#prog-text', text)
    page.click('#prog-add')
    assert page.text_content('#prog-note').startswith('Added 0 sections and 0 answers')
    page.context.close()
    # no storage at all: the page still reads and still tracks for the visit
    page = new_page(browser, base, 'long-read-1-2', init=NO_STORAGE)
    reading(page, 'long-read-1-2')
    page.keyboard.press('n')
    reading(page, 'long-read-1-3')
    assert page.evaluate('Object.keys(__us.PR.opened).length') == 2
    page.click('#theme-btn')
    page.wait_for_timeout(500)
    page.context.close()
    return 'saved, restored, shown in tree and contents, copied, pasted, merged; works with storage off'


# ---------------------------------------------------------------- 12. file://
@check('12. opened by double-click (file://): a friendly panel with the one command to run, not a broken page')
def t_file(browser, base, shelf):
    ctx = browser.new_context(viewport={'width': 1200, 'height': 800})
    ctx.grant_permissions(['clipboard-read', 'clipboard-write'])
    page = ctx.new_page()
    page.on('console', lambda m: CONSOLE.append(f'file: {m.type}: {m.text}') if m.type in ('error', 'warning') else None)
    page.on('pageerror', lambda e: CONSOLE.append(f'file: pageerror: {e}'))
    page.goto('file://' + os.path.join(shelf, 'index.html') + '#long-read-1-2')
    page.wait_for_function("document.body.dataset.mode === 'blocked'")
    assert page.text_content('#notice h1') == 'One step to open your books'
    assert page.text_content('#n-cmd') == 'python3 scripts/us_reader.py --serve'
    assert 'Nothing is wrong with your books' in page.text_content('#notice')
    assert not page.is_visible('#cols') and not page.is_visible('#sheet') and not page.is_visible('#q')
    page.click('#n-copy')
    page.wait_for_timeout(250)
    copied = page.evaluate('navigator.clipboard.readText().catch(() => "")')
    note = page.text_content('#n-note')
    assert copied == 'python3 scripts/us_reader.py --serve' or 'by hand' in note, f'copy said: {note}'
    page.keyboard.press('Tab')
    ctx.close()
    return 'panel shown, command copyable, nothing else on the page'


# ---------------------------------------------------------------- 13. contrast
CONTRAST_JS = r"""() => {
    const parse = c => { const m = c && c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; };
    const hex = h => ({ r: parseInt(h.slice(1, 3), 16), g: parseInt(h.slice(3, 5), 16), b: parseInt(h.slice(5, 7), 16), a: 1 });
    const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
    const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
    const own = e => {
        if (e.matches('.btn, .panel')) { const c = parse(getComputedStyle(e, '::after').backgroundColor); if (c && c.a > 0) return c; }
        if (e.matches('mark.fresh')) { const c = parse(getComputedStyle(e, '::before').backgroundColor); if (c && c.a > 0) return c; }
        const c = parse(getComputedStyle(e).backgroundColor); return c && c.a > 0 ? c : null; };
    const bgOf = el => { for (let e = el; e && e.nodeType === 1; e = e.parentElement) { const c = own(e); if (c) return c; } return parse(getComputedStyle(document.documentElement).backgroundColor); };
    const visible = el => { if (!el.getClientRects().length) return false; const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || +cs.opacity === 0) return false; if (el.closest('.sr-only, .ghost')) return false; const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
    const stage = document.getElementById('stage'), stageBg = bgOf(stage);
    const svgBg = el => { const node = el.closest('.node'); if (node) { for (const q of ['.rbg', '.hd', '.box']) { const b = node.querySelector(q); if (!b) continue; const f = parse(getComputedStyle(b).fill); if (f && f.a > 0) return f; }
        if (node.classList.contains('sec')) { const k = node.dataset.key; const u = __us.G.layout.rows.get(k); const p = u && document.querySelector(`#g-nodes [data-key="${u.parent.id}"] .box`); if (p) return parse(getComputedStyle(p).fill); } }
        return stageBg; };
    const BODY = '.prose p, .prose li, .prose td, .prose blockquote, .card-body, .desc, .tree .ti > .row .name, #detail-h, .links .bt > span:first-child, .levels li, #graph text.t, #graph text.tc, #graph text.r, .toc-list a, .beats a, .notice-card p, #article h1, .prose h2, .r-title';
    const fails = [], seen = { text: 0, body: 0, ui: 0 };
    let minText = 99, minBody = 99, minUi = 99;
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const els = new Set();
    for (let t = walker.nextNode(); t; t = walker.nextNode()) if (t.textContent.trim() && t.parentElement) els.add(t.parentElement);
    for (const el of els) {
        if (el.closest('script, style, .skip, dialog:not([open])') || !visible(el)) continue;
        const inSvg = el instanceof SVGElement;
        if (inSvg && (el.closest('#graph.overview') || !el.closest('#graph'))) continue;
        const fg = parse(inSvg ? getComputedStyle(el).fill : getComputedStyle(el).color);
        const bg = inSvg ? svgBg(el) : bgOf(el);
        const r = ratio(fg, bg); seen.text++; minText = Math.min(minText, r);
        const body = el.matches(BODY) && !el.closest('.planned, .k, code [class^=hljs]') && !el.matches('.k, .no');
        const what = `"${el.textContent.trim().slice(0, 28)}" <${el.tagName.toLowerCase()} class="${el.getAttribute('class') || ''}">`;
        if (body) { seen.body++; minBody = Math.min(minBody, r); if (r < 7) fails.push(`body text ${r.toFixed(2)} ${what}`); }
        else if (r < 4.5) fails.push(`text ${r.toFixed(2)} ${what}`);
    }
    // the edge of every control and frame against what is around it
    for (const el of document.querySelectorAll('.btn, input[type=search], .panel, .sheet, .code, .tablewrap, details.card, .fig img, .fig-svg, .tree [aria-selected=true] > .row, .toc-list a[aria-current], .menu:not([hidden]), .results:not([hidden]), .prose h2.beat-remember + ul, textarea')) {
        if (!visible(el)) continue;
        const surf = el.matches('.btn, .panel');
        const cs = getComputedStyle(el, surf ? '::after' : null);
        if (parseFloat(cs.borderTopWidth) < 1 || cs.borderTopStyle === 'none') continue;
        const fg = parse(cs.borderTopColor); if (!fg || fg.a === 0) continue;
        const bg = bgOf(el.parentElement);
        // a filled thing is bounded by its fill or by its border, whichever is stronger
        const fill = el.matches('[aria-selected=true] > .row, [aria-current], .btn') ? parse(cs.backgroundColor) : null;
        const r = Math.max(ratio(fg, bg), fill && fill.a > 0 ? ratio(fill, bg) : 0); seen.ui++; minUi = Math.min(minUi, r);
        if (r < 3) fails.push(`edge ${r.toFixed(2)} ${el.id || el.className}`);
    }
    if (stage.getClientRects().length) {
        for (const box of document.querySelectorAll('#g-nodes .node .box, #g-bands .bandbox')) {
            const cs = getComputedStyle(box); if (cs.stroke === 'none' || parseFloat(cs.strokeWidth) === 0) continue;
            const sel = box.closest('.node.sel');
            const r = Math.max(ratio(parse(cs.stroke), stageBg), sel ? ratio(parse(cs.fill), stageBg) : 0); seen.ui++; minUi = Math.min(minUi, r);
            if (r < 3) fails.push(`graph box ${r.toFixed(2)} ${box.parentElement.getAttribute('class')}`);
        }
        for (const p of document.querySelectorAll('#g-edges path')) { const r = ratio(parse(getComputedStyle(p).stroke), stageBg); seen.ui++; minUi = Math.min(minUi, r); if (r < 3) fails.push(`edge line ${r.toFixed(2)} ${p.getAttribute('class')}`); }
    }
    const root = getComputedStyle(document.documentElement);
    const ring = hex(root.getPropertyValue('--blue').trim());
    for (const v of ['--paper', '--ground', '--sunken']) { const r = ratio(ring, hex(root.getPropertyValue(v).trim())); minUi = Math.min(minUi, r); if (r < 3) fails.push(`focus ring on ${v} ${r.toFixed(2)}`); }
    return { fails, seen, minText, minBody, minUi };
}"""


@check('13. contrast, measured: reading text 7:1, other text 4.5:1, edges, rings and lines 3:1; map and chapter, light and dark, every state')
def t_contrast(browser, base, shelf):
    notes = []

    def measure(page, label):
        page.mouse.move(0, 0)
        page.wait_for_timeout(280)
        r = page.evaluate(CONTRAST_JS)
        assert not r['fails'], f'{label}: ' + '; '.join(r['fails'][:5])
        notes.append((r['minBody'], r['minText'], r['minUi']))

    for scheme in ('light', 'dark'):
        for w, h in ((1440, 900), (390, 844)):
            tag = f'{scheme} {w}px'
            page = new_page(browser, base, 'first-steps-c-1-2', w=w, h=h, scheme=scheme)
            reading(page, 'first-steps-c-1-2')
            assert page.evaluate('document.documentElement.dataset.theme') == scheme
            measure(page, tag + ' chapter top')
            page.click('.prose details.card >> nth=0 >> summary')
            page.evaluate("document.querySelector('.beat-the-code').scrollIntoView()")
            measure(page, tag + ' code and trace')
            page.evaluate("document.querySelector('.beat-check').scrollIntoView()")
            measure(page, tag + ' answers and pager')
            page.evaluate('scrollTo(0, 0)')
            if w > 700:
                page.keyboard.press('/')
                page.keyboard.type('print')
                page.wait_for_selector('.r-hit')
                measure(page, tag + ' search results')
                page.keyboard.press('Escape')
                page.click('#prog-btn')
                page.click('#prog-paste')
                measure(page, tag + ' progress menu')
                page.keyboard.press('Escape')
            else:
                page.click('#toc-btn')
                page.wait_for_timeout(300)
                measure(page, tag + ' contents drawer')
                page.keyboard.press('Escape')
            if HAVE_C:
                page.evaluate("__us.go('learn-c-8-4')")
                reading(page, 'learn-c-8-4')
                measure(page, tag + ' a real chapter')
            # the map
            page.evaluate("__us.go('map-first-steps-c-2-2')")
            page.wait_for_function("document.body.dataset.mode === 'map'")
            page.wait_for_timeout(500)
            if w > 700:
                measure(page, tag + ' map: section selected, needs and unlocks')
                page.fill('#q', 'choi')
                page.wait_for_timeout(200)
                measure(page, tag + ' map: filter marks')
                page.press('#q', 'Escape')
                page.hover('#fit-all')
                measure(page, tag + ' map: hover')
            else:
                for tab in ('tree', 'graph', 'detail'):
                    page.click(f'.tabs [data-tab={tab}]')
                    measure(page, f'{tag} map: {tab}')
            page.context.close()
    # the notices
    for scheme in ('light', 'dark'):
        ctx = browser.new_context(viewport={'width': 900, 'height': 700}, color_scheme=scheme)
        page = ctx.new_page()
        page.goto('file://' + os.path.join(shelf, 'index.html'))
        page.wait_for_function("document.body.dataset.mode === 'blocked'")
        measure(page, scheme + ' notice')
        ctx.close()
    return f'{len(notes)} states measured; minimum reading text {min(n[0] for n in notes):.1f}, other text {min(n[1] for n in notes):.1f}, edges {min(n[2] for n in notes):.1f}'


# ---------------------------------------------------------------- 14. viewports
MATRIX = [  # w, h, device scale, touch
    (320, 568, 2, True), (360, 800, 2, True), (390, 844, 3, True), (430, 932, 3, True), (844, 390, 3, True),
    (768, 1024, 2, True), (1024, 768, 1, False), (1280, 720, 1, False), (1366, 768, 1, False), (1440, 900, 1, False),
    (1920, 1080, 1, False), (2560, 1440, 1, False), (720, 450, 2, False),  # the last is 1440x900 at 200% zoom
]

GEOMETRY_JS = """([w, h, touch]) => {
    const vis = e => { if (!e.getClientRects().length) return false; const cs = getComputedStyle(e); if (cs.visibility === 'hidden' || e.closest('[hidden], .sr-only, .ghost')) return false; const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
    const R = e => e.getBoundingClientRect();
    const name = e => e.id || e.textContent.trim().slice(0, 14) || e.getAttribute('aria-label') || e.className;
    const fixed = [...document.querySelectorAll('.bar button, .bar input, .bar a.brand, .tabs button, .panel-head button, .gfoot button, [role=separator]')].filter(vis).filter(e => !e.closest('.menu'));
    const out = { outside: [], overlap: [], small: [], tiny: [], sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth };
    for (const e of fixed) { const r = R(e); if (r.left < -0.5 || r.top < -0.5 || r.right > w + 0.5 || r.bottom > h + 0.5) out.outside.push(name(e) + ` ${Math.round(r.left)},${Math.round(r.top)},${Math.round(r.right)},${Math.round(r.bottom)}`); }
    for (let i = 0; i < fixed.length; i++) for (let j = i + 1; j < fixed.length; j++) {
        const a = R(fixed[i]), b = R(fixed[j]); const ix = Math.min(a.right, b.right) - Math.max(a.left, b.left), iy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        if (ix > 3 && iy > 3) out.overlap.push(name(fixed[i]) + ' / ' + name(fixed[j])); }
    const targets = [...document.querySelectorAll('button, input[type=search], .tree .row, summary, .pager a, .toc-list > li > a, a.brand, .beats a, .toc-book, .toc-other')].filter(vis).filter(e => !e.classList.contains('fig-zoom'));
    const min = touch ? 43.5 : 23.5;
    for (const e of targets) { const r = R(e); if (r.width < min || r.height < min) out.small.push(name(e) + ` ${Math.round(r.width)}x${Math.round(r.height)}`); }
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let t = walker.nextNode(); t; t = walker.nextNode()) { const el = t.parentElement; if (!t.textContent.trim() || !el || el.closest('svg, script, style, .sr-only, .skip') || !vis(el)) continue;
        const fs = parseFloat(getComputedStyle(el).fontSize); if (fs < 13) out.tiny.push(`${fs}px "${t.textContent.trim().slice(0, 16)}"`); }
    const shown = q => { const e = document.querySelector(q); return !!e && vis(e); };
    out.layout = { tabs: shown('.tabs'), tree: shown('#treepanel .tree-wrap'), graph: shown('#stage'), detail: shown('#detail-body'), detailRail: shown('#detail .rail-btn'), seps: shown('#sep-tree'), status: shown('#status'),
                   cols: R(document.getElementById('cols')).height, toc: shown('#toc'), otp: shown('#otp'), tocBtn: shown('#toc-btn'), sheet: shown('#sheet'), search: shown('#q'), where: shown('#where') };
    const sheet = document.getElementById('sheet'), p = document.querySelector('.prose > p');
    if (shown('#sheet') && p) { const sr = R(sheet), cs = getComputedStyle(p); out.read = { left: sr.left, right: sr.right, text: R(p).width, font: parseFloat(cs.fontSize), lh: parseFloat(cs.lineHeight) / parseFloat(cs.fontSize), bar: R(document.querySelector('.bar')).height }; }
    return out; }"""


def geometry(page, w, h, touch, tag):
    g = page.evaluate(GEOMETRY_JS, [w, h, touch])
    assert g['sw'] <= g['cw'], f'{tag}: the page scrolls sideways ({g["sw"]} > {g["cw"]})'
    assert not g['outside'], f'{tag}: controls outside the window: {g["outside"][:3]}'
    assert not g['overlap'], f'{tag}: controls overlap: {g["overlap"][:3]}'
    assert not g['tiny'], f'{tag}: text under 13 px: {g["tiny"][:3]}'
    assert not g['small'], f'{tag}: targets under {44 if touch else 24} px: {g["small"][:4]}'
    return g


@check('14. viewport matrix, 13 sizes from 320 to 2560 and phone landscape, map and chapter: no sideways scroll, controls inside and apart, text >= 13 px, 44 px on touch, forks as designed')
def t_matrix(browser, base, shelf):
    done = []
    for w, h, dsf, touch in MATRIX:
        page = new_page(browser, base, 'map-first-steps-c-1-3', w=w, h=h, dsf=dsf, touch=touch, settle=500)
        for st in (['tree', 'graph', 'detail'] if w < 768 else ['open']):
            if w < 768:
                page.click(f'.tabs [data-tab={st}]')
                page.wait_for_timeout(300)
            tag = f'{w}x{h}{" touch" if touch else ""} map {st}'
            L = geometry(page, w, h, touch, tag)['layout']
            if w < 768:
                assert L['tabs'] and L[st], f'{tag}: tabs or the {st} panel missing: {L}'
            elif w < 1280:
                assert L['tree'] and L['graph'] and L['detailRail'] and not L['tabs'], f'{tag}: expected tree, graph and a detail rail: {L}'
            else:
                assert L['tree'] and L['graph'] and L['detail'] and L['seps'], f'{tag}: expected three panels and dividers: {L}'
            if h < 500:
                assert not L['status'] and L['cols'] >= h * 0.6, f'{tag}: work area {L["cols"]:.0f} of {h}'
        if 768 <= w < 1280:  # the rail opens on demand
            page.click('#detail .rail-btn')
            page.wait_for_timeout(150)
            g = geometry(page, w, h, touch, f'{w}x{h} map, detail opened')
            assert g['layout']['detail']
        # the chapter, at the same size
        page.evaluate("__us.go('first-steps-c-1-2')")
        reading(page, 'first-steps-c-1-2')
        page.wait_for_timeout(250)
        tag = f'{w}x{h}{" touch" if touch else ""} chapter'
        for where in ('top', '.beat-the-code', '.beat-check', 'end'):
            if where == 'end':
                page.evaluate('scrollTo(0, document.documentElement.scrollHeight)')
            elif where != 'top':
                page.evaluate(f"document.querySelector('{where}').scrollIntoView()")
            page.wait_for_timeout(120)
            g = geometry(page, w, h, touch, f'{tag} at {where}')
        L, rd = g['layout'], g['read']
        assert L['sheet'] and not L['tabs'] and not L['tree'] and not L['status'], f'{tag}: {L}'
        if HAVE_C:  # the longest titles on the shelf must fit the bar and the page too
            page.evaluate("__us.go('learn-c-11-1')")
            reading(page, 'learn-c-11-1')
            page.wait_for_timeout(150)
            geometry(page, w, h, touch, f'{tag}, long titles')
            page.evaluate("__us.go('first-steps-c-1-2')")
            reading(page, 'first-steps-c-1-2')
        if w >= 1280:
            assert L['toc'] and L['otp'] and not L['tocBtn'], f'{tag}: expected contents, sheet and On this page: {L}'
        elif w >= 1024:
            assert L['toc'] and not L['otp'] and not L['tocBtn'], f'{tag}: expected contents and sheet: {L}'
        else:
            assert not L['toc'] and L['tocBtn'], f'{tag}: expected the contents behind a button: {L}'
        assert L['search'] == (w >= 768) and L['where'] == (w >= 1024), f'{tag}: search/where {L}'
        assert rd['font'] >= 17 and 1.5 <= rd['lh'] <= 1.75, f'{tag}: reading type {rd}'
        assert rd['text'] >= min(w - 60, 280) * 0.9, f'{tag}: the text column is {rd["text"]:.0f}px'
        assert rd['text'] / rd['font'] <= 33, f'{tag}: the measure is {rd["text"] / rd["font"]:.1f}em'
        assert rd['bar'] <= max(64, h * 0.17), f'{tag}: the bar takes {rd["bar"]:.0f}px of {h}'
        if w < 1024:  # the drawer opens, holds the contents, and closes
            page.click('#toc-btn')
            page.wait_for_timeout(350)
            d = page.evaluate("""() => { const r = document.getElementById('toc').getBoundingClientRect(); return { vis: r.width > 0, right: r.right, inert: document.getElementById('sheet').inert, cur: document.activeElement.getAttribute('aria-current'), beats: document.querySelectorAll('#toc-beats a').length }; }""")
            assert d['vis'] and d['right'] <= w and d['inert'] and d['cur'] == 'page' and d['beats'] == 8, f'{tag}: drawer {d}'
            geometry(page, w, h, touch, f'{tag} drawer')
            page.keyboard.press('Escape')
            page.wait_for_timeout(100)
            assert page.evaluate("document.body.dataset.toc") == 'closed' and page.evaluate("document.activeElement.id") == 'toc-btn'
        if w < 768:   # the search row folds away while reading, and comes back on its button
            page.click('#search-btn')
            page.wait_for_timeout(200)
            assert page.is_visible('#q') and page.evaluate("document.activeElement.id") == 'q'
            page.keyboard.type('vari')
            page.wait_for_selector('.r-hit')
            geometry(page, w, h, touch, f'{tag} search')
            r = page.evaluate("document.getElementById('results').getBoundingClientRect().toJSON()")
            assert r['left'] >= 0 and r['right'] <= w and r['bottom'] <= h, f'{tag}: results {r}'
            page.keyboard.press('Escape')
        done.append(f'{w}x{h}')
        page.context.close()
    return f'{len(done)} sizes, map and chapter'


# ---------------------------------------------------------------- 15. keyboard
@check('15. keyboard only: from the top of the map into a chapter, through it, and back to the map; focus always visible and never lost')
def t_keyboard(browser, base, shelf):
    page = new_page(browser, base)
    page.evaluate('localStorage.clear()')
    page.reload()
    page.wait_for_function('window.__us && __us.S.book')
    page.wait_for_timeout(600)
    focus = lambda: page.evaluate("(() => { const a = document.activeElement; return a.id || a.className || a.tagName; })()")  # noqa: E731
    ring = lambda: page.evaluate("""(() => { const a = document.activeElement; const t = a.matches('[role=treeitem]') ? a.firstElementChild : a; const cs = getComputedStyle(t); return cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) >= 2; })()""")  # noqa: E731
    page.keyboard.press('Tab')
    assert focus() == 'skip' and page.evaluate("document.getElementById('skip').getBoundingClientRect().top") >= 0
    page.keyboard.press('Enter')
    assert focus() == 'ti-shelf' and ring(), 'the skip link should land on the tree'
    # down to the first chapter of the first book, open it, down to its second section
    for _ in range(40):
        if focus() == 'ti-first-steps-c-1':
            break
        page.keyboard.press('ArrowDown')
    assert focus() == 'ti-first-steps-c-1'
    page.keyboard.press('ArrowRight')
    page.keyboard.press('ArrowDown')
    page.keyboard.press('ArrowDown')
    assert focus() == 'ti-first-steps-c-1-2' and ring()
    page.keyboard.press('Enter')                      # select it: the detail panel shows Read
    assert page.evaluate('__us.S.sel') == 'first-steps-c-1-2' and page.get_attribute('#primary', 'href') == '#first-steps-c-1-2'
    # the long way: Tab to the Read link in the detail panel
    hops = 0
    while focus() != 'primary' and hops < 60:
        page.keyboard.press('Tab')
        hops += 1
        assert page.evaluate('document.activeElement !== document.body'), 'focus fell to the page'
    assert focus() == 'primary' and ring(), f'Read not reached by Tab ({hops} stops)'
    page.keyboard.press('Enter')
    reading(page, 'first-steps-c-1-2')
    assert page.evaluate("document.activeElement === document.querySelector('#article h1')"), 'focus should be on the section heading'
    # through the page: every stop is visible under the bar, the copy button and a card work
    seen = set()
    for _ in range(40):
        page.keyboard.press('Tab')
        info = page.evaluate("""(() => { const a = document.activeElement, r = a.getBoundingClientRect(), bar = document.querySelector('.bar').getBoundingClientRect().bottom;
            return { what: a.matches('summary') ? 'summary' : a.matches('button.copy') ? 'copy' : a.matches('.pager a') ? 'pager' : a.matches('.beats a') ? 'beat' : a.matches('a.xref') ? 'xref' : a.matches('pre, .tablewrap') ? 'scroller' : a.id || a.className,
                     ok: a === document.body || (r.top >= bar - 1 && r.bottom <= innerHeight + 4) || r.height > innerHeight - bar }; })()""")
        assert info['ok'], f"focus on {info['what']} is hidden under the bar or off the page"
        seen.add(info['what'])
        if info['what'] == 'summary':
            page.keyboard.press(' ')
            page.wait_for_timeout(100)
            assert page.evaluate("document.activeElement.parentElement.open"), 'Space should turn the card'
            break
    assert {'xref', 'copy', 'scroller', 'summary'} <= seen, f'stops met: {sorted(seen)}'
    # next section and back with the keys; then the map, by the brand link
    page.keyboard.press('n')
    reading(page, 'first-steps-c-1-3')
    page.keyboard.press('p')
    reading(page, 'first-steps-c-1-2')
    page.focus('a.brand')
    assert ring()
    page.keyboard.press('Enter')
    page.wait_for_function("document.body.dataset.mode === 'map'")
    page.wait_for_timeout(200)
    assert focus() == 'ti-first-steps-c-1-2', f'back on the map, focus is on {focus()}'
    # Enter again on the selected section opens it at once; the browser's Back returns
    page.keyboard.press('Enter')
    reading(page, 'first-steps-c-1-2')
    page.go_back()
    page.wait_for_function("document.body.dataset.mode === 'map'")
    # single-key shortcuts can be turned off (WCAG 2.1.4)
    page.click('#prog-btn')
    page.uncheck('#keys-on')
    page.keyboard.press('Escape')
    page.evaluate('document.activeElement.blur()')
    page.keyboard.press('/')
    assert page.evaluate('document.activeElement.id') != 'q', '"/" should do nothing once shortcuts are off'
    page.context.close()
    return f'skip link, tree, detail, Read, {len(seen)} kinds of stop in the text, n/p, back to the map'


# ---------------------------------------------------------------- 16. motion
ANIMS_JS = """() => document.getAnimations().filter(a => a.playState === 'running').map(a => { const kf = a.effect.getKeyframes(); const props = new Set(); for (const k of kf) for (const p of Object.keys(k)) if (!['offset', 'easing', 'composite', 'computedOffset'].includes(p)) props.add(p);
    const t = a.effect.getComputedTiming(); return { props: [...props], dur: t.duration + t.delay, on: (a.effect.target && (a.effect.target.id || a.effect.target.className && String(a.effect.target.className.baseVal || a.effect.target.className))) || '' }; })"""


@check('16. reduced motion: nothing travels, scales or turns, on the map or in a chapter; what remains is colour or opacity within 120 ms')
def t_motion(browser, base, shelf):
    seen = []
    page = new_page(browser, base, 'long-read-1-2', reduced='reduce')
    reading(page, 'long-read-1-2')

    def act(label, fn):
        fn()
        anims = page.evaluate(ANIMS_JS)
        for a in anims:
            moving = [p for p in a['props'] if p in ('transform', 'strokeDashoffset', 'clipPath', 'translate', 'scale', 'rotate')]
            assert not moving, f'{label}: {a["on"]} animates {moving}'
            assert a['dur'] <= 121, f'{label}: {a["on"]} runs {a["dur"]} ms'
        seen.append(label)
        page.wait_for_timeout(200)
    act('turn a card', lambda: page.click('.prose details.card >> nth=0 >> summary'))
    act('next section', lambda: page.click('.pager .next'))
    act('a beat', lambda: page.click('#otp .beats a >> nth=4'))
    assert page.evaluate("getComputedStyle(document.documentElement).scrollBehavior") == 'auto'
    act('theme', lambda: page.click('#theme-btn'))
    act('to the map', lambda: page.click('a.brand'))
    page.wait_for_function("document.body.dataset.mode === 'map'")
    act('open a chapter row', lambda: page.click('#ti-long-read-1 > .row'))
    act('fit all', lambda: page.click('#fit-all'))
    act('filter', lambda: page.fill('#q', 'lesson'))
    page.context.close()
    page = new_page(browser, base, 'first-steps-c-1-2', w=390, h=844, reduced='reduce', touch=True)
    reading(page, 'first-steps-c-1-2')
    act('contents drawer', lambda: page.click('#toc-btn'))
    page.keyboard.press('Escape')
    act('enlarge a figure', lambda: page.click('.fig-svg.ready'))
    page.context.close()
    # with motion allowed the drawer and the card do move, briefly
    page = new_page(browser, base, 'first-steps-c-1-2', w=390, h=844, touch=True)
    reading(page, 'first-steps-c-1-2')
    page.click('#toc-btn')
    a = page.evaluate(ANIMS_JS)
    assert any('transform' in x['props'] and x['dur'] <= 300 for x in a), f'the drawer should slide in, within 300 ms: {a}'
    rules = page.evaluate("""() => { const bad = []; for (const sh of document.styleSheets) for (const r of sh.cssRules) { const walk = rule => { if (rule.cssRules) for (const x of rule.cssRules) walk(x);
        if (rule.style && /(^|[ ,])all( |,|$)/.test(rule.style.transitionProperty || '')) bad.push(rule.selectorText); }; walk(r); } return bad; }""")
    assert not rules, f'"transition: all" in {rules[:3]}'
    page.context.close()
    return ', '.join(seen)


# ---------------------------------------------------------------- 17. print
@check('17. print: the current chapter, whole and clean: no bars or buttons, black on white in either theme, code wraps, nothing left behind afterwards')
def t_print(browser, base, shelf):
    page = new_page(browser, base, 'first-steps-c-1-2', scheme='dark')
    reading(page, 'first-steps-c-1-2')
    page.wait_for_selector('.fig-svg.ready')
    before = page.evaluate('document.getElementById("article").childElementCount')
    page.emulate_media(media='print')
    page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
    page.wait_for_timeout(300)
    p = page.evaluate("""() => { const vis = q => [...document.querySelectorAll(q)].some(e => e.getClientRects().length > 0); const cs = getComputedStyle(document.querySelector('.prose p'));
        const heads = [...document.querySelectorAll('#article .sec-head h1')].map(h => h.textContent.trim().slice(0, 3));
        const pre = document.querySelector('.code.prog pre code'), fig = document.querySelector('.fig-svg.ready');
        return { chrome: ['.bar', '.toc', '.otp', '.pager', 'button.copy', '.fig-zoom', '.privacy', '.status'].filter(vis), heads, color: cs.color, bg: getComputedStyle(document.body).backgroundColor,
                 sheetBorder: getComputedStyle(document.getElementById('sheet')).borderTopWidth, wrap: getComputedStyle(pre).whiteSpace, overflow: getComputedStyle(pre.parentElement).overflowX,
                 fig: fig.shadowRoot.querySelector('svg').getAttribute('data-theme'), comments: document.getElementById('article').innerHTML.includes('<!--') }; }""")
    assert not p['chrome'], f'still printing: {p["chrome"]}'
    assert p['heads'] == ['1.1', '1.2', '1.3', '1.4'], f'sections printed: {p["heads"]}'
    assert p['color'] == 'rgb(0, 0, 0)' and p['bg'] == 'rgb(255, 255, 255)' and p['sheetBorder'] == '0px', p
    assert p['wrap'] == 'pre-wrap' and p['overflow'] == 'visible' and p['fig'] == 'light' and not p['comments'], p
    pdf = page.pdf(format='A4')
    assert len(pdf) > 20000 and pdf[:4] == b'%PDF'
    page.evaluate("window.dispatchEvent(new Event('afterprint'))")
    page.emulate_media(media='screen')
    page.wait_for_timeout(150)
    after = page.evaluate("""() => ({ n: document.getElementById('article').childElementCount, extra: document.querySelectorAll('.print-only').length, fig: document.querySelector('.fig-svg.ready').shadowRoot.querySelector('svg').getAttribute('data-theme') })""")
    assert after == {'n': before, 'extra': 0, 'fig': 'dark'}, after
    assert page.locator('#print-btn').count() == 1
    page.context.close()
    return f'4 sections on paper, {len(pdf) // 1024} KB PDF'


# ---------------------------------------------------------------- 18. offline
@check('18. offline and plug-and-play: one file, no request leaves the shelf, system fonts, no alert/confirm/prompt, clipboard only on a click; served from a sub-folder as GitHub Pages does')
def t_offline(browser, base, shelf):
    html = open(HTML, encoding='utf-8').read()
    ours = html.split('<script>')[-1]                                     # our own script, after the two vendored ones
    assert not re.search(r'\b(alert|confirm|prompt)\s*\(', ours), 'alert/confirm/prompt in the page script'
    assert not re.search(r'<(link|script|img|iframe)[^>]+(src|href)=["\']https?:', html), 'the page loads something from another site'
    css = html.split('</style>')[0]
    assert '@font-face' not in html and 'woff' not in html and not re.search(r'url\((?!#)', css), 'fonts or url() in the styles'
    assert '@import' not in css
    # every use of the clipboard sits in a function that only a click handler calls
    uses = [m.start() for m in re.finditer(r'navigator\.clipboard', ours)]
    assert uses and len(uses) <= 6
    for fn in ('copyText(', "addEventListener('click'"):
        assert fn in ours
    src = ''.join(open(os.path.join(ROOT, 'reader', 'src', n), encoding='utf-8').read() for n in ('core.js', 'map.js', 'read.js', 'app.js'))
    for m in re.finditer(r'navigator\.clipboard\.(writeText|readText)\(', src):
        fn = src[:m.start()].rsplit('\nasync function ', 1)[-1][:40] if '\nasync function ' in src[:m.start()][-900:] else src[:m.start()].rsplit("addEventListener('click'", 1)[-1][:40]
        near = src[max(0, m.start() - 900):m.start()]
        assert 'async function copyText' in near or "addEventListener('click', async" in near, f'clipboard used outside a click path near: {fn}'
        assert 'try {' in near, 'clipboard call without try/catch'
    calls = [m.group(0) for m in re.finditer(r'copyText\(', src)]
    assert len(calls) >= 5
    # a full visit, watching the network: the page and the book files only
    FOREIGN.clear()
    reqs = []
    page = new_page(browser, base, settle=300)
    page.on('request', lambda r: reqs.append(r.url[len(base):]))
    page.evaluate("__us.go('first-steps-c-1-2')")
    reading(page, 'first-steps-c-1-2')
    page.wait_for_selector('.fig-svg.ready')
    page.keyboard.press('/')
    page.keyboard.type('print')
    page.wait_for_selector('.r-hit')
    page.keyboard.press('Escape')
    page.evaluate("__us.go('first-steps-c-1-3')")
    reading(page, 'first-steps-c-1-3')
    page.wait_for_timeout(300)
    assert not FOREIGN, f'requests left the shelf: {FOREIGN[:3]}'
    assert reqs.count('/first-steps-c/chapters/01-first-steps.md') == 1, f'the chapter file should be fetched once: {reqs}'
    assert all(not r.startswith('/long-read') and not r.startswith('/learn-c') for r in reqs), 'a chapter that was not opened was fetched'
    posts = page.evaluate("performance.getEntriesByType('resource').map(e => e.name)")
    assert all(u.startswith(base) for u in posts)
    page.context.close()
    # GitHub Pages: the shelf lives in a sub-folder of the site, opened by its folder address
    parent = os.path.dirname(shelf)
    b2 = serve(parent)
    page = new_page(browser, b2, 'first-steps-c-1-2', path='/' + os.path.basename(shelf) + '/')
    reading(page, 'first-steps-c-1-2')
    page.wait_for_selector('.fig-svg.ready')
    assert page.evaluate('location.pathname').endswith('/' + os.path.basename(shelf) + '/')
    page.context.close()
    return f'{len(reqs)} requests in a visit, all to the shelf; works from a sub-folder'


# ---------------------------------------------------------------- 19. the script
@check('19. scripts/us_reader.py: copies the page beside several books, refreshes the index, serves it, and the served page reads')
def t_script(browser, base, shelf):
    home = make_shelf(books=(), index=False)
    try:
        shutil.copytree(os.path.join(ROOT, 'scripts'), os.path.join(home, 'scripts'), ignore=shutil.ignore_patterns('__pycache__'))
        os.makedirs(os.path.join(home, 'reader'))
        shutil.copy(HTML, os.path.join(home, 'reader', 'index.html'))
        shutil.copy(os.path.join(ROOT, 'understudy.yaml'), home)
        book = os.path.join(home, 'book')
        os.makedirs(book)
        for name in ('first-steps-c', 'long-read'):
            shutil.copytree(os.path.join(shelf, name), os.path.join(book, name))
        env = dict(os.environ, PYTHONUNBUFFERED='1')
        env.pop('UNDERSTUDY_PRIVATE', None)
        res = subprocess.run([sys.executable, os.path.join(home, 'scripts', 'us_reader.py')], capture_output=True, text=True, env=env, timeout=60)
        assert res.returncode == 0, res.stdout + res.stderr
        assert open(os.path.join(book, 'index.html'), encoding='utf-8').read() == open(HTML, encoding='utf-8').read()
        assert os.path.exists(os.path.join(book, '.nojekyll'))
        assert [b['name'] for b in manifest(book)['books']] == ['first-steps-c', 'long-read']
        proc = subprocess.Popen([sys.executable, os.path.join(home, 'scripts', 'us_reader.py'), '--serve'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
        SERVERS.append(proc)
        addr = None
        for _ in range(40):
            line = proc.stdout.readline()
            m = re.search(r'open (http://localhost:\d+)', line)
            if m:
                addr = m.group(1)
                break
        assert addr, 'us_reader.py --serve did not print an address'
        page = new_page(browser, addr.replace('localhost', '127.0.0.1'), 'long-read-1-1', path='/')
        reading(page, 'long-read-1-1')
        assert page.evaluate('__us.S.book.books.length') == 2
        page.context.close()
        proc.terminate()
    finally:
        shutil.rmtree(home, ignore_errors=True)
    return f'two books served at {addr}'


# ---------------------------------------------------------------- 20. budgets
@check('20. budgets on this machine: index.html under 450 KB; the map of the 11-chapter book paints in under a second; a 30,000-word chapter opens and scrolls smoothly')
def t_budget(browser, base, shelf):
    size = os.path.getsize(HTML)
    assert size < 450 * 1024, f'index.html is {size / 1024:.0f} KB'
    words = sum(c['words'] for b in manifest(shelf)['books'] if b['name'] == 'long-read' for p in b['parts'] for c in p['chapters'])
    assert words >= 30000, f'the long chapter has {words} words'
    # first paint of the map, cold (a new browser profile each time), the big book selected
    times = []
    for _ in range(3):
        ctx = browser.new_context(viewport={'width': 1366, 'height': 768})
        page = ctx.new_page()
        page.on('pageerror', lambda e: CONSOLE.append(f'pageerror: {e}'))
        page.goto(base + '/index.html#map-' + BIG)
        page.wait_for_function("window.__us && __us.S.book && document.querySelectorAll('#tree .ti').length > 5 && document.querySelectorAll('#g-nodes .node').length > 2")
        t = page.evaluate("""() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => { const p = performance.getEntriesByType('paint').find(e => e.name === 'first-contentful-paint');
            r({ fcp: p ? p.startTime : -1, ready: performance.now(), layout: __us.G.lastMs, boxes: document.querySelectorAll('#g-nodes .node').length }); })))""")
        times.append(t)
        ctx.close()
    ready = sorted(t['ready'] for t in times)[1]
    fcp = sorted(t['fcp'] for t in times)[1]
    assert 0 <= fcp < 1000 and ready < 1000, f'first paint {fcp:.0f} ms, map drawn {ready:.0f} ms'
    assert times[0]['boxes'] >= (12 if HAVE_C else 3)
    # the same on a slow machine: the processor held to a quarter of its speed
    ctx = browser.new_context(viewport={'width': 1366, 'height': 768})
    page = ctx.new_page()
    cdp = ctx.new_cdp_session(page)
    cdp.send('Emulation.setCPUThrottlingRate', {'rate': 4})
    page.goto(base + '/index.html#map-' + BIG)
    page.wait_for_function("window.__us && __us.S.book && document.querySelectorAll('#g-nodes .node').length > 2")
    slow = page.evaluate("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => r(performance.now()))))")
    # the long chapter, still at a quarter speed: open a section, then scroll it
    opened = page.evaluate("""() => new Promise(r => { const t = performance.now(); __us.go('long-read-1-9');
        const wait = () => (__us.R.sec && __us.R.sec.id === 'long-read-1-9' && document.querySelector('#article h1')) ? requestAnimationFrame(() => r(performance.now() - t)) : setTimeout(wait, 4); wait(); })""")
    again = page.evaluate("""() => new Promise(r => { const t = performance.now(); __us.go('long-read-1-10');
        const wait = () => (__us.R.sec && __us.R.sec.id === 'long-read-1-10') ? requestAnimationFrame(() => r(performance.now() - t)) : setTimeout(wait, 4); wait(); })""")
    nodes = page.evaluate("document.getElementById('article').querySelectorAll('*').length")
    frames = page.evaluate("""() => new Promise(r => { const gaps = []; let last = performance.now(), n = 0; const max = document.documentElement.scrollHeight - innerHeight;
        const step = now => { gaps.push(now - last); last = now; scrollTo(0, max * (++n / 90)); if (n < 90) requestAnimationFrame(step); else r({ worst: Math.max(...gaps.slice(2)), mean: gaps.slice(2).reduce((a, b) => a + b, 0) / (gaps.length - 2), max }); };
        requestAnimationFrame(step); })""")
    cdp.send('Emulation.setCPUThrottlingRate', {'rate': 1})
    ctx.close()
    assert slow < 2500, f'at quarter speed the map takes {slow:.0f} ms'
    assert opened < 1500 and again < 600, f'at quarter speed a section of the long chapter opens in {opened:.0f} ms (first) and {again:.0f} ms'
    assert nodes < 1500, f'{nodes} elements for one section: only the section in view should be rendered'
    assert frames['worst'] < 100 and frames['mean'] < 34, f'scrolling: worst frame {frames["worst"]:.0f} ms, mean {frames["mean"]:.1f} ms'
    return (f'{size / 1024:.0f} KB; first paint {fcp:.0f} ms, map drawn {ready:.0f} ms ({slow:.0f} ms at quarter speed); '
            f'{words} words: section opens in {opened:.0f} ms then {again:.0f} ms, scroll worst frame {frames["worst"]:.0f} ms, all at quarter speed')


# ---------------------------------------------------------------- 21. odd shelves
ODD_MD = """# Chapter 1: Odd

<!-- contents -->
- [1.1 x](#11-x)
<!-- /contents -->

Text before the first section.

## 1.1 Written `code` one

### The question

A header named <stdio.h> typed without backticks, and `<!--` in inline code.

<!-- fig: id=never
title: this must never show
kind: memory
-->

<script>window.__pwned = 1</script>
<img src="x-missing.png" onerror="window.__pwned = 2">

[a bad link](javascript:window.__pwned=3) and [a good one](https://example.com/page).

![a picture on another site](https://example.com/x.png)

![a drawing that misbehaves](evil.svg)

```html
<!-- this comment is part of a program and must show -->
<p>hello</p>
```

<details>
<summary>Outer</summary>

Outer answer.

<details>
<summary>Inner</summary>

Inner answer.

</details>

</details>

## 1.2 Planned two
"""


def odd_shelf():
    import random
    shelf = make_shelf(books=())
    os.makedirs(os.path.join(shelf, 'odd', 'chapters'))
    with open(os.path.join(shelf, 'odd', 'chapters', '01.md'), 'w', encoding='utf-8') as f:
        f.write(ODD_MD)
    with open(os.path.join(shelf, 'odd', 'chapters', 'evil.svg'), 'w', encoding='utf-8') as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 200 100" onload="window.__pwned = 5">'
                '<style>@import url(https://example.com/x.css); .a { fill: url(https://example.com/y.svg#p); } .b { fill: #123456; }</style>'
                '<script>window.__pwned = 6</script><image href="https://example.com/a.png" width="10" height="10"/>'
                '<use xlink:href="https://example.com/z.svg#s"/><rect class="b" width="200" height="100" style="stroke: url(https://example.com/q.svg#s)"/>'
                '<text x="10" y="50" class="a">kept</text></svg>')
    sec = lambda i, t, st, lv=1: {'id': i, 'title': t, 'kind': 'lesson', 'level': lv, 'state': st, 'words': 100 if st == 'written' else 0, 'teaches': [], 'anchor': i.replace('.', '') + '-x'}  # noqa: E731
    odd = {'name': 'odd', 'title': '<script>window.__pwned = 4</script> & "odd"', 'for': 'TODO who the book is for', 'parts': [{'title': '', 'chapters': [
        {'n': 1, 'title': '<b>Odd</b> one', 'file': 'odd/chapters/01.md', 'state': 'writing', 'words': 100, 'sections': [sec('1.1', 'Written `code` one', 'written', 9), sec('1.2', 'Planned two', 'planned', 2)]},
        {'n': 2, 'title': 'Missing file', 'file': 'odd/chapters/02-missing.md', 'state': 'written', 'words': 50, 'sections': [sec('2.1', 'Lost', 'written')]},
        {'n': 3, 'title': 'No sections yet', 'file': None, 'state': 'planned', 'words': 0, 'sections': []}]}]}
    rnd = random.Random(7)
    wide = {'name': 'wide', 'title': 'A very large book', 'for': '', 'parts': [{'title': 'Part %d' % (p + 1), 'chapters': [
        {'n': p * 30 + c + 1, 'title': 'Chapter number %d' % (p * 30 + c + 1), 'file': None, 'state': 'planned', 'words': 0,
         'sections': [sec('%d.%d' % (p * 30 + c + 1, k + 1), 'Section %d' % (k + 1), 'planned') for k in range(8)]} for c in range(30)]} for p in range(10)]}
    edges = [{'from': 'wide:%d' % n, 'to': 'wide:%d' % rnd.randint(max(1, n - 12), n - 1), 'ideas': 1} for n in range(2, 301) for _ in range(2)]
    man = {'schema': 3, 'books': [{'name': 'empty-book', 'title': 'An empty book', 'for': '', 'parts': []}, odd, wide],
           'edges': [{'from': 'odd:1.2', 'to': 'odd:1.1', 'idea': 'x'}, {'from': 'odd:9.9', 'to': 'odd:1.1', 'idea': 'ghost'}],
           'chapter_edges': [{'from': 'odd:1', 'to': 'odd:2', 'ideas': 1}, {'from': 'odd:2', 'to': 'odd:1', 'ideas': 1}, {'from': 'odd:3', 'to': 'nowhere:1', 'ideas': 1}] + edges}
    with open(os.path.join(shelf, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(man, f)
    return shelf


@check('21. odd shelves: an empty book, a cycle, a missing chapter file, hostile Markdown, a 300-chapter book: nothing breaks, nothing runs, nothing is fetched from elsewhere')
def t_odd(browser, base, shelf):
    odd = odd_shelf()
    b2 = serve(odd)
    page = new_page(browser, b2, quiet=True)   # the missing files are logged by the browser itself as 404s
    errs = []
    page.on('pageerror', lambda e: errs.append(str(e)))
    assert page.evaluate('__us.S.book.books.length') == 3 and page.locator('#tree .ti.book').count() == 3
    assert page.evaluate("document.querySelector('#ti-odd').getAttribute('aria-label')").startswith('<script>window.__pwned = 4</script>'), 'titles are text'
    for sel in ('empty-book', 'odd', 'odd-1', 'odd-1-1', 'odd-1-2', 'odd-2', 'odd-3', 'shelf'):
        page.evaluate(f"__us.select('{sel}', {{ from: 'tree' }})")
        page.wait_for_timeout(60)
    g = page.evaluate(GRAPH_JS)
    assert not g['overlaps'] and not g['through'], f"{g['overlaps'][:2]} {g['through'][:2]}"
    page.evaluate("__us.select('odd-3', { from: 'tree' })")
    assert page.get_attribute('#primary', 'data-copy') == 'Write chapter 3 of odd'
    # the large book: opened, laid out and drawn quickly; every section in the tree
    page.evaluate("__us.select('wide-150', { from: 'tree' })")
    ms = page.evaluate('__us.G.lastMs')
    g = page.evaluate(GRAPH_JS)
    assert g['units'] >= 300 and not g['overlaps'] and not g['through'], f"{g['units']} boxes; {g['overlaps'][:2]} {g['through'][:2]}"
    assert ms < 800, f'laying out 300 chapters took {ms:.0f} ms'
    t = page.evaluate("(() => { const t = performance.now(); document.querySelector('[data-depth=all]').click(); return performance.now() - t; })()")
    assert page.locator('#tree .ti.section').count() == 2403 and t < 1500, f'{t:.0f} ms to open every row'
    # hostile Markdown
    page.evaluate("__us.go('odd-1-1')")
    reading(page, 'odd-1-1')
    page.wait_for_timeout(400)
    text = page.evaluate('document.getElementById("article").innerText')
    assert page.evaluate('window.__pwned') is None, f"something ran: __pwned = {page.evaluate('window.__pwned')}"
    assert '<stdio.h>' in text and 'this must never show' not in text and 'this comment is part of a program and must show' in text and 'Text before the first section.' in text
    assert page.evaluate("document.querySelector('.prose :not(pre) > code').textContent") == '<!--'
    assert page.locator('.prose script, .prose [onerror], .prose a[href^="javascript"]').count() == 0
    assert 'A picture kept on another site is not loaded here' in text and page.locator('.prose img[src*="example.com"]').count() == 0
    assert page.get_attribute('.prose a.ext', 'rel') == 'noopener noreferrer' and page.get_attribute('.prose a.ext', 'target') == '_blank'
    page.wait_for_selector('.fig-svg.ready')
    evil = page.evaluate("(() => { const r = document.querySelector('.fig-svg.ready').shadowRoot; return { html: r.innerHTML, fill: getComputedStyle(r.querySelector('rect')).fill, label: r.querySelector('svg').getAttribute('aria-label') }; })()")
    assert 'example.com' not in evil['html'] and 'onload' not in evil['html'] and '<script' not in evil['html'] and 'kept' in evil['html'], evil['html'][:300]
    assert evil['fill'] == 'rgb(18, 52, 86)' and evil['label'] == 'a drawing that misbehaves', evil
    assert page.evaluate('window.__pwned') is None
    assert not FOREIGN, f'a request left the shelf: {FOREIGN[:2]}'
    assert page.text_content('#article h1').strip() == '1.1 Written code one' and 'Level 5, Teach' in page.text_content('.sec-meta')
    # nested answers: the inner one stays out until both are turned
    assert 'Outer answer' not in text and 'Inner answer' not in text
    page.click('.prose details.card >> summary')
    page.wait_for_function("document.querySelector('.prose .card-body').childNodes.length > 0")
    assert 'Outer answer' in page.inner_text('#article') and 'Inner answer' not in page.inner_text('#article')
    page.click('.prose .card-body details.card >> summary')
    page.wait_for_function("document.getElementById('article').innerText.includes('Inner answer')")
    # a chapter whose file is gone: said plainly, with the way back
    page.evaluate("__us.go('odd-2-1')")
    page.wait_for_selector('.trouble')
    assert 'could not be opened' in page.text_content('.trouble h1') and 'python3 scripts/us_index.py' in page.text_content('.trouble')
    assert page.locator('.trouble a[href="#map-odd-2"]').count() == 1 and page.locator('.toc-list a').count() == 1
    page.click('.trouble a.btn')
    page.wait_for_function("document.body.dataset.mode === 'map'")
    assert not errs, errs[:3]
    page.context.close()
    shutil.rmtree(odd, ignore_errors=True)
    return f'300 chapters laid out in {ms:.0f} ms, 2,403 section rows in {t:.0f} ms; hostile Markdown inert'


# ---------------------------------------------------------------- 23, 24. a book about a terminal tool
SHIP = []
NOTE = 'Not run on the machine this book was written on: %s. Your screen is the first to show what it prints.'


def ship():
    """The shelf with the terminal-tool book (blocks marked unrun, lines far too long), made and served once."""
    if not SHIP:
        folder = make_shelf(books=['ship-it'])
        SHELVES.append(folder)
        SHIP.extend([serve(folder), folder])
    return SHIP


@check('23. not run: a block marked unrun="why" has the standard note right under it, like the page\'s other notes, in both themes, in an answer and on paper; the map, the contents and the progress menu say "N not run"')
def t_unrun(browser, base, shelf):
    b2, folder = ship()
    ch = manifest(folder)['books'][0]['parts'][0]['chapters'][0]
    assert ch.get('unrun') == 3, f'manifest.json should carry "unrun": 3 for the chapter; it has {ch.get("unrun")}'
    assert not any('unrun' in c for b in manifest(shelf)['books'] for p in b['parts'] for c in p['chapters']), 'a chapter with every block run carries no count'
    css = open(os.path.join(ROOT, 'reader', 'src', 'reader.css'), encoding='utf-8').read()
    mine = [line for line in css.split('\n') if re.search(r'\.unrun\b|\.wrap\b|data-wrap', line)]
    assert mine and not any(re.search(r'#[0-9A-Fa-f]{3,8}\b|rgba?\(', line) for line in mine), 'the note and the switch must use the page\'s own colours only'
    for scheme in ('light', 'dark'):
        page = new_page(browser, b2, 'ship-it-1-1', scheme=scheme)
        reading(page, 'ship-it-1-1')
        n = page.evaluate("""() => { const ns = [...document.querySelectorAll('#article .unrun')], n = ns[0], root = getComputedStyle(document.documentElement);
            const rgb = v => { const e = document.createElement('i'); e.style.color = v; document.body.appendChild(e); const c = getComputedStyle(e).color; e.remove(); return c; };
            const look = e => { const c = getComputedStyle(e); return [c.backgroundColor, c.borderLeftColor, c.borderLeftWidth, c.borderLeftStyle, c.paddingLeft, c.paddingTop, c.fontSize, c.fontFamily, c.color]; };
            const q = document.createElement('blockquote'); q.className = 'note'; q.textContent = 'x'; document.querySelector('.prose').appendChild(q); const other = look(q); q.remove();
            const prev = n.previousElementSibling;
            return { count: ns.length, text: n.textContent, tag: n.tagName, prev: prev.className, cmd: prev.querySelector('.cmd').textContent, gap: n.getBoundingClientRect().top - prev.getBoundingClientRect().bottom,
                     mine: look(n), other, sunken: rgb(root.getPropertyValue('--sunken')), ink: rgb(root.getPropertyValue('--ink')), html: document.getElementById('article').innerHTML }; }""")
        assert n['count'] == 1, f'{scheme}: one note in the page (the answer is still face down), found {n["count"]}'
        assert n['text'] == NOTE % 'Docker Hub cannot be reached from here', n['text']
        assert n['tag'] == 'P' and n['prev'] == 'code term' and n['cmd'] == 'docker pull alpine:3.20', 'the note belongs right under its block'
        assert 0 <= n['gap'] <= 16, f'{scheme}: the note sits {n["gap"]:.0f} px under its block'
        assert n['mine'] == n['other'], f'{scheme}: the note should look like the page\'s other notes: {n["mine"]} / {n["other"]}'
        assert n['mine'][0] == n['sunken'] and n['mine'][1] == n['ink'], f'{scheme}: note colours {n["mine"][:2]}'
        assert 'unrun=' not in n['html'] and '<!--' not in n['html'], 'the marker itself shows'
        r = page.evaluate(CONTRAST_JS)
        assert not r['fails'], f'{scheme}: ' + '; '.join(r['fails'][:4])
        # inside an answer: the note comes into the page with the answer, under the answer's own block
        page.click('.prose details.card summary')
        page.wait_for_timeout(350)
        inner = page.evaluate("[...document.querySelectorAll('details.card .card-body > *')].map(e => [e.className, e.textContent])")
        assert [c for c, _ in inner] == ['code term', 'unrun'] and inner[1][1] == NOTE % 'it needs the image, and the image could not be pulled', inner
        if scheme == 'light':   # on paper: every note of the chapter, the hostile one included, as text
            page.emulate_media(media='print')
            page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
            page.wait_for_timeout(300)
            shown = page.evaluate("[...document.querySelectorAll('#article .unrun')].filter(e => e.getClientRects().length).map(e => e.textContent)")
            assert len(shown) == 3 and all(t.startswith('Not run on the machine') for t in shown), shown
            page.evaluate("window.dispatchEvent(new Event('afterprint'))")
            page.emulate_media(media='screen')
        assert page.text_content('#toc-prog').strip() == '1 of 2 sections opened, 3 not run'
        page.context.close()
    # a reason is text, whatever it holds; a block that ran has no note
    page = new_page(browser, b2, 'ship-it-1-2')
    reading(page, 'ship-it-1-2')
    odd = page.evaluate("""() => ({ notes: [...document.querySelectorAll('#article .unrun')].map(e => e.textContent), kids: document.querySelectorAll('#article .unrun *').length,
        after: [...document.querySelectorAll('#article .prose .code')].map(c => c.nextElementSibling && c.nextElementSibling.className) })""")
    assert odd['notes'] == [NOTE % '<img src=x onerror=alert(1)> *star* & `tick`'] and odd['kids'] == 0, odd
    assert odd['after'][0] == 'unrun' and odd['after'][1] != 'unrun', odd['after']
    # the marker, read: quoted or not, only the fence right under it, the fence's own indentation, never from inside a fence
    got = page.evaluate("""(cases) => cases.map(md => __us.splitChapter('# Chapter 1: T\\n\\n## 1.1 A\\n\\n' + md).parts.get('1.1').split('\\n').filter(l => l.includes('class="unrun"')))""", [
        '<!-- code: id=a unrun=offline -->\n```console\n$ x\n```\nafter\n',
        '<!-- code: id=a unrun="the \\"hub\\" is closed." -->\n\n~~~console\n$ x\n~~~\n',
        '<!-- code: id=a unrun="no" -->\nSome words first.\n\n```console\n$ x\n```\n',
        '1. Item\n\n   <!-- code: id=a unrun="in a list" -->\n   ```console\n   $ x\n   ```\n',
        '<!-- code: id=a mode=fragment -->\n```console\n$ x\n```\n\n<!-- teaches: unrun = not run -->\n```text\n<!-- code: id=b unrun="shown, not meant" -->\n```\n',
        '<!-- code: id=a unrun="" -->\n```console\n$ x\n```\n',
    ])
    p = '<p class="unrun">'
    assert got[0] == [p + NOTE % 'offline' + '</p>'], got[0]
    assert got[1] == [p + NOTE % 'the &quot;hub&quot; is closed' + '</p>'], got[1]
    assert got[2] == [] and got[4] == [], f'a note where no block is marked: {got[2]} {got[4]}'
    assert got[3] == ['   ' + p + NOTE % 'in a list' + '</p>'], got[3]
    assert got[5] == [p + (NOTE % '').replace(': .', '.') + '</p>'], got[5]
    # the map: the chapter row, its spoken label, its detail; the progress menu
    page.evaluate("__us.go('map-ship-it-1')")
    page.wait_for_function("document.body.dataset.mode === 'map'")
    page.wait_for_timeout(400)
    m = page.evaluate("""() => ({ row: document.querySelector('#ti-ship-it-1 > .row').innerText, label: document.getElementById('ti-ship-it-1').getAttribute('aria-label'),
        facts: document.querySelector('#detail-body .facts').textContent })""")
    assert '3 not run' in m['row'] and ', 3 not run' in m['label'] and '3 not run on the machine this book was written on' in m['facts'], m
    page.click('#prog-btn')
    assert '3 not run where the book was written, in 1 chapter.' in page.text_content('#prog-sum')
    page.context.close()
    page = new_page(browser, base)   # a shelf where everything ran says nothing of it
    page.click('#prog-btn')
    assert 'not run' not in page.text_content('#tree') and 'not run' not in page.text_content('#prog-sum')
    page.context.close()
    return 'note under the block in light and dark, in an answer, on paper; reason kept as text; "3 not run" in the tree, the detail, the contents and the progress menu'


WRAP_JS = """() => ({ on: document.documentElement.hasAttribute('data-wrap'), sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth,
    focus: document.activeElement.className, top: document.activeElement.getBoundingClientRect().top,
    boxes: [...document.querySelectorAll('#article .prose .code')].map(c => { const pre = c.querySelector('pre'), b = c.querySelector('button.wrap'), R = e => e.getBoundingClientRect();
        return { kind: c.className.slice(5), sw: !!b, pressed: b && b.getAttribute('aria-pressed'), name: b && b.getAttribute('aria-label'), label: b && b.innerText.trim(),
                 over: pre.scrollWidth > pre.clientWidth + 1, tab: pre.getAttribute('tabindex'), role: pre.getAttribute('role'), ws: getComputedStyle(pre.querySelector('code')).whiteSpace,
                 inside: [...c.querySelectorAll('.code-top > *')].every(e => R(e).left >= R(c).left - 0.5 && R(e).right <= R(c).right + 0.5),
                 size: b && Math.min(R(b).width, R(b).height), shown: !!b && b.getClientRects().length > 0 }; }) })"""


@check('24. wrap lines: a switch on each terminal and output box with a line too long for it; worked from the keyboard; long lines wrap instead of scrolling; remembered in this browser; a program keeps its lines')
def t_wrap(browser, base, shelf):
    b2, _ = ship()
    col = lambda s, k: [b[k] for b in s['boxes']]  # noqa: E731
    page = new_page(browser, b2, 'ship-it-1-1')
    reading(page, 'ship-it-1-1')
    s = page.evaluate(WRAP_JS)
    assert col(s, 'kind') == ['term', 'term', 'term', 'prog', 'out'], col(s, 'kind')
    assert not s['on'] and col(s, 'sw') == [False, True, False, False, True], f'the switch belongs on the terminal and the output box with a long line: {col(s, "sw")}'
    assert col(s, 'over') == [False, True, False, True, True] and all(b['tab'] == '0' and b['role'] == 'region' for b in s['boxes'] if b['over'])
    assert all(b['pressed'] == 'false' and b['name'] == 'Wrap lines' and b['label'] == 'Wrap lines' and b['inside'] for b in s['boxes'] if b['sw']), s['boxes']
    # keyboard only: Tab reaches the switch on the output box, the ring shows, Space turns it on
    for _ in range(30):
        page.keyboard.press('Tab')
        if page.evaluate("!!document.activeElement.closest('.code.out') && document.activeElement.matches('button.wrap')"):
            break
    else:
        raise AssertionError('Tab never reaches the switch')
    ring = page.evaluate("(() => { const c = getComputedStyle(document.activeElement); return [c.outlineStyle, c.outlineWidth]; })()")
    assert ring == ['solid', '3px'], f'focus ring on the switch: {ring}'
    top = page.evaluate(WRAP_JS)['top']
    page.keyboard.press('Space')
    page.wait_for_timeout(200)
    s = page.evaluate(WRAP_JS)
    assert s['on'] and [b['pressed'] for b in s['boxes'] if b['sw']] == ['true', 'true'], 'Space should turn every switch on'
    assert col(s, 'over') == [False, False, False, True, False], f'long lines should wrap, a program should not: {col(s, "over")}'
    assert col(s, 'ws') == ['pre-wrap', 'pre-wrap', 'pre-wrap', 'pre', 'pre-wrap'] and s['sw'] <= s['cw']
    assert [b['tab'] for b in s['boxes']] == [None, None, None, '0', None] and [b['role'] for b in s['boxes']] == [None, None, None, 'region', None], 'only what still scrolls sideways is a tab stop'
    assert 'wrap' in s['focus'] and abs(s['top'] - top) <= 2, f'focus stays on the switch, where it was: {s["focus"]} moved {s["top"] - top:.0f} px'
    assert page.evaluate("[...document.querySelectorAll('.code.out pre')].every(p => p.textContent.includes('Forbidden') && p.getBoundingClientRect().right <= innerWidth)")
    r = page.evaluate(CONTRAST_JS)
    assert not r['fails'], 'light, switch on: ' + '; '.join(r['fails'][:4])
    # an answer turned over afterwards follows the same switch
    page.click('.prose details.card summary')
    page.wait_for_timeout(350)
    card = page.evaluate("(() => { const c = document.querySelector('details.card .code.term'), b = c.querySelector('button.wrap'), p = c.querySelector('pre'); return [b && b.getAttribute('aria-pressed'), p.scrollWidth > p.clientWidth + 1]; })()")
    assert card == ['true', False], f'the block in the answer: {card}'
    # remembered in this browser: after a reload it is still on, and the switches are where they were
    page.reload()
    reading(page, 'ship-it-1-1')
    s = page.evaluate(WRAP_JS)
    assert s['on'] and col(s, 'sw') == [False, True, False, False, True] and [b['pressed'] for b in s['boxes'] if b['sw']] == ['true', 'true'], 'not remembered after a reload'
    assert col(s, 'over') == [False, False, False, True, False]
    # Enter turns it off again: the lines scroll inside their boxes and can be reached from the keyboard again
    page.focus('.code.term button.wrap')
    page.keyboard.press('Enter')
    page.wait_for_timeout(200)
    s = page.evaluate(WRAP_JS)
    assert not s['on'] and col(s, 'over') == [False, True, False, True, True] and all(b['tab'] == '0' for b in s['boxes'] if b['over']), s['boxes']
    assert [b['pressed'] for b in s['boxes'] if b['sw']] == ['false', 'false'] and col(s, 'ws') == ['pre'] * 5
    # a narrower window: a line that fitted is now too long, and its box gets the switch
    page.set_viewport_size({'width': 390, 'height': 800})
    page.wait_for_timeout(300)
    assert col(page.evaluate(WRAP_JS), 'sw') == [False, True, True, False, True], 'after the window narrows'
    page.emulate_media(media='print')
    assert not any(col(page.evaluate(WRAP_JS), 'shown')), 'the switch should not be printed'
    page.context.close()
    # a phone, dark: a short label, a 44 px target, nothing leaves its box or the page, off and on, in an answer too
    page = new_page(browser, b2, 'ship-it-1-1', w=320, h=568, scheme='dark', touch=True, dsf=2)
    reading(page, 'ship-it-1-1')
    page.tap('.prose details.card summary')
    page.wait_for_timeout(350)
    for state in ('off', 'on'):
        s = page.evaluate(WRAP_JS)
        sw = [b for b in s['boxes'] if b['sw']]
        assert s['on'] == (state == 'on') and len(sw) == 4, f'320 px, {state}: {len(sw)} switches'
        assert all(b['label'] == 'Wrap' and b['name'] == 'Wrap lines' and b['size'] >= 43.5 for b in sw), f'320 px, {state}: {sw}'
        assert all(b['inside'] for b in s['boxes']) and s['sw'] <= s['cw'], f'320 px, {state}: something leaves its box or the page'
        assert state == 'off' or not any(b['over'] for b in s['boxes'] if b['kind'] != 'prog'), '320 px, on: a long line still scrolls'
        r = page.evaluate(CONTRAST_JS)
        assert not r['fails'], f'dark, 320 px, {state}: ' + '; '.join(r['fails'][:4])
        if state == 'off':
            page.tap('.code.out button.wrap')
            page.wait_for_timeout(250)
    page.context.close()
    return 'on 2 of 5 boxes at 1440 px, 4 on a phone; Tab and Space; wraps, a program does not; survives a reload; Enter turns it off'


# ---------------------------------------------------------------- 22. console (run last, after 23 and 24)
@check('22. no console errors or warnings anywhere in the run')
def t_console(browser, base, shelf):
    assert not CONSOLE, ' | '.join(CONSOLE[:5])
    assert not FOREIGN, f'requests left the shelf: {FOREIGN[:3]}'


CHECKS = [t_tree, t_graph, t_detail, t_shelves, t_routes, t_text, t_code, t_answers, t_figures, t_search, t_progress,
          t_file, t_contrast, t_matrix, t_keyboard, t_motion, t_print, t_offline, t_script, t_budget, t_odd, t_unrun, t_wrap, t_console]


# ---------------------------------------------------------------- screenshots
def shots(browser, base):
    os.makedirs(SHOTS, exist_ok=True)
    made = 0
    chapter = 'learn-c-8-2' if HAVE_C else 'first-steps-c-1-2'
    for scheme in ('light', 'dark'):
        for w, h, touch in ((390, 844, True), (768, 1024, True), (1440, 900, False), (1920, 1080, False)):
            page = new_page(browser, base, 'map-' + chapter.rsplit('-', 1)[0], w=w, h=h, scheme=scheme, touch=touch, settle=800)
            page.screenshot(path=os.path.join(SHOTS, f'map-{scheme}-{w}.png'))
            page.evaluate(f"__us.go('{chapter}')")
            reading(page, chapter)
            page.wait_for_timeout(400)
            page.screenshot(path=os.path.join(SHOTS, f'chapter-{scheme}-{w}.png'))
            page.evaluate("document.querySelector('.beat-the-code').scrollIntoView()")
            page.wait_for_timeout(300)
            page.screenshot(path=os.path.join(SHOTS, f'chapter-{scheme}-{w}-code.png'))
            made += 3
            page.context.close()
    print(f'{made} screenshots in {os.path.relpath(SHOTS, ROOT)}')


def main():
    want = [a for a in sys.argv[1:] if a.isdigit()]
    if not os.path.exists(HTML):
        print('reader/index.html is missing: run python3 reader/build.py')
        return 1
    shelf = make_shelf()
    base = serve(shelf)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
            for fn in CHECKS:
                if want and fn.label.split('.')[0] not in want:
                    continue
                fn(browser, base, shelf)
            if '--shots' in sys.argv:
                shots(browser, base)
            browser.close()
    finally:
        for proc in SERVERS:
            proc.terminate()
        for folder in [shelf] + SHELVES:
            shutil.rmtree(folder, ignore_errors=True)
    bad = sum(1 for _, ok in RESULTS if not ok)
    print(f'{len(RESULTS) - bad} passed, {bad} failed')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
