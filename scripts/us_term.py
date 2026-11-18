#!/usr/bin/env python3
"""A small terminal model for us_run.py: what a reader's screen finally shows, and the keys typed into it.

    final_screen(raw_text) -> text   progress displays that redraw themselves (carriage return, cursor up,
                                     erase line: docker build, docker compose, pip, git) come out as the
                                     reader finally sees them, not once per frame; colours are dropped.
    keys(stdin) -> [bytes]           stdin= split into what is typed one at a time: each line, and ^C / ^D
                                     as the key presses Ctrl-C and Ctrl-D.
"""
import re

ROWS = 24     # the height of the reader's terminal: where "cursor home" puts the cursor
TOKEN = re.compile(r"\x1b\[([0-?]*)[ -/]*([@-~])"             # CSI: cursor moves, erasing, colours
                   r"|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)"      # OSC: window titles, links
                   r"|\x1b([78])|\x1b[()][0-9A-Za-z]|\x1b[=>]"  # save/restore cursor, character sets
                   r"|[\r\n\x08\t\x07]|[^\x1b\r\n\x08\t\x07]+|\x1b", re.S)


def final_screen(raw):
    """The text a terminal shows after printing raw (scrolled-off lines kept, 80 columns not wrapped)."""
    rows, erased = [[]], set()       # erased: rows wiped by an erase; one left empty was a redraw's leftover
    row = col = 0
    saved = (0, 0)

    def go(r):
        nonlocal row
        row = max(0, r)
        while len(rows) <= row:
            rows.append([])

    for m in TOKEN.finditer(raw):
        t = m.group(0)
        line = rows[row]
        if m.group(2):
            p = [int(x) if x.isdigit() else 0 for x in m.group(1).lstrip("?").split(";")]
            n, cmd = max(p[0], 1), m.group(2)
            if cmd in "AF":
                go(row - n)
                col = 0 if cmd == "F" else col
            elif cmd in "BE":
                go(row + n)
                col = 0 if cmd == "E" else col
            elif cmd == "C":
                col += n
            elif cmd == "D":
                col = max(0, col - n)
            elif cmd == "G":
                col = n - 1
            elif cmd in "Hf":
                go(max(0, len(rows) - ROWS) + n - 1)
                col = max(p[1] if len(p) > 1 else 1, 1) - 1
            elif cmd == "K":
                erased.add(row)
                if p[0] == 0:
                    del line[col:]
                elif p[0] == 1:
                    line[:col + 1] = [" "] * min(col + 1, len(line))
                else:
                    line.clear()
            elif cmd == "J":
                first = row + 1 if p[0] == 0 else max(0, len(rows) - ROWS) if p[0] == 2 else len(rows)
                if p[0] == 0:
                    del line[col:]
                    erased.add(row)
                for k in range(first, len(rows)):
                    rows[k].clear()
                    erased.add(k)
            elif cmd == "s":
                saved = (row, col)
            elif cmd == "u":
                go(saved[0])
                col = saved[1]
        elif m.group(3):
            if m.group(3) == "7":
                saved = (row, col)
            else:
                go(saved[0])
                col = saved[1]
        elif t == "\n":
            go(row + 1)
            col = 0
        elif t == "\r":
            col = 0
        elif t == "\x08":
            col = max(0, col - 1)
        elif t == "\t":
            col = (col // 8 + 1) * 8
            line.extend(" " * (col - len(line)))
        elif t[0] != "\x1b" and t != "\x07":
            line.extend(" " * (col - len(line)))
            line[col:col + len(t)] = t
            col += len(t)
    last = len(rows) - 1
    return "\n".join("".join(r).rstrip(" ") for k, r in enumerate(rows)
                     if r and any(c != " " for c in r) or k not in erased or k == last)


def keys(stdin):
    """b"Arjun\\nexit\\n" -> [b"Arjun\\n", b"exit\\n"]; b"^C" -> [b"\\x03"]: what is typed, one item at a time."""
    out = []
    for part in re.split(rb"(\^[CD])", stdin):
        if part in (b"^C", b"^D"):
            out.append(b"\x03" if part == b"^C" else b"\x04")
        else:
            out += [x for x in re.split(rb"(?<=\n)", part) if x]
    return out
