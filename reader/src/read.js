/* =====================================================================
   10. THE CHAPTER READING VIEW
   One section is one page: its seven beats, then Check yourself. The
   chapter file is fetched once and split at its "## N.M" headings; only
   the section in view is rendered, so a 30,000-word chapter opens as
   fast as a short one.
   ===================================================================== */
const R = { ch: null, sec: null, doc: null, docs: new Map(), pos: new Map(), spy: null, token: 0 };
const articleEl = $('#article'), tocEl = $('#toc'), otpEl = $('#otp');
const slug = s => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');

/** Chapter text -> { preface, parts: Map(number -> Markdown) }. Build markers
    (HTML comments) and the generated contents list are dropped here, outside
    code fences only, so they can never show. One marker leaves a trace: a
    block marked unrun="why" gets the standard note under it. */
function splitChapter(text) {
  const out = { preface: [], parts: new Map() };
  let cur = out.preface, fence = null, comment = false, contents = false, unrun = null;
  for (let line of text.replace(/\r\n?/g, '\n').split('\n')) {
    if (fence) {
      cur.push(line);
      const m = /^(\s*)(`{3,}|~{3,})\s*$/.exec(line);
      if (m && m[2][0] === fence[0] && m[2].length >= fence.length) {
        fence = null;
        if (unrun !== null) cur.push(`${m[1]}<p class="unrun">Not run on the machine this book was written on${unrun ? ': ' + esc(unrun) : ''}. Your screen is the first to show what it prints.</p>`, '');
        unrun = null;
      }
      continue;
    }
    if (comment) { const k = line.indexOf('-->'); if (k < 0) continue; comment = false; line = line.slice(k + 3); if (!line.trim()) continue; }
    const t = line.trim();
    if (t === '<!-- contents -->') { contents = true; continue; }
    if (contents) { if (t === '<!-- /contents -->') contents = false; continue; }
    let had = false;
    for (let i = line.indexOf('<!--'); i >= 0; i = line.indexOf('<!--', i)) {
      if ((line.slice(0, i).match(/`/g) || []).length % 2) { i += 4; continue; } // inside inline code: it is text
      const k = line.indexOf('-->', i + 4);
      had = true;
      if (k < 0) { line = line.slice(0, i); comment = true; break; }
      const u = /^\s*code:.*?\sunrun=("(?:[^"\\]|\\.)*"|\S+)/.exec(line.slice(i + 4, k));
      if (u) unrun = u[1].replace(/^"|"$/g, '').replace(/\\(.)/g, '$1').replace(/[.\s]+$/, '');
      line = line.slice(0, i) + line.slice(k + 3);
    }
    if (had && !line.trim()) continue;
    const f = /^\s*(`{3,}|~{3,})/.exec(line);
    if (f) { fence = f[1]; cur.push(line); continue; }
    if (line.trim()) unrun = null;   // the marker's block is the fence right under it, nothing further down
    if (/^# /.test(line) && cur === out.preface && !out.title) { out.title = line.slice(2).trim(); continue; }
    const h = /^## +(\d+\.\d+)\b/.exec(line);
    if (h) { cur = []; out.parts.set(h[1], cur); continue; }
    cur.push(line);
  }
  out.preface = out.preface.join('\n').trim();
  for (const [k, v] of out.parts) out.parts.set(k, v.join('\n'));
  return out;
}
async function loadChapter(ch) {
  if (R.docs.has(ch.id)) return R.docs.get(ch.id);
  const res = await fetch(encodeURI(ch.file), { cache: 'no-cache' });
  if (!res.ok) throw new Error(`${ch.file}: ${res.status}`);
  const doc = splitChapter(await res.text());
  R.docs.set(ch.id, doc);
  return doc;
}

/* ---- Markdown to a safe fragment ---- */
const ALLOWED = new Set('A ABBR B BLOCKQUOTE BR CODE DD DEL DETAILS DIV DL DT EM H1 H2 H3 H4 H5 H6 HR I IMG INPUT KBD LI MARK OL P PRE S SMALL SPAN STRONG SUB SUMMARY SUP TABLE TBODY TD TFOOT TH THEAD TR U UL'.split(' '));
function clean(html) { // the book is the learner's own, but a published book is anyone's: allow a short list, drop handlers
  const t = document.createElement('template');
  t.innerHTML = html;
  for (const el of [...t.content.querySelectorAll('*')]) {
    if (!t.content.contains(el)) continue;
    if (!ALLOWED.has(el.tagName)) {
      if (/^(SCRIPT|STYLE|IFRAME|OBJECT|EMBED|LINK|META|BASE|FORM|TEMPLATE|SVG|MATH)$/i.test(el.tagName)) el.remove();
      else el.replaceWith(document.createTextNode('<' + el.tagName.toLowerCase() + '>'), ...el.childNodes); // "<stdio.h>" typed in prose is text
      continue;
    }
    for (const a of [...el.attributes]) {
      if (/^on|^style$|^srcdoc$|^id$|^name$/i.test(a.name) || (/^(href|src)$/i.test(a.name) && /^\s*(javascript|vbscript|data):/i.test(a.value))) el.removeAttribute(a.name);
    }
    if (el.tagName === 'INPUT') el.disabled = true;
  }
  return t.content;
}
function highlight(code, lang) {
  try { if (window.hljs && hljs.getLanguage(lang)) return hljs.highlight(code, { language: lang, ignoreIllegals: true }).value; } catch (e) { /* fall through to plain text */ }
  return esc(code);
}
const COPY = `<button class="btn flat copy" type="button">${CK}<span class="bl">Copy</span></button>`;
const answerBodies = new WeakMap(); // a hidden answer lives here, outside the page, until its card is turned over
const figSources = new Map();       // file url -> SVG text, fetched once
const urlOf = (src, sec) => new URL(src, new URL(encodeURI(sec.chapter.file), location.href));

/** Turn one section's Markdown into the page's own structures. */
function renderMarkdown(md, sec, ids) {
  const frag = clean(marked.parse(md, { gfm: true, async: false }));
  const q = s => [...frag.querySelectorAll(s)];
  // headings: the page's h1 is the section title, so the beats ("###") become h2
  const seen = new Set();
  for (const h of q('h1,h2,h3,h4,h5,h6')) {
    const lvl = Math.min(4, Math.max(2, Number(h.tagName[1]) - 1));
    const n = document.createElement('h' + lvl);
    n.append(...h.childNodes);
    let s = slug(n.textContent) || 'part';
    while (seen.has(s)) s += '-2';
    seen.add(s);
    if (lvl === 2) { n.className = 'beat beat-' + s; if (ids) n.id = `${sec.id}-${s}`; }
    h.replaceWith(n);
  }
  for (const p of q('p')) { // "**Check yourself**" is the eighth heading of a lesson
    if (p.childNodes.length === 1 && p.firstChild.nodeName === 'STRONG' && /^check yourself$/i.test(p.textContent.trim())) {
      const n = document.createElement('h2');
      n.className = 'beat beat-check'; n.textContent = 'Check yourself';
      if (ids) n.id = `${sec.id}-check-yourself`;
      p.replaceWith(n);
    }
  }
  // code: programs are highlighted, numbered and can be copied; output and plain text are left quiet
  for (const code of q('pre > code')) {
    const lang = ((code.className.match(/language-([\w+#.-]+)/) || [])[1] || 'text').toLowerCase();
    const raw = code.textContent.replace(/\n$/, '');
    const box = document.createElement('div');
    if (lang === 'console') {
      box.className = 'code term';
      box.innerHTML = `<div class="code-top"><span class="lang">terminal</span>${COPY.replace('>Copy<', '>Copy commands<')}</div><pre><code>${raw.split('\n').map(l =>
        l.startsWith('$ ') ? `<span class="prompt">$ </span><span class="cmd">${esc(l.slice(2))}</span>` : esc(l)).join('\n')}</code></pre>`;
    } else if (lang !== 'text' && lang !== 'plaintext' && window.hljs && hljs.getLanguage(lang)) {
      const n = raw.split('\n').length;
      box.className = 'code prog';
      box.innerHTML = `<div class="code-top"><span class="lang">${esc(lang)}</span>${COPY}</div><pre>${n > 1 ? `<span class="ln" aria-hidden="true">${Array.from({ length: n }, (_, i) => i + 1).join('\n')}</span>` : ''}<code class="hl">${highlight(raw, lang)}</code></pre>`;
    } else {
      box.className = 'code out';
      box.innerHTML = `<pre><code>${esc(raw)}</code></pre>`;
    }
    code.parentElement.replaceWith(box);
  }
  for (const t of q('table')) { // a hand trace scrolls inside itself, never the page
    const w = document.createElement('div');
    w.className = 'tablewrap';
    t.replaceWith(w); w.appendChild(t);
  }
  // figures
  for (const img of q('img')) {
    const src = img.getAttribute('src') || '', alt = img.getAttribute('alt') || '';
    const fig = document.createElement('figure');
    fig.className = 'fig';
    if (/^[a-z][a-z0-9+.-]*:/i.test(src) || src.startsWith('//')) { // this page makes no request to another site
      fig.innerHTML = `<p class="fig-missing">A picture kept on another site is not loaded here: <a href="${esc(src)}" target="_blank" rel="noopener noreferrer">${esc(src)}</a>${alt ? `. It shows: ${esc(alt)}` : ''}</p>`;
    } else {
      const url = urlOf(src, sec).href;
      if (/\.svg(\?|#|$)/i.test(src)) {
        const host = document.createElement('span');
        host.className = 'fig-svg'; host.dataset.src = url; host.dataset.alt = alt;
        host.textContent = alt; // shown until the drawing arrives, and if it never does
        fig.appendChild(host);
      } else {
        const im = document.createElement('img');
        im.src = url; im.alt = alt; im.loading = 'lazy'; im.decoding = 'async';
        fig.appendChild(im);
      }
      fig.insertAdjacentHTML('beforeend', '<button class="btn flat fig-zoom" type="button" aria-label="Enlarge this figure"><svg class="ic" viewBox="0 0 16 16" aria-hidden="true"><path d="M9 2h5v5M7 14H2V9M14 2 9.5 6.5M2 14l4.5-4.5"/></svg><span class="bl">Enlarge</span></button>');
    }
    const p = img.parentElement;
    if (p && p.tagName === 'P' && p.childNodes.length === 1) {
      const cap = p.nextElementSibling;
      p.replaceWith(fig);
      if (cap && cap.tagName === 'P' && cap.firstChild && cap.firstChild.nodeName === 'EM' && /^Figure\b/.test(cap.textContent)) {
        const fc = document.createElement('figcaption');
        fc.append(...cap.childNodes); cap.remove(); fig.appendChild(fc);
      }
    } else img.replaceWith(fig);
  }
  for (const b of q('blockquote')) if (/^simplified here/i.test(b.textContent.trim())) b.classList.add('note');
  // links: section references, other chapters, and the wider web
  const book = sec.book;
  const secLink = n => { const s = S.book.byKey.get(`${book.name}:${n}`); return s ? (isDone(s) && s.chapter.file ? '#' + s.id : '#map-' + s.id) : null; };
  for (const a of q('a[href]')) {
    const href = a.getAttribute('href');
    if (/^(https?:|mailto:)/i.test(href)) { a.target = '_blank'; a.rel = 'noopener noreferrer'; a.classList.add('ext'); continue; }
    let u;
    try { u = urlOf(href, sec); } catch (e) { continue; }
    const anchor = decodeURIComponent(u.hash.slice(1));
    const file = decodeURIComponent(u.href.split('#')[0].slice(new URL('.', location.href).href.length));
    const ch = href.startsWith('#') ? sec.chapter : S.book.chapters.find(c => c.file === file);
    if (!ch) { a.href = u.href; a.target = '_blank'; a.rel = 'noopener'; continue; }
    const to = ch.children.find(s => s.anchor === anchor);
    a.setAttribute('href', to ? (isDone(to) ? '#' + to.id : '#map-' + to.id) : ch === sec.chapter && anchor ? `#${sec.id}-${slug(anchor)}` : '#' + ch.id);
  }
  const walker = document.createTreeWalker(frag, NodeFilter.SHOW_TEXT);
  const texts = [];
  for (let t = walker.nextNode(); t; t = walker.nextNode()) if (t.data.includes('§') && !t.parentElement.closest('a, pre, code')) texts.push(t);
  for (const t of texts) {
    const parts = t.data.split(/(§\s?\d+\.\d+)/);
    if (parts.length < 2) continue;
    t.replaceWith(...parts.map((p, i) => {
      const href = i % 2 ? secLink(p.replace(/^§\s?/, '')) : null;
      if (!href) return document.createTextNode(p);
      const a = document.createElement('a');
      a.className = 'xref'; a.href = href; a.textContent = p;
      return a;
    }));
  }
  // hidden answers, last, so that what is inside them is already dressed: cards, deepest first; the answer leaves the page until the card is turned
  q('details').reverse().forEach(d => {
    const sum = d.querySelector(':scope > summary') || document.createElement('summary');
    const label = sum.textContent.trim() || 'Answer';
    const body = document.createDocumentFragment();
    body.append(...[...d.childNodes].filter(c => c !== sum));
    answerBodies.set(d, body);
    d.className = body.querySelector('.code, .tablewrap, figure') ? 'card wide' : 'card'; d.open = false;
    sum.innerHTML = `<span class="disc" aria-hidden="true"></span><span class="cl">${esc(label)}</span><span class="ch">turn over</span>`;
    d.replaceChildren(sum, Object.assign(document.createElement('div'), { className: 'card-body' }));
  });
  return frag;
}

