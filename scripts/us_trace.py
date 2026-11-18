"""Helper of us_run.py, copied into a chapter's working folder: walk one run of a program and write to
trace.out one JSON line [line, [value, ...]] each time a line of `at` has just finished.

    gdb -batch -nx -x us_trace.py ./PROGRAM     C and C++ (built with -g -O0)
    python3 us_trace.py                         Python

Settings come from trace.json in the current folder: src, args, stdin, at, watch, rows, first.
"""
import json
import os
import re
import sys

CONF = json.load(open("trace.json", encoding="utf-8"))
SRC = CONF["src"]
TEXT = open(SRC, encoding="utf-8").read().splitlines()
AT, ROWS = set(CONF["at"]), CONF["rows"]
SEEN = set()
OUT = open("trace.out", "w", encoding="utf-8")
ROWS_DONE = [0]


def wanted(line):
    """True if a row is written for this finished line (and counts it)."""
    if line not in AT or ROWS_DONE[0] >= ROWS or (CONF["first"] and line in SEEN):
        return False
    SEEN.add(line)
    ROWS_DONE[0] += 1
    return True


def emit(line, values):
    OUT.write(json.dumps([line, values]) + "\n")
    OUT.flush()


# ---------------------------------------------------------------- C and C++, inside gdb

SET_RE = [re.compile(r"&\s*([A-Za-z_]\w*)"),
          re.compile(r"\b([A-Za-z_]\w*)\s*(?:\[[^\]]*\]\s*)*(?:[-+*/%&|^]|<<|>>)?=(?!=)"),
          re.compile(r"(?:\+\+|--)\s*([A-Za-z_]\w*)"), re.compile(r"\b([A-Za-z_]\w*)\s*(?:\+\+|--)")]


def set_names(line):
    """Names a source line gives a value to: assigned, incremented, or handed over by address."""
    text = TEXT[line - 1] if 0 < line <= len(TEXT) else ""
    return {m for r in SET_RE for m in r.findall(text)}


def gdb_main():
    import gdb
    for cmd in ("set confirm off", "set pagination off", "set width 0", "rbreak %s:." % SRC):
        gdb.execute(cmd, to_string=True)
    run = "run " + " ".join(CONF["args"]) + " < trace.stdin > /dev/null"
    gdb.execute(run, to_string=True)
    frames = []                       # per frame of the program, oldest first: [pending line, names set]
    for _ in range(100000):           # shortcut: a run longer than this many lines is cut short
        try:
            f = gdb.selected_frame()
        except gdb.error:
            break
        ours, fr = 0, f
        while fr is not None:
            sal = fr.find_sal()
            ours += bool(sal.symtab and os.path.basename(sal.symtab.filename) == SRC)
            fr = fr.older()
        if ours == 0 or ROWS_DONE[0] >= ROWS:
            break
        while len(frames) > ours:     # returned: the callee's last line is done
            finish(gdb, f, frames.pop(), frames)
        if len(frames) == ours and frames:
            finish(gdb, f, frames[-1], frames)
        if len(frames) < ours:
            frames.append([None, set()])
        frames[-1][0] = f.find_sal().line
        try:
            gdb.execute("next", to_string=True)
        except gdb.error:
            break
    OUT.close()
    gdb.execute("kill", to_string=True)


def finish(gdb, frame, slot, frames):
    """Line slot[0] of a frame has just finished: note what it set, write its row if wanted."""
    line = slot[0]
    if line is None:
        return
    slot[1] |= set_names(line)
    if wanted(line):
        names = frames[-1][1] if frames else set()
        emit(line, [c_value(gdb, frame, w, names) for w in CONF["watch"]])


def c_value(gdb, frame, expr, names):
    """One watched expression as the book shows it, or ? when uninitialised or out of scope."""
    try:
        block = frame.block()
        for name in set(re.findall(r"(?<![.\w>])[A-Za-z_]\w*", expr)):
            sym = gdb.lookup_symbol(name, block)[0]
            if sym is None and not re.match(r"(?:sizeof|NULL|nullptr|true|false)$", name):
                return "?"
            if sym is not None and sym.is_variable and not sym.is_argument \
                    and sym.addr_class != gdb.SYMBOL_LOC_STATIC and name not in names:
                return "?"
        return show(gdb, gdb.parse_and_eval(expr), addresses(gdb, frame))
    except Exception:                 # gdb.error, MemoryError: nothing readable there
        return "?"


