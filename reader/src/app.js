/* =====================================================================
   11. SEARCH across the shelf, from search.json
   ===================================================================== */
const qEl = $('#q'), resultsEl = $('#results');
const SR = { index: null, loading: null, hits: [], active: -1 };
function loadSearch() {
  if (SR.index || SR.loading || !S.book) return SR.loading;
  SR.loading = fetch('search.json', { cache: 'no-cache' }).then(r => r.ok ? r.json() : { sections: [] }).catch(() => ({ sections: [] })).then(d => {
    const extra = new Map((d.sections || []).map(e => [`${e.book}:${e.id}`, e]));
    SR.index = [];
    for (const ch of S.book.chapters) SR.index.push({ n: ch, title: `${ch.n} ${ch.title}`.toLowerCase(), terms: '', idea: '', text: '' });
    for (const s of S.book.sections) {
      const e = extra.get(pkey(s)) || {};
      SR.index.push({ n: s, title: `${s.num} ${s.title}`.toLowerCase(), terms: (e.terms || s.teaches).join(' · ').toLowerCase(), termList: e.terms || [], idea: e.idea || '', text: (e.idea || '').toLowerCase() });
    }
    if (qEl.value.trim()) runSearch();
  });
  return SR.loading;
}
/** Every word of the query must be found; a title counts most, then a key term, then the opening words. */
function search(q) {
  const words = q.toLowerCase().split(/\s+/).filter(Boolean), phrase = words.join(' ');
  if (!words.length || !SR.index) return [];
  const at = (hay, w) => { const i = hay.indexOf(w); return i < 0 ? 0 : (i === 0 || /[^a-z0-9]/.test(hay[i - 1]) ? 2 : 1); };
  const out = [];
  for (const e of SR.index) {
    let score = 0, ok = true;
    for (const w of words) {
      const t = at(e.title, w), k = at(e.terms, w), x = at(e.text, w);
      const ctx = e.n.kind === 'section' ? at(e.n.chapter.title.toLowerCase(), w) : 0;
      if (!t && !k && !x && !ctx) { ok = false; break; }
      score += t * 5 + k * 3 + x + ctx * 0.5;
    }
    if (!ok) continue;
    if (words.length > 1) score += e.title.includes(phrase) ? 6 : e.terms.includes(phrase) ? 4 : e.text.includes(phrase) ? 2 : 0; // the words together count for more
    if (e.n.kind === 'chapter') score += 1;
    if (!isDone(e.n)) score -= 2;
    out.push({ e, score });
  }
  out.sort((a, b) => b.score - a.score || a.e.n.index - b.e.n.index);
  return out.slice(0, 24);
}
function snippet(e, words) {
  const w = words.find(x => e.text.includes(x));
  if (!e.idea) return '';
  let from = 0;
  if (w) { const i = e.text.indexOf(w); from = Math.max(0, e.idea.lastIndexOf(' ', Math.max(0, i - 40)) + 1); }
  const s = e.idea.slice(from, from + 110);
  return (from ? '…' : '') + s + (from + 110 < e.idea.length ? '…' : '');
}
function markWords(text, words) {
  if (!words.length) return esc(text);
  const re = new RegExp('(' + words.map(w => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|') + ')', 'ig');
  return text.split(re).map((p, i) => i % 2 ? `<mark>${esc(p)}</mark>` : esc(p)).join('');
}
function runSearch() {
  const q = qEl.value.trim();
  if (!q) return closeResults();
  if (!SR.index) { loadSearch(); resultsEl.innerHTML = '<p class="r-none">Reading the index…</p>'; openResults(); return; }
  const words = q.toLowerCase().split(/\s+/).filter(Boolean);
  const found = search(q);
  // grouped by book and chapter, the best group first
  const groups = new Map();
  for (const h of found) {
    const n = h.e.n, ch = n.kind === 'chapter' ? n : n.chapter;
    if (!groups.has(ch)) groups.set(ch, []);
    groups.get(ch).push(h);
  }
  SR.hits = [];
  let html = '';
  for (const [ch, list] of groups) {
    list.sort((a, b) => a.e.n.index - b.e.n.index);
    const gid = 'rg-' + ch.id;
    html += `<div role="group" aria-labelledby="${gid}"><div class="r-group" id="${gid}"><span class="r-book">${esc(ch.book.title)}</span><span><span class="no">${esc(ch.n)}</span> ${esc(ch.title)}</span></div>`;
    for (const { e } of list) {
      const n = e.n, i = SR.hits.length;
      SR.hits.push(n);
      const term = n.kind === 'section' && e.termList.find(t => words.some(w => t.toLowerCase().includes(w)));
      html += `<div class="r-hit" role="option" id="hit-${i}" data-i="${i}" aria-selected="false">` +
        `<span class="stat ${statOf(n)}" aria-hidden="true"></span><span class="r-main"><span class="r-title">${n.kind === 'chapter' ? 'The whole chapter' : `<span class="no">${esc(n.num)}</span> ${markWords(n.title, words)}`}` +
        `${isDone(n) || n.kind === 'chapter' && n.readable ? '' : ' <span class="k">planned</span>'}</span>` +
        `${term ? `<span class="r-term">teaches ${markWords(term, words)}</span>` : ''}${n.kind === 'section' && snippet(e, words) ? `<span class="r-snip">${markWords(snippet(e, words), words)}</span>` : ''}</span></div>`;
    }
    html += '</div>';
  }
  resultsEl.innerHTML = html || `<p class="r-none">Nothing on your shelf matches “${esc(q)}”.</p>`;
  SR.active = SR.hits.length ? 0 : -1;
  markActive(false);
  openResults();
  live(SR.hits.length ? `${plural(SR.hits.length, 'result')}. Up and Down to choose, Enter to open.` : 'No results', 400);
}
function openResults() { resultsEl.hidden = false; qEl.setAttribute('aria-expanded', 'true'); }
function closeResults() {
  resultsEl.hidden = true; resultsEl.textContent = ''; SR.hits = []; SR.active = -1;
  qEl.setAttribute('aria-expanded', 'false'); qEl.removeAttribute('aria-activedescendant');
}
function markActive(scroll) {
  $$('.r-hit', resultsEl).forEach(el => el.setAttribute('aria-selected', String(Number(el.dataset.i) === SR.active)));
  if (SR.active >= 0) { qEl.setAttribute('aria-activedescendant', 'hit-' + SR.active); if (scroll) $('#hit-' + SR.active).scrollIntoView({ block: 'nearest' }); }
  else qEl.removeAttribute('aria-activedescendant');
}
function openHit(i) {
  const n = SR.hits[i];
  if (!n) return;
  const to = readTarget(n);
  clearSearch();
  qEl.blur();
  go(to && (n.kind === 'section' || n.kind === 'chapter') ? (n.kind === 'chapter' ? readable(n)[0] || to : to).id : 'map-' + n.id);
}
function clearSearch() {
  qEl.value = ''; closeResults();
  if (S.book && (S.q || S.filt)) { S.q = ''; applyFilter(false); }
  document.body.dataset.search = 'closed'; $('#search-btn').setAttribute('aria-expanded', 'false');
}
qEl.addEventListener('focus', loadSearch);
qEl.addEventListener('input', () => {
  if (!S.book) return;
  if (S.mode === 'map') { S.q = qEl.value; applyFilter(false); } // on the map the tree narrows as well
  runSearch();
});
qEl.addEventListener('keydown', e => {
  const n = SR.hits.length;
  if (e.key === 'Escape') { e.preventDefault(); const had = qEl.value; clearSearch(); if (!had) qEl.blur(); else live('Search cleared'); }
  else if (e.key === 'ArrowDown' && n) { e.preventDefault(); SR.active = (SR.active + 1) % n; markActive(true); }
  else if (e.key === 'ArrowUp' && n) { e.preventDefault(); SR.active = (SR.active + n - 1) % n; markActive(true); }
  else if (e.key === 'Enter' && SR.active >= 0) { e.preventDefault(); openHit(SR.active); }
});
resultsEl.addEventListener('pointerdown', e => { if (e.target.closest('.r-hit')) e.preventDefault(); }); // keep the caret in the box
resultsEl.addEventListener('click', e => { const h = e.target.closest('.r-hit'); if (h) openHit(Number(h.dataset.i)); });
document.addEventListener('pointerdown', e => { if (!resultsEl.hidden && !e.target.closest('.search')) closeResults(); });
$('#search-btn').addEventListener('click', e => { // phone, while reading: the search row folds away
  const open = document.body.dataset.search !== 'open';
  document.body.dataset.search = open ? 'open' : 'closed';
  e.currentTarget.setAttribute('aria-expanded', String(open));
  if (open) qEl.focus(); else clearSearch();
});

/* =====================================================================
   12. THE PROGRESS MENU, KEYS, THEME
   ===================================================================== */
const progBtn = $('#prog-btn'), progMenu = $('#prog-menu');
function updateProgressMenu() {
  if (!S.book) return;
  const written = S.book.sections.filter(s => isDone(s));
  const opened = written.filter(wasOpened).length;
  const answers = Object.values(PR.answers).reduce((a, l) => a + l.length, 0);
  const unrun = S.book.chapters.filter(c => c.unrun);
  $('#prog-sum').textContent = `${opened} of ${plural(written.length, 'written section')} opened, ${plural(answers, 'answer')} turned over.` +
    (unrun.length ? ` ${unrun.reduce((a, c) => a + c.unrun, 0)} not run where the book was written, in ${plural(unrun.length, 'chapter')}.` : '');
}
function closeMenu(refocus) { progMenu.hidden = true; progBtn.setAttribute('aria-expanded', 'false'); if (refocus) progBtn.focus(); }
progBtn.addEventListener('click', () => {
  const open = progMenu.hidden;
  progMenu.hidden = !open; progBtn.setAttribute('aria-expanded', String(open));
  if (open) { updateProgressMenu(); $('#prog-copy').focus(); }
});
document.addEventListener('pointerdown', e => { if (!progMenu.hidden && !e.target.closest('.progress')) closeMenu(false); });
$('#prog-copy').addEventListener('click', async e => {
  const ok = await copyText(progressText(), e.currentTarget);
  $('#prog-note').textContent = ok ? 'Copied. In the other browser, open this menu and choose Paste progress.' : 'The clipboard is not available here. Copy the text below by hand.';
  if (!ok) { $('#prog-paste-box').hidden = false; $('#prog-text').value = progressText(); $('#prog-text').select(); }
});
$('#prog-paste').addEventListener('click', async () => {
  // reading the clipboard needs permission; the box below always works
  $('#prog-paste-box').hidden = false;
  let text = '';
  try { if (navigator.clipboard && navigator.clipboard.readText) text = await navigator.clipboard.readText(); } catch (e) { text = ''; }
  const box = $('#prog-text');
  if (!box.value && /^\s*(understudy-progress|\{)/.test(text)) box.value = text;   // never over what the reader has put there
  $('#prog-note').textContent = box.value ? 'Found progress on the clipboard. Choose Add it to this browser.' : 'Paste the copied text into the box, then choose Add it to this browser.';
  box.focus();
});
$('#prog-add').addEventListener('click', () => {
  const r = mergeProgress($('#prog-text').value);
  if (!r) { $('#prog-note').textContent = 'That text is not understudy progress. Copy it again with Copy my progress, then paste all of it.'; $('#prog-text').focus(); return; }
  $('#prog-note').textContent = `Added ${plural(r.sections, 'section')} and ${plural(r.answers, 'answer')}. Nothing was removed.`;
  $('#prog-text').value = ''; $('#prog-paste-box').hidden = true;
  updateProgressMenu(); refreshRows(); renderDetail(false);
  if (S.mode === 'read' && R.sec) { // the contents show the new ticks; the page itself stays where it is
    const beats = $('#toc-beats') ? $('#toc-beats').innerHTML : '';
    tocEl.innerHTML = tocHTML(R.ch, R.sec);
    if ($('#toc-beats')) $('#toc-beats').innerHTML = beats;
    showAnswerCount();
  }
  live('Progress added');
  $('#prog-paste').focus();
});
let keysOn = store.get('keys') !== false;
$('#keys-on').checked = keysOn;
$('#keys-on').addEventListener('change', e => { keysOn = e.currentTarget.checked; store.set('keys', keysOn); });
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    if (!progMenu.hidden) { closeMenu(true); return; }
    if (document.body.dataset.toc === 'open') { setDrawer(false, true); return; }
  }
  const t = e.target;
  if (!keysOn || e.ctrlKey || e.metaKey || e.altKey || (t.closest && t.closest('input, textarea, select, [contenteditable]'))) return;
  if (e.key === '/' && S.book) {
    e.preventDefault();
    if (matchMedia('(max-width: 767px)').matches && S.mode === 'read') { document.body.dataset.search = 'open'; $('#search-btn').setAttribute('aria-expanded', 'true'); }
    qEl.focus(); qEl.select();
  } else if (S.mode === 'read' && R.sec && (e.key === 'n' || e.key === 'p') && !(t.closest && t.closest('[role="tree"], #graph'))) {
    const { prev, next } = neighbours(R.sec), to = e.key === 'n' ? next : prev;
    if (to) { e.preventDefault(); go(to.id); } else live(e.key === 'n' ? 'This is the last written section' : 'This is the first section');
  }
});