/* ---- figures: an SVG is inlined in its own shadow tree, so its styles stay its own and it follows the page theme ---- */
function mountFigure(host) {
  const put = text => {
    const svgEl = new DOMParser().parseFromString(text, 'image/svg+xml').documentElement;
    if (!svgEl || svgEl.nodeName !== 'svg') throw new Error('not an SVG');
    // a drawing may hold shapes, text and its own styles; nothing that runs, and nothing that fetches from elsewhere
    const local = v => v.replace(/@import[^;]*;?/gi, '').replace(/url\(\s*['"]?(?!#)[^)]*\)/gi, 'none');
    svgEl.querySelectorAll('script, foreignObject, a, image, iframe, audio, video').forEach(x => x.remove());
    for (const x of [svgEl, ...svgEl.querySelectorAll('*')]) for (const a of [...x.attributes]) {
      if (/^on/i.test(a.name) || (/href$/i.test(a.name) && !a.value.startsWith('#'))) x.removeAttribute(a.name);
      else if (a.name === 'style' || /url\(/i.test(a.value)) x.setAttribute(a.name, local(a.value));
    }
    for (const st of svgEl.querySelectorAll('style')) st.textContent = local(st.textContent);
    const w = parseFloat(svgEl.getAttribute('width')) || (svgEl.viewBox.baseVal && svgEl.viewBox.baseVal.width) || 0;
    if (!svgEl.getAttribute('viewBox') && w) svgEl.setAttribute('viewBox', `0 0 ${w} ${parseFloat(svgEl.getAttribute('height')) || w}`);
    svgEl.removeAttribute('width'); svgEl.removeAttribute('height');
    svgEl.setAttribute('data-theme', printing ? 'light' : document.documentElement.dataset.theme);
    svgEl.style.cssText = 'display:block;width:100%;height:auto';
    if (!svgEl.querySelector('title') && host.dataset.alt) { svgEl.setAttribute('role', 'img'); svgEl.setAttribute('aria-label', host.dataset.alt); }
    host.textContent = '';
    if (w) host.style.maxWidth = w + 'px';
    (host.shadowRoot || host.attachShadow({ mode: 'open' })).replaceChildren(document.importNode(svgEl, true));
    host.classList.add('ready');
  };
  const url = host.dataset.src;
  if (figSources.has(url)) { try { put(figSources.get(url)); } catch (e) { /* the alt text stays */ } return; }
  fetch(url).then(r => r.ok ? r.text() : Promise.reject(new Error(r.status))).then(t => { figSources.set(url, t); if (host.isConnected) put(t); })
    .catch(() => { host.classList.add('failed'); });
}
function themeFigures(t) { for (const h of $$('.fig-svg.ready')) { const s = h.shadowRoot && h.shadowRoot.querySelector('svg'); if (s) s.setAttribute('data-theme', t); } }
/** After a fragment is on the page: draw the figures, then fit what is too wide. */
function settle(root) {
  $$('.fig-svg:not(.ready)', root).forEach(mountFigure);
  requestAnimationFrame(() => fit(root));
}
/* ---- wrap lines: one switch for every terminal and output box, kept in this browser ---- */
const html = document.documentElement;
html.toggleAttribute('data-wrap', store.get('wrap') === true);
/** A terminal or output box with a line too long for it gets the switch; anything that still scrolls sideways gets a keyboard's way in. */
function fit(root) {
  const on = html.hasAttribute('data-wrap'), wide = el => el.scrollWidth > el.clientWidth + 1;
  html.removeAttribute('data-wrap');   // measured with the lines unwrapped, so the switch stays where it was
  const need = $$('.code.term pre, .code.out pre', root).filter(wide);
  html.toggleAttribute('data-wrap', on);
  const btn = `<button class="btn flat wrap" type="button" aria-pressed="${on}" aria-label="Wrap lines"><span class="bl">Wrap<span class="wl"> lines</span></span></button>`;
  for (const pre of need) {
    const box = pre.parentElement;
    if ($('.wrap', box)) continue;
    if (box.classList.contains('term')) $('.copy', box).insertAdjacentHTML('beforebegin', btn);
    else box.insertAdjacentHTML('afterbegin', `<div class="code-top"><span class="lang">output</span>${btn}</div>`);
  }
  for (const el of $$('pre, .tablewrap', root)) {
    if (wide(el)) { el.tabIndex = 0; el.setAttribute('role', 'region'); el.setAttribute('aria-label', el.tagName === 'PRE' ? 'Code, scrolls sideways' : 'Table, scrolls sideways'); }
    else if (el.getAttribute('role') === 'region') for (const a of ['tabindex', 'role', 'aria-label']) el.removeAttribute(a);
  }
}
function setWrap(on, from) {
  const y = from.getBoundingClientRect().top;
  html.toggleAttribute('data-wrap', on);
  store.set('wrap', on);
  for (const b of $$('button.wrap', articleEl)) b.setAttribute('aria-pressed', String(on));
  fit(articleEl);
  scrollBy(0, from.getBoundingClientRect().top - y);   // the switch that was pressed stays where it is on the screen
  live(on ? 'Long lines wrap' : 'Long lines scroll sideways');
}

/* ---- the lightbox: tap a figure to enlarge it ---- */
const lightbox = $('#lightbox');
function enlarge(fig) {
  const img = fig.querySelector('img'), host = fig.querySelector('.fig-svg');
  const body = $('#lightbox-body');
  body.textContent = '';
  let el, natural, ratio, shown;
  if (img && img.naturalWidth) {
    el = img.cloneNode(); el.loading = 'eager';
    natural = img.naturalWidth; ratio = img.naturalHeight / img.naturalWidth; shown = img.clientWidth;
  } else if (host && host.shadowRoot) {
    const svgEl = host.shadowRoot.querySelector('svg'), vb = svgEl.viewBox.baseVal;
    el = document.createElement('span');
    el.className = 'fig-svg ready';
    el.attachShadow({ mode: 'open' }).appendChild(svgEl.cloneNode(true));
    natural = (parseFloat(host.style.maxWidth) || vb.width || 640) * 2.5; ratio = vb.width ? vb.height / vb.width : 0.6; shown = host.clientWidth;
  } else return;
  const cap = fig.querySelector('figcaption');
  $('#lightbox-cap').textContent = cap ? cap.textContent : '';
  // as large as the window allows; when that is hardly larger than on the page (a phone), larger still, to scroll around
  const availW = innerWidth - 16 - 6 - 24, availH = innerHeight - 16 - 6 - 24 - 52 - (cap ? 64 : 0);
  let w = Math.min(natural, availW, availH / ratio);
  if (w < shown * 1.25) w = Math.min(natural, shown * 1.8);
  el.style.width = Math.round(w) + 'px';
  body.appendChild(el);
  lightbox._from = document.activeElement;
  try { lightbox.showModal(); } catch (e) { return; }
  $('#lightbox-hint').textContent = body.scrollWidth > body.clientWidth + 1 || body.scrollHeight > body.clientHeight + 1 ? 'Scroll to see the rest' : '';
  if (M.fade()) M.run(lightbox, M.reduced ? [{ opacity: 0 }, { opacity: 1 }] : [{ opacity: 0, transform: 'scale(0.96)' }, { opacity: 1, transform: 'none' }], { duration: M.reduced ? 100 : 200, easing: EASE_OUT });
}
lightbox.addEventListener('click', e => { if (e.target === lightbox || e.target.closest('#lightbox-close')) lightbox.close(); });
lightbox.addEventListener('close', () => { $('#lightbox-body').textContent = ''; const f = lightbox._from; if (f && f.isConnected) f.focus({ preventScroll: true }); });

/* ---- one click handler for everything inside the text ---- */
articleEl.addEventListener('click', e => {
  const copy = e.target.closest('button.copy');
  if (copy) {
    const box = copy.closest('.code'), code = box.querySelector('code');
    const text = box.classList.contains('term') ? $$('.cmd', code).map(c => c.textContent).join('\n') || code.textContent : code.textContent;
    copyText(text, copy);
    return;
  }
  const wrap = e.target.closest('button.wrap');
  if (wrap) { setWrap(!html.hasAttribute('data-wrap'), wrap); return; }
  const ask = e.target.closest('[data-copy]');
  if (ask) { copyText(ask.dataset.copy, ask, ask.parentElement.querySelector('.confirm')); return; }
  const fig = e.target.closest('figure.fig');
  if (fig && (e.target.closest('.fig-zoom') || e.target.closest('img, .fig-svg'))) enlarge(fig);
});
articleEl.addEventListener('error', e => { // a picture that is not there: say so, and say what it showed
  const img = e.target;
  if (img.tagName !== 'IMG' || !img.closest('figure.fig')) return;
  const fig = img.closest('figure.fig'), cap = fig.querySelector('figcaption');
  fig.innerHTML = `<p class="fig-missing">A picture is missing: <code>${esc(decodeURIComponent(img.src.slice(new URL('.', location.href).href.length)))}</code>${img.alt ? `. It shows: ${esc(img.alt)}` : ''}</p>`;
  if (cap) fig.appendChild(cap);
}, true);
/* A card is turned over: the answer comes back into the page and is noted
   as seen. Turned back, it leaves again, so neither find-in-page nor print
   can show an answer the reader has not asked for. */
articleEl.addEventListener('toggle', e => {
  const d = e.target;
  if (!(d instanceof HTMLDetailsElement) || !d.classList.contains('card')) return;
  const body = d.querySelector(':scope > .card-body');
  if (d.open) {
    const f = answerBodies.get(d);
    if (f) { body.appendChild(f); settle(body); }
    d.querySelector('.ch').textContent = 'hide';
    const i = topCards().indexOf(d);
    if (R.sec && i >= 0) markAnswer(R.sec, i);
    if (M.move()) M.run(body, [{ opacity: 0, transform: 'perspective(900px) rotateX(-70deg)' }, { opacity: 1, transform: 'perspective(900px) rotateX(0)' }], { duration: 220, easing: EASE_OUT });
    else if (M.fade() && M.reduced) M.run(body, [{ opacity: 0 }, { opacity: 1 }], { duration: 100, easing: 'ease' });
  } else {
    const f = document.createDocumentFragment();
    f.append(...body.childNodes);
    answerBodies.set(d, f);
    d.querySelector('.ch').textContent = 'turn over';
  }
}, true);
function markAnswer(sec, i) {
  const k = pkey(sec), list = PR.answers[k] || (PR.answers[k] = []);
  if (!list.includes(i)) { list.push(i); list.sort((a, b) => a - b); saveProgress(); updateProgressMenu(); }
  showAnswerCount();
}
const topCards = () => $$('.prose:not(.print-only) details.card', articleEl).filter(x => !x.parentElement.closest('.card-body'));
function showAnswerCount() {
  const cards = topCards();
  const seen = R.sec ? answersSeen(R.sec) : [];
  cards.forEach((d, i) => d.classList.toggle('seen', seen.includes(i)));
  for (const a of $$('[data-q]')) { const on = seen.includes(Number(a.dataset.q)); a.classList.toggle('on', on); a.setAttribute('aria-label', `Exercise ${Number(a.dataset.q) + 1}${on ? ', answer turned over' : ''}`); }
  for (const el of $$('.check-count')) el.textContent = cards.length ? `${seen.filter(i => i < cards.length).length}/${cards.length}` : '';
}

/* ---- the page for one section ---- */
const levelSquares = l => `<span class="lv" aria-hidden="true">${[1, 2, 3, 4, 5].map(i => `<i${i <= l ? ' class="on"' : ''}></i>`).join('')}</span>`;
function neighbours(sec) { // previous and next written sections, across chapters of the same book
  const all = bookSections(sec.book), i = all.indexOf(sec);
  return { prev: all[i - 1] || null, next: all[i + 1] || null, i, all };
}
function tocHTML(ch, sec) {
  const done = readCount(ch), list = readable(ch);
  const chs = S.book.chapters.filter(c => c.book === ch.book), ci = chs.indexOf(ch);
  const other = (c, dir) => c ? `<a class="toc-other" href="#${c.readable ? esc(c.id) : 'map-' + esc(c.id)}"><span class="k">${dir} chapter${c.readable ? '' : ', not written'}</span><span>${esc(c.n)} ${esc(c.title)}</span></a>` : '';
  return `<div class="toc-head"><a class="toc-book" href="#map-${esc(ch.id)}"><svg class="ic" viewBox="0 0 16 16" aria-hidden="true"><path d="M10 3 5 8l5 5"/></svg><span>${esc(ch.book.title)}</span></a>` +
    `<p class="toc-title"><span class="no">${esc(ch.n)}</span> ${esc(ch.title)}</p>` +
    `<p class="toc-prog" id="toc-prog">${done} of ${list.length} sections opened${ch.unrun ? `, ${ch.unrun} not run` : ''}</p></div>` +
    `<ol class="toc-list">${ch.children.map(s => {
      const cur = s === sec, ok = isDone(s);
      return `<li class="${ok ? '' : 'planned'}"><a href="#${ok ? '' : 'map-'}${esc(s.id)}"${cur ? ' aria-current="page"' : ''}${ok ? '' : ' title="Planned, not written yet"'}>` +
        `<span class="no">${esc(s.num)}</span><span class="tt">${esc(s.title)}${ok ? '' : ' <span class="k">planned</span>'}</span>${ok && wasOpened(s) ? TICK + '<span class="sr-only">opened</span>' : ''}</a>${cur ? '<ol class="beats" id="toc-beats"></ol>' : ''}</li>`;
    }).join('')}</ol>` +
    `<div class="toc-foot">${other(chs[ci - 1], 'Previous')}${other(chs[ci + 1], 'Next')}<button class="btn" type="button" id="print-btn">Print this chapter</button></div>`;
}
function headHTML(sec, first) {
  const ch = sec.chapter, kind = sec.sort === 'story' ? 'Story' : sec.sort === 'practice' ? 'Practice' : 'Lesson';
  return `<header class="sec-head">${first ? `<p class="ch-title"><span class="k">Chapter ${esc(ch.n)}</span>${esc(ch.title)}</p>` : `<p class="ch-line">Chapter ${esc(ch.n)}: ${esc(ch.title)}</p>`}` +
    `<h1 tabindex="-1"><span class="secno">${esc(sec.num)}</span> ${esc(sec.title)}</h1>` +
    `<p class="sec-meta">${levelSquares(sec.level)}<span>Level ${sec.level}, ${LEVELS[sec.level - 1]}</span><span>${kind}</span><span>${num(sec.words)} words, about ${minutes(sec.words)} min</span></p></header>`;
}
function pagerHTML(sec) {
  const { prev, next } = neighbours(sec);
  const link = (s, cls, label) => `<a class="btn ${cls}" href="#${esc(s.id)}" rel="${cls.includes('next') ? 'next' : 'prev'}"><span class="k">${label}${s.chapter !== sec.chapter ? `, chapter ${esc(s.chapter.n)}` : ''}</span><span class="tt">${esc(s.num)} ${esc(s.title)}</span></a>`;
  let h = '<nav class="pager" aria-label="Previous and next section">';
  h += prev ? link(prev, 'prev', 'Previous') : `<a class="btn prev" href="#map-${esc(sec.chapter.id)}"><span class="k">Back</span><span class="tt">The map of your books</span></a>`;
  if (next) h += link(next, 'primary next', 'Next');
  else {
    const ask = request(sec.book);
    h += ask ? `<div class="pager-end"><p>That is everything written in this book so far.</p><button class="btn primary" type="button" data-copy="${esc(ask)}">${CK}<span class="bl">Copy a request for Claude</span></button><p class="cmdtext">Copies: ${esc(ask)}</p><p class="confirm"></p></div>`
      : `<div class="pager-end"><p>That is the last section of the book.</p><a class="btn primary" href="#map-${esc(sec.book.id)}">Back to the map</a></div>`;
  }
  return h + '</nav>';
}
/** Show one section. `anchor` is a heading inside it; `restore` puts the reader back where they were. */
async function showSection(sec, anchor, restore) {
  const token = ++R.token, ch = sec.chapter;
  if (R.sec) R.pos.set(R.sec.id, scrollY);
  setMode('read');
  let doc;
  try { doc = await loadChapter(ch); } catch (err) {
    if (token !== R.token) return;
    R.sec = null; R.ch = ch;
    tocEl.innerHTML = tocHTML(ch, sec); otpEl.innerHTML = '';
    articleEl.innerHTML = `<div class="trouble"><h1 tabindex="-1">This chapter could not be opened</h1><p>The index lists <code>${esc(ch.file)}</code>, but the file did not load (${esc(err.message)}). The rest of your books still work.</p>` +
      `<p>If the chapter was moved or renamed, run this in your understudy folder, then reload:</p><pre class="cmdline"><code>python3 scripts/us_index.py</code></pre><p><a class="btn" href="#map-${esc(ch.id)}">Back to the map</a></p></div>`;
    document.title = 'Could not open the chapter';
    return;
  }
  if (token !== R.token) return;
  const md = doc.parts.get(sec.num);
  R.ch = ch; R.sec = sec; R.doc = doc;
  const first = readable(ch)[0] === sec;
  const prose = document.createElement('div');
  prose.className = 'prose';
  if (md === undefined) prose.innerHTML = `<div class="trouble"><p>Section ${esc(sec.num)} is in the index but not in <code>${esc(ch.file)}</code>. Run <code>python3 scripts/us_index.py</code> in your understudy folder, then reload.</p></div>`;
  else {
    if (first && doc.preface) prose.appendChild(renderMarkdown(doc.preface, sec, false));
    prose.appendChild(renderMarkdown(md, sec, true));
  }
  articleEl.innerHTML = headHTML(sec, first);
  articleEl.appendChild(prose);
  articleEl.insertAdjacentHTML('beforeend', pagerHTML(sec) + '<p class="privacy">What you have opened is remembered in this browser only. Nothing is sent anywhere.</p>');
  // progress: this section is now opened
  const k = pkey(sec);
  if (!PR.opened[k]) PR.opened[k] = Math.floor(Date.now() / 864e5);
  if (!anchor && restore && PR.last === k && PR.beat) anchor = PR.beat;   // a reload: back to the beat that was being read
  if (PR.last !== k) PR.beat = '';
  PR.last = k; saveProgress();
  tocEl.innerHTML = tocHTML(ch, sec);
  const beats = $$('h2.beat', prose);
  const items = beats.map((h, i) => `<li><a href="#${esc(h.id)}" data-beat="${i}"><span>${esc(h.textContent)}${h.classList.contains('beat-check') ? ' <span class="check-count k"></span>' : ''}</span></a></li>`).join('');
  const cards = beats.length ? [] : topCards();   // a practice section has no beats: list its exercises instead
  cards.forEach((d, i) => { const q = d.previousElementSibling || d; if (!q.id) q.id = `${sec.id}-q${i + 1}`; d.dataset.q = q.id; });
  const qs = cards.length > 2 ? `<ol class="qs">${cards.map((d, i) => `<li><a href="#${esc(d.dataset.q)}" data-q="${i}" aria-label="Exercise ${i + 1}">${i + 1}</a></li>`).join('')}</ol>` : '';
  otpEl.innerHTML = beats.length ? `<h2 id="otp-h">On this page</h2><ol class="beats">${items}</ol>` : qs ? `<h2 id="otp-h">Exercises <span class="check-count k"></span></h2>${qs}<p class="k qs-key">A filled square is an answer you have turned over.</p>` : '';
  const tb = $('#toc-beats'); if (tb) tb.innerHTML = items;
  $('#where').innerHTML = `<a href="#map-${esc(sec.book.id)}">${esc(sec.book.title)}</a><span aria-hidden="true">/</span><a href="#map-${esc(ch.id)}">${esc(ch.n)} ${esc(ch.title)}</a>`;
  $('#toc-btn .bl').textContent = sec.num;
  $('#toc-btn').setAttribute('aria-label', `Contents of chapter ${ch.n}; you are at section ${sec.num}`);
  document.title = `${sec.num} ${sec.title} · ${sec.book.title}`;
  showAnswerCount(); settle(prose); spyBeats(beats); refreshRows(); updateProgressMenu();
  const cur = $('.toc-list [aria-current]');
  if (cur && tocEl.scrollHeight > tocEl.clientHeight) tocEl.scrollTop = Math.max(0, cur.offsetTop - tocEl.clientHeight / 3);
  // where to stand: a heading that was asked for, the place the reader left, or the top
  const target = anchor && document.getElementById(`${sec.id}-${anchor}`);
  const h1 = $('h1', articleEl);
  if (!restore || document.activeElement === document.body || !document.activeElement.isConnected) h1.focus({ preventScroll: true });
  if (restore && R.pos.has(sec.id)) scrollTo(0, R.pos.get(sec.id)); // Back and Forward: where the reader was
  else if (target) target.scrollIntoView({ block: 'start' });
  else scrollTo(0, 0);
  updateProgressLine();
  live(`${sec.num} ${sec.title}`);
}
/* ---- on this page: which beat is being read ---- */
function spyBeats(beats) {
  if (R.spy) R.spy.disconnect();
  if (!beats.length || !('IntersectionObserver' in window)) return;
  const on = i => { for (const a of $$('[data-beat]')) { if (Number(a.dataset.beat) === i) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current'); } };
  R.spy = new IntersectionObserver(() => {
    if (S.mode !== 'read' || !R.sec) return;   // hidden behind the map: nothing is being read
    const line = (parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop) || 80) + 40;
    let cur = -1;
    beats.forEach((h, i) => { if (h.getBoundingClientRect().top < line) cur = i; });
    on(cur);
    const at = cur < 0 ? '' : beats[cur].id.slice(R.sec.id.length + 1);
    if (R.sec && PR.last === pkey(R.sec) && PR.beat !== at) { PR.beat = at; saveProgress(); }
  }, { rootMargin: '0px 0px -60% 0px', threshold: [0, 1] });
  beats.forEach(h => R.spy.observe(h));
}
/* ---- the progress line: how far through this section ---- */
let lineRaf = 0;
function updateProgressLine() {
  const max = document.documentElement.scrollHeight - innerHeight;
  $('#read-line').style.transform = `scaleX(${max > 0 ? Math.min(1, Math.max(0, scrollY / max)).toFixed(4) : 1})`;
}
addEventListener('scroll', () => { if (S.mode === 'read' && !lineRaf) lineRaf = requestAnimationFrame(() => { lineRaf = 0; updateProgressLine(); }); }, { passive: true });
addEventListener('resize', () => { if (S.mode === 'read') { updateProgressLine(); fit(articleEl); } });

/* ---- the contents drawer (below 1024 px the contents column is a drawer) ---- */
const tocBtn = $('#toc-btn');
function setDrawer(open, refocus) {
  document.body.dataset.toc = open ? 'open' : 'closed';
  tocBtn.setAttribute('aria-expanded', String(open));
  for (const el of [$('#sheet'), otpEl, $('.bar')]) el.inert = open;
  if (open) {
    const cur = $('.toc-list [aria-current]') || $('.toc-book');
    if (M.move()) M.run(tocEl, [{ transform: 'translateX(-24px)', opacity: 0 }, { transform: 'none', opacity: 1 }], { duration: 200, easing: EASE_OUT });
    if (cur) { cur.focus({ preventScroll: true }); tocEl.scrollTop = Math.max(0, cur.offsetTop - tocEl.clientHeight / 3); }
  } else if (refocus) tocBtn.focus({ preventScroll: true });
}
tocBtn.addEventListener('click', () => setDrawer(document.body.dataset.toc !== 'open', false));
$('#scrim').addEventListener('click', () => setDrawer(false, true));
tocEl.addEventListener('click', e => {
  if (e.target.closest('#print-btn')) { window.print(); return; }
  if (e.target.closest('a') && document.body.dataset.toc === 'open') setDrawer(false, false);
});
tocEl.addEventListener('keydown', e => {
  if (document.body.dataset.toc !== 'open') return;
  if (e.key === 'Escape') { e.preventDefault(); setDrawer(false, true); }
  if (e.key === 'Tab') { // the drawer is modal: Tab stays inside it
    const f = $$('a[href], button', tocEl).filter(x => x.offsetParent), first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }
});
addEventListener('resize', () => { if (document.body.dataset.toc === 'open' && innerWidth >= 1024) setDrawer(false, false); });

/* ---- print: the whole current chapter, cleanly; answers stay hidden unless turned over ---- */
let printing = false;
function beforePrint() {
  if (printing || S.mode !== 'read' || !R.sec || !R.doc) return;
  printing = true;
  const prose = $('.prose', articleEl), list = readable(R.ch), at = list.indexOf(R.sec);
  const page = (s, i) => {
    const d = document.createElement('div');
    d.className = 'prose print-only';
    d.innerHTML = headHTML(s, i === 0);
    const md = R.doc.parts.get(s.num);
    if (i === 0 && R.doc.preface) d.appendChild(renderMarkdown(R.doc.preface, s, false));
    if (md !== undefined) d.appendChild(renderMarkdown(md, s, false));
    return d;
  };
  const head = $('.sec-head', articleEl);
  list.forEach((s, i) => { if (i < at) head.before(page(s, i)); });
  const after = document.createDocumentFragment();
  list.forEach((s, i) => { if (i > at) after.appendChild(page(s, i)); });
  prose.after(after);
  $$('.fig-svg:not(.ready)', articleEl).forEach(mountFigure);
  themeFigures('light');
}
function afterPrint() {
  if (!printing) return;
  printing = false;
  $$('.print-only', articleEl).forEach(el => el.remove());
  themeFigures(document.documentElement.dataset.theme);
}
addEventListener('beforeprint', beforePrint);
addEventListener('afterprint', afterPrint);
