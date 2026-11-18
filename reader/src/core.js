/* =====================================================================
   understudy reading page
   One file after the build, no framework, no network of its own. It reads
   manifest.json and search.json beside it and fetches chapter Markdown on
   demand. It never writes to the book.

   1. HELPERS, STORAGE, MOTION
   ===================================================================== */
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const plural = (n, w) => `${n} ${w}${n === 1 ? '' : 's'}`;
const num = n => Number(n).toLocaleString('en');
const KEY = 'understudy:v1:' + location.pathname.replace(/[^/]*$/, '');
const store = { // localStorage only inside try/catch; the page works without it
  get(k) { try { const v = window.localStorage.getItem(KEY + k); return v ? JSON.parse(v) : null; } catch (e) { return null; } },
  set(k, v) { try { window.localStorage.setItem(KEY + k, JSON.stringify(v)); } catch (e) { /* no storage: keep going */ } }
};
const LEVELS = ['Use', 'Explain', 'Build', 'Design', 'Teach'];
const STATE = { planned: 'Planned', writing: 'Being written', written: 'Written', reviewed: 'Written and reviewed' };
const minutes = w => Math.max(1, Math.round(w / 200));

/* MOTION: a small, deliberate system (from the approved map)
   Every animation answers "did it hear me", "is it working" or "what
   happened". Pointer actions may move things; keyboard actions never do.
   Reduced motion keeps only colour and opacity changes of 120 ms or less.
   ---------------------------------------------------------------------
   what              trigger            property            ms   easing
   press             pointer down/up    transform           90/140 out
   tree rows in/out  open/close         opacity, transform  140/110 out
   graph boxes       open/close         transform, opacity  260  in-out (FLIP)
   needs/unlocks     select by pointer  stroke-dashoffset   <=300 out
   camera            fit, centre        SVG view (rAF)      260  in-out
   detail swap       selection change   opacity, transform  100 out, 160 in
   phone tabs        tab by pointer     opacity, transform  220  out
   filter marks      new match          transform scaleX    140  out
   copy check        copy               stroke-dashoffset   200  out
   answer card       turned by pointer  transform rotateX   220  out
   figure, drawer    opened             opacity, transform  200  out
   theme             toggle by pointer  View Transition wipe 380 in-out
   first load        once per page      transform, opacity  <450 out */
const EASE_OUT = 'cubic-bezier(0.23, 1, 0.32, 1)', EASE_IN_OUT = 'cubic-bezier(0.77, 0, 0.175, 1)';
const M = (() => {
  const rm = matchMedia('(prefers-reduced-motion: reduce)');
  let modality = 'pointer';
  const mark = m => { if (modality !== m) { modality = m; document.documentElement.dataset.input = m; } };
  addEventListener('pointerdown', () => mark('pointer'), true);
  addEventListener('keydown', e => { if (!['Shift', 'Control', 'Alt', 'Meta', 'Tab'].includes(e.key)) mark('key'); }, true);
  let scale = 1;
  Object.defineProperty(window, '__motionScale', { // review hook only: 10 plays every animation at 10% speed
    get() { return scale; },
    set(v) { scale = Number(v) > 0 ? Number(v) : 1; document.documentElement.style.setProperty('--ms', String(scale)); },
    configurable: true
  });
  const M = {
    get reduced() { return rm.matches; },
    get key() { return modality === 'key'; },
    d: ms => ms * scale,
    move: () => !rm.matches && modality !== 'key',      // may this change travel?
    fade: () => modality !== 'key',                     // may this change fade (also under reduced motion)?
    run(el, frames, o) { try { return el.animate(frames, Object.assign({}, o, { duration: M.d(o.duration || 0), delay: M.d(o.delay || 0) })); } catch (e) { return null; } }
  };
  return M;
})();
const easeInOut = (() => { // cubic-bezier(0.77, 0, 0.175, 1) for the rAF camera
  const x1 = 0.77, y1 = 0, x2 = 0.175, y2 = 1;
  const bx = t => 3 * x1 * t * (1 - t) ** 2 + 3 * x2 * t * t * (1 - t) + t ** 3;
  const by = t => 3 * y1 * t * (1 - t) ** 2 + 3 * y2 * t * t * (1 - t) + t ** 3;
  return x => { let lo = 0, hi = 1; for (let i = 0; i < 24; i++) { const m = (lo + hi) / 2; if (bx(m) < x) lo = m; else hi = m; } return by((lo + hi) / 2); };
})();
const live = (() => { // one stable polite live region
  let t = 0;
  return (msg, delay = 0) => {
    clearTimeout(t);
    t = setTimeout(() => { const el = $('#live'); el.textContent = ''; requestAnimationFrame(() => { el.textContent = msg; }); }, delay);
  };
})();
const CK = '<svg class="ck" viewBox="0 0 14 14" aria-hidden="true"><path d="M2 7.5 5.5 11 12 3"/></svg>';
/* Copy, only ever called from a click handler. The label becomes "Copied"
   with a check that draws itself, then returns. Failure says what to do. */