// theme: follows the system until the reader chooses. The button names the theme it switches to.
const mq = matchMedia('(prefers-color-scheme: dark)');
function setTheme(t, save) {
  document.documentElement.dataset.theme = t;
  const next = t === 'dark' ? 'light' : 'dark';
  $('#theme-btn').setAttribute('aria-label', `Switch to ${next} theme`);
  $('#theme-tl').textContent = next === 'dark' ? 'Dark theme' : 'Light theme';
  document.querySelector('meta[name="theme-color"]').setAttribute('content', t === 'dark' ? '#2A2F36' : '#E4E9ED');
  themeFigures(t);
  if (save) store.set('theme', t);
}
/* Rare moment one: a hard-edged wipe, an ink line crossing the page (View
   Transitions). Without the API, from the keyboard or with reduced motion:
   a short colour cross-fade on explicit properties. */
function switchTheme() {
  const t = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  const apply = () => setTheme(t, true);
  live(t === 'dark' ? 'Dark theme' : 'Light theme');
  if (M.move() && document.startViewTransition) {
    const line = document.createElement('div');
    line.className = 'wipe-line'; line.setAttribute('aria-hidden', 'true');
    let vt;
    try { vt = document.startViewTransition(() => { apply(); document.body.appendChild(line); }); } catch (e) { apply(); return; }
    vt.ready.then(() => {
      const o = { duration: M.d(380), easing: EASE_IN_OUT, fill: 'both' };
      document.documentElement.animate({ clipPath: ['inset(0 100% 0 0)', 'inset(0 0 0 0)'] }, Object.assign({ pseudoElement: '::view-transition-new(root)' }, o));
      document.documentElement.animate({ transform: ['translateX(-4px)', `translateX(${innerWidth}px)`] }, Object.assign({ pseudoElement: '::view-transition-group(wipeline)' }, o));
    }).catch(() => {});
    vt.finished.finally(() => line.remove());
  } else {
    const html = document.documentElement;
    html.classList.add('theme-fade');
    apply();
    setTimeout(() => html.classList.remove('theme-fade'), M.d(220));
  }
}
$('#theme-btn').addEventListener('click', switchTheme);
mq.addEventListener('change', () => { if (!store.get('theme')) setTheme(mq.matches ? 'dark' : 'light', false); });

