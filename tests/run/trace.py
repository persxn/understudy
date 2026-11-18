#!/usr/bin/env python3
"""Tests for trace markers in scripts/us_run.py. One line per test and "N passed, M failed"; exit 1 on failure.

    python3 tests/run/trace.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run import env, read, write, ROOT, SCRIPT, TMP  # noqa: E402  (TMP holds every temp folder)

RESULTS = []

POINTER = """# Chapter 1: T

<!-- code: id=reaim -->
```c
#include <stdio.h>

int main(void) {
    int x = 5, y = 7;
    int *p = &x;
    x = 99;
    p = &y;
    printf("%d %d\\n", x, *p);
    return 0;
}
```

<!-- trace: id=reaim watch="x y p *p" at="5 6 7" -->
"""
POINTER_TABLE = """| Line | Statement | `x` | `y` | `p` | `*p` |
|---|---|---|---|---|---|
| 5 | `int *p = &x;` | 5 | 7 | &x | 5 |
| 6 | `x = 99;` | 99 | 7 | &x | 99 |
| 7 | `p = &y;` | 99 | 7 | &y | 7 |
"""
CALL = """# Chapter 1: T

<!-- code: id=bump -->
```c
#include <stdio.h>

void bump(int *q, int by) {
    int old = *q;
    *q = old + by;
}

int main(void) {
    int x = 5;
    bump(&x, 1);
    for (int i = 0; i < 20; i++) {
        x += i;
    }
    printf("%d\\n", x);
    return 0;
}
```

<!-- trace: id=bump watch="x old *q q" at="5 10" -->

<!-- trace: id=bump watch="i x" at="12" rows=3 -->
"""
PY = """# Chapter 1: T

<!-- code: id=add -->
```python
def add(a, b):
    s = a + b
    return s

total = add(2, 3)
print(total)
```

<!-- trace: id=add watch="a s total" at="2 5" -->
"""


def test(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else f": {detail}"))


def chapter(text):
    d = tempfile.mkdtemp(prefix="us-trace-test-")
    os.chmod(d, 0o755)
    write(os.path.join(d, "ch.md"), text)
    return os.path.join(d, "ch.md")


def us_run(*args, environ=None, stdin=None):
    p = subprocess.run([sys.executable, SCRIPT] + list(args), capture_output=True, text=True, input=stdin,
                       env=environ or env())
    return p.returncode, p.stdout, p.stderr


def table(text, marker):
    """The table lines directly below the trace marker that starts with `marker`."""
    lines = text.splitlines(keepends=True)
    i = next(k for k, x in enumerate(lines) if x.startswith(marker))
    out = []
    for x in lines[i + 1:]:
        if not x.startswith("|"):
            break
        out.append(x)
    return "".join(out)


def main():
    if not shutil.which("gdb"):
        print("no gdb here: the C tests below fail")
    ch = chapter(POINTER)
    code, out, err = us_run(ch)
    got = table(read(ch), "<!-- trace: id=reaim")
    test("C: a pointer re-aimed shows as &x then &y, with the values after each line", got == POINTER_TABLE,
         got + out + err)
    print(got, end="")
    first = read(ch)
    code, out, _ = us_run(ch, "--force")
    test("idempotent: a second run changes nothing", code == 0 and read(ch) == first, out)
    write(ch, first.replace("| 6 | `x = 99;` | 99 |", "| 6 | `x = 99;` | 98 |"))
    code, out, _ = us_run(ch, "--check")
    test("--check: a hand-edited table is out of date, and the file is left alone",
         code == 1 and "trace id=reaim" in out and "differs" in out and "| 98 |" in read(ch), out)
    us_run(ch)
    test("a run puts the table right, touching nothing else", read(ch) == first)

    ch = chapter(CALL)
    code, out, err = us_run(ch)
    text = read(ch)
    calls = table(text, '<!-- trace: id=bump watch="x old')
    test("C: a function call: values inside the callee, out of scope as ?, then after the call",
         "| 5 | `*q = old + by;` | ? | 5 | 6 | &x |" in calls and "| 10 | `bump(&x, 1);` | 6 | ? | ? | ? |" in calls,
         calls + out + err)
    loop = table(text, '<!-- trace: id=bump watch="i x"')
    test("C: a loop line is a row each time, capped by rows=",
         loop.count("\n") == 5 and "| 12 | `x += i;` | 2 | 9 |" in loop, loop + out)

    ch = chapter(PY)
    code, out, err = us_run(ch)
    got = table(read(ch), "<!-- trace: id=add")
    test("Python: values inside the function, then after the call",
         "| 2 | `s = a + b` | 2 | 5 | ? |" in got and "| 5 | `total = add(2, 3)` | ? | ? | 5 |" in got, got + out + err)

    ch = chapter("# Chapter 1: T\n\n<!-- code: id=js -->\n```bash\necho hi\n```\n\n"
                 "<!-- trace: id=js watch=\"x\" at=\"1\" -->\n")
    code, out, _ = us_run(ch)
    test("unsupported language: one clear line, write it by hand",
         code == 1 and "trace is not supported for bash; write the table by hand" in out, out)

    ch = chapter(POINTER.replace("trace: id=reaim", "trace: id=nope"))
    code, out, _ = us_run(ch)
    test("a missing id is a problem", code == 1 and "trace id=nope  no program with this id" in out, out)

    bin_dir = tempfile.mkdtemp(prefix="us-trace-bin-")
    os.chmod(bin_dir, 0o755)
    for name in os.listdir("/usr/bin"):
        if name != "gdb":
            os.symlink(os.path.join("/usr/bin", name), os.path.join(bin_dir, name))
    ch = chapter(POINTER)
    code, out, err = us_run(ch, environ=env(PATH=bin_dir))
    test("no gdb: one line, the marker is left for a hand table, the chapter does not fail",
         code == 0 and "no gdb on this machine" in err and "| Line |" not in read(ch), out + err)

    top = tempfile.mkdtemp(prefix="us-trace-book-")
    os.chmod(top, 0o755)
    os.makedirs(os.path.join(top, "book", "chapters"))
    write(os.path.join(top, "book", "PLAN.md"), "# T\nfor: x\nrun: c\n\n### 1 One\n1.1 A\n")
    section = POINTER.split("\n", 2)[2]
    code, out, _ = us_run("try", os.path.join(top, "book"), "1", stdin=section,
                          environ=env(UNDERSTUDY_PRIVATE=os.path.join(top, "private")))
    test("try prints the table under a trace header", code == 0 and "== trace id=reaim at input:" in out
         and POINTER_TABLE in out, out)

    shutil.rmtree(TMP, ignore_errors=True)
    failed = RESULTS.count(False)
    print(f"{len(RESULTS) - failed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