def addresses(gdb, frame):
    """Address -> name of every variable (and array element) in the program's frames, innermost first."""
    names, fr = {}, frame
    while fr is not None:
        try:
            block = fr.block()
        except RuntimeError:
            block = None
        while block is not None:
            for sym in block:
                if sym.is_variable or sym.is_argument:
                    try:
                        v = sym.value(fr)
                        t = v.type.strip_typedefs()
                        if t.code == gdb.TYPE_CODE_ARRAY:
                            lo, hi = t.range()
                            for i in range(lo, hi + 1):
                                names.setdefault(int(v[i].address), "&%s[%d]" % (sym.name, i))
                        names.setdefault(int(v.address), "&" + sym.name)
                    except (gdb.error, TypeError):
                        pass
            if block.function is not None:
                break
            block = block.superblock
        fr = fr.older()
    return names


def show(gdb, v, names):
    t = v.type.strip_typedefs()
    if t.code == gdb.TYPE_CODE_REF:
        return show(gdb, v.referenced_value(), names)
    if t.code == gdb.TYPE_CODE_PTR:
        a = int(v)
        if a == 0:
            return "NULL"
        if a in names:
            return names[a]
        if t.target().strip_typedefs().sizeof == 1 and t.target().strip_typedefs().code == gdb.TYPE_CODE_INT:
            text = v.string(errors="replace")
            return '"%s"' % (text if len(text) <= 40 else text[:40] + "…")
        return "(address)"            # somewhere no variable is: its number changes between runs
    if t.code == gdb.TYPE_CODE_ARRAY:
        lo, hi = t.range()
        el = t.target().strip_typedefs()
        if el.sizeof == 1 and el.code == gdb.TYPE_CODE_INT:
            return '"%s"' % v.string(length=hi - lo + 1, errors="replace").split("\0")[0]
        items = [show(gdb, v[i], names) for i in range(lo, min(hi, lo + 7) + 1)]
        return "{%s}" % ", ".join(items + (["…"] if hi - lo + 1 > 8 else []))
    if t.code == gdb.TYPE_CODE_STRUCT:
        return "{%s}" % ", ".join("%s = %s" % (f.name, show(gdb, v[f.name], names)) for f in t.fields())
    text = str(v)
    if t.code == gdb.TYPE_CODE_INT and t.sizeof == 1:
        m = re.match(r"^-?\d+ ('.*')$", text)
        return m.group(1) if m else text
    return text


# ---------------------------------------------------------------- Python, by sys.settrace

def py_value(frame, expr):
    try:
        v = eval(expr, frame.f_globals, dict(frame.f_locals))
    except Exception:
        return "?"
    if isinstance(v, (list, tuple)) and len(v) > 8:
        text = repr(type(v)(v[:8]))
        return text[:-1] + ", …" + text[-1]
    text = repr(v)
    return text if len(text) <= 60 else text[:59] + "…"


def py_main():
    path = os.path.abspath(SRC)
    pending = {}

    def tracer(frame, event, arg):
        if frame.f_code.co_filename != path or ROWS_DONE[0] >= ROWS:
            return None
        if event in ("line", "return"):
            line = pending.pop(frame, None)
            if line is not None and wanted(line):
                emit(line, [py_value(frame, w) for w in CONF["watch"]])
            if event == "line":
                pending[frame] = frame.f_lineno
        return tracer
    code = compile("\n".join(TEXT) + "\n", path, "exec")
    sys.argv = [SRC] + CONF["args"]
    sys.stdout = open(os.devnull, "w")
    sys.settrace(tracer)
    try:
        exec(code, {"__name__": "__main__", "__file__": path})
    except SystemExit:
        pass
    finally:
        sys.settrace(None)
        OUT.close()


if "gdb" in sys.modules:
    gdb_main()
elif __name__ == "__main__":
    py_main()
