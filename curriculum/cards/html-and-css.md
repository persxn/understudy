# html-and-css: HTML and CSS for people who will build pages others must be able to use
kind: language
aliases: html, css, semantic html, flexbox, css grid, responsive design, web accessibility
needs: none
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: MDN Learn, Core modules (order); web.dev Learn HTML, Learn CSS contents (coverage); MDN
  Cascade, Stacking context, Ordering flex items, reading-flow; WCAG 2.2 Understanding 1.4.3 (ratios);
  webaim.org/projects/million 2026 (failures); web.dev/articles/cls (numbers); traces and step-note runs in Chromium
unverified: traces run in Chromium only; default form-control fonts, validation messages and accessible names may differ by engine

## Promise
Mark up and style pages that work by keyboard and screen reader, hold at any width, and debug their layout in developer tools.

## The one idea
HTML says what each piece of content is; CSS rules compete, the browser settles each property of each element to one value, then lays out boxes. Picture: a court ranking laws that claim one case. Where it breaks: layout is not a contest; a box's size depends on its parent, children and content together.

## In production
- Pages come from components and frameworks; the browser still gets HTML and CSS, bugs included.
- Accessibility is a legal duty in many places; checkers find only part of the problems, so keyboard and screen-reader checks are by hand.

## Teaching order
1. A document and its tree: `<!doctype html>`, `<html lang>`, `<meta charset>`, the viewport `<meta>`, `<title>`; elements, attributes, nesting; the parsed tree in the Elements panel.
2. Semantic structure: `h1` to `h6` in order, `header`, `nav`, `main`, `footer`, `article`, lists; `<a href>` navigates, `<button>` acts; `alt`, `alt=""`; `<caption>`, `<th scope>`; the accessibility tree.
3. Forms: `<label for>`, `name`, input `type`s, `required`, `pattern`, `autocomplete`, `fieldset` and `legend`; built-in validation, `:invalid`; errors linked by `aria-describedby`.
4. Keyboard and names: Tab in source order; a clickable `div` is not focusable; `:focus-visible`; `tabindex="0"`, never positive; native element before ARIA; contrast 4.5:1, 3:1 for large text.
5. How CSS decides: selectors, combinators, pseudo-classes and -elements; the cascade (origin and `!important`, `@layer`, inline `style`, specificity, order); inheritance, `inherit`, `initial`; the Styles and Computed panels.
6. The box model: content, padding, border, margin; `box-sizing: border-box`; block, inline, `inline-block`; margin collapsing; `overflow`.
7. Units and text: `px`, `rem`, `em`, `%`, `vw`, `ch`; `clamp()`; `max-width` for line length; font stacks, `line-height`.
8. Normal flow, then flexbox: block and inline flow; `display: flex`: main and cross axis, `justify-content`, `align-items`, `gap`, `flex: 1`, `flex-wrap`, `min-width: 0`.
9. Grid for two dimensions: `grid-template-columns`, `fr`, `repeat(auto-fill, minmax(...))`, `grid-template-areas`; grid for the page, flex for a row.
10. Responsive layout: mobile first, `@media (min-width: ...)`, `max-width: 100%` images, `srcset`, `width` and `height` on images against layout shift; zoom to 200%.
11. Positioning and stacking: `relative`, `absolute` and its containing block, `fixed`, `sticky`; `z-index` inside stacking contexts and what makes one (positioned with `z-index`, `fixed`, `sticky`, `opacity`, `transform`, `isolation`).
12. Custom properties and organising CSS: `var(--brand, fallback)`, cascading and inherited; themes with `prefers-color-scheme`; `@layer` for reset, components, utilities (unlayered rules beat layers).
13. Debugging in developer tools: struck-out rules in Styles, the box-model diagram, flex and grid overlays, device mode, the Accessibility pane, a Lighthouse or axe audit.

## How it runs
- [1,5,13] HTML is parsed into the DOM (bad nesting repaired, never refused), CSS into rules; cascade and inheritance give each element computed values; layout sizes and places every box; paint draws. A classic `<script>` without `defer` stops parsing.
- [5] `<div id="main"><p class="note warn">`: `#main p` (1,0,1) beats `.note.warn` (0,2,0) and `p.note` (0,1,1). Equal specificity: the later rule wins, whatever the order of names in `class`. Inline `style` beats a later class, but not an `!important` one.
- [5,7] `color` and `font-size` inherit, `border` and `width` do not; a `<button>` ignores the body's 20px (13.33px in Chromium) until `font: inherit`.