async function copyText(text, btn, note) {
  let ok = false;
  try {
    if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error('no clipboard');
    await navigator.clipboard.writeText(text); ok = true;
  } catch (err) { ok = false; }
  if (note) note.textContent = ok ? 'Copied. Paste it to your agent.' : 'The clipboard is not available here. Select the text shown and copy it by hand.';
  live(ok ? 'Copied' : 'Could not copy. Select the text and copy it by hand.');
  if (btn && btn.isConnected) { // the button itself answers: "Copied", or that it could not
    const bl = btn.querySelector('.bl') || btn;
    if (!btn._label) btn._label = bl.textContent;
    btn.style.minWidth = btn.offsetWidth + 'px';
    btn.classList.toggle('copied', ok); bl.textContent = ok ? 'Copied' : 'Not copied';
    clearTimeout(btn._t);
    btn._t = setTimeout(() => { btn.classList.remove('copied'); bl.textContent = btn._label; btn.style.minWidth = ''; }, M.d(1600));
  }
  return ok;
}

/* =====================================================================
   2. THE SHELF: books, parts, chapters and sections from manifest.json
   ===================================================================== */
const hashSafe = s => String(s).replace(/[^A-Za-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'x';
const isBranch = n => n.kind !== 'section';
const isDone = n => n.state === 'written' || n.state === 'reviewed';
const DEPTH = { shelf: 0, book: 1, part: 2, chapter: 3, section: 4 }; // tree -L counts kinds, so a book without parts lines up with one that has them
function buildShelf(man) {
  const byId = new Map(), byKey = new Map(); // byKey: the manifest's own names, "book:8" and "book:8.2"
  const mk = (kind, id, title, parent, extra) => {
    while (byId.has(id)) id += '-x';
    const n = Object.assign({ id, kind, title: String(title || id).replace(/`/g, ''), parent, children: [], nest: parent ? parent.nest + 1 : 0, depth: DEPTH[kind], index: 0,
      state: null, needs: [], unlocks: [], total: 0, written: 0, words: 0 }, extra);
    byId.set(id, n);
    if (parent) parent.children.push(n);
    return n;
  };
  const root = mk('shelf', 'shelf', 'Your books', null, { seg: 'book' });
  const books = [], chapters = [], sections = [];
  for (const b of man.books || []) {
    const book = mk('book', hashSafe(b.name), b.title || b.name, root, { name: b.name, seg: b.name, audience: /^todo\b/i.test(b.for || '') ? '' : (b.for || '') });
    book.book = book; books.push(book);
    (b.parts || []).forEach((p, pi) => {
      const holder = p.title ? mk('part', `${book.id}-part-${pi + 1}`, p.title, book, { book }) : book;
      for (const c of p.chapters || []) {
        const ch = mk('chapter', `${book.id}-${hashSafe(c.n)}`, c.title, holder, { book, n: c.n, file: c.file || null, state: c.state || 'planned', levels: [], unrun: Number(c.unrun) || 0 });
        byKey.set(`${b.name}:${c.n}`, ch); chapters.push(ch);
        for (const s of c.sections || []) {
          const sec = mk('section', `${book.id}-${hashSafe(s.id)}`, s.title, ch, { book, chapter: ch, num: String(s.id), state: s.state || 'planned',
            level: Math.min(5, Math.max(1, s.level || 1)), sort: s.kind || 'lesson', words: s.words || 0, teaches: s.teaches || [], anchor: s.anchor || '' });
          byKey.set(`${b.name}:${s.id}`, sec); sections.push(sec);
          ch.words += sec.words;
          if (!ch.levels.includes(sec.level)) ch.levels.push(sec.level);
        }
        ch.levels.sort();
        ch.total = ch.children.length; ch.written = ch.children.filter(isDone).length;
        ch.readable = !!ch.file && ch.written > 0;
        for (let q = ch.parent; q; q = q.parent) { q.total++; q.words += ch.words; if (isDone(ch)) q.written++; }
      }
    });
  }
  const link = (list, a, b) => { const x = byKey.get(a), y = byKey.get(b); if (x && y && x !== y && !x.needs.includes(y.id)) { x.needs.push(y.id); y.unlocks.push(x.id); } };
  for (const e of man.edges || []) link(sections, e.from, e.to);
  for (const e of man.chapter_edges || []) link(chapters, e.from, e.to);
  const order = [];
  (function walk(n) { n.index = order.length; order.push(n); n.children.forEach(walk); })(root);
  return { root, byId, byKey, order, books, chapters, sections };
}
/** The written sections of a chapter, in order. */
const readable = ch => ch.children.filter(s => isDone(s));
/** Every written section of a book, in reading order. */
const bookSections = book => S.book.sections.filter(s => s.book === book && isDone(s) && s.chapter.file);

/* =====================================================================
   3. GRAPH ALGORITHMS (pure functions; tested from the outside)
   ===================================================================== */
/** Everything a chapter or section needs, transitively. */
function ancestorsOf(book, id) {
  const out = new Set(), stack = [id];
  while (stack.length) for (const m of book.byId.get(stack.pop()).needs) if (!out.has(m)) { out.add(m); stack.push(m); }
  return out;
}
/** Everything a chapter or section unlocks, transitively. */
function descendantsOf(book, id) {
  const out = new Set(), stack = [id];
  while (stack.length) for (const m of book.byId.get(stack.pop()).unlocks) if (!out.has(m)) { out.add(m); stack.push(m); }
  return out;
}
/** A learner's order: unwritten prerequisite chapters, each after everything it needs. Ties go to book order. */
function learningPath(book, id) {
  const anc = ancestorsOf(book, id);
  const left = new Set(anc), done = new Set(), out = [];
  while (left.size) {
    let best = null;
    for (const a of left) {
      const n = book.byId.get(a);
      if (!n.needs.every(m => done.has(m) || !anc.has(m))) continue;
      if (!best || n.index < best.index) best = n;
    }
    if (!best) break; // a cycle; cannot happen with a checked plan
    left.delete(best.id); done.add(best.id); out.push(best);
  }
  return out.filter(n => !isDone(n));
}

/* ---------- text wrapping (pure, given a measure function) ---------- */
function wrapText(text, maxW, measure) {
  const words = String(text).split(/\s+/).filter(Boolean), lines = [];
  let cur = '';
  const pushLong = w => { // a word wider than the box is cut by characters
    let part = '';
    for (const ch of w) { if (measure(part + ch) > maxW && part) { lines.push(part); part = ch; } else part += ch; }
    return part;
  };
  const parts = [];
  for (const w of words) {
    if (measure(w) <= maxW || !w.includes('-')) { parts.push(w); continue; }
    const bits = w.split('-');
    bits.forEach((b, i) => parts.push(i < bits.length - 1 ? b + '-' : b));
  }
  for (const w of parts) {
    const glue = cur && !cur.endsWith('-') ? ' ' : '';
    const tryLine = cur ? cur + glue + w : w;
    if (measure(tryLine) <= maxW) { cur = tryLine; continue; }
    if (cur) lines.push(cur);
    cur = measure(w) <= maxW ? w : pushLong(w);
  }
  if (cur) lines.push(cur);
  return lines.length ? lines : [''];
}

/* Layout constants, in graph units (1 unit = 1 CSS px at 100%). */
const GL = { W: 224, WC: 168, PAD: 12, TLH: 20, CLH: 21, RLH: 18, GAPY: 28, GAPIN: 20, BPAD: 16, HEADGAP: 12, MARGIN: 12, TRACK: 9, GAPMIN: 60, LANE: 9, OBST: 10 };

/** Size of every box. A closed book is a small cluster; a chapter is a box
    whose head carries its title, and which lists its sections when open. */
function sizeUnit(u, measure) {
  const n = u.node;
  if (u.kind === 'cluster') {
    u.lines = wrapText(n.title, GL.WC - 2 * GL.PAD - 22, s => measure(s, 'cluster'));
    const per = Math.floor((GL.WC - 2 * GL.PAD + 3) / 12);
    u.sqRows = Math.ceil(n.total / per); u.sqPer = per;
    u.w = GL.WC; u.h = u.headH = GL.PAD + u.lines.length * GL.CLH + 6 + 18 + 8 + u.sqRows * 12 + GL.PAD - 3;
    return;
  }
  u.lines = wrapText(`${n.n} ${n.title}`, GL.W - 2 * GL.PAD - 24, s => measure(s, 'title'));
  u.w = GL.W; u.headH = GL.PAD + u.lines.length * GL.TLH + 10 + 15 + GL.PAD;
  u.rows = [];
  let y = u.headH;
  if (u.open) for (const s of n.children) {
    const lines = wrapText(`${s.num} ${s.title}`, GL.W - 2 * GL.PAD - 20, t => measure(t, 'row'));
    const h = lines.length * GL.RLH + 10;
    u.rows.push({ id: s.id, node: s, lines, y, h });
    y += h;
  }
  u.h = y + (u.rows.length ? 4 : 0);
}

/** One row of a book: boxes with a column each (u.rank, from 0), ordered in
    their columns, with orthogonal edges routed through the column gaps and
    free horizontal lanes. Sets u.x and u.y from (0, 0). */
function layoutChunk(units, edges) {
  const U = new Map(units.map(u => [u.id, u]));
  const succ = new Map(units.map(u => [u.id, []])), pred = new Map(units.map(u => [u.id, []]));
  for (const e of edges) { succ.get(e.from).push(e.to); pred.get(e.to).push(e.from); }
  const ncols = Math.max(...units.map(u => u.rank)) + 1;
  const cols = [];
  for (let c = 0; c < ncols; c++) cols.push(units.filter(u => u.rank === c));
  // order each column by the barycentre of its neighbours (a few sweeps)
  const posOf = () => { const p = new Map(); cols.forEach(col => col.forEach((u, i) => p.set(u.id, (i + 0.5) / col.length))); return p; };
  for (let it = 0; it < 8; it++) {
    const p = posOf(), down = it % 2 === 0;
    for (const col of down ? cols.slice(1) : cols.slice(0, -1).reverse()) {
      for (const u of col) {
        const nb = (down ? pred : succ).get(u.id).filter(t => p.has(t));
        u.bary = nb.length ? nb.reduce((s, t) => s + p.get(t), 0) / nb.length : p.get(u.id);
      }
      col.sort((x, y) => x.bary - y.bary || x.node.index - y.node.index);
      col.forEach((u, i) => p.set(u.id, (i + 0.5) / col.length));
    }
  }
  // columns are stacked from the top; edges leave and arrive at the level of a box's head
  for (const col of cols) { let y = 0; for (const u of col) { u.y = y; y += u.h + GL.GAPIN; } }
  const mid = u => u.y + u.headH / 2;
  // routing, phase one: obstacles per column, then a free lane for each long edge
  const obst = Array.from({ length: ncols }, () => []);
  for (const u of units) obst[u.rank].push([u.y - GL.OBST, u.y + u.h + GL.OBST]);
  const usedLanes = Array.from({ length: ncols }, () => []);
  const routes = edges.map(e => { const u = U.get(e.from), v = U.get(e.to); return { e, u, v, i: u.rank, j: v.rank, sy: mid(u), ty: mid(v), lane: null }; });
  routes.sort((p, q) => (p.j - p.i) - (q.j - q.i) || p.sy - q.sy);
  for (const r of routes) {
    if (r.j - r.i < 2) continue;
    const iv = [];
    for (let c = r.i + 1; c < r.j; c++) iv.push(...obst[c]);
    iv.sort((p, q) => p[0] - q[0]);
    const merged = [];
    for (const x of iv) { const l = merged[merged.length - 1]; if (l && x[0] <= l[1]) l[1] = Math.max(l[1], x[1]); else merged.push(x.slice()); }
    const free = [];
    let lo = -Infinity;
    for (const m of merged) { free.push([lo, m[0]]); lo = m[1]; }
    free.push([lo, Infinity]);
    const lanes = [];
    for (let c = r.i + 1; c < r.j; c++) lanes.push(...usedLanes[c]);
    const clash = y => lanes.some(l => Math.abs(l - y) < GL.LANE);
    const want0 = Math.min(r.sy, r.ty), want1 = Math.max(r.sy, r.ty);
    let best = null, bestCost = Infinity;
    for (const [flo, fhi] of free) {
      if (fhi - flo < 2) continue;
      const lo2 = flo + 1, hi2 = fhi - 1;
      let y0 = Math.max(lo2, Math.min(hi2, Math.max(want0, Math.min(want1, (r.sy + r.ty) / 2))));
      if (!isFinite(y0)) y0 = isFinite(lo2) ? lo2 + 6 : hi2 - 6;
      for (let k = 0; k < 40; k++) {
        let hit = null;
        for (const y of [y0 + k * GL.LANE, y0 - k * GL.LANE]) if (y >= lo2 && y <= hi2 && !clash(y)) { hit = y; break; }
        if (hit !== null) {
          const cost = Math.abs(hit - r.sy) + Math.abs(hit - r.ty);
          if (cost < bestCost) { bestCost = cost; best = hit; }
          break;
        }
      }
    }
    r.lane = best;
    for (let c = r.i + 1; c < r.j; c++) usedLanes[c].push(best);
  }
  // phase two: vertical tracks in each gap (shared per source or per target)
  const gapSegs = Array.from({ length: Math.max(0, ncols - 1) }, () => new Map());
  const addSeg = (gap, key, y1, y2, r, which) => {
    const m = gapSegs[gap];
    if (!m.has(key)) m.set(key, { lo: Infinity, hi: -Infinity, refs: [] });
    const s = m.get(key); s.lo = Math.min(s.lo, y1, y2); s.hi = Math.max(s.hi, y1, y2); s.refs.push([r, which]);
  };
  for (const r of routes) {
    if (r.j - r.i < 2) addSeg(r.i, 'S' + r.u.id, r.sy, r.ty, r, 'a');
    else { addSeg(r.i, 'S' + r.u.id, r.sy, r.lane, r, 'a'); addSeg(r.j - 1, 'T' + r.v.id, r.lane, r.ty, r, 'b'); }
  }
  const gapW = [], gapTracks = [];
  gapSegs.forEach(m => {
    const segs = [...m.values()].sort((p, q) => p.lo - q.lo || p.hi - q.hi);
    const ends = [];
    for (const s of segs) {
      let t = ends.findIndex(e => e + 8 < s.lo);
      if (t < 0) { t = ends.length; ends.push(s.hi); } else ends[t] = s.hi;
      s.track = t;
    }
    gapTracks.push(segs);
    gapW.push(Math.max(GL.GAPMIN, 40 + ends.length * GL.TRACK));
    for (const s of segs) s.nt = ends.length;
  });
  // x placement and final points
  const colW = new Array(ncols).fill(0);
  for (const u of units) colW[u.rank] = Math.max(colW[u.rank], u.w);
  const colX = [0];
  for (let c = 1; c < ncols; c++) colX.push(colX[c - 1] + colW[c - 1] + gapW[c - 1]);
  for (const u of units) u.x = colX[u.rank];
  gapTracks.forEach((segs, g) => {
    const left = colX[g] + colW[g], w = gapW[g];
    for (const s of segs) {
      const x = left + w / 2 - (s.nt - 1) * GL.TRACK / 2 + s.track * GL.TRACK;
      for (const [r, which] of s.refs) r[which === 'a' ? 'xa' : 'xb'] = x;
    }
  });
  const out = routes.map(r => {
    const x1 = r.u.x + r.u.w, x2 = r.v.x;
    let pts = r.lane === null
      ? [[x1, r.sy], [r.xa, r.sy], [r.xa, r.ty], [x2, r.ty]]
      : [[x1, r.sy], [r.xa, r.sy], [r.xa, r.lane], [r.xb, r.lane], [r.xb, r.ty], [x2, r.ty]];
    pts = pts.filter((p, k) => k === 0 || p[0] !== pts[k - 1][0] || p[1] !== pts[k - 1][1]);
    return { from: r.e.from, to: r.e.to, points: pts };
  });
  let minY = 0, maxY = Math.max(...units.map(u => u.y + u.h));
  for (const e of out) for (const p of e.points) { minY = Math.min(minY, p[1] - 4); maxY = Math.max(maxY, p[1] + 4); }
  if (minY < 0) { for (const u of units) u.y -= minY; for (const e of out) for (const p of e.points) p[1] -= minY; }
  return { edges: out, colX, colW, w: colX[ncols - 1] + colW[ncols - 1], h: maxY - minY };
}

/** One open book: its chapters ranked by what they need, wrapped into rows of
    at most `C` columns so a book that is one long chain reads like lines of
    text. Only the edges that no longer route already implies are drawn.
    Positions are from the book's own (0, 0). */
function layoutBook(units, needs, C) {
  const U = new Map(units.map(u => [u.id, u]));
  let edges = needs.filter(e => U.has(e.from) && U.has(e.to) && e.from !== e.to);
  // rank = longest path from a chapter that needs nothing (Kahn; a cycle cannot stall it)
  const indeg = new Map(units.map(u => [u.id, 0])), out = new Map(units.map(u => [u.id, []]));
  for (const e of edges) { indeg.set(e.to, indeg.get(e.to) + 1); out.get(e.from).push(e.to); }
  for (const u of units) u.grank = -1;
  const queue = units.filter(u => !indeg.get(u.id));
  for (const u of queue) u.grank = 0;
  for (let i = 0; i < queue.length; i++) for (const t of out.get(queue[i].id)) {
    const v = U.get(t);
    v.grank = Math.max(v.grank, queue[i].grank + 1);
    indeg.set(t, indeg.get(t) - 1);
    if (!indeg.get(t)) queue.push(v);
  }
  const top = Math.max(0, ...units.map(u => u.grank));
  for (const u of units) if (u.grank < 0) u.grank = top + 1; // inside a cycle: after everything else
  edges = edges.filter(e => U.get(e.from).grank < U.get(e.to).grank);
  // transitive reduction: drop an edge when a longer route says the same
  const succ = new Map(units.map(u => [u.id, new Set()]));
  for (const e of edges) succ.get(e.from).add(e.to);
  const reach = new Map();
  for (const u of [...units].sort((a, b) => b.grank - a.grank)) {
    const r = new Set();
    for (const t of succ.get(u.id)) { r.add(t); for (const x of reach.get(t)) r.add(x); }
    reach.set(u.id, r);
  }
  edges = edges.filter(e => ![...succ.get(e.from)].some(t => t !== e.to && reach.get(t).has(e.to)));
  // rows
  const chunks = [];
  for (const u of units) { u.chunk = Math.floor(u.grank / C); u.rank = u.grank % C; (chunks[u.chunk] = chunks[u.chunk] || []).push(u); }
  const far = edges.filter(e => U.get(e.to).chunk - U.get(e.from).chunk > 1);
  const xLeft = far.length ? far.length * GL.TRACK + 12 : 0; // a margin for edges that pass whole rows
  const drawn = [];
  const inter = edges.filter(e => U.get(e.from).chunk !== U.get(e.to).chunk);
  const dropOf = new Map(), riseOf = new Map(); // one shared track per source, and per target
  const laneCount = chunks.map(() => 0);
  let y = 0, width = 0;
  const base = [];
  // room on the left for the edges that arrive at the first box of a row; the same for every row, so the rows line up
  const firstIn = c => new Set(inter.filter(e => U.get(e.to).chunk === c && U.get(e.to).rank === 0).map(e => e.to)).size;
  const xIn = chunks.length > 1 ? Math.max(...chunks.map((_, c) => firstIn(c) ? 12 + firstIn(c) * GL.TRACK : 0)) : 0;
  chunks.forEach((list, ci) => {
    const L = layoutChunk(list, edges.filter(e => U.get(e.from).chunk === ci && U.get(e.to).chunk === ci));
    const x0 = xLeft + xIn;
    for (const u of list) { u.x += x0; u.y += y; }
    for (const e of L.edges) { for (const p of e.points) { p[0] += x0; p[1] += y; } drawn.push(e); }
    const leaving = [...new Set(inter.filter(e => U.get(e.from).chunk === ci).map(e => e.from))].length;
    width = Math.max(width, x0 + L.w + (leaving ? 14 + leaving * GL.TRACK : 0));
    const lanes = inter.filter(e => U.get(e.from).chunk === ci).length + far.filter(e => U.get(e.to).chunk === ci + 1).length;
    base[ci] = y + L.h;                       // the bottom of this row; its lanes start below it
    y += L.h + (ci < chunks.length - 1 ? (lanes ? 22 + lanes * GL.LANE : GL.GAPY) : 0);
  });
  const lane = ci => base[ci] + 14 + (laneCount[ci]++) * GL.LANE;
  inter.sort((a, b) => U.get(a.from).grank - U.get(b.from).grank || U.get(a.to).grank - U.get(b.to).grank);
  far.forEach((e, i) => { e.xm = 6 + i * GL.TRACK; });
  for (const e of inter) {
    const u = U.get(e.from), v = U.get(e.to);
    if (!dropOf.has(u.id)) dropOf.set(u.id, [...dropOf.keys()].filter(k => U.get(k).chunk === u.chunk && U.get(k).rank === u.rank).length);
    if (!riseOf.has(v.id)) riseOf.set(v.id, [...riseOf.keys()].filter(k => U.get(k).chunk === v.chunk && U.get(k).rank === v.rank).length);
    const sy = u.y + u.headH / 2, ty = v.y + v.headH / 2;
    const colRight = Math.max(...chunks[u.chunk].filter(q => q.rank === u.rank).map(q => q.x + q.w));
    const colLeft = Math.min(...chunks[v.chunk].filter(q => q.rank === v.rank).map(q => q.x));
    const xa = colRight + 14 + dropOf.get(u.id) * GL.TRACK, xb = colLeft - 14 - riseOf.get(v.id) * GL.TRACK;
    const la = lane(u.chunk);
    const pts = [[u.x + u.w, sy], [xa, sy], [xa, la]];
    if (v.chunk - u.chunk > 1) { const lb = lane(v.chunk - 1); pts.push([e.xm, la], [e.xm, lb], [xb, lb]); } else pts.push([xb, la]);
    pts.push([xb, ty], [v.x, ty]);
    drawn.push({ from: e.from, to: e.to, points: pts });
  }
  return { edges: drawn, w: width, h: y };
}

/** The whole shelf: closed books stand side by side like books on a shelf;
    an open book takes a row of its own, its head box above its chapters. */
function layoutShelf(model, measure, C, maxW) {
  const units = new Map(), rows = new Map(), bands = [], edges = [];
  const succ = new Map(), pred = new Map();
  let x = GL.MARGIN, y = GL.MARGIN, rowH = 0, width = 0;
  const newRow = () => { if (rowH) { y += rowH + GL.GAPY; x = GL.MARGIN; rowH = 0; } };
  for (const g of model.groups) {
    if (!g.open) {
      const u = g.units[0];
      sizeUnit(u, measure);
      if (x > GL.MARGIN && x + u.w > maxW) newRow();
      u.x = x; u.y = y; u.rank = 0; u.chunk = 0;
      units.set(u.id, u); succ.set(u.id, []); pred.set(u.id, []);
      x += u.w + GL.GAPY; rowH = Math.max(rowH, u.h); width = Math.max(width, u.x + u.w);
      continue;
    }
    newRow();
    for (const u of g.units) sizeUnit(u, measure);
    const headLines = wrapText(g.node.title, GL.W - 2 * GL.PAD - 26, s => measure(s, 'cluster'));
    const headH = GL.PAD + headLines.length * GL.CLH + 4 + 18 + GL.PAD - 2;
    const L = g.units.length ? layoutBook(g.units, g.needs, C) : { edges: [], w: 0, h: 0 };
    const ox = x + GL.BPAD, oy = y + headH + GL.HEADGAP;
    for (const u of g.units) {
      u.x += ox; u.y += oy;
      units.set(u.id, u); succ.set(u.id, []); pred.set(u.id, []);
      for (const r of u.rows) rows.set(r.id, { id: r.id, node: r.node, parent: u, lines: r.lines, x: u.x, y: u.y + r.y, w: u.w, h: r.h });
    }
    for (const e of L.edges) {
      for (const p of e.points) { p[0] += ox; p[1] += oy; }
      succ.get(e.from).push(e.to); pred.get(e.to).push(e.from);
      edges.push({ id: e.from + '>' + e.to, from: e.from, to: e.to, points: e.points });
    }
    const w = Math.max(GL.W + GL.BPAD, L.w + 2 * GL.BPAD), h = headH + GL.HEADGAP + L.h + GL.BPAD;
    bands.push({ id: g.id, node: g.node, x, y, w, h, headH, headLines });
    width = Math.max(width, x + w);
    rowH = h; newRow(); y += 8;
  }
  const height = y + rowH;
  return { units, rows, bands, edges, succ, pred, width: width + GL.MARGIN, height: height + (rowH ? GL.MARGIN : GL.MARGIN - GL.GAPY), minY: 0 };
}

/* =====================================================================
   4. STATE, AND READING PROGRESS (kept in this browser only)
   ===================================================================== */
const S = {
  book: null,                                 // the shelf, once manifest.json is read
  mode: 'load',                               // load | map | read | empty | blocked
  open: new Set(), sel: null, focus: null,    // tree: open rows, selected node, roving row
  expanded: new Set(), openCh: new Set(),     // graph: books drawn as chapters, chapters listing their sections
  q: '', chip: 'all', saved: null, filt: null // filter text, chip, open state before filtering
};
function persist() {
  if (S.book) store.set('map', { open: [...(S.saved || S.open)], sel: S.sel, expanded: [...S.expanded], openCh: [...S.openCh] });
}
/* opened: { "book:8.2": day }, answers: { "book:8.2": [0, 2] }, last: "book:8.2".
   The keys are the manifest's own names, so progress survives a page update. */
let PR = { v: 1, opened: {}, answers: {}, last: null, beat: '' };   // beat: the heading being read in the last section
const pkey = s => `${s.book.name}:${s.num}`;
const wasOpened = s => !!PR.opened[pkey(s)];
const readCount = ch => ch.children.filter(wasOpened).length;
const answersSeen = s => PR.answers[pkey(s)] || [];
function saveProgress() { store.set('progress', PR); }
function loadProgress() {
  const d = store.get('progress');
  if (d && d.v === 1 && d.opened && d.answers) PR = d;
}
/** Progress as one line of text, for moving between browsers. */
const progressText = () => 'understudy-progress ' + JSON.stringify(PR);
/** Add pasted progress to what is here. Returns what was added, or null if the text is not progress. */
function mergeProgress(text) {
  let d;
  try { d = JSON.parse(String(text).trim().replace(/^understudy-progress\s*/, '')); } catch (e) { return null; }
  if (!d || d.v !== 1 || typeof d.opened !== 'object' || typeof d.answers !== 'object' || !d.opened || !d.answers) return null;
  let sections = 0, answers = 0;
  for (const [k, v] of Object.entries(d.opened)) if (typeof k === 'string' && !PR.opened[k]) { PR.opened[k] = Number(v) || 1; sections++; }
  for (const [k, list] of Object.entries(d.answers)) {
    if (!Array.isArray(list)) continue;
    const have = new Set(PR.answers[k] || []);
    for (const i of list) if (Number.isInteger(i) && i >= 0 && i < 500 && !have.has(i)) { have.add(i); answers++; }
    PR.answers[k] = [...have].sort((a, b) => a - b);
  }
  if (!PR.last && typeof d.last === 'string') { PR.last = d.last; PR.beat = /^[a-z0-9-]*$/.test(d.beat || '') ? d.beat || '' : ''; }
  saveProgress();
  return { sections, answers };
}