/* =====================================================================
   13. ROUTES. Only a plain name is ever put in location.hash:
     (nothing)            the map, as you left it
     map-<id>             the map, with that book, part, chapter or section selected
     <book>               the map with the book selected
     <book>-<n>           chapter n: its first written section
     <book>-<n>-<m>       section n.m, to read (the map if it is not written yet)
     <section>-<heading>  a heading inside that section
   ===================================================================== */
try { history.scrollRestoration = 'manual'; } catch (e) { /* older browsers restore by themselves */ }
let ownNav = false; // true when this page asked for the change (a link, a key); false for Back and Forward
function setMode(m) {
  if (S.mode === m) return;
  const was = S.mode;
  S.mode = m;
  document.body.dataset.mode = m;
  if (document.body.dataset.toc === 'open') setDrawer(false, false);
  if (was === 'read') { clearSearch(); if (R.sec) R.pos.set(R.sec.id, scrollY); scrollTo(0, 0); }
  if (m === 'map') { document.title = 'Your books · understudy'; if (S.book) { renderDetail(false); scheduleSticky(); } }
}
function setHash(h) { // the map's own selection replaces the entry: Back leaves the map, it does not replay clicks
  if (location.hash.slice(1) === h) return;
  try { history.replaceState(null, '', h ? '#' + h : location.pathname + location.search); } catch (e) { /* file:// in some browsers: the address simply stays */ }
}
function go(h) { ownNav = true; if (location.hash.slice(1) === h) route(); else location.hash = h; }
function resolve(h) { // -> { node, anchor, map }
  if (!h) return { node: null, map: true };
  const byId = S.book.byId;
  if (h.startsWith('map-') && byId.has(h.slice(4))) return { node: byId.get(h.slice(4)), map: true };
  if (byId.has(h)) return { node: byId.get(h) };
  for (let i = h.lastIndexOf('-'); i > 0; i = h.lastIndexOf('-', i - 1)) { // a heading inside a section
    const n = byId.get(h.slice(0, i));
    if (n && n.kind === 'section') return { node: n, anchor: h.slice(i + 1) };
  }
  return { node: null, map: true, unknown: true };
}
function route() {
  if (!S.book) return;
  const own = ownNav; ownNav = false;
  const raw = location.hash.slice(1), h = /^[A-Za-z0-9-]*$/.test(raw) ? raw : '';
  const r = resolve(h);
  let n = r.node;
  if (n && !r.map) {
    const sec = n.kind === 'section' ? (readTarget(n) && n) : n.kind === 'chapter' ? readable(n)[0] : null;
    if (sec && sec.chapter.file) {
      if (S.sel !== sec.id) select(sec.id, { from: 'route' });       // the map keeps its place beside the reader
      if (r.anchor && R.sec === sec && S.mode === 'read') { const el = document.getElementById(`${sec.id}-${r.anchor}`); if (el) { el.scrollIntoView({ block: 'start' }); return; } }
      showSection(sec, r.anchor, !own);
      return;
    }
  }
  setMode('map');
  if (r.unknown) live('That address does not name anything on your shelf. Showing the map.');
  if (n && n.id !== S.sel) select(n.id, { from: 'route' });
  if (!G.fitted) fitOnce();
  const hd = !own && document.activeElement === document.body ? null : rowEls.get(S.sel);
  if (own && hd) focusRow(S.sel);
}
addEventListener('hashchange', route);
document.addEventListener('click', e => { // a link inside this page is this page's own navigation
  const a = e.target.closest && e.target.closest('a[href^="#"]');
  if (!a || e.defaultPrevented || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
  const h = a.getAttribute('href').slice(1);
  if (a.id === 'skip') return;
  ownNav = true;
  if (location.hash.slice(1) === h) { e.preventDefault(); route(); }
  else if (R.sec && h.startsWith(R.sec.id + '-') && !S.book.byId.has(h)) { // a beat on this page: move there, keep one history entry
    e.preventDefault(); ownNav = false;
    const el = document.getElementById(h);
    if (el) { el.scrollIntoView({ block: 'start', behavior: M.move() ? 'smooth' : 'auto' }); setHash(h); if (document.body.dataset.toc === 'open') setDrawer(false, false); }
  }
});
$('#skip').addEventListener('click', e => { // no hash change: focus the main thing of the view
  e.preventDefault();
  if (S.mode === 'read') { const h1 = $('h1', articleEl); if (h1) h1.focus(); return; }
  if (S.mode !== 'map') { const b = $('#notice h1'); if (b) b.focus(); return; }
  if (document.body.dataset.tab !== 'tree' && matchMedia('(max-width: 767px)').matches) setTab('tree');
  const li = rowEls.get(roving); if (li) { li.focus({ preventScroll: true }); ensureRowVisible(li); }
});

/* =====================================================================
   14. START: read the index beside this page, or say plainly why not
   ===================================================================== */
const MARK = $('.brand .mark').outerHTML;
function notice(kind, err) {
  const cmd = (text, label, shell) => `<div class="cmdline"><code>${shell ? '<span class="dollar" aria-hidden="true">$ </span>' : ''}<span id="n-cmd">${esc(text)}</span></code><button class="btn" type="button" id="n-copy" data-copy="${esc(text)}">${CK}<span class="bl">${label}</span></button></div><p class="confirm" id="n-note"></p>`;
  let h;
  if (kind === 'blocked') {
    h = `<h1 tabindex="-1">One step to open your books</h1><p>This page was opened straight from a file, and a browser will not let a page opened that way read the book files beside it. Nothing is wrong with your books.</p>` +
      `<p>In your understudy folder, run this:</p>${cmd('python3 scripts/us_reader.py --serve', 'Copy the command', true)}` +
      `<p>Then open the address it prints (usually <code>http://localhost:8765</code>). It needs no internet, and it sends nothing anywhere.</p>`;
  } else if (kind === 'empty') {
    h = `<h1 tabindex="-1">Your shelf is empty</h1><p>A book appears here as soon as your agent writes one. Start your coding agent in your understudy folder and tell it what you want to learn, for example:</p>` +
      `${cmd('I want to learn C from scratch', 'Copy this sentence')}` +
      `<p>It asks what it needs, shows you the book's contents page to approve, then writes the first chapter. Reload this page when it has: the book, its chapters and what each one needs will be here.</p>`;
  } else {
    h = `<h1 tabindex="-1">The index of your books could not be read</h1><p>This page reads <code>manifest.json</code> beside it and could not use it (${esc(err && err.message || 'unknown reason')}). Your chapters are untouched.</p>` +
      `<p>Build the index again in your understudy folder, then reload:</p>${cmd('python3 scripts/us_index.py', 'Copy the command', true)}`;
  }
  $('#notice').innerHTML = `<div class="panel notice-card">${MARK}${h}</div>`;
  S.mode = kind; document.body.dataset.mode = kind;
  document.title = kind === 'empty' ? 'Your shelf is empty · understudy' : kind === 'blocked' ? 'One step to open your books · understudy' : 'The index could not be read · understudy';
  $('#n-copy').addEventListener('click', e => copyText(e.currentTarget.dataset.copy, e.currentTarget, $('#n-note')));
}
setTheme(store.get('theme') || (mq.matches ? 'dark' : 'light'), false);
setView(store.get('view') || 'both');
if (store.get('minimap') === false) $('#map-btn').setAttribute('aria-pressed', 'false');
applyBand();
(async () => {
  let man;
  if (location.protocol === 'file:') return notice('blocked'); // browsers do not let a page opened from disk read its neighbours; asking would only log an error
  try {
    const res = await fetch('manifest.json', { cache: 'no-cache' });
    if (res.status === 404) return notice('empty');
    if (!res.ok) throw new Error('manifest.json: ' + res.status);
    man = await res.json();
    if (!man || !Array.isArray(man.books)) throw new Error(man && man.nodes ? 'it was made by an older understudy' : 'it does not list any books');
  } catch (err) {
    return notice('broken', err);
  }
  if (!man.books.length) return notice('empty');
  S.book = buildShelf(man);
  loadProgress();
  const raw = location.hash.slice(1), h = /^[A-Za-z0-9-]*$/.test(raw) ? raw : '';
  const r = resolve(h);
  document.body.dataset.mode = S.mode = 'map';
  const firstVisit = startMap(r.node ? r.node.id : null);
  updateProgressMenu();
  $('#shelf-sum').textContent = `${plural(S.book.books.length, 'book')}, ${plural(S.book.chapters.length, 'chapter')}`;
  route();
  if (S.mode === 'map') entrance(firstVisit);
  (window.requestIdleCallback || setTimeout)(loadSearch, { timeout: 1500 });
})();

// a small, read-only handle for the tests
window.__us = { S, G, GL, R, SR, M, get PR() { return PR; }, buildShelf, layoutShelf, layoutBook, ancestorsOf, descendantsOf, learningPath, wrapText, splitChapter, search, select, fitAll, boxOf, camera, LABEL_K, progressText, mergeProgress, beforePrint, afterPrint, go };
