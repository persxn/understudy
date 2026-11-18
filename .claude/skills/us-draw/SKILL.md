---
name: us-draw
description: Draws a diagram for the learner's book as an SVG: a flow, layers, a tree, a sequence of messages, memory boxes, pointers or an array layout. Use when the learner asks for a diagram, picture, figure or drawing of something they are studying, when a chapter being written needs a picture, or to fix or restyle a figure. Not for charts of data or interface designs.
---

# us-draw

A figure is made from a short description by a script, never drawn by hand. That keeps one style across the book, makes every figure right on a phone, in dark mode and for a screen reader, and makes a figure nearly free.

## Does it earn a place

Draw where a shape carries the idea: boxes in memory, a pointer, a stack of frames, a tree, layers, steps that branch, messages over time. A list of facts is a table or a sentence. One figure, one idea, twelve boxes at most; otherwise split it.

To choose the figure type for an idea (a sequence of events, parts, a changing state, a flow of data, memory), or to decide that a table or text block is better, read `references/figures.md`.

## Making one

1. `python3 scripts/us_draw.py --format` prints the description format. Read it once per session.
2. In the chapter, where the figure belongs, write the description as a comment, and under it a caption that says what to see:

   ```text
   <!-- fig: id=pointer-box-and-arrow
   vars: p=1000@2000 x=5@1000
   ptr p -> x
   -->

   *Figure 8.2a: The pointer arrow starts in the box that holds the number and ends on the box that number names.*
   ```

3. `python3 scripts/us_draw.py --chapter <chapter file>` draws it, writes the image line and its alt text, and prints one line per problem with the fix. Run it after writing the chapter; `us_check.py` calls a figure with no image line an ERROR, so none is forgotten. Change the description until it prints no problem. Never edit the SVG or the image line.
4. Every label and number comes from a program's real output or from the text, like everything else in the book.
5. If this harness can show images, add `--png` once per chapter and look: the right content, readable without hunting, nothing touching.
6. A convention, once chosen, holds for the whole book (a pointer is always the dashed arrow). Say it in the caption where it first appears.

## Changes

Change the description and rerun. To restyle every figure, change `scripts/fig-style.json` and run `python3 scripts/us_draw.py --all book`.
