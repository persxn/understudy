/* =====================================================================
   5. THE TREE (WAI-ARIA tree view, lazy rows): book, part, chapter, section
   ===================================================================== */
const treeEl = $('#tree'), treeScroll = $('#tree-scroll'), stickyEl = $('#sticky');
const rowEls = new Map(); // node id -> treeitem element, only for rows in the DOM
let roving = null;
const TICK = '<svg class="tick" viewBox="0 0 12 12" aria-hidden="true"><path d="M2 6.5 5 9.5 10 3"/></svg>';
const segOf = n => n.kind === 'shelf' ? 'book/' : n.kind === 'book' ? n.seg + '/' : n.title;
const numOf = n => n.kind === 'section' ? n.num : n.kind === 'chapter' ? String(n.n) : '';
const statOf = n => isDone(n) ? 'written' : n.state === 'writing' ? 'writing' : 'planned';

function nodeLabel(n) {
  if (n.kind === 'section') return `Section ${n.num}, ${n.title}, ${isDone(n) ? 'written' : 'planned'}, level ${n.level} ${LEVELS[n.level - 1]}${wasOpened(n) ? ', opened' : ''}`;
  if (n.kind === 'chapter') { const r = readCount(n); return `Chapter ${n.n}, ${n.title}, ${STATE[n.state] || n.state}, ${n.written} of ${plural(n.total, 'section')} written${n.unrun ? `, ${n.unrun} not run` : ''}${r ? `, ${r} opened` : ''}`; }
  const what = n.kind === 'shelf' ? 'book, your shelf' : n.kind === 'book' ? `${n.title}, book, folder ${n.seg}` : `${n.title}, part`;
  return `${what}, ${n.written} of ${plural(n.total, 'chapter')} written`;
}
function hl(text) { // mark the matching part with <mark>
  const q = S.q.trim();
  if (!q) return esc(text);
  const i = text.toLowerCase().indexOf(q.toLowerCase());
  if (i < 0) return esc(text);
  return esc(text.slice(0, i)) + '<mark>' + esc(text.slice(i, i + q.length)) + '</mark>' + esc(text.slice(i + q.length));
}
function hlNode(n, text) { // a new match wipes its mark in; a match that stays does not repeat it
  const h = hl(text);
  return S.filt && S.filt.fresh && S.filt.fresh.has(n) && !M.reduced ? h.replace('<mark>', '<mark class="fresh">') : h;
}
function rowHTML(n) {
  if (n.kind === 'section') {
    const sq = [1, 2, 3, 4, 5].map(l => `<i${l <= n.level ? ' class="on"' : ''}></i>`).join('');
    return `<span class="lead"><span class="stat ${statOf(n)}"></span><span class="name"><span class="no">${esc(n.num)}</span> ${hlNode(n, n.title)} ` +
      `<span class="meta"><span class="lv">${sq}</span>${wasOpened(n) ? TICK : ''}</span></span></span>`;
  }
  const count = `<span class="count">${n.written}/${n.total}</span>`;
  if (n.kind === 'chapter') {
    const r = readCount(n);
    return `<span class="lead"><span class="disc"></span><span class="stat ${statOf(n)}"></span><span class="name"><span class="no">${esc(n.n)}</span> ${hlNode(n, n.title)}` +
      `${n.unrun ? ` <span class="meta">${n.unrun} not run</span>` : ''}${r ? ` <span class="meta">${r === n.written ? TICK : ''}${r}/${n.written} read</span>` : ''}</span></span>${count}`;
  }
  return `<span class="lead"><span class="disc"></span><span class="name">${hlNode(n, segOf(n))}</span></span>${count}`;
}
/* ---- filter ---- */
function filterActive() { return S.q.trim() !== '' || S.chip !== 'all'; }
function chipOk(ch) {
  if (S.chip === 'written') return isDone(ch);
  if (S.chip === 'planned') return !isDone(ch);
  if (S.chip === 'unread') return ch.readable && readCount(ch) < ch.written;
  return true;
}
function computeFilter() {
  const q = S.q.trim().toLowerCase();
  const match = new Set(), keep = new Set();
  const has = t => t.toLowerCase().includes(q);
  for (const n of S.book.order) {
    if (n.kind === 'chapter') { if (chipOk(n) && (!q || has(`${n.n} ${n.title}`))) match.add(n); }
    else if (n.kind === 'section') { if (q && chipOk(n.chapter) && has(`${n.num} ${n.title}`)) match.add(n); }
    else if (q && S.chip === 'all' && n.kind !== 'shelf' && (has(segOf(n)) || has(n.title))) match.add(n);
  }
  for (const n of match) for (let p = n; p && !keep.has(p); p = p.parent) keep.add(p);
  return { match, keep, chapters: [...match].filter(n => n.kind === 'chapter').length, sections: [...match].filter(n => n.kind === 'section').length };
}
function visibleKids(n) {
  if (!S.filt) return n.children;
  const kept = n.children.filter(c => S.filt.keep.has(c));
  if (kept.length) return kept;
  return S.filt.match.has(n) ? n.children.filter(c => c.kind !== 'chapter' || chipOk(c)) : [];
}
function applyFilter(announce = true) {
  if (filterActive()) {
    if (!S.saved) S.saved = new Set(S.open);
    const was = S.filt ? S.filt.match : new Set();
    S.filt = computeFilter();
    S.filt.fresh = new Set([...S.filt.match].filter(n => !was.has(n)));
    S.open = new Set([...S.filt.keep].filter(n => isBranch(n) && n.children.some(c => S.filt.keep.has(c))).map(n => n.id));
    S.open.add(S.book.root.id);
    renderTree();
    const f = S.filt, other = f.match.size - f.chapters - f.sections;
    if (announce) live(f.match.size ? [f.chapters && plural(f.chapters, 'chapter'), f.sections && plural(f.sections, 'section'), other && plural(other, 'book or part')].filter(Boolean).join(', ') + ' in the tree' : 'Nothing in the tree matches', 350);
  } else {
    S.filt = null;
    if (S.saved) { S.open = S.saved; S.saved = null; }
    renderTree();
    if (announce) live('Filter cleared, tree restored', 350);
  }
  syncChips(); updateStatus(); persist();
}
function syncChips() { $$('[data-chip]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.chip === S.chip))); }
function leaveFilter() { // keep the current open state, drop the filter
  if (!filterActive() && !S.saved) return;
  S.q = ''; $('#q').value = ''; S.chip = 'all'; S.filt = null; S.saved = null; syncChips(); closeResults();
}

/* ---- rendering ---- */
function makeItem(n, level, size, pos) {
  const li = document.createElement('li');
  li.setAttribute('role', 'treeitem');
  li.id = 'ti-' + n.id;
  li.dataset.id = n.id;
  li.className = `ti ${n.kind}${isBranch(n) ? ' branch' : ''}`;
  li.setAttribute('aria-level', level);
  li.setAttribute('aria-setsize', size);
  li.setAttribute('aria-posinset', pos);
  li.setAttribute('aria-selected', String(n.id === S.sel));
  li.setAttribute('aria-label', nodeLabel(n));
  li.tabIndex = -1;
  const row = document.createElement('div');
  row.className = 'row';
  row.innerHTML = rowHTML(n);
  li.appendChild(row);
  rowEls.set(n.id, li);
  if (isBranch(n)) {
    const open = S.open.has(n.id);
    li.setAttribute('aria-expanded', String(open));
    if (open) li.appendChild(makeGroup(n, level + 1));
  }
  return li;
}
function makeGroup(n, level) { // children rows are created only when a row opens
  const ul = document.createElement('ul');
  ul.setAttribute('role', 'group');
  ul.className = 'grp';
  const kids = visibleKids(n);
  kids.forEach((c, i) => ul.appendChild(makeItem(c, level, kids.length, i + 1)));
  return ul;
}
function renderTree() {
  rowEls.clear();
  treeEl.textContent = '';
  treeEl.appendChild(makeItem(S.book.root, 1, 1, 1));
  const target = [S.focus, S.sel, S.book.root.id].find(id => id && rowEls.has(id));
  setRoving(target);
  updateDepthButtons();
  scheduleSticky();
}
/** Redraw the rows that show reading progress, where they are. */
function refreshRows() {
  for (const [id, li] of rowEls) {
    const n = S.book.byId.get(id);
    if (n.kind !== 'section' && n.kind !== 'chapter') continue;
    li.firstElementChild.innerHTML = rowHTML(n);
    li.setAttribute('aria-label', nodeLabel(n));
  }
}
function setRoving(id) {
  if (roving && rowEls.get(roving)) rowEls.get(roving).tabIndex = -1;
  const li = rowEls.get(id) || rowEls.get(S.book.root.id);
  li.tabIndex = 0; roving = li.dataset.id; S.focus = roving;
}
function visibleRows() { return [...treeEl.querySelectorAll('[role="treeitem"]')]; }
function setOpen(n, open, anim) {
  if (!isBranch(n)) return;
  if (open) S.open.add(n.id); else S.open.delete(n.id);
  const li = rowEls.get(n.id);
  if (!li) return;
  li.setAttribute('aria-expanded', String(open));
  li.querySelectorAll(':scope > .grp.leaving').forEach(x => x.remove()); // a closing group still fading out
  const g = li.querySelector(':scope > [role="group"]');
  if (open && !g) { const ng = makeGroup(n, Number(li.getAttribute('aria-level')) + 1); li.appendChild(ng); if (anim) revealGroup(ng); }
  if (!open && g) {
    const hadFocus = g.contains(document.activeElement);
    g.querySelectorAll('[role="treeitem"]').forEach(x => rowEls.delete(x.dataset.id));
    if (anim && M.move()) leaveGroup(g); else g.remove();
    if (!rowEls.has(roving)) setRoving(n.id);
    if (hadFocus) li.focus({ preventScroll: true });
  }
}
/* Opened with a pointer: rows rise in top to bottom while the guide draws
   downward; the whole stagger is capped at 160 ms. Keyboard: instant. */
function revealGroup(g) {
  if (!M.move()) return;
  const items = [...g.children].slice(0, 24); // rows far below the fold need no entrance
  const step = items.length > 1 ? Math.min(22, 160 / (items.length - 1)) : 0;
  items.forEach((li, i) => {
    const o = { duration: 140, delay: i * step, easing: EASE_OUT, fill: 'backwards' };
    M.run(li.firstElementChild, [{ opacity: 0, transform: 'translateY(6px)' }, { opacity: 1, transform: 'none' }], o);
    M.run(li, [{ transform: 'scaleY(0)' }, { transform: 'scaleY(1)' }], Object.assign({ pseudoElement: '::before' }, o));
    M.run(li, [{ transform: 'scaleX(0)' }, { transform: 'scaleX(1)' }], Object.assign({ pseudoElement: '::after' }, o, { delay: i * step + 40 }));
  });
}
/* Closed with a pointer: the rows leave the tree's semantics at once and
   fade up and out in 110 ms; only then do they leave the page. */
function leaveGroup(g) {
  g.classList.add('leaving');
  g.inert = true;
  g.setAttribute('aria-hidden', 'true');
  for (const el of [g, ...g.querySelectorAll('*')]) {
    for (const a of ['role', 'id', 'tabindex', 'aria-selected', 'aria-level', 'aria-setsize', 'aria-posinset', 'aria-label', 'aria-expanded']) {
      if (a === 'aria-expanded' && el.getAttribute(a) === 'true') { el.dataset.open = '1'; }
      el.removeAttribute(a);
    }
  }
  const a = M.run(g, [{ opacity: 1, transform: 'none' }, { opacity: 0, transform: 'translateY(-4px)' }], { duration: 110, easing: EASE_OUT, fill: 'forwards' });
  if (a) a.onfinish = () => g.remove(); else g.remove();
}
function openSubtree(n, anim) { // Shift+click, Shift+Enter
  const walk = m => { if (isBranch(m)) { S.open.add(m.id); m.children.forEach(walk); } };
  walk(n);
  const li = rowEls.get(n.id);
  if (li) { // rebuild just this subtree
    const g = li.querySelector(':scope > [role="group"]');
    if (g) { g.querySelectorAll('[role="treeitem"]').forEach(x => rowEls.delete(x.dataset.id)); g.remove(); }
    li.setAttribute('aria-expanded', 'true');
    const ng = makeGroup(n, Number(li.getAttribute('aria-level')) + 1);
    li.appendChild(ng);
    if (anim) revealGroup(ng);
  }
  treeChanged();
}
function revealInTree(n) { // open the ancestors so the row exists
  const chain = [];
  for (let p = n.parent; p; p = p.parent) chain.unshift(p);
  if (S.filt && !S.filt.keep.has(n)) return false;
  for (const p of chain) if (!S.open.has(p.id) || !rowEls.has(p.id)) setOpen(p, true);
  return rowEls.has(n.id);
}
function treeChanged() { updateDepthButtons(); updateStatus(); persist(); scheduleSticky(); }
function markSelected() {
  treeEl.querySelectorAll('[aria-selected="true"]').forEach(li => li.setAttribute('aria-selected', 'false'));
  const li = rowEls.get(S.sel);
  if (li) li.setAttribute('aria-selected', 'true');
}
function maxPinned() { return Math.max(1, Math.min(4, Math.floor(treeScroll.clientHeight * 0.34 / stickyRowH()))); }
function stickyRowH() { return parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--row-pad')) * 2 + 22 + 4; }
function ensureRowVisible(li) {
  const row = li.firstElementChild;
  const cr = treeScroll.getBoundingClientRect(), rr = row.getBoundingClientRect();
  if (!cr.height) return;
  const n = S.book.byId.get(li.dataset.id);
  const pinned = Math.min(n.nest, maxPinned()) * stickyRowH();
  if (rr.top < cr.top + pinned + 4) treeScroll.scrollTop -= (cr.top + pinned + 4 - rr.top);
  else if (rr.bottom > cr.bottom - 4) treeScroll.scrollTop += Math.min(rr.bottom - cr.bottom + 4, rr.top - cr.top - pinned - 4);
}
function focusRow(id) {
  const li = rowEls.get(id);
  if (!li) return;
  setRoving(id);
  li.focus({ preventScroll: true });
  ensureRowVisible(li);
  scheduleSticky();
}

/* ---- tree keyboard: the full APG tree view pattern ---- */
const typeahead = { buf: '', t: 0 };
const rowText = n => (numOf(n) ? `${numOf(n)} ${n.title}` : segOf(n)).toLowerCase();
const typeText = n => (n.kind === 'chapter' || n.kind === 'section' ? n.title : segOf(n)).toLowerCase();
treeEl.addEventListener('keydown', e => {
  const li = e.target.closest('[role="treeitem"]');
  if (!li || e.altKey || e.ctrlKey || e.metaKey) return;
  const n = S.book.byId.get(li.dataset.id);
  const rows = visibleRows(), i = rows.indexOf(li);
  const isOpen = li.getAttribute('aria-expanded') === 'true';
  let handled = true;
  switch (e.key) {
    case 'ArrowDown': if (i < rows.length - 1) focusRow(rows[i + 1].dataset.id); break;
    case 'ArrowUp': if (i > 0) focusRow(rows[i - 1].dataset.id); break;
    case 'Home': focusRow(rows[0].dataset.id); break;
    case 'End': focusRow(rows[rows.length - 1].dataset.id); break;
    case 'ArrowRight':
      if (isBranch(n)) {
        if (!isOpen) { setOpen(n, true); treeChanged(); }
        else { const first = li.querySelector(':scope > [role="group"] > [role="treeitem"]'); if (first) focusRow(first.dataset.id); }
      }
      break;
    case 'ArrowLeft':
      if (isBranch(n) && isOpen) { setOpen(n, false); treeChanged(); }
      else if (n.parent) focusRow(n.parent.id);
      break;
    case 'Enter': case ' ':
      if (e.key === 'Enter' && e.shiftKey && isBranch(n)) { openSubtree(n); select(n.id, { from: 'tree', anim: true }); break; }
      if (e.key === 'Enter' && n.kind === 'section' && S.sel === n.id && readTarget(n)) { go(readTarget(n).id); break; } // Enter again on the selected section opens it
      if (isBranch(n)) { setOpen(n, !isOpen); treeChanged(); }
      select(n.id, { from: 'tree', anim: true });
      break;
    case '*': {
      const sibs = n.parent ? visibleKids(n.parent) : [n];
      for (const s of sibs) if (isBranch(s)) setOpen(s, true);
      treeChanged();
      break;
    }
    default:
      if (e.key.length === 1 && /\S/.test(e.key)) {
        clearTimeout(typeahead.t);
        typeahead.buf += e.key.toLowerCase();
        typeahead.t = setTimeout(() => { typeahead.buf = ''; }, 500);
        const b = typeahead.buf, same = [...b].every(c => c === b[0]);
        const order = rows.slice(i + 1).concat(rows.slice(0, i + 1));
        // a fresh buffer starts after the current row; a growing one may stay on it
        const pool = b.length > 1 && !same ? [li].concat(order.filter(r => r !== li)) : order;
        const starts = (r, s) => { const m = S.book.byId.get(r.dataset.id); return typeText(m).startsWith(s) || rowText(m).startsWith(s); };
        const hit = pool.find(r => starts(r, b)) || (same ? pool.find(r => starts(r, b[0])) : null);
        if (hit) focusRow(hit.dataset.id);
      } else handled = false;
  }
  if (handled) e.preventDefault();
});
treeEl.addEventListener('click', e => {
  const li = e.target.closest('[role="treeitem"]');
  if (!li || !e.target.closest('.row')) return;
  const n = S.book.byId.get(li.dataset.id);
  if (isBranch(n)) {
    if (e.shiftKey) openSubtree(n, true);
    else { setOpen(n, li.getAttribute('aria-expanded') !== 'true', true); treeChanged(); }
  }
  setRoving(n.id);
  li.focus({ preventScroll: true });
  select(n.id, { from: 'tree', anim: true });
  if (band === 'phone' && n.kind === 'section') setTab('detail'); // on a phone a tapped section shows what it is, and the way in
});
treeEl.addEventListener('dblclick', e => { // a pointer shortcut for "Read"; the detail panel has the button
  const li = e.target.closest('[role="treeitem"]'), n = li && S.book.byId.get(li.dataset.id);
  if (n && n.kind === 'section' && readTarget(n)) go(readTarget(n).id);
});
treeEl.addEventListener('focusin', e => { const li = e.target.closest('[role="treeitem"]'); if (li && li.dataset.id !== roving) setRoving(li.dataset.id); });

/* ---- depth (tree -L), collapse all ---- */
function folderSetToDepth(L) {
  const s = new Set();
  for (const n of S.book.order) if (isBranch(n) && n.depth < L) s.add(n.id);
  return s;
}
function maxDepth() { return Math.max(...S.book.order.map(n => n.depth)); }
function setDepth(L) {
  leaveFilter();
  S.open = folderSetToDepth(L === 'all' ? Infinity : L);
  renderTree();
  treeChanged();
}
function collapseAll() { leaveFilter(); S.open = new Set(); renderTree(); treeChanged(); }
function visibleOpenFolders() { return [...rowEls.keys()].filter(id => S.open.has(id)); }
function currentDepthL() { // the -L that the visible rows correspond to
  let L = 0;
  for (const id of rowEls.keys()) L = Math.max(L, S.book.byId.get(id).depth);
  return L;
}
function updateDepthButtons() {
  if (!S.book) return;
  const vis = new Set(visibleOpenFolders());
  const eq = (a, b) => a.size === b.size && [...a].every(x => b.has(x));
  $$('[data-depth]').forEach(b => {
    const L = b.dataset.depth === 'all' ? Infinity : Number(b.dataset.depth);
    b.setAttribute('aria-pressed', String(!S.filt && eq(vis, new Set([...folderSetToDepth(L)].filter(id => S.book.byId.get(id).children.length)))));
  });
}

/* ---- sticky ancestors ---- */
let stickyRaf = 0;
function scheduleSticky() { if (!stickyRaf) stickyRaf = requestAnimationFrame(() => { stickyRaf = 0; updateSticky(); }); }
function updateSticky() {
  if (!S.book) return;
  const cr = treeScroll.getBoundingClientRect();
  if (!cr.height) return;
  const rows = visibleRows();
  const rh = stickyRowH();
  let pinned = [];
  for (let pass = 0; pass < 2; pass++) {
    const topY = cr.top + pinned.length * rh;
    let first = null;
    for (const li of rows) if (li.firstElementChild.getBoundingClientRect().bottom > topY + 2) { first = li; break; }
    if (!first) break;
    const anc = [];
    for (let p = S.book.byId.get(first.dataset.id).parent; p; p = p.parent) {
      const el = rowEls.get(p.id);
      if (el && el.firstElementChild.getBoundingClientRect().top < topY - 1) anc.unshift(p);
    }
    pinned = anc.slice(-maxPinned());
  }
  stickyEl.style.right = (treeScroll.offsetWidth - treeScroll.clientWidth) + 'px';
  stickyEl.innerHTML = pinned.map(p => `<div class="sticky-row" data-id="${esc(p.id)}" style="padding-left:${12 + p.nest * 22}px"><span class="disc open"></span><span class="sn">${esc(numOf(p) ? `${numOf(p)} ${p.title}` : segOf(p))}</span><span class="count">${p.written}/${p.total}</span></div>`).join('');
  // never let the pinned rows cover more than about a third of the tree
  while (stickyEl.children.length > 1 && stickyEl.offsetHeight > treeScroll.clientHeight * 0.36) stickyEl.firstElementChild.remove();
}
treeScroll.addEventListener('scroll', scheduleSticky, { passive: true });
stickyEl.addEventListener('click', e => { // pointer convenience; the keyboard has Left to reach a parent
  const r = e.target.closest('.sticky-row');
  if (!r) return;
  const li = rowEls.get(r.dataset.id);
  if (!li) return;
  treeScroll.scrollTop += li.getBoundingClientRect().top - treeScroll.getBoundingClientRect().top - Math.min(S.book.byId.get(r.dataset.id).nest, maxPinned()) * stickyRowH();
  focusRow(r.dataset.id);
});

/* ---- status line: the state as the command that would produce it ---- */
function updateStatus() {
  if (!S.book) return;
  let cmd = 'tree book/', note = '';
  if (S.filt) {
    if (S.q.trim()) cmd += ` | grep -i "${S.q.trim()}"`;
    if (S.chip !== 'all') cmd += ` | grep ${S.chip}`;
  } else if (!S.open.has(S.book.root.id)) {
    cmd = 'ls -d book/';
  } else {
    const L = currentDepthL(), full = folderSetToDepth(L), vis = new Set(visibleOpenFolders());
    if (L < maxDepth()) cmd += ` -L ${L}`;
    const missing = [...full].filter(id => !vis.has(id) && S.book.byId.get(id).children.length).length;
    if (missing) note = `, ${full.size - missing} of ${full.size} rows open to that depth`;
  }
  let shown = 0, written = 0;
  for (const id of rowEls.keys()) { const n = S.book.byId.get(id); if (n.kind === 'chapter') { shown++; if (isDone(n)) written++; } }
  $('#cmd').textContent = cmd;
  $('#counts').textContent = `${plural(shown, 'chapter')} shown, ${written} written${note}`;
}

/* =====================================================================
   6. GRAPH VIEW (drawing, pan and zoom, keyboard)
   A book is a cluster; open, it is a band of chapter boxes; a chapter box
   opens into the list of its sections.
   ===================================================================== */
const svg = $('#graph'), vp = $('#vp'), stage = $('#stage');
const G = { layout: null, model: null, k: 1, tx: 0, ty: 0, focus: null, els: new Map(), lastMs: 0, justDragged: false, fitted: false, cols: 3, user: false }; // user: the reader has moved the view themselves
const ZMIN = 0.3, ZMAX = 2, LABEL_K = 11 / 15; // 15 px is the smallest graph text; never show it under 11 px
const measure = (() => {
  const ctx = document.createElement('canvas').getContext('2d');
  const serif = getComputedStyle(document.documentElement).getPropertyValue('--serif').trim();
  const cache = new Map();
  const FONT = { title: `16px ${serif}`, cluster: `700 17px ${serif}`, row: `15px ${serif}` };
  return (s, kind) => {
    const key = kind + '|' + s;
    if (cache.has(key)) return cache.get(key);
    ctx.font = FONT[kind];
    const w = ctx.measureText(s).width;
    cache.set(key, w);
    return w;
  };
})();
const unitKeyOf = n => { // which drawn box stands for a node
  if (!G.layout || !n) return null;
  if (n.kind === 'book') return S.expanded.has(n.id) ? 'band:' + n.id : n.id;
  if (n.kind === 'chapter') return S.expanded.has(n.book.id) ? n.id : n.book.id;
  if (n.kind === 'section') return !S.expanded.has(n.book.id) ? n.book.id : G.layout.rows.has(n.id) ? n.id : n.chapter.id;
  return null; // the shelf and the parts have no box
};
function buildGraphModel(book, expanded, openCh) {
  return { groups: book.books.map(b => {
    const open = expanded.has(b.id), chs = book.chapters.filter(c => c.book === b);
    return { id: b.id, node: b, open,
      units: open ? chs.map(c => ({ id: c.id, kind: 'chapter', node: c, group: b.id, open: openCh.has(c.id) && c.children.length > 0 })) : [{ id: b.id, kind: 'cluster', node: b, group: b.id }],
      needs: open ? chs.flatMap(c => c.needs.map(m => ({ from: m, to: c.id }))) : [] };
  }) };
}

function pmSVG(x, y, plus) {
  return `<rect class="pm" x="${x}" y="${y}" width="18" height="18"/><line class="pml" x1="${x + 4}" y1="${y + 9}" x2="${x + 14}" y2="${y + 9}"/>` +
    (plus ? `<line class="pml" x1="${x + 9}" y1="${y + 4}" x2="${x + 9}" y2="${y + 14}"/>` : '');
}
function chapterSVG(u) {
  const n = u.node, w = u.w, h = u.h;
  const t = u.lines.map((l, i) => `<tspan x="${GL.PAD}" y="${GL.PAD + 15 + i * GL.TLH}">${esc(l)}</tspan>`).join('');
  const y0 = GL.PAD + u.lines.length * GL.TLH + 10;
  let sq = '';
  for (let l = 1; l <= 5; l++) sq += `<rect class="sq${n.levels.includes(l) ? ' on' : ''}" x="${GL.PAD + (l - 1) * 13}" y="${y0 + 1}" width="10" height="10"/>`;
  const sx = GL.PAD + 5 * 13 + 10;
  return `<rect class="sh" x="6" y="6" width="${w}" height="${h}"/><rect class="box" width="${w}" height="${h}"/><rect class="hd" x="2" y="2" width="${w - 4}" height="${u.headH - (u.open ? 3 : 4)}"/><path class="tab" d="M0 0H16L0 16Z"/>` +
    `<text class="t">${t}</text>${sq}<rect class="st ${statOf(n)}" x="${sx}" y="${y0}" width="12" height="12"/>` +
    (n.state === 'writing' ? `<rect class="sthalf" x="${sx}" y="${y0}" width="6" height="12"/>` : '') +
    `<text class="m" x="${sx + 18}" y="${y0 + 12}">${n.state === 'writing' ? 'being written' : statOf(n)}</text>` +
    (n.children.length ? pmSVG(w - GL.PAD - 18, GL.PAD - 1, !u.open) : '') +
    (u.open ? `<line class="hr" x1="0" y1="${u.headH}" x2="${w}" y2="${u.headH}"/>` : '') +
    `<rect class="ring" x="-7" y="-7" width="${w + 14}" height="${(u.open ? u.headH : h) + 14}"/>`;
}
function rowSVG(r) {
  const t = r.lines.map((l, i) => `<tspan x="${GL.PAD + 20}" y="${5 + 13 + i * GL.RLH}">${esc(l)}</tspan>`).join('');
  return `<rect class="rbg" x="2" width="${r.w - 4}" height="${r.h}"/><rect class="st ${statOf(r.node)}" x="${GL.PAD}" y="${5 + 3}" width="10" height="10"/>` +
    `<text class="r">${t}</text><rect class="ring" x="5" y="1" width="${r.w - 10}" height="${r.h - 2}"/>`;
}
function clusterSVG(u) {
  const n = u.node, w = u.w, h = u.h;
  const t = u.lines.map((l, i) => `<tspan x="${GL.PAD}" y="${GL.PAD + 16 + i * GL.CLH}">${esc(l)}</tspan>`).join('');
  const yc = GL.PAD + u.lines.length * GL.CLH + 6 + 14;
  const ys = yc + 13;
  let sq = '';
  S.book.chapters.filter(c => c.book === n).forEach((c, i) => {
    const r = Math.floor(i / u.sqPer), k = i % u.sqPer;
    sq += `<rect class="sq${isDone(c) ? ' on' : ''}" x="${GL.PAD + k * 12}" y="${ys + r * 12}" width="9" height="9"/>`;
  });
  return `<rect class="sh" x="6" y="6" width="${w}" height="${h}"/><rect class="box" width="${w}" height="${h}"/><path class="tab" d="M0 0H16L0 16Z"/>` +
    `<text class="tc">${t}</text><text class="m" x="${GL.PAD}" y="${yc}">${n.written}/${n.total} written</text>${sq}` +
    pmSVG(w - GL.PAD - 18, GL.PAD - 1, true) + `<rect class="ring" x="-7" y="-7" width="${w + 14}" height="${h + 14}"/>`;
}
function bandheadSVG(b) {
  const w = GL.W + GL.BPAD, h = b.headH;
  const t = b.headLines.map((l, i) => `<tspan x="${GL.PAD}" y="${GL.PAD + 16 + i * GL.CLH}">${esc(l)}</tspan>`).join('');
  return `<rect class="sh" x="6" y="6" width="${w}" height="${h}"/><rect class="box" width="${w}" height="${h}"/><text class="tc">${t}</text>` +
    `<text class="m" x="${GL.PAD}" y="${GL.PAD + b.headLines.length * GL.CLH + 4 + 14}">${b.node.written}/${b.node.total} written, open</text>` +
    pmSVG(w - GL.PAD - 18, GL.PAD - 1, false) + `<rect class="ring" x="-5" y="-5" width="${w + 10}" height="${h + 10}"/>`;
}
function edgeSVG(e) {
  const d = 'M' + e.points.map(p => p[0] + ' ' + p[1]).join('L');
  const [x, y] = e.points[e.points.length - 1];
  return `<g data-e="${esc(e.id)}"><path class="edge" d="${d}"/><polygon class="ah" points="${x},${y} ${x - 10},${y - 5.5} ${x - 10},${y + 5.5}"/></g>`;
}
/* The graph adapts to its own panel, not the window: compact boxes when
   narrow, and as many columns to a row as fit at a readable size. */
function graphCompact() { const w = stage.clientWidth; return w > 0 && w < 600; }
function graphCols() {
  const w = stage.clientWidth;
  if (!w) return G.cols;
  const bw = (w < 600 ? 192 : 224) + GL.GAPMIN;
  return Math.max(2, Math.min(6, Math.floor((w / 0.8 - 2 * (GL.BPAD + GL.MARGIN) + GL.GAPMIN - 30) / bw)));   // a row must fit at 80% or more
}
function renderGraph(anchor) {
  // anchor: { key, sx, sy } keeps a box where the reader was looking
  cancelGraphMotion();
  G.compact = graphCompact(); G.cols = graphCols();
  GL.W = G.compact ? 192 : 224; GL.WC = G.compact ? 152 : 168;
  const t0 = performance.now();
  G.model = buildGraphModel(S.book, S.expanded, S.openCh);
  G.layout = layoutShelf(G.model, measure, G.cols, Math.max(360, (stage.clientWidth || 720) / 0.85));
  G.lastMs = performance.now() - t0;
  const L = G.layout;
  let bands = '', nodes = '', edges = '';
  const node = (cls, key, x, y, inner) => `<g class="node ${cls}" data-key="${esc(key)}" transform="translate(${x},${y})" tabindex="-1" role="button">${inner}</g>`;
  for (const b of L.bands) {
    bands += `<g class="band" data-b="${esc(b.id)}"><rect class="bandbox" x="${b.x}" y="${b.y}" width="${b.w}" height="${b.h}"/></g>`;
    nodes += node('bandhead', 'band:' + b.id, b.x, b.y, bandheadSVG(b));
  }
  for (const u of L.units.values()) nodes += node(u.kind + (u.open ? ' open' : ''), u.id, u.x, u.y, u.kind === 'chapter' ? chapterSVG(u) : clusterSVG(u));
  for (const r of L.rows.values()) nodes += node('sec', r.id, r.x, r.y, rowSVG(r));
  for (const e of L.edges) edges += edgeSVG(e);
  $('#g-bands').innerHTML = bands;
  $('#g-edges').innerHTML = edges;
  $('#g-nodes').innerHTML = nodes;
  G.els = new Map([...$('#g-nodes').children].map(el => [el.dataset.key, el]));
  G.edgeEls = new Map([...$('#g-edges').children].map(el => [el.dataset.e, el]));
  if (!G.focus || !G.els.has(G.focus)) G.focus = (S.sel && unitKeyOf(S.book.byId.get(S.sel))) || [...G.els.keys()][0];
  if (!G.els.has(G.focus)) G.focus = [...G.els.keys()][0];
  setGraphRoving(G.focus);
  if (anchor) {
    const r = boxOf(anchor.key);
    if (r) { G.tx = anchor.sx - r.x * G.k; G.ty = anchor.sy - r.y * G.k; }
  }
  applyGraphClasses();
  applyView();
}
function boxOf(key) { // box of a drawn node in graph units
  if (!G.layout || !key) return null;
  if (key.startsWith('band:')) { const b = G.layout.bands.find(x => 'band:' + x.id === key); return b && { x: b.x, y: b.y, w: GL.W + GL.BPAD, h: b.headH }; }
  const u = G.layout.units.get(key) || G.layout.rows.get(key);
  return u && { x: u.x, y: u.y, w: u.w, h: u.h };
}
function nodeAria(key) {
  const sel = S.sel && S.book.byId.get(S.sel);
  const rel = G.rel || {};
  if (key.startsWith('band:')) {
    const n = S.book.byId.get(key.slice(5));
    return `${n.title}, open book, ${plural(n.total, 'chapter')}, ${n.written} written. Press Enter to close it.`;
  }
  const n = S.book.byId.get(key);
  const titles = ids => ids.map(id => { const m = S.book.byId.get(id); return `${numOf(m)} ${m.title}`; }).join(', ') || 'nothing';
  if (n.kind === 'book') return `${n.title}, book, ${plural(n.total, 'chapter')}, ${n.written} written. Closed: press Enter to open it.`;
  let s = n.kind === 'chapter'
    ? `Chapter ${n.n}, ${n.title}. ${STATE[n.state] || n.state}, ${n.written} of ${plural(n.total, 'section')} written.`
    : `Section ${n.num}, ${n.title}. ${isDone(n) ? 'Written' : 'Planned'}, level ${n.level} ${LEVELS[n.level - 1]}.`;
  s += ` Needs: ${titles(n.needs)}. Unlocks: ${titles(n.unlocks)}.`;
  if (sel && sel.id === n.id) s += ' Selected.';
  else if (rel.anc && rel.anc.has(n.id)) s += ' Needed before the selection.';
  else if (rel.desc && rel.desc.has(n.id)) s += ' Unlocked by the selection.';
  if (n.kind === 'chapter' && n.children.length) s += S.openCh.has(n.id) ? ' Its sections are listed: press Enter to fold them.' : ' Press Enter to list its sections.';
  return s;
}
function applyGraphClasses() {
  if (!G.layout) return;
  const sel = S.sel ? S.book.byId.get(S.sel) : null;
  const rel = !!sel && (sel.kind === 'chapter' || sel.kind === 'section');
  const anc = rel ? ancestorsOf(S.book, sel.id) : new Set();
  const desc = rel ? descendantsOf(S.book, sel.id) : new Set();
  const chOf = set => new Set([...set].map(id => { const n = S.book.byId.get(id); return n.kind === 'section' ? n.chapter.id : n.id; }));
  const selCh = rel ? (sel.kind === 'section' ? sel.chapter.id : sel.id) : null;
  const ancCh = chOf(anc), descCh = chOf(desc);
  ancCh.delete(selCh); descCh.delete(selCh);
  G.rel = { anc, desc, ancCh, descCh, selCh };
  const selKey = sel && unitKeyOf(sel);
  for (const [key, el] of G.els) {
    let cls = '';
    if (key === selKey) cls = 'sel';
    else if (key.startsWith('band:')) cls = '';
    else if (G.layout.rows.has(key)) cls = anc.has(key) ? 'needs' : desc.has(key) ? 'unlocks' : '';
    else if (rel) {
      const u = G.layout.units.get(key);
      if (u.kind === 'chapter') cls = ancCh.has(key) ? 'needs' : descCh.has(key) ? 'unlocks' : key === selCh ? 'holds' : 'quiet';
      else cls = 'quiet';
    }
    el.classList.remove('sel', 'needs', 'unlocks', 'quiet', 'holds');
    if (cls) el.classList.add(cls);
    el.setAttribute('aria-label', nodeAria(key));
  }
  // edges: needs on the chain into the selection, unlocks on the chain out of it
  const front = [], back = [];
  for (const e of G.layout.edges) {
    const el = G.edgeEls.get(e.id);
    let cls = rel ? 'faint' : '';
    if (rel) {
      if (ancCh.has(e.from) && (ancCh.has(e.to) || e.to === selCh)) cls = 'needs';
      else if ((e.from === selCh || descCh.has(e.from)) && descCh.has(e.to)) cls = 'unlocks';
    }
    for (const c of el.children) { c.classList.remove('needs', 'unlocks', 'faint'); if (cls) c.classList.add(cls); }
    (cls === 'needs' || cls === 'unlocks' ? front : back).push(el);
  }
  const ge = $('#g-edges');
  for (const el of back.concat(front)) ge.appendChild(el); // highlighted chains drawn on top
  // the selected box is drawn last so its shadow sits over its neighbours (its section rows stay above it)
  if (selKey && G.els.get(selKey) && G.layout.units.has(selKey)) {
    const gn = $('#g-nodes');
    gn.appendChild(G.els.get(selKey));
    for (const r of G.layout.units.get(selKey).rows || []) gn.appendChild(G.els.get(r.id));
  }
  $('#fit-sel').disabled = !selKey;
  drawMinimap();
}
/* Selected with a pointer: the needs and unlocks edges draw outward from the
   chapter along their paths (stroke-dashoffset), nearer edges first, all
   within 300 ms, so the direction of dependence is seen once. */
function drawRelations() {
  if (!M.move() || !G.layout || !G.rel.selCh) return;
  const hop = new Map([[G.rel.selCh, 0]]); // hops from the selection along the drawn edges, both ways
  for (const dir of ['pred', 'succ']) {
    let front = [G.rel.selCh], d = 0;
    while (front.length) { d++; const next = []; for (const id of front) for (const m of (G.layout[dir].get(id) || [])) if (!hop.has(m)) { hop.set(m, d); next.push(m); } front = next; }
  }
  const items = [];
  for (const e of G.layout.edges) {
    const g = G.edgeEls.get(e.id), path = g && g.querySelector('path');
    if (!path || !(path.classList.contains('needs') || path.classList.contains('unlocks'))) continue;
    const needs = path.classList.contains('needs');
    items.push({ g, path, needs, near: hop.get(needs ? e.to : e.from) || 0 });
  }
  if (!items.length) return;
  const far = Math.max(...items.map(i => i.near)), step = far ? Math.min(60, 140 / far) : 0;
  for (const q of $$('#g-edges path[style]')) q.style.strokeDasharray = '';
  for (const it of items) {
    const L = Math.ceil(it.path.getTotalLength()), p = it.path, delay = it.near * step;
    let dash, from;
    if (it.needs) { dash = `${L} ${L}`; from = -L; }       // solid: grows back from the end nearer the selection
    else {                                                // dashed: the 7 4 pattern unrolls forward, then a gap
      const n = Math.ceil(L / 11), parts = [];
      for (let i = 0; i < n; i++) parts.push(7, 4);
      parts.push(0, L);
      dash = parts.join(' '); from = n * 11;
    }
    p.style.strokeDasharray = dash;
    const a = M.run(p, [{ strokeDashoffset: from }, { strokeDashoffset: 0 }], { duration: 160, delay, easing: EASE_OUT, fill: 'backwards' });
    const ah = it.g.querySelector('.ah');
    const b = !it.needs && ah ? M.run(ah, [{ opacity: 0 }, { opacity: 1 }], { duration: 60, delay: delay + 110, easing: EASE_OUT, fill: 'backwards' }) : null;
    const end = () => { p.style.strokeDasharray = ''; };
    if (a) { graphAnims.push(a); a.finished.then(end, end); } else end();
    if (b) graphAnims.push(b);
  }
}
function setGraphRoving(key) {
  for (const el of G.els.values()) el.setAttribute('tabindex', '-1');
  const el = G.els.get(key);
  if (el) { el.setAttribute('tabindex', '0'); G.focus = key; }
}
function focusGraphNode(key) {
  const el = G.els.get(key);
  if (!el) return;
  setGraphRoving(key);
  el.focus({ preventScroll: true });
  revealBox(key, false);
}

/* ---- view transform ---- */
function stageSize() { return { w: stage.clientWidth, h: stage.clientHeight }; }
function applyView() {
  vp.setAttribute('transform', `translate(${G.tx.toFixed(2)},${G.ty.toFixed(2)}) scale(${G.k.toFixed(4)})`);
  svg.classList.toggle('overview', G.k < LABEL_K - 1e-6);
  $('#ov-note').hidden = !(G.k < LABEL_K - 1e-6);
  $('#z-read').textContent = Math.round(G.k * 100) + '%';
  $('#z-in').disabled = G.k >= ZMAX - 1e-6;
  $('#z-out').disabled = G.k <= ZMIN + 1e-6;
  drawMinimapView();
  scheduleNavkit();
}
/* The way around (pan buttons and the overview map) is shown only when the
   drawing does not fit; it sits in the graph's foot, never on the canvas.
   Deferred a frame so a resize it causes is not seen inside the observer. */
let navRaf = 0;
function scheduleNavkit() { if (!navRaf) navRaf = requestAnimationFrame(() => { navRaf = 0; updateNavkit(); }); }
function updateNavkit() {
  const L = G.layout, s = stageSize();
  if (!L || !s.w) return;
  const x0 = G.tx, y0 = L.minY * G.k + G.ty, x1 = L.width * G.k + G.tx, y1 = L.height * G.k + G.ty;
  const fits = x0 >= -1 && y0 >= -1 && x1 <= s.w + 1 && y1 <= s.h + 1;
  $('#navkit').hidden = fits;
  $('#minimap').hidden = fits || $('#map-btn').getAttribute('aria-pressed') !== 'true';
}
/* ---- the camera: Fit all, Fit selection and centring glide for 260 ms
   (pointer only), driven by rAF and cancelled by any drag, wheel or key ---- */
let cam = null;
function cancelCamera() { if (cam) { cancelAnimationFrame(cam.raf); cam = null; } }
function camera(fn, anim) {
  cancelCamera();
  const from = { k: G.k, tx: G.tx, ty: G.ty };
  fn(); // computes and applies the end state synchronously; nothing paints in between
  const to = { k: G.k, tx: G.tx, ty: G.ty };
  if (!anim || !M.move() || (Math.abs(to.k - from.k) < 1e-4 && Math.hypot(to.tx - from.tx, to.ty - from.ty) < 1)) return;
  Object.assign(G, from); applyView();
  const t0 = performance.now(), dur = M.d(260);
  // zoom is interpolated in log space so the speed of scale change feels even
  const lk0 = Math.log(from.k), lk1 = Math.log(to.k);
  const step = now => {
    const p = Math.min(1, (now - t0) / dur), e = easeInOut(p);
    G.k = Math.exp(lk0 + (lk1 - lk0) * e); G.tx = from.tx + (to.tx - from.tx) * e; G.ty = from.ty + (to.ty - from.ty) * e;
    applyView();
    if (p < 1) cam.raf = requestAnimationFrame(step); else cam = null;
  };
  cam = { raf: requestAnimationFrame(step), to };
}
function zoomAt(k, sx, sy) {
  k = Math.max(ZMIN, Math.min(ZMAX, k));
  const gx = (sx - G.tx) / G.k, gy = (sy - G.ty) / G.k;
  G.k = k; G.tx = sx - gx * k; G.ty = sy - gy * k;
  applyView();
}
function zoomBy(f) { const s = stageSize(); zoomAt(G.k * f, s.w / 2, s.h / 2); }
function fitBox(x, y, w, h, maxK = 1) {
  const s = stageSize();
  if (!s.w || !s.h) return;
  const m = 16;
  const k = Math.max(ZMIN, Math.min(maxK, (s.w - 2 * m) / w, (s.h - 2 * m) / h));
  G.k = k; G.tx = (s.w - w * k) / 2 - x * k; G.ty = (s.h - h * k) / 2 - y * k;
  if (h * k > s.h - 2 * m) G.ty = m - y * k; // too tall: start at the top
  applyView();
}
/* Fit all: the whole drawing, but never smaller than the scale at which the
   smallest label is 11 px. If it does not fit at that scale, keep the
   selection (or the top-left) in view; the minimap shows the rest. */
function fitAll() {
  if (!G.layout) return;
  const L = G.layout;
  fitBox(0, L.minY, L.width, L.height - L.minY, 1);
  if (G.k < LABEL_K) {
    G.k = LABEL_K;
    const s = stageSize();
    const w = L.width * G.k, h = (L.height - L.minY) * G.k;
    G.tx = w < s.w ? (s.w - w) / 2 : 0; G.ty = (h < s.h ? (s.h - h) / 2 : 0) - L.minY * G.k; // overflow starts top-left
    applyView();
    const n = S.sel && S.book.byId.get(S.sel), key = n && unitKeyOf(n);
    if (key) revealBox(key, false);
  }
}
function boundsOf(keys, pad) {
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const k of keys) { const b = k && boxOf(k); if (!b) continue; x0 = Math.min(x0, b.x); y0 = Math.min(y0, b.y); x1 = Math.max(x1, b.x + b.w); y1 = Math.max(y1, b.y + b.h); }
  return isFinite(x0) ? { x: x0 - pad, y: y0 - pad, w: x1 - x0 + 2 * pad, h: y1 - y0 + 2 * pad } : null;
}
function fitSelection() {
  const sel = S.sel && S.book.byId.get(S.sel);
  if (!sel || !unitKeyOf(sel)) return;
  const keys = new Set([unitKeyOf(sel)]);
  if (G.rel) for (const id of [...G.rel.ancCh, ...G.rel.descCh]) keys.add(unitKeyOf(S.book.byId.get(id)));
  const b = boundsOf(keys, 16);
  if (!b) return;
  fitBox(b.x, b.y, b.w, b.h, 1.2);
  if (G.k < LABEL_K) { G.k = LABEL_K; revealBox(unitKeyOf(sel), true); applyView(); } // never below readable
}
/* The first view of a selection: it, what it needs and what it unlocks
   directly, at up to 100%, never under the readable scale. */
function fitNeighbours(n) {
  const key = unitKeyOf(n);
  if (!key) return fitAll();
  const bandOf = n.book && G.layout.bands.find(x => x.id === n.book.id), st = stageSize();
  if (bandOf && Math.min((st.w - 32) / bandOf.w, (st.h - 32) / bandOf.h) >= LABEL_K + 0.01) { // the whole book fits at a readable size: show it
    fitBox(bandOf.x, bandOf.y, bandOf.w, bandOf.h, 1);
    return;
  }
  const keys = new Set([key]);
  for (const id of n.needs.concat(n.unlocks)) keys.add(unitKeyOf(S.book.byId.get(id)));
  const bb = boundsOf(keys, 24);
  if (!bb) return;
  fitBox(bb.x, bb.y, bb.w, bb.h, 1);
  const b = boxOf(key), s = stageSize(), KMIN = 0.85;
  if (G.k < KMIN) { // too wide to show at a comfortable size: keep the text readable, start from what it needs
    G.k = KMIN;
    const bandTop = n.book && G.layout.bands.find(x => x.id === n.book.id);   // show the book's edge and head when they fit
    const left = Math.max(bandTop ? bandTop.x - 16 / G.k : bb.x, b.x + b.w / 2 - s.w / G.k * 0.62);   // the selection a little left of centre
    G.tx = -left * G.k;
    G.ty = s.h / 2 - (b.y + b.h / 2) * G.k;
    if (bandTop && (b.y - bandTop.y) * G.k < s.h - b.h * G.k - 40) G.ty = Math.max(G.ty, 16 - bandTop.y * G.k);
    applyView();
  }
  revealBox(key, true);
}
function revealBox(key, centre) { // centre a box if any part of it is off-screen
  const b = boxOf(key), s = stageSize();
  if (!b || !s.w) return;
  const x = b.x * G.k + G.tx, y = b.y * G.k + G.ty, w = b.w * G.k, h = b.h * G.k, m = 16;
  if (x >= m && y >= m && x + w <= s.w - m && y + h <= s.h - m) return;
  if (w > s.w - 2 * m || h > s.h - 2 * m) { // larger than the stage: show its top-left corner
    G.tx = Math.min(m, s.w / 2 - w / 2) - b.x * G.k; G.ty = m - b.y * G.k;
    if (w <= s.w - 2 * m) G.tx = s.w / 2 - (b.x + b.w / 2) * G.k;
  } else if (centre) { G.tx = s.w / 2 - (b.x + b.w / 2) * G.k; G.ty = s.h / 2 - (b.y + b.h / 2) * G.k; }
  else {
    if (x < m) G.tx += m - x; else if (x + w > s.w - m) G.tx -= x + w - (s.w - m);
    if (y < m) G.ty += m - y; else if (y + h > s.h - m) G.ty -= y + h - (s.h - m);
  }
  applyView();
}

/* ---- opening and closing in place ---- */
function screenOf(key) { const b = boxOf(key); return b && { sx: b.x * G.k + G.tx, sy: b.y * G.k + G.ty }; }
/* ---- motion in the graph: object constancy, then the edges ---- */
let graphAnims = [];
function cancelGraphMotion() {
  for (const a of graphAnims) if (a) a.cancel();
  graphAnims = [];
  $('#g-ghost').textContent = '';
  for (const q of $$('#g-edges path[style]')) q.style.strokeDasharray = '';
}
function graphBefore(leaves) { // where everything is now, before a relayout; `leaves` picks the boxes about to go
  const boxes = new Map();
  for (const k of G.els.keys()) { const b = boxOf(k); if (b) boxes.set(k, b); }
  const bands = new Map(G.layout.bands.map(b => [b.id, { x: b.x, y: b.y }]));
  const leaving = [];
  for (const [k, el] of G.els) if (leaves(k)) leaving.push(el.cloneNode(true));
  return { boxes, bands, leaving, bandEls: new Map([...$('#g-bands').children].map(g => [g.dataset.b, g.cloneNode(true)])), edges: $('#g-edges').cloneNode(true), tx: G.tx, ty: G.ty, k: G.k };
}
/* FLIP, with transforms on each box's <g>: boxes that exist before and after
   glide to their new places; boxes that appear start at `srcKey`'s old place
   at 96% and transparent; boxes that leave shrink into `dstKey`. Edges fade
   out first and are drawn again once the boxes have landed. */
function flipGraph(before, srcKey, dstKey, alias) {
  const ox = (before.tx - G.tx) / G.k, oy = (before.ty - G.ty) / G.k; // old units -> new units
  const T = (x, y, sc) => `translate(${x}px, ${y}px)` + (sc ? ` scale(${sc})` : '');
  const o = { duration: 260, easing: EASE_IN_OUT };
  const add = a => { if (a) graphAnims.push(a); };
  const src = before.boxes.get(srcKey);
  for (const [key, el] of G.els) {
    const to = boxOf(key);
    const from = key === alias ? src : before.boxes.get(key);
    if (from) {
      const fx = from.x + ox, fy = from.y + oy;
      if (Math.abs(fx - to.x) < 0.5 && Math.abs(fy - to.y) < 0.5) continue;
      add(M.run(el, [{ transform: T(fx, fy) }, { transform: T(to.x, to.y) }], o));
    } else if (src) {
      add(M.run(el, [{ transform: T(src.x + ox, src.y + oy, 0.96), opacity: 0 }, { transform: T(to.x, to.y), opacity: 1 }], o));
    }
  }
  const ghost = $('#g-ghost');
  ghost.setAttribute('transform', `translate(${ox},${oy})`);
  for (const g of $('#g-bands').children) {
    const id = g.dataset.b, was = before.bands.get(id), now = G.layout.bands.find(b => b.id === id);
    if (was && now) { const dx = was.x + ox - now.x, dy = was.y + oy - now.y; if (Math.abs(dx) + Math.abs(dy) > 0.5) add(M.run(g, [{ transform: T(dx, dy) }, { transform: 'none' }], o)); }
    else add(M.run(g, [{ opacity: 0 }, { opacity: 1 }], { duration: 140, delay: 200, easing: EASE_OUT, fill: 'backwards' }));
  }
  // the old drawing's edges (and a closing band) fade out where they were
  const old = before.edges; old.removeAttribute('id');
  ghost.appendChild(old);
  add(M.run(old, [{ opacity: 1 }, { opacity: 0 }], { duration: 90, easing: EASE_OUT, fill: 'forwards' }));
  for (const [id, g] of before.bandEls) if (!G.layout.bands.some(b => b.id === id)) {
    g.removeAttribute('data-b'); ghost.appendChild(g);
    add(M.run(g, [{ opacity: 1 }, { opacity: 0 }], { duration: 120, easing: EASE_OUT, fill: 'forwards' }));
  }
  const cl = dstKey && boxOf(dstKey);
  if (cl) for (const el of before.leaving) {
    for (const a of ['tabindex', 'role', 'aria-label', 'data-key']) el.removeAttribute(a);
    ghost.appendChild(el);
    const m = /translate\(([-\d.]+),([-\d.]+)\)/.exec(el.getAttribute('transform')) || [0, 0, 0];
    add(M.run(el, [{ transform: T(+m[1], +m[2]), opacity: 1 }, { transform: T(cl.x - ox, cl.y - oy, 0.96), opacity: 0 }], o));
  }
  const last = graphAnims[graphAnims.length - 1];
  add(M.run($('#g-edges'), [{ opacity: 0 }, { opacity: 1 }], { duration: 140, delay: 260, easing: EASE_OUT, fill: 'backwards' }));
  const done = () => { $('#g-ghost').textContent = ''; };
  if (last) last.finished.then(done, () => {});
  setTimeout(done, M.d(420));
}
const inBook = id => k => { const n = S.book.byId.get(k); return !!n && n.kind !== 'book' && n.book && n.book.id === id; };
function openCluster(id, focus, anim) {
  const a = screenOf(id);
  const before = anim && M.move() ? graphBefore(() => false) : null;
  S.expanded.add(id);
  renderGraph(a && { key: 'band:' + id, ...a });
  if (before) flipGraph(before, id, null, 'band:' + id);
  camera(() => showBand(id), !!before);
  persist();
  if (focus) focusGraphNode('band:' + id);
  live(`${S.book.byId.get(id).title} opened in the graph`);
}
/* After opening: bring the opened book into view, without zooming in. */
function showBand(id) {
  const b = G.layout.bands.find(x => x.id === id), s = stageSize(), m = 16;
  if (!b || !s.w) return;
  const k = Math.max(LABEL_K, Math.min(G.k, (s.w - 2 * m) / b.w, (s.h - 2 * m) / b.h));
  const sx = b.x * G.k + G.tx, sy = b.y * G.k + G.ty; // where the band head is now
  G.k = k;
  // keep the band head where it was if the whole band then fits; otherwise move it in
  G.tx = sx - b.x * k; G.ty = sy - b.y * k;
  const L = b.x * k + G.tx, T = b.y * k + G.ty, Rr = L + b.w * k, B = T + b.h * k;
  if (Rr > s.w - m) G.tx -= Math.min(Rr - (s.w - m), L - m);
  if (B > s.h - m) G.ty -= Math.min(B - (s.h - m), T - m);
  if (b.x * k + G.tx < m) G.tx = m - b.x * k;
  if (b.y * k + G.ty < m) G.ty = m - b.y * k;
  applyView();
}
function closeCluster(id, focus, anim) {
  const a = screenOf('band:' + id);
  const before = anim && M.move() ? graphBefore(inBook(id)) : null;
  S.expanded.delete(id);
  renderGraph(a && { key: id, ...a });
  if (before) flipGraph(before, 'band:' + id, id, id);
  persist();
  if (focus) focusGraphNode(id);
  live(`${S.book.byId.get(id).title} closed in the graph`);
}
/** A chapter box lists its sections, or folds them away, where it stands. */
function toggleChapter(id, open, focus, anim) {
  const a = screenOf(id), n = S.book.byId.get(id);
  const before = anim && M.move() ? graphBefore(k => { const m = S.book.byId.get(k); return !!m && m.kind === 'section' && m.chapter.id === id; }) : null;
  if (open) S.openCh.add(id); else S.openCh.delete(id);
  renderGraph(a && { key: id, ...a });
  if (before) flipGraph(before, id, open ? null : id, null);
  if (open) camera(() => revealBox(id, false), !!before);
  persist();
  if (focus) focusGraphNode(id);
  live(open ? `${plural(n.children.length, 'section')} of chapter ${n.n} listed in the graph` : `Sections of chapter ${n.n} folded away`);
}
function activateGraphNode(key, kbd) {
  if (key.startsWith('band:')) return closeCluster(key.slice(5), kbd, !kbd);
  const n = S.book.byId.get(key);
  if (n.kind === 'book') return openCluster(n.id, kbd, !kbd);
  const again = S.sel === n.id;
  select(n.id, { from: 'graph', anim: !kbd });
  if (n.kind === 'chapter' && n.children.length && (again || !S.openCh.has(n.id))) toggleChapter(n.id, !S.openCh.has(n.id), kbd, !kbd);
  if (kbd) focusGraphNode(key);
}

/* ---- graph keyboard: one tab stop; Right and Left follow the arrows, Up and Down move through what is above and below ---- */
const cyOf = key => { const b = boxOf(key), u = G.layout.units.get(key); return b.y + (u ? u.headH : b.h) / 2; };
function nearestBy(keys, y) { let best = null, bd = Infinity; for (const k of keys || []) { const d = Math.abs(cyOf(k) - y); if (d < bd) { bd = d; best = k; } } return best; }
function beside(key, dx, dy) { // the nearest box in a direction, for boxes no arrow joins
  const a = boxOf(key);
  let best = null, bd = Infinity;
  for (const k of G.els.keys()) {
    if (k === key) continue;
    const b = boxOf(k);
    let d;
    if (dy) { if (b.x >= a.x + a.w || b.x + b.w <= a.x || (b.y - a.y) * dy <= 0) continue; d = Math.abs(b.y - a.y); }
    else { if ((b.x - a.x) * dx <= 0 || b.y >= a.y + a.h || b.y + b.h <= a.y) continue; d = Math.abs(b.x - a.x) + Math.abs(b.y - a.y) / 4; }
    if (d < bd) { bd = d; best = k; }
  }
  return best;
}
svg.addEventListener('keydown', e => {
  const node = e.target.closest && e.target.closest('.node');
  if (!node || e.altKey || e.ctrlKey || e.metaKey) return;
  const key = node.dataset.key;
  const row = G.layout.rows.get(key), ukey = row ? row.parent.id : key;
  let to = null, handled = true;
  switch (e.key) {
    case 'ArrowRight': to = nearestBy(G.layout.succ.get(ukey), cyOf(ukey)) || beside(key, 1, 0); break;
    case 'ArrowLeft': to = nearestBy(G.layout.pred.get(ukey), cyOf(ukey)) || beside(key, -1, 0); break;
    case 'ArrowUp': to = beside(key, 0, -1); break;
    case 'ArrowDown': to = beside(key, 0, 1); break;
    case 'Enter': case ' ': activateGraphNode(key, true); break;
    case '+': case '=': zoomBy(1.25); break;
    case '-': case '_': zoomBy(0.8); break;
    case '0': fitAll(); break;
    case 'Escape': {
      const sel = S.sel && S.book.byId.get(S.sel);
      if (sel) { revealInTree(sel); treeChanged(); markSelected(); focusRow(sel.id); }
      break;
    }
    default: handled = false;
  }
  if (to) focusGraphNode(to);
  if (handled) e.preventDefault();
});
svg.addEventListener('focusin', e => { const n = e.target.closest && e.target.closest('.node'); if (n) setGraphRoving(n.dataset.key); });

/* ---- pointer: drag to pan, pinch and Ctrl/Cmd+wheel to zoom, click to act ---- */
const ptrs = new Map();
let drag = null, pinch = null;
svg.addEventListener('pointerdown', e => {
  cancelCamera();
  if (e.button !== 0) return;
  ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
  if (ptrs.size === 1) drag = { id: e.pointerId, x: e.clientX, y: e.clientY, tx: G.tx, ty: G.ty, moved: false };
  if (ptrs.size === 2) {
    const [p, q] = [...ptrs.values()];
    pinch = { d: Math.hypot(p.x - q.x, p.y - q.y), k: G.k };
    drag = null;
  }
});
svg.addEventListener('pointermove', e => {
  if (!ptrs.has(e.pointerId)) return;
  ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
  const r = svg.getBoundingClientRect();
  if (pinch && ptrs.size === 2) {
    const [p, q] = [...ptrs.values()];
    const d = Math.hypot(p.x - q.x, p.y - q.y);
    zoomAt(pinch.k * d / pinch.d, (p.x + q.x) / 2 - r.left, (p.y + q.y) / 2 - r.top);
    G.justDragged = true;
    return;
  }
  if (!drag || drag.id !== e.pointerId) return;
  const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
  if (!drag.moved && Math.hypot(dx, dy) > 4) { drag.moved = true; svg.setPointerCapture(e.pointerId); svg.classList.add('panning'); }
  if (drag.moved) { G.tx = drag.tx + dx; G.ty = drag.ty + dy; applyView(); }
});
const endPtr = e => {
  ptrs.delete(e.pointerId);
  if (ptrs.size < 2) pinch = null;
  if (drag && drag.id === e.pointerId) {
    if (drag.moved) { G.justDragged = true; setTimeout(() => { G.justDragged = false; }, 0); }
    drag = null; svg.classList.remove('panning');
  }
  if (!ptrs.size && G.justDragged) setTimeout(() => { G.justDragged = false; }, 0);
};
svg.addEventListener('pointerup', endPtr);
svg.addEventListener('pointercancel', endPtr);
svg.addEventListener('click', e => {
  if (G.justDragged) return;
  const node = e.target.closest('.node');
  if (node) { setGraphRoving(node.dataset.key); activateGraphNode(node.dataset.key, false); }
});
svg.addEventListener('wheel', e => {
  e.preventDefault();
  cancelCamera();
  const r = svg.getBoundingClientRect();
  if (e.ctrlKey || e.metaKey) zoomAt(G.k * Math.exp(-e.deltaY * 0.0025), e.clientX - r.left, e.clientY - r.top);
  else { G.tx -= e.deltaX; G.ty -= e.deltaY; applyView(); }
}, { passive: false });

/* ---- minimap ---- */
const mm = $('#mm');
function drawMinimap() {
  const L = G.layout;
  if (!L) return;
  mm.setAttribute('viewBox', `0 ${L.minY} ${L.width} ${L.height - L.minY}`);
  mm.setAttribute('preserveAspectRatio', 'xMidYMid meet');
  const sel = S.sel && S.book.byId.get(S.sel), selKey = sel && unitKeyOf(sel);
  let s = L.bands.map(b => `<rect class="mb" x="${b.x}" y="${b.y}" width="${b.w}" height="${b.h}" vector-effect="non-scaling-stroke"/>`).join('');
  for (const u of L.units.values()) s += `<rect class="mu${u.id === selKey || (u.rows || []).some(r => r.id === selKey) ? ' sel' : ''}" x="${u.x}" y="${u.y}" width="${u.w}" height="${u.h}"/>`;
  s += '<rect class="mv" id="mm-v"/>';
  mm.innerHTML = s;
  drawMinimapView();
}
function drawMinimapView() {
  const r = document.getElementById('mm-v'), s = stageSize();
  if (!r || !s.w) return;
  r.setAttribute('x', -G.tx / G.k); r.setAttribute('y', -G.ty / G.k);
  r.setAttribute('width', s.w / G.k); r.setAttribute('height', s.h / G.k);
}
(() => {
  const mmBox = $('#minimap');
  let down = false;
  const move = e => {
    const L = G.layout, r = mmBox.getBoundingClientRect(), s = stageSize();
    const W = L.width, H = L.height - L.minY, sc = Math.min(r.width / W, r.height / H);
    const ox = (r.width - W * sc) / 2, oy = (r.height - H * sc) / 2;
    const gx = (e.clientX - r.left - ox) / sc, gy = (e.clientY - r.top - oy) / sc + L.minY;
    G.tx = s.w / 2 - gx * G.k; G.ty = s.h / 2 - gy * G.k; applyView();
  };
  mmBox.addEventListener('pointerdown', e => { down = true; mmBox.setPointerCapture(e.pointerId); move(e); });
  mmBox.addEventListener('pointermove', e => { if (down) move(e); });
  mmBox.addEventListener('pointerup', () => { down = false; });
  mmBox.addEventListener('pointercancel', () => { down = false; });
})();

/* =====================================================================
   7. DETAIL PANEL (the graph's text equivalent, and the one next action)
   ===================================================================== */
const detailEl = $('#detail-body');
const pathOf = n => n.kind === 'shelf' ? 'book/' : n.kind === 'book' ? `book/${n.name}/` : n.kind === 'part' ? `book/${n.book.name}/PLAN.md` :
  (n.kind === 'chapter' ? n : n.chapter).file ? 'book/' + (n.kind === 'chapter' ? n : n.chapter).file : `book/${n.book.name}/PLAN.md`;
/** The sentence to give the agent for something not written yet. */
function request(n) {
  if (n.kind === 'section') return `Write section ${n.num} of ${n.book.name}`;
  if (n.kind === 'chapter') return `${n.state === 'writing' ? 'Finish' : 'Write'} chapter ${n.n} of ${n.book.name}`;
  const next = S.book.chapters.find(c => (n.kind === 'shelf' || c.book === n.book) && (n.kind !== 'part' || c.parent === n) && !isDone(c));
  return next ? request(next) : '';
}
/** Where "Read" goes from a node: a written section, or null. */
function readTarget(n) {
  if (n.kind === 'section') return isDone(n) && n.chapter.file ? n : null;
  const last = PR.last && S.book.byKey.get(PR.last);
  const inside = s => { for (let p = s; p; p = p.parent) if (p === n) return true; return false; };
  if (last && isDone(last) && last.chapter.file && inside(last)) return last;
  return S.book.sections.find(s => isDone(s) && s.chapter.file && inside(s)) || null;
}
function nodeButton(n) {
  const kind = n.kind === 'section' ? `section ${n.num}` : n.kind === 'chapter' ? `chapter ${n.n}` : n.kind;
  const st = n.kind === 'section' || n.kind === 'chapter' ? (n.state === 'writing' ? 'being written' : statOf(n)) : `${n.written}/${n.total} written`;
  if (n.kind === 'book' || n.kind === 'part') return `<button class="btn fbtn" type="button" data-goto="${esc(n.id)}"><span class="fn">${esc(segOf(n))}</span><span class="k">${st}</span></button>`;
  return `<button class="btn" type="button" data-goto="${esc(n.id)}"><span class="stat ${statOf(n)}" aria-hidden="true"></span><span class="bt"><span>${esc(n.title)}</span><span class="k">${kind}, ${st}</span></span></button>`;
}
/* When the selection changes: old content out (100 ms), new in (160 ms)
   with a 4 px rise. Keyboard: at once. Reduced motion: a short fade only. */
function renderDetail(anim) {
  const n = S.sel && S.book.byId.get(S.sel);
  const host = detailEl.parentNode;
  host.querySelectorAll('.detail-body.ghost').forEach(g => g.remove());
  detailEl.getAnimations().forEach(a => a.cancel());
  let ghost = null;
  if (anim && detailEl.childElementCount && detailEl.offsetParent && detailEl.offsetHeight) {
    ghost = detailEl.cloneNode(true);
    ghost.removeAttribute('id');
    ghost.querySelectorAll('[id]').forEach(e => e.removeAttribute('id'));
    ghost.classList.add('ghost'); ghost.setAttribute('aria-hidden', 'true'); ghost.inert = true;
    Object.assign(ghost.style, { position: 'absolute', left: detailEl.offsetLeft + 'px', top: detailEl.offsetTop + 'px',
      width: detailEl.offsetWidth + 'px', height: detailEl.offsetHeight + 'px', overflow: 'hidden', pointerEvents: 'none' });
    host.appendChild(ghost);
    ghost.scrollTop = detailEl.scrollTop;
  }
  detailEl.innerHTML = detailHTML(n);
  detailEl.scrollTop = 0;
  if (ghost) {
    const out = M.run(ghost, [{ opacity: 1 }, { opacity: 0 }], { duration: M.reduced ? 80 : 100, easing: EASE_OUT, fill: 'forwards' });
    const end = () => ghost.remove();
    if (out) out.finished.then(end, end); else end();
    M.run(detailEl, M.reduced ? [{ opacity: 0 }, { opacity: 1 }] : [{ opacity: 0, transform: 'translateY(4px)' }, { opacity: 1, transform: 'none' }],
      { duration: M.reduced ? 120 : 160, delay: M.reduced ? 0 : 80, easing: EASE_OUT, fill: 'backwards' });
  }
}
function detailHTML(n) {
  if (!n) return '<h3 id="detail-h">Nothing selected</h3>';
  const sec = n.kind === 'section', ch = n.kind === 'chapter';
  const head = sec ? `<span class="no">${esc(n.num)}</span> ` : ch ? `<span class="no">${esc(n.n)}</span> ` : '';
  let h = `<div class="dgroup"><p class="dkind">${sec ? `Section in chapter ${n.chapter.n}` : ch ? `Chapter in ${esc(n.book.title)}` : n.kind === 'shelf' ? 'Your shelf' : n.kind === 'part' ? `Part of ${esc(n.book.title)}` : 'Book'}</p>` +
    `<h3 id="detail-h" tabindex="-1">${head}${esc(n.kind === 'shelf' ? 'Your books' : n.title)}</h3>`;
  if (sec) h += `<p class="facts"><span class="stat ${statOf(n)}" aria-hidden="true"></span><span>${isDone(n) ? `Written, ${num(n.words)} words, about ${minutes(n.words)} min` : 'Planned, not written yet'}${wasOpened(n) ? '. You have opened it.' : ''}</span></p>`;
  else if (ch) {
    const r = readCount(n);
    h += `<p class="facts"><span class="stat ${statOf(n)}" aria-hidden="true"></span><span>${STATE[n.state] || n.state}: ${n.written} of ${plural(n.total, 'section')}${n.words ? `, ${num(n.words)} words, about ${minutes(n.words)} min` : ''}${n.unrun ? `; ${n.unrun} not run on the machine this book was written on` : ''}${r ? `. You have opened ${r}.` : ''}</span></p>`;
  } else h += `<p class="facts">${plural(n.total, 'chapter')}: ${n.written} written, ${n.total - n.written} to write${n.words ? `; ${num(n.words)} words` : ''}</p>`;
  h += '</div>';
  if (n.kind === 'book' && n.audience) h += `<p class="desc">For ${esc(n.audience.replace(/\.$/, ''))}.</p>`;
  if (sec && n.teaches.length) h += `<p class="desc">Teaches ${n.teaches.map(t => `<span class="idea">${esc(/[A-Z_.]{4,}/.test(t) ? t.replace(/^[A-Z0-9]+\./, '').replace(/_/g, ' ').toLowerCase() : t.replace(/-/g, ' '))}</span>`).join(', ')}.</p>`;
  // the one next action
  const target = readTarget(n), ask = request(n);
  if (target) {
    const resume = PR.last && S.book.byKey.get(PR.last) === target, beat = resume && /^[a-z0-9-]+$/.test(PR.beat || '') ? PR.beat : '';
    h += `<div class="action"><a class="btn primary" id="primary" href="#${esc(target.id)}${beat ? '-' + beat : ''}">${resume && !sec ? 'Continue reading' : 'Read'}</a>` +
      `<p class="cmdtext">${sec ? `Opens section ${esc(n.num)}${beat ? ', where you stopped' : ''}.` : `${resume ? 'Where you stopped' : 'Starts at'}: ${esc(target.num)} ${esc(target.title)}`}</p></div>`;
  } else if (ask) {
    h += `<div class="action"><button class="btn primary" type="button" id="primary" data-copy="${esc(ask)}">${CK}<span class="bl">Copy a request for Claude</span></button>` +
      `<p class="cmdtext">Copies: <span id="ask-text">${esc(ask)}</span></p><p class="confirm" id="confirm"></p></div>`;
  } else if (n.kind === 'shelf') h += '<p class="none">Every chapter on this shelf is written.</p>';
  if (sec || ch) {
    const lv = ch ? n.levels : [n.level];
    h += `<section><h4>Level${ch ? 's it reaches' : ''}</h4><ol class="levels">${LEVELS.map((w, i) => {
      const k = ch ? n.children.filter(s => s.level === i + 1).length : 0;
      return `<li><span class="sqbig${lv.includes(i + 1) ? ' on' : ''}" aria-hidden="true"></span>${i + 1} ${w}<span class="w">${ch ? (k ? plural(k, 'section') : 'none') : lv.includes(i + 1) ? 'this section' : ''}</span></li>`;
    }).join('')}</ol></section>`;
    const needs = n.needs.map(id => S.book.byId.get(id)), unl = n.unlocks.map(id => S.book.byId.get(id));
    const before = sec && n.parent.children.indexOf(n) > 0 ? `<p class="none">${needs.length ? 'And' : 'Only'} the sections before it in chapter ${n.chapter.n}.</p>` : '';
    h += `<section><h4><i class="sw needs" aria-hidden="true"></i>Needs first</h4>${needs.length ? `<ul class="links needs">${needs.map(m => `<li>${nodeButton(m)}</li>`).join('')}</ul>` : before ? '' : '<p class="none">Nothing. You can start here.</p>'}${before}</section>`;
    h += `<section><h4><i class="sw unlocks" aria-hidden="true"></i>Unlocks</h4>${unl.length ? `<ul class="links unlocks">${unl.map(m => `<li>${nodeButton(m)}</li>`).join('')}</ul>` : `<p class="none">Nothing yet. No ${n.kind} names this one as needed.</p>`}</section>`;
  }
  if (ch && !isDone(n)) {
    const lp = learningPath(S.book, n.id);
    h += `<section><h4>Learning path</h4>${lp.length
      ? `<p class="none" style="margin-bottom:8px">${plural(lp.length, 'unwritten chapter')} to write first, in this order:</p><ol class="path-list" id="learning-path">${lp.map(m => `<li><button class="btn" type="button" data-goto="${esc(m.id)}">${esc(m.n)} ${esc(m.title)}</button></li>`).join('')}</ol>`
      : '<p class="none" id="learning-path-none">Every chapter it needs is already written.</p>'}</section>`;
  }
  if (!sec && n.children.length) h += `<section><h4>${ch ? 'Sections' : n.kind === 'shelf' ? 'Books' : 'Contents'}</h4><ul class="links">${n.children.map(c => `<li>${nodeButton(c)}</li>`).join('')}</ul></section>`;
  h += `<div class="path-line"><code class="path" id="d-path">${esc(pathOf(n))}</code><button class="btn" type="button" id="copy-path" data-copy="${esc(pathOf(n))}">${CK}<span class="bl">Copy path</span></button></div>`;
  return h;
}
detailEl.addEventListener('click', e => {
  const goto = e.target.closest('[data-goto]');
  if (goto) { select(goto.dataset.goto, { from: 'detail', anim: true }); const hd = $('#detail-h'); if (hd) hd.focus({ preventScroll: true }); return; }
  const c = e.target.closest('[data-copy]');
  if (c) copyText(c.dataset.copy, c, c.id === 'primary' ? $('#confirm') : null);
});

/* =====================================================================
   8. SELECTION: keeps tree, graph and detail in step
   ===================================================================== */
function select(id, opts = {}) {
  const n = S.book.byId.get(id);
  if (!n) return;
  const prevSel = S.sel;
  S.sel = id;
  // tree: open the ancestors, mark, scroll the row into view (focus stays put)
  const had = rowEls.has(id);
  const shown = revealInTree(n);
  markSelected();
  if (shown) {
    if (opts.from !== 'tree') { setRoving(id); ensureRowVisible(rowEls.get(id)); }
    if (!had) treeChanged();
  }
  // graph: open the right book (and chapter), centre the node if it is off-screen
  let relayout = false, fit = false;
  if (n.kind === 'chapter' || n.kind === 'section') {
    if (!S.expanded.has(n.book.id)) { S.expanded.add(n.book.id); relayout = true; }
    if (n.kind === 'section' && !S.openCh.has(n.chapter.id)) { if (opts.from !== 'graph') S.openCh.clear(); S.openCh.add(n.chapter.id); relayout = true; }
  } else if (n === S.book.root) { if (S.expanded.size && (opts.from === 'tree' || opts.from === 'detail')) { S.expanded.clear(); relayout = true; } fit = opts.from === 'tree'; }
  else if (n.kind === 'book' && opts.from !== 'graph') {
    if (!(S.expanded.size === 1 && S.expanded.has(n.id))) { S.expanded = new Set([n.id]); relayout = true; }
  }
  if (relayout) renderGraph(); else applyGraphClasses();
  const key = unitKeyOf(n);
  if (key && opts.from !== 'graph') { setGraphRoving(key); camera(() => { if (fit) fitAll(); else revealBox(key, true); }, opts.anim); }
  else if (fit) camera(fitAll, opts.anim);
  if (opts.anim && (n.kind === 'chapter' || n.kind === 'section')) drawRelations();
  renderDetail(prevSel !== id && opts.from !== 'init' && opts.from !== 'test' && M.fade());
  if (S.mode === 'map' && opts.from !== 'route' && opts.from !== 'init') setHash(n === S.book.root ? '' : 'map-' + id);
  persist(); updateStatus();
}

/* =====================================================================
   9. LAYOUT OF THE MAP: width bands, rails and the dividers
     phone < 768: tabs.  tablet 768-1023: tree + graph, detail on demand,
     one side panel at a time.  laptop 1024-1279: tree + graph, detail on
     demand.  desktop >= 1280: all three.  Rails fold a side panel to a
     strip; dividers resize it by pointer or keyboard and are remembered.
   ===================================================================== */
const colsEl = $('#cols');
const SIDES = {
  tree: { sep: $('#sep-tree'), min: 240, max: 520, panel: $('#treepanel'), other: 'detail', name: 'contents' },
  detail: { sep: $('#sep-detail'), min: 260, max: 520, panel: $('#detail'), other: 'tree', name: 'selection' }
};
const savedW = store.get('widths') || {};
const bandOf = w => w < 768 ? 'phone' : w < 1024 ? 'tablet' : w < 1280 ? 'laptop' : 'desktop';
let band = null;
function defaultWidth(side) {
  const w = innerWidth;
  if (w < 1280) return w < 1024 ? 320 : 300;
  return Math.round(Math.min(380, Math.max(side === 'tree' ? 320 : 300, w * (side === 'tree' ? 0.2 : 0.18) + 56)));
}
const wantW = side => savedW[side] || defaultWidth(side);
function maxWidth(side) { // the graph keeps at least 400 px
  const o = SIDES[side].other, other = document.body.dataset[o] === 'rail' ? 52 : Math.min(wantW(o), SIDES[o].max);
  return Math.max(SIDES[side].min, Math.min(SIDES[side].max, innerWidth - 70 - other - 400));
}
const widthNow = side => Math.round(Math.max(SIDES[side].min, Math.min(maxWidth(side), wantW(side))));
function applyWidths() {
  for (const side of ['tree', 'detail']) {
    const w = widthNow(side), sep = SIDES[side].sep;
    colsEl.style.setProperty(`--w-${side}-open`, w + 'px');
    sep.setAttribute('aria-valuenow', String(w));
    sep.setAttribute('aria-valuemax', String(maxWidth(side)));
    sep.setAttribute('aria-valuetext', `${w} pixels wide`);
  }
}
function setWidth(side, w) { savedW[side] = Math.round(Math.max(SIDES[side].min, Math.min(maxWidth(side), w))); applyWidths(); }
for (const side of ['tree', 'detail']) {
  const sep = SIDES[side].sep, sign = side === 'tree' ? 1 : -1;
  let dragging = null;
  sep.addEventListener('pointerdown', e => {
    if (e.button) return;
    e.preventDefault();
    dragging = { x: e.clientX, w: widthNow(side) };
    sep.setPointerCapture(e.pointerId); sep.classList.add('dragging');
  });
  sep.addEventListener('pointermove', e => { if (dragging) setWidth(side, dragging.w + sign * (e.clientX - dragging.x)); });
  const end = () => { if (!dragging) return; dragging = null; sep.classList.remove('dragging'); store.set('widths', savedW); };
  sep.addEventListener('pointerup', end); sep.addEventListener('pointercancel', end);
  sep.addEventListener('dblclick', () => { delete savedW[side]; applyWidths(); store.set('widths', savedW); live(`The ${SIDES[side].name} width is back to its default`); });
  sep.addEventListener('keydown', e => {
    const step = e.shiftKey ? 64 : 16;
    let w = widthNow(side);
    if (e.key === 'ArrowLeft') w -= sign * step;
    else if (e.key === 'ArrowRight') w += sign * step;
    else if (e.key === 'Home') w = SIDES[side].min;
    else if (e.key === 'End') w = maxWidth(side);
    else if (e.key === 'Enter') { delete savedW[side]; w = widthNow(side); }
    else return;
    e.preventDefault();
    setWidth(side, w);
    store.set('widths', savedW);
  });
}
function setRail(side, railed, user) {
  document.body.dataset[side] = railed ? 'rail' : 'open';
  $$(`button[data-rail="${side}"]`).forEach(b => b.setAttribute('aria-expanded', String(!railed)));
  if (user && !railed && band === 'tablet') setRail(SIDES[side].other, true, false); // one side panel at a time
  applyWidths();
}
$$('button[data-rail]').forEach(b => b.addEventListener('click', () => {
  const side = b.dataset.rail, railed = document.body.dataset[side] !== 'rail';
  setRail(side, railed, true);
  // focus moves to the control that now stands for this panel
  SIDES[side].panel.querySelector(railed ? '.rail-btn' : '.rail-toggle').focus();
  if (!railed && side === 'tree') scheduleSticky();
}));
function applyBand() {
  const b = bandOf(innerWidth);
  if (b !== band) {
    band = b;
    setRail('tree', false, false);
    setRail('detail', b === 'tablet' || b === 'laptop', false);
  }
  applyWidths();
}
addEventListener('resize', applyBand);

// views (desktop) and tabs (phone)
function setView(v) {
  document.body.dataset.view = v;
  $$('button[data-view]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.view === v)));
  store.set('view', v);
}
const TABS = { tree: '#treepanel', graph: '#graphpanel', detail: '#detail' };
let revealPending = true; // reveal the selected row once the tree has its real height
function setTab(t) {
  const prev = document.body.dataset.tab;
  document.body.dataset.tab = t;
  if (t === 'tree') revealPending = true;
  $$('button[data-tab]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.tab === t)));
  // the new panel slides in from the side of its tab (pointer only)
  if (prev && prev !== t && band === 'phone' && M.fade()) {
    const keys = Object.keys(TABS), dir = keys.indexOf(t) > keys.indexOf(prev) ? 1 : -1;
    M.run($(TABS[t]), M.reduced ? [{ opacity: 0 }, { opacity: 1 }] : [{ opacity: 0, transform: `translateX(${dir * 24}px)` }, { opacity: 1, transform: 'none' }],
      { duration: M.reduced ? 100 : 220, easing: EASE_OUT });
  }
}
$$('button[data-view]').forEach(b => b.addEventListener('click', () => setView(b.dataset.view)));
$$('button[data-tab]').forEach(b => b.addEventListener('click', () => setTab(b.dataset.tab)));

function fitOnce() { // first view: the whole shelf at root, otherwise the selection at 100%
  const s = stageSize();
  if (!s.w || !s.h || !G.layout) return;
  const n = S.sel && S.book.byId.get(S.sel), k = n && unitKeyOf(n);
  if (!k || n === S.book.root) fitAll();
  else fitNeighbours(n);
  G.fitted = true;
}
new ResizeObserver(() => {
  const s = stageSize();
  if (!s.w || !s.h || !G.layout) return;
  if (graphCompact() !== G.compact || graphCols() !== G.cols) { // the panel changed size class: lay out again where the reader was looking
    const key = G.focus && G.els.has(G.focus) ? G.focus : null, a = key && G.fitted && screenOf(key);
    renderGraph(a && { key, ...a });
  }
  if (!G.fitted || !G.user) fitOnce(); else applyView();   // until the reader moves the view, it keeps fitting its panel
  scheduleSticky();
}).observe(stage);
for (const ev of ['pointerdown', 'wheel', 'keydown']) stage.addEventListener(ev, () => { G.user = true; }, { passive: true, capture: true });
$('.graph-tools').addEventListener('click', () => { G.user = true; }, true);
$('#navkit').addEventListener('pointerdown', () => { G.user = true; }, true);
new ResizeObserver(() => {
  if (revealPending && treeScroll.clientHeight && S.book) {
    revealPending = false;
    const li = rowEls.get(S.sel);
    if (li) ensureRowVisible(li);
  }
  scheduleSticky();
}).observe(treeScroll);

// controls of the map
$$('[data-chip]').forEach(b => b.addEventListener('click', () => { S.chip = b.dataset.chip; applyFilter(); }));
$$('[data-depth]').forEach(b => b.addEventListener('click', () => setDepth(b.dataset.depth === 'all' ? 'all' : Number(b.dataset.depth))));
$('#collapse-all').addEventListener('click', collapseAll);
$('#tree-opts').addEventListener('click', e => { // phone only: the controls fold away to give the tree the room
  const open = e.currentTarget.getAttribute('aria-expanded') !== 'true';
  e.currentTarget.setAttribute('aria-expanded', String(open));
  $('#tree-ctrls').classList.toggle('open', open);
  scheduleSticky();
});
$('#z-in').addEventListener('click', () => zoomBy(1.25));
$('#z-out').addEventListener('click', () => zoomBy(0.8));
$('#fit-all').addEventListener('click', () => camera(fitAll, true));
$('#fit-sel').addEventListener('click', () => camera(fitSelection, true));
$('#keys-btn').addEventListener('click', e => { // the keyboard help, folded away until asked for
  const open = e.currentTarget.getAttribute('aria-expanded') !== 'true';
  e.currentTarget.setAttribute('aria-expanded', String(open));
  $('#graph-hint').hidden = !open;
});
$('#map-btn').addEventListener('click', e => { // the overview map can be dismissed, and brought back
  const on = e.currentTarget.getAttribute('aria-pressed') !== 'true';
  e.currentTarget.setAttribute('aria-pressed', String(on));
  store.set('minimap', on);
  updateNavkit();
});
addEventListener('keydown', cancelCamera, true);
$$('[data-pan]').forEach(b => b.addEventListener('click', () => {
  const d = 120, dir = b.dataset.pan;
  if (dir === 'left') G.tx += d; if (dir === 'right') G.tx -= d; if (dir === 'up') G.ty += d; if (dir === 'down') G.ty -= d;
  applyView();
}));

/* Rare moment two, first load only: the panels settle and their shadows
   drop into place in order, then the first rows of the tree cascade.
   Under 450 ms, never blocks input; skipped with reduced motion, and the
   rows do not wait for it when the reader is coming back. */
function entrance(firstVisit) {
  if (M.reduced) return;
  const d = getComputedStyle(document.documentElement).getPropertyValue('--sh-panel').trim() || '6px';
  ['#treepanel', '#graphpanel', '#detail'].map(q => $(q)).filter(p => p.offsetParent).forEach((p, i) => {
    M.run(p, [{ transform: 'translateY(-6px)' }, { transform: 'none' }], { duration: 220, delay: i * 50, easing: EASE_OUT, fill: 'backwards' });
    M.run(p, [{ transform: 'translate(0px, 0px)' }, { transform: `translate(${d}, ${d})` }], { pseudoElement: '::before', duration: 200, delay: 40 + i * 50, easing: EASE_OUT, fill: 'backwards' });
  });
  if (!firstVisit) return;
  [...treeEl.querySelectorAll('.ti')].slice(0, 14).forEach((li, i) => {
    const o = { duration: 140, delay: 160 + i * 9, easing: EASE_OUT, fill: 'backwards' };
    M.run(li.firstElementChild, [{ opacity: 0, transform: 'translateY(6px)' }, { opacity: 1, transform: 'none' }], o);
    for (const pe of ['::before', '::after']) M.run(li, [{ opacity: 0 }, { opacity: 1 }], Object.assign({ pseudoElement: pe }, o)); // guides arrive with their rows
  });
}
/** Build the map from the shelf, once, and restore what the reader had open. */
function startMap(hashId) {
  const saved = store.get('map');
  const valid = id => S.book.byId.has(id);
  S.open = saved ? new Set(saved.open.filter(valid)) : new Set(S.book.order.filter(n => isBranch(n) && n.kind !== 'chapter').map(n => n.id));
  S.expanded = new Set(saved && saved.expanded ? saved.expanded.filter(id => valid(id) && S.book.byId.get(id).kind === 'book') : (S.book.books.length === 1 ? [S.book.books[0].id] : []));
  S.openCh = new Set(saved && saved.openCh ? saved.openCh.filter(valid) : []);
  renderTree();
  renderGraph();
  G.fitted = false;
  const start = hashId && valid(hashId) ? hashId : saved && saved.sel && valid(saved.sel) ? saved.sel : S.book.root.id;
  select(start, { from: 'init' });
  fitOnce();
  updateStatus();
  return !saved;
}