## Step notes
### 1
Need: I put a `div` inside a `p`, and `p div` matches nothing; what did the browser do with my HTML?
Show: `<p>Hello <div>world</div></p>`; `innerHTML`: `<p>Hello </p><div>world</div><p></p>`, and a bare `<tr>` gains a `<tbody>` (the HTML standard fixes these repairs: every engine makes them). An unstyled `h1` computes to 32px: the browser's own stylesheet already competed.
Explain: The parser repairs bad nesting by fixed rules, never refusing; CSS styles the repaired tree, starting from the browser's own rules.
Try: predict: a link inside a link (two siblings), checked in Elements; build: their page's head (`lang`, `charset`, viewport, `title`).
### 2
Need: It looks right; why can a screen-reader user jump to nothing?
Show: a header as `<div class="nav">`, then `<header><nav>`, in the Accessibility pane (Chromium): the divs are unnamed `generic`; `header`, `nav`, `main` give `banner`, `navigation`, `main`; a bold 24px `div` is no heading, `<h3>` is `heading level 3`; a link around an `<img>` without `alt` is `link ""`; with `alt=""` an image leaves the tree.
Explain: Screen readers read the accessibility tree: a role from each element, a name from its text, label or `alt`; looks count for nothing.
Try: decide: `alt` for three of their images (content, in a link, decoration); fix: an icon-only button of theirs, unnamed.
### 3
Need: "Email" is right beside the box; why does the screen reader only say "edit text"?
Show: `Email <input type="email">` against `<label for="b">Email</label><input id="b" type="email" required>` (Chromium): `textbox ""` against `textbox "Email"`. Type `not-an-email`, press Send: the submit handler runs 0 times; `:invalid` matches field and form. A lone `placeholder` still names the field after you type, though it vanishes from sight.
Explain: `for`/`id` or wrapping gives a field its name and a bigger target; validation stops only this form, in this browser.
Try: fix: each unnamed field in their form until the Accessibility pane names it; explain: why their server must refuse `email=x` sent by `curl`.
### 4
Need: The Save `div` works with a mouse; why do keyboard users say there is no Save button?
Show: a link, `<div onclick>`, `<div role="button" tabindex="0" onclick>`, `<button>`. Tab (Chromium): link, role-div, button; the plain div (`tabIndex` -1) is skipped. Enter, then Space: the role-div fires 0 clicks, the button 2. `#777` on white: 4.48:1, failing 4.5 (`#767676`: 4.54).
Explain: Native controls bring focus, key activation, role and name; ARIA only changes what is announced, so a `div` needs `tabindex`, key handlers and a role to match a `<button>`.
Try: fix: a clickable non-button of theirs until Tab, Enter and Space work; apply: a `:focus-visible` style, tabbed through a page.
### 5
Need: My rule is right there, later in the file; why is it struck out in DevTools?
Show: `<a class="c link active">` in `<nav id="nav">`, hit by `#nav a` (1,0,1), eleven `.c`s (0,11,0) and, later, `a.c.link.active` (0,4,1). Most pick the last or the eleven; Chromium uses `#nav a`. `!important` on `.link` beats it; unlayered `a` beats `@layer base { #nav a.c }`; both `!important`: the layered wins.
Explain: Per property, declarations rank by origin and importance, then layer, then specificity read column by column, then order; the first difference decides.
Try: predict: the winner among four of their rules, checked in Computed; fix: a rule of theirs that "does nothing", without `!important`.
### 6
Need: I set `width: 200px`; why does DevTools say 250, and why don't my margins add up?
Show: `width: 200px; padding: 20px; border: 5px`: 250px wide (Chromium); `border-box`: 200. Margins 30px over 20px: gap 30; over -10px: 20. A card's first `h2` with `margin-top: 24px`: the card drops 24px instead; a flex card keeps it inside.
Explain: `width` sizes the content box unless `box-sizing: border-box`; touching vertical margins (a parent's and its first child's too) collapse into one, except in flex or grid containers.
Try: fix: `width: 100%` with `padding: 16px` in a 390px column (422px) of theirs; predict: the gap from margins of 40px and 25px.
### 7
Need: The body is 20px; why is my `2rem` heading 32px, and why does nested list text shrink?
Show: body 20px: `2em` nested twice: 80px; `2rem`: 32px (the root's 16px); `li {font-size: .8em}` three lists deep at 16px: 8.192px; `clamp(1rem, 2.5vw, 2rem)` at 390, 800, 1280px wide: 16, 20, 32px (Chromium).
Explain: `em` multiplies the parent's computed font size (for other properties, the element's own), `rem` the root's; computed sizes inherit, so `em` compounds.
Try: predict: `max-width: 60ch` in px for their text (600 at 20px here); decide: `px`, `rem` or `em` for fonts, paddings, breakpoints.
### 8
Need: Why does my div not centre, and why does one `flex: 1` column push the page sideways?
Show: a 40px box in `display: flex` with both centrings: centred across but at the top, the container being 40px tall; `min-height: 100vh` fixes it. A 300px row, two `flex: 1` items, one holding a long URL: that item grows past 300px, the row overflows (the widths follow the URL and font); `min-width: 0` and `overflow-wrap: anywhere`: 150 each.
Explain: Flex shares only the space left above each item's minimum, by default (`min-width: auto`) its longest unbreakable content; `align-items` centres within the container's own height.
Try: fix: a row of theirs that overflows a phone; predict: `flex: 1` and `flex: 2` in 600px with `gap: 20px` (193.3, 386.7).
### 9
Need: `1fr 1fr` should be halves; why is one column nearly four times the other?
Show: an 800px grid, `200px 1fr 2fr`, `gap: 20px`: `200px 186.656px 373.344px` (Chromium): `fr` shares the 560px left. `1fr 1fr`, an 80-character `<pre>` in one cell: 626 and 174 (with this monospace font); `minmax(0, 1fr) 1fr`: 400 each. `repeat(auto-fill, minmax(200px, 1fr))` in 650px, `gap: 16px`: three 206px tracks.
Explain: Grid sizes fixed tracks and gaps, then splits the rest by the `fr` total; `1fr` is `minmax(auto, 1fr)`, so content can widen a track.
Try: build: their layout with `grid-template-areas`, changed at one breakpoint; predict: `repeat(3, 1fr)` in 1000px, `gap: 24px` (317.33).
### 10
Need: The page jumps while I read on my phone; what pushes the text down?
Show: an 800×600 image (`max-width: 100%; height: auto`) served 600 ms late, 400px window. Without `width`/`height` the next paragraph jumps down 288px (the image's scaled height) when it lands; with them it starts there, Chromium's layout-shift score 0. A 390px phone without the viewport `<meta>`: `innerWidth` 980 (Chromium).
Explain: Before an image arrives its box comes only from `width` and `height`, as a ratio; without the viewport `<meta>` a phone lays out desktop-wide, then shrinks.
Try: fix: the largest layout shift on their page (Performance panel); apply: their page at 390px and 200% zoom, no sideways scroll.
### 11
Need: My dropdown has `z-index: 9999`; why is it under the sticky header?
Show: a `sticky` header, `z-index: 10`; a card with `transform: translateX(0)` holds an absolute menu, `z-index: 9999`, overlapping it. `elementFromPoint` there: the header. No transform: the menu; `opacity: .99`: the header (Chromium); card `position: relative; z-index: 11`: the menu. A parent at `z-index: 1` likewise sinks a 9999 child under its `z-index: 2` sibling.
Explain: `transform`, `opacity` below 1 and a positioned `z-index` each make a stacking context; `z-index` competes only inside the nearest: here the card's 0 against 10.
Try: fix: a menu of theirs stuck underneath, by finding the ancestor that made the context; predict: an absolute `top: 0` child with and without a `relative` parent.
### 12
Need: I wrote `color: var(--space, red)` with `--space: 12px`; why is the text not red?
Show: `:root {--brand: green; --space: 12px; --gap: 10}`, body grey: `var(--brand)` green (in `.dark {--brand: …}`, the dark value); `var(--nope, red)` red; `var(--space, red)` grey, inherited; `padding: var(--gap)px` 0; `calc(var(--gap) * 1px)` 10px (Chromium).
Explain: A custom property is inherited text substituted at computed-value time; the fallback serves only when it is missing; an invalid result makes the property `unset`.
Try: build: light and dark themes for their site from five custom properties; decide: their `@layer` order, and whether unlayered library CSS wins.
### 13
Need: My page scrolls sideways on phones; which element does it?
Show: at 390px, a `section` (`width: 100%; padding: 20px`) and a 350px `<pre>` with a long line: `scrollWidth` above 390; the box whose right edge passes 390 is the `section` (430). With `border-box` no box sticks out, yet the page still scrolls: `scrollWidth` above `clientWidth` finds the `<pre>`, whose text overflows it; `pre {overflow-x: auto}`: 390 (Chromium).
Explain: DevTools show the browser's own records (rules in cascade order, box sizes, the accessibility tree): measure, never guess.
Try: fix: one bug of theirs found with the box-model diagram or an overlay, naming its rule; apply: a Lighthouse or axe audit, each failure fixed or explained.

## Believable numbers
- [4] Contrast: 4.5:1 for text, 3:1 for large text (about 24px, or 18.5px bold); thresholds, never rounded: 4.48 fails (WCAG 2.2 Understanding 1.4.3).
- [7,10] An unset root font is 16px; a phone such as the iPhone 13 is 390 CSS px wide at 3 device pixels per px, and lays out 980px wide without the viewport `<meta>` (Playwright's device list, run here, Nov 2026).
- [10] Layout shift: 0.1 or less is "good", above 0.25 "poor", at the 75th percentile of loads (web.dev/articles/cls); one late image without `width`/`height` (step 10): about 0.015 here.

## Go deep, leave for later
- Deep steps: 4, 5, 6, 8 (keyboard and screen-reader access; the cascade; how the box model and flex compute sizes, where most layout bugs live).
- Later: animations, container queries, `<dialog>`, popover, web components, utility frameworks, SVG.

## Never omit
- Every page is used by keyboard alone, read in the accessibility tree, tried at phone width and 200% zoom.
- Look up when planned: browser support of newer features, the WCAG version and law.

## Wrong beliefs
- [2,4] "A clickable `div` is as good as a `button`" (no focus, no Enter or Space, no role).
- [3] "Browser validation protects the server" (anyone can send the request without the form).
- [4] "Adding ARIA makes it accessible" (a native element first; a wrong role or missing keyboard support is worse than none).
- [5] "Enough classes beat an id" (the columns compare in order; no number of classes reaches an id).
- [8] "`order` and `row-reverse` reorder the page" (only on screen; Tab and screen readers follow the source unless the newer `reading-flow` says otherwise).
- [11] "A higher `z-index` always wins" (it is compared only inside one stacking context).
- [12] "`var(--x, fallback)` uses the fallback when `--x` is wrong" (only when `--x` is missing; an invalid result unsets the property).

## Failures to diagnose
- [3-4] A field announced with no name: no `<label>` (51% of the top million home pages, WebAIM 2026; low contrast on 84%).
- [4] Keyboard users lost: `outline: none`, no `:focus-visible` style.
- [5] A rule "does nothing": a more specific one wins; it is struck out in Styles.
- [6,10] Sideways scroll on phones: `width: 100%` plus padding, or a fixed width.
- [10] A phone shows a tiny desktop page: no viewport `<meta>`.
- [11] A menu under the header despite `z-index: 9999`: an ancestor made a stacking context.

## Practice and project
Project: the learner's own site or app screens: semantic HTML, a working form, one flex and one grid layout, a theme in custom properties; finish line: usable by keyboard alone, every control named, no sideways scroll from phone width to 200% zoom, no contrast failure in the audit.

## Mastery ladder
- Use: build a page with header, navigation, form and card grid from a sketch.
- Explain: for an element, show in developer tools which rule won each property and why, and where each pixel of its width came from.
- Build: the project above.
- Design: choose layout methods, breakpoints and custom property names for a set of screens, defended.

## Words to own
[1] element, attribute, DOM, (user-agent stylesheet); [2] semantic HTML, landmark, accessibility tree, alt text; [3] form validation,
label; [4] keyboard focus, accessible name, ARIA, contrast ratio; [5] cascade, specificity, inheritance,
computed value; [6] box model, margin collapsing; [7] relative unit; [8] normal flow, flex container, main axis;
[9] grid track, fr unit; [10] media query, breakpoint, viewport, layout shift; [11] containing block, stacking
context; [12] custom property, cascade layer; [13] developer tools
