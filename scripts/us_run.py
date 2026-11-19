#!/usr/bin/env python3
"""Run the programs of a chapter and paste their real output below them.

    python3 scripts/us_run.py CHAPTER.md [--only ID] [--check] [--force] [--list] [--strict] [--fresh]
    python3 scripts/us_run.py try BOOK N [--file PATH] [--fresh]   markers and fences on stdin (or in PATH)
    python3 scripts/us_run.py --reset BOOK   remove all the book's runs made in Docker, built images included

A program is marked by a hidden comment directly above its fence:

    <!-- code: id=NAME mode=run stdin="3 4\\n" args="a b" file=util.h exit=3 timeout=5 varies
               stderr=hide nosan danger="why" answer after=ID[,ID] check="python3 NAME.py" -->

    args="in.txt -n"   command-line arguments: the program runs as ./NAME in.txt -n
    exit=1             the exit code it must end with (default 0); in a console block, the last command's
    after=save-log     it reads files that block (above it) makes; try runs that block first, silently
    check="CMD"        the reader's own program, run by CMD in their folder with the same stdin and args, must
                       print this output (us_practice.py check); only on a mode=run program, not varies

mode=run (default) builds with warnings on, runs it twice and writes what it printed as the ```text
fence directly below the code fence (creating or replacing that fence). It runs as on the reader's
terminal: standard output and error on a pseudo-terminal, in their real order (stderr=hide drops the
error stream). A C or C++ run program is also built once with -fsanitize=address,undefined and run
once more, unseen: a sanitizer report is a problem (nosan: the fault is the lesson).
mode=compile must build cleanly; mode=warns must build with warnings (the messages are pasted,
then the output if it runs) and mode=error must fail to build (the messages are pasted);
mode=crash must be killed by a signal: its output so far is pasted, then one line such as
"Segmentation fault". mode=fragment is not touched. With `answer` the output goes in the first
```text fence of the next <details> block instead (a program already inside a <details> keeps its
output under it).

A ```console fence is a terminal session: its "$ " lines run in order and the fence is rewritten
with what they printed. A command that opens a here-document (<<EOF ... EOF) or ends with a backslash
goes on over the next lines, shown with no prompt. The sessions of a book are one story: chapter N
starts in a private HOME holding what chapter N-1 left there (a snapshot saved when a full run of
chapter N-1 ends with no problem; if it is missing, as after a reboot, chapter N-1 is first run again,
quietly and without rewriting it, to make it; an empty HOME with --fresh, or if chapter N-1 cannot
be run to its end without a problem, said in one line). Each session
starts in the folder where the one before it ended (the first in HOME) and finds the files,
repositories and settings earlier fences (and programs) made. stdin= on a session is typed at the
terminal a line at a time when a command waits for it, so the answers show on the screen as a reader's
would; ^C and ^D in it are the keys Ctrl-C and Ctrl-D; with wait=N each item is typed N seconds after
the command starts (or after the item before), waiting or not: for programs in containers
(docker run -it) and for Ctrl-C. A session's time limit counts per command: timeout= on the marker,
else the book's `timeout: N` plan line, else 5 seconds. Progress displays that redraw themselves are
pasted as their final screen (scripts/us_term.py).
They run on an 80-column pseudo-terminal (so `ls` prints columns and git decorates its log), with
LC_ALL=C.UTF-8, TZ=UTC, PAGER=cat, GIT_PAGER=cat and the `env:` lines of the book's PLAN.md
(env: GIT_AUTHOR_DATE=2026-01-05T10:00:00 ...); colour codes and carriage returns are dropped and a
path under HOME is shown as /home/you/... With `answer` the question keeps
the commands only, and the whole session goes in the first ```console fence of the next <details>.

A hand trace is made from a real run by a marker where the table belongs:

    <!-- trace: id=PROGRAM watch="x y *p" at="7 14 16" rows=12 hits=all -->

The table directly below it (rows starting "|") is owned by this script: one row each time one of
the `at` lines of the program has just finished, with the value of each watched expression then.
C and C++ are walked with gdb, Python with sys.settrace (scripts/us_trace.py).

`try` runs a section's programs before the section is written, as a run of the chapter would:
every program and session already in the chapter runs first, silently and in order (and programs
named in after= that were tried before). It keeps each tried one (tried/ID.md in the chapter's run
folder, for us_section.py to fill in) and prints what each printed, under "== id=NAME (mode)".

Every run and every try starts from a clean working folder: files the programs made are removed
first (sources and builds stay), so a result never depends on how often it was tried. The run
folder is <temp>/understudy-run/<book>-<hash>/<chapter file>/: home/ is where programs and sessions
run; the cache, tried programs and the tool's own builds sit beside it.

A book whose PLAN.md says `state: docker` makes things in Docker: the containers, networks, volumes
and images its sessions made are noted (state.json beside the run folders, scripts/us_state.py), and
only those are removed: containers, networks and volumes before every run and try and after it, and
after a session that timed out; images only with --reset. Commands that would touch the learner's own
Docker (prune, rm $(docker ...)) are refused like the dangerous ones; a port published to every
address gets a note. When pasted output is compared with a new run, ids, digests, times and ages
are ignored, and so is text that matches the plan's `mask: REGEX` lines (in any book).
unrun="why" marks a block that cannot run on this machine: it is tried on every run, stays as it is
with no problem while it fails (counted as unrun N), and is pasted with unrun= dropped ("now run: ID")
once it runs.

Prints nothing per block on success, one line per problem, and one summary line.
Exit 1 if there is any problem (with --check: also if any pasted output is out of date).
"""
import argparse
import fcntl
import functools
import hashlib
import json
import os
import pwd
import re
import resource
import select
import shlex
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import termios
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import us_bookfmt as bf  # noqa: E402
import us_state  # noqa: E402
import us_term  # noqa: E402
from us_lib import ROOT, load_config  # noqa: E402

VERSION = "8"  # part of every cache key: bump it when the way output is made changes

# Errors in gcc 14 but only warnings in gcc 13: made errors everywhere, so both agree. (g++ refuses
# these flags with a warning; in C++ the three are errors already.)
C_ERRORS = "-Werror=implicit-function-declaration -Werror=incompatible-pointer-types -Werror=int-conversion"

# How each language is built and run. {src} source file, {exe} ./NAME, {cls} Java class.
# "main" names the step that understudy.yaml may override with a line "run.<tag>: COMMAND".
# {posix} is -D_POSIX_C_SOURCE=200809L when the program includes a POSIX header, else nothing.
LANGS = {
    "c":          {"ext": ".c",    "build": "gcc -std=c17 -Wall -Wextra -pedantic " + C_ERRORS +
                   " {posix} {src} -o {exe} -lm", "run": "{exe}", "main": "build"},
    "cpp":        {"ext": ".cpp",  "build": "g++ -std=c++17 -Wall -Wextra -pedantic {src} -o {exe} -lm",
                   "run": "{exe}", "main": "build"},
    "python":     {"ext": ".py",   "build": "python3 -m py_compile {src}", "run": "python3 {src}", "main": "run"},
    "bash":       {"ext": ".sh",   "build": "bash -n {src}", "run": "bash {src}", "main": "run"},
    "sh":         {"ext": ".sh",   "build": "sh -n {src}", "run": "sh {src}", "main": "run"},
    "javascript": {"ext": ".js",   "build": "node --check {src}", "run": "node {src}", "main": "run"},
    "java":       {"ext": ".java", "build": "javac -Xlint:all -d . {src}", "run": "java -cp . {cls}",
                   "main": "build"},
}
ALIASES = {"c++": "cpp", "cxx": "cpp", "py": "python", "python3": "python", "js": "javascript",
           "node": "javascript", "shell": "bash"}
CONSOLE = "console"
MODES = ["run", "compile", "warns", "error", "crash", "fragment"]
MODE_ALIASES = {"compile-error": "error"}
ATTRS = {"id", "mode", "stdin", "args", "file", "exit", "timeout", "varies", "danger", "stderr", "answer", "after",
         "nosan", "unrun", "wait", "check"}
POSIX_RE = re.compile(r'^\s*#\s*include\s*<(?:unistd|fcntl|dirent|sys/\w+)\.h>', re.M)
SAN_FLAGS = ["-g", "-fsanitize=address,undefined", "-w"]
SAN_ENV = {"ASAN_OPTIONS": "detect_leaks=0", "UBSAN_OPTIONS": "print_stacktrace=1"}  # a leak is no fault here
SAN_RE = re.compile(r"ERROR: AddressSanitizer|runtime error:|ERROR: \w+Sanitizer")
MAX_LINES = 60
MAX_CHARS = 8000  # one endless line is as unreadable as a thousand short ones
SHOW_LINES = 20   # of output over MAX_LINES, the first lines shown (try prints them)
UNPRINTABLE = "output has unprintable bytes: show them with `od -c` or `xxd` instead of printing them"
CRASH = {signal.SIGSEGV: "Segmentation fault", signal.SIGABRT: "Aborted", signal.SIGFPE: "Floating point exception",
         signal.SIGBUS: "Bus error", signal.SIGILL: "Illegal instruction", signal.SIGTRAP: "Trace/breakpoint trap"}
KEEP = {"trace.json", "trace.stdin", "trace.out", "us_trace.py"}
TRY_LINES = 40
FALLBACK_USER = "ubuntu"
BUILD_TIMEOUT = 60
FILE_LIMIT = 64 * 1024 * 1024
# A python program saved as NAME.py hides the module NAME from every program run in its folder.
HIDDEN_MODULES = set(getattr(sys, "stdlib_module_names", ())) | {"numpy", "pandas", "requests", "flask", "django",
                                                                 "pytest"}

# Commands refused in console and shell blocks unless the marker carries danger="why".
DANGER = [r"\bpkill\b(?!.*\s-u\b)", r"\bkillall\b", r"\brm\s+(-\S*\s+)*-[a-zA-Z]*[rR]", r"\brm\s+.*--recursive",
          r"\bsudo\b", r"\bkill\s+(-\w+\s+)?-1\b", r"\bshutdown\b", r"\breboot\b", r"\bmkfs", r"\bdd\b.*\bof=/dev",
          r">\s*/dev/sd", r"\bchmod\s+-R\b", r":\(\)\s*\{", r"\b(curl|wget)\b[^|]*\|\s*(sudo\s+)?(ba|z)?sh\b"]

HEREDOC = re.compile(r"(?<!<)<<-?\s*(['\"]?)([A-Za-z_][\w-]*)\1")
MARKER = re.compile(r"^\s*<!--\s*code:(.*?)-->\s*$")
TRACE = re.compile(r"^\s*<!--\s*trace:(.*?)-->\s*$")
TRACE_ATTRS = {"id", "watch", "at", "rows", "hits"}
TRACE_LANGS = {"c": "gcc", "cpp": "g++", "python": "python3"}
FENCE_OPEN = re.compile(r"^( {0,3})(`{3,}|~{3,})\s*([^\s`{]*)")
DIAG = [  # (file, line, message) from a compiler or interpreter message
    re.compile(r"^(?P<file>[^\s:]+):(?P<line>\d+):(?:\d+:)? (?P<msg>(?:fatal )?(?:error|warning): .*)$"),
    re.compile(r"^(?P<file>[^\s:]+): line (?P<line>\d+): (?P<msg>.*)$"),
    re.compile(r'^\s*File "(?P<file>[^"]+)", line (?P<line>\d+)'),
    re.compile(r"^(?P<file>[^\s:]+\.js):(?P<line>\d+)$"),
]


# ---------------------------------------------------------------- reading the chapter


def command_spans(lines):
    """(first, last) index of each '$ ' command among a console fence's lines: a command that ends with a
    backslash or opens a here-document goes on over the next lines (to the line that ends the here-document)."""
    spans, start, ends = [], None, []
    for i, line in enumerate(lines):
        if start is None and not line.startswith("$ "):
            continue
        if start is None:
            start = i
        elif ends:
            ends = ends[1:] if line.lstrip("\t") == ends[0] else ends
            if ends:
                continue
        ends = ends or [m.group(2) for m in HEREDOC.finditer(line)]
        if not ends and not line.endswith("\\"):
            spans.append((start, i))
            start = None
    if start is not None:
        spans.append((start, len(lines) - 1))
    return spans


class Block:
    def __init__(self, marker_line, attrs):
        self.marker = marker_line        # 1-based line of the marker
        self.attrs = attrs
        self.id = attrs.get("id", "")
        self.mode = MODE_ALIASES.get(attrs.get("mode", "run"), attrs.get("mode", "run"))
        self.tag = ""                    # fence tag as written
        self.lang = ""                   # key of LANGS, or "console"
        self.open = self.close = 0       # 0-based indices of the code fence lines
        self.code = ""
        self.out_start = self.out_end = 0  # 0-based half-open region this script owns
        self.src = ""
        self.details = None              # answer: 0-based line of the <details> its output goes in
        self.pad = (False, False)        # answer: blank lines before and after a new output fence
        self.answer_at = 0               # answer: 0-based line where its output fence starts or goes


def parse_attrs(text):
    """'id=x stdin="3 4\\n" varies' -> {"id": "x", "stdin": "3 4\\n", "varies": ""}."""
    attrs, pos = {}, 0
    pattern = re.compile(r'\s*([A-Za-z_][\w-]*)(?:=("(?:[^"\\]|\\.)*"|\'[^\']*\'|[^\s"\']+))?')
    text = text.strip()
    while pos < len(text):
        m = pattern.match(text, pos)
        if not m or m.end() == pos:
            raise ValueError("cannot read the marker near: " + text[pos:pos + 20])
        key, value = m.group(1), m.group(2)
        if value is None:
            value = ""
        elif value[0] in "\"'":
            value = value[1:-1].replace('\\"', '"') if value[0] == '"' else value[1:-1]
        if key in attrs:
            raise ValueError(f"attribute {key} given twice")
        attrs[key] = value
        pos = m.end()
    return attrs


def unescape(text):
    """stdin text: \\n is a newline, \\t a tab, \\\\ a backslash."""
    return re.sub(r"\\(.)", lambda m: {"n": "\n", "t": "\t", "\\": "\\", '"': '"'}.get(m.group(1), m.group(0)),
                  text)


def strip_end(line):
    return line.rstrip("\r\n")


def find_fence_close(lines, start, char, size):
    close = re.compile("^ {0,3}" + re.escape(char) + "{" + str(size) + r",}\s*$")
    for i in range(start, len(lines)):
        if close.match(strip_end(lines[i])):
            return i
    return -1


def parse_chapter(lines, answers=True):
    """Return (blocks, errors). errors are (line, id, message). With answers=False an `answer`
    block owns the place under its fence like any other (for try, which writes nothing)."""
    blocks, errors, seen = [], [], {}
    i = 0
    while i < len(lines):
        m = MARKER.match(strip_end(lines[i]))
        if not m:
            i += 1
            continue
        try:
            block = Block(i + 1, parse_attrs(m.group(1)))
        except ValueError as e:
            errors.append((i + 1, "", str(e)))
            i += 1
            continue
        i = read_block(lines, i, block, errors, answers)
        if block.open is None:
            continue
        check_block(block, errors, seen)
        blocks.append(block)
    answers = {}
    for block in blocks:
        if block.details is not None:
            if block.details in answers:
                errors.append((block.marker, block.id, f"answer: id={answers[block.details]} already puts its "
                               "output in the same <details>; give each its own hidden answer"))
            answers.setdefault(block.details, block.id)
    return blocks, errors


def read_block(lines, i, block, errors, answers=True):
    """Find the fence after the marker at i; return the index to continue from."""
    j = i + 1
    while j < len(lines) and not strip_end(lines[j]).strip():
        j += 1
    fm = FENCE_OPEN.match(strip_end(lines[j])) if j < len(lines) else None
    if not fm:
        errors.append((i + 1, block.id, "marker with no fenced block after it"))
        block.open = None
        return i + 1
    close = find_fence_close(lines, j + 1, fm.group(2)[0], len(fm.group(2)))
    if close < 0:
        errors.append((j + 1, block.id, "fence is never closed"))
        block.open = None
        return j + 1
    block.open, block.close = j, close
    block.tag = fm.group(3).lower()
    block.lang = CONSOLE if block.tag == CONSOLE else ALIASES.get(block.tag, block.tag)
    block.code = "".join(strip_end(x) + "\n" for x in lines[j + 1:close])
    if "answer" in block.attrs and answers and hidden_already(lines, i):
        del block.attrs["answer"]        # it sits inside a hidden answer: its output stays there, under it
    if "answer" in block.attrs and answers:
        find_answer(lines, close + 1, block, errors)
        if block.lang == CONSOLE and block.open is not None:   # the commands, then the answer, are one region
            between = next((k + 1 for k in range(close + 1, block.answer_at) if MARKER.match(strip_end(lines[k]))), 0)
            if between:
                errors.append((between, block.id, "answer: another program stands between this session and its "
                               "hidden answer; move it"))
                block.open = None
            block.out_start = j + 1
    elif block.lang == CONSOLE:
        block.out_start, block.out_end = j + 1, close
    else:
        block.out_start = block.out_end = close + 1
        t = close + 1                    # blank lines may stand between the program and its output fence
        while t < len(lines) and not strip_end(lines[t]).strip():
            t += 1
        tm = FENCE_OPEN.match(strip_end(lines[t])) if t < len(lines) else None
        if tm and tm.group(3).lower() == "text":
            end = find_fence_close(lines, t + 1, tm.group(2)[0], len(tm.group(2)))
            if end >= 0:
                block.out_end = end + 1
    return close + 1


def hidden_already(lines, i):
    """True when line i is inside a <details> block of its own section."""
    depth = 0
    for k in range(i - 1, -1, -1):
        line = strip_end(lines[k])
        if re.match(r"^#{1,2} ", line):
            break
        depth += line.count("</details>") - line.count("<details")
        if depth < 0:
            return True
    return False


def find_answer(lines, start, block, errors):
    """Owned region of an `answer` block: the first ```text (for a session, ```console) fence inside the
    next <details> block, or the place after its </summary> line (and a blank line) where that fence goes."""
    k = start
    while k < len(lines) and not strip_end(lines[k]).strip().startswith("<details>"):
        if re.match(r"^#{1,2} ", strip_end(lines[k])):
            k = len(lines)  # not past the end of the section
        k += 1
    end = next((e for e in range(k, len(lines)) if "</details>" in lines[e]), -1) if k < len(lines) else -1
    summary = next((e for e in range(k, end) if "</summary>" in lines[e]), -1) if end >= 0 else -1
    if summary < 0:
        errors.append((block.marker, block.id, "answer: no <details> block with a <summary> after the program "
                       "in this section; add the hidden answer, or drop answer"))
        block.open = None
        return
    block.details = k
    e = summary + 1
    while e < end:
        fm = FENCE_OPEN.match(strip_end(lines[e]))
        if fm:
            close = find_fence_close(lines, e + 1, fm.group(2)[0], len(fm.group(2)))
            if close < 0 or close >= end:
                break
            if fm.group(3).lower() == ("console" if block.lang == CONSOLE else "text") and \
                    not MARKER.match(strip_end(lines[e - 1])):
                block.out_start = block.answer_at = e
                block.out_end = close + 1
                return
            e = close  # another fence inside the answer: skip it
        e += 1
    blank = summary + 1 < len(lines) and not strip_end(lines[summary + 1]).strip()
    block.out_start = block.out_end = block.answer_at = summary + (2 if blank else 1)
    block.pad = (not blank, True)


def check_block(block, errors, seen):
    line = block.marker
    if not block.id:
        errors.append((line, "", "marker has no id="))
    elif block.id in seen:
        errors.append((line, block.id, f"duplicate id (first used on line {seen[block.id]})"))
    else:
        seen[block.id] = line
    unknown = sorted(set(block.attrs) - ATTRS)
    if unknown:
        errors.append((line, block.id, "unknown attribute " + ", ".join(unknown) + "; known: " +
                       " ".join(sorted(ATTRS))))
    if block.mode not in MODES:
        errors.append((line, block.id, f"unknown mode {block.mode}; modes: " + " ".join(MODES)))
    if block.mode != "fragment" and block.lang not in LANGS and block.lang != CONSOLE:
        errors.append((line, block.id, f"cannot run a '{block.tag or 'untagged'}' fence; supported tags: " +
                       " ".join(list(LANGS) + [CONSOLE])))
    if block.lang == CONSOLE and block.mode not in ("run", "fragment"):
        errors.append((line, block.id, "a console block has no mode but run or fragment"))
    for key in ("exit", "timeout", "wait"):
        value = block.attrs.get(key)
        if value is not None and not re.fullmatch(r"-?\d+|any" if key == "exit" else r"\d+(\.\d+)?", value):
            errors.append((line, block.id, f"{key}= must be a number, not '{value}'"))
    if block.mode == "crash" and "exit" in block.attrs:
        errors.append((line, block.id, "mode=crash takes no exit="))
    if block.attrs.get("stderr", "show") not in ("show", "hide"):
        errors.append((line, block.id, "stderr= takes show or hide"))
    if "check" in block.attrs:
        why = ("a console session" if block.lang == CONSOLE else "mode=" + block.mode if block.mode != "run"
               else "varies" if "varies" in block.attrs else "an empty command" if not block.attrs["check"].strip()
               else "")
        if why:
            errors.append((line, block.id, f"check= needs a mode=run program whose output is pasted, not {why}: "
                           "remove check= or make it such a program"))


class Trace:
    """A trace marker and the table below it that this script owns."""
    def __init__(self, i, attrs, lines):
        self.marker, self.attrs, self.prog = i + 1, attrs, attrs.get("id", "")
        self.id = f"trace@{i + 1}"       # key of its owned region, beside the blocks' ids
        self.out_start = self.out_end = i + 1
        while self.out_end < len(lines) and strip_end(lines[self.out_end]).lstrip().startswith("|"):
            self.out_end += 1


def parse_traces(lines):
    """Return (traces, errors) for every trace marker; errors are (line, id, message)."""
    traces, errors = [], []
    for i, line in enumerate(lines):
        m = TRACE.match(strip_end(line))
        if not m:
            continue
        try:
            t = Trace(i, parse_attrs(m.group(1)), lines)
        except ValueError as e:
            errors.append((i + 1, "", "trace: " + str(e)))
            continue
        a, bad = t.attrs, []
        bad += ["unknown attribute " + k for k in sorted(set(a) - TRACE_ATTRS)]
        bad += [f"no {k}=" for k in ("id", "watch", "at") if not a.get(k)]
        if not re.fullmatch(r"\d+( \d+)*", " ".join(a.get("at", "1").split())):
            bad.append("at= must be line numbers of the program, such as at=\"7 14\"")
        if not a.get("rows", "1").isdigit() or a.get("hits", "all") not in ("all", "first"):
            bad.append("rows= takes a number and hits= all or first")
        errors += [(t.marker, t.prog, "trace: " + b) for b in bad]
        if not bad:
            traces.append(t)
    return traces, errors


# ---------------------------------------------------------------- where and as whom

def book_of(chapter):
    """The book folder a chapter file belongs to, or None."""
    chapter = os.path.abspath(chapter)
    cfg = load_config()
    book_root = cfg["book"] if os.path.isabs(cfg["book"]) else os.path.join(ROOT, cfg["book"])
    rel = os.path.relpath(chapter, book_root)
    if not rel.startswith("..") and os.sep in rel:
        return os.path.join(book_root, rel.split(os.sep)[0])
    top = os.path.dirname(os.path.dirname(chapter))
    if os.path.basename(os.path.dirname(chapter)) == "chapters" and os.path.exists(os.path.join(top, "PLAN.md")):
        return top
    return None


def run_folder(chapter):
    """<temp>/understudy-run/<book>-<hash>/<chapter file>/: outside any git repository and outside this
    product; the hash of the book's (or loose chapter's folder's) path keeps two books apart."""
    chapter = os.path.abspath(chapter)
    top = book_of(chapter) or os.path.dirname(chapter)
    tag = hashlib.sha256(top.encode()).hexdigest()[:8]
    return os.path.join(tempfile.gettempdir(), "understudy-run", f"{os.path.basename(top)}-{tag}",
                        os.path.basename(chapter))


def chapter_snapshot(chapter, n):
    """Where the HOME that a full run of chapter n of chapter's book left is kept: beside the run folders."""
    return os.path.join(os.path.dirname(run_folder(chapter)), f"snapshot-{n}")


def start_of(chapter, n, opts):
    """(HOME a run of chapter n starts from, its key): what a full run of chapter n-1 left, else ("", "")."""
    if n < 2 or getattr(opts, "fresh", False):
        return "", ""
    snap = chapter_snapshot(chapter, n - 1)
    try:
        with open(os.path.join(snap, "key")) as f:
            return os.path.join(snap, "home"), f.read()
    except (OSError, UnicodeDecodeError):
        return "", ""


def working_folder(chapter):
    """Where a chapter's programs and sessions run: HOME, holding only what they made (and sources)."""
    return os.path.join(run_folder(chapter), "home")


def ordinary_user():
    """The user programs run as when this script is started as root: (pw entry or None, warning)."""
    if os.geteuid() != 0:
        return None, ""
    bad = ""
    for where, name in (("US_RUN_USER", os.environ.get("US_RUN_USER")), ("SUDO_USER", os.environ.get("SUDO_USER")),
                        ("run.user in understudy.yaml", load_config().get("run.user")), ("", FALLBACK_USER)):
        if not name:
            continue
        try:
            pw = pwd.getpwnam(name)
        except KeyError:
            bad = bad or (f"{where}={name}" if where else "")
            continue
        if pw.pw_uid != 0:
            return pw, (f"warning: {bad} is not a user here; programs run as {pw.pw_name}" if bad else "")
    if bad:
        return None, f"warning: {bad} is not a user here; programs run as root"
    return None, "warning: running as root; set US_RUN_USER to an ordinary user to run programs as that user"


def can_reach(path, pw):
    """True if user pw can enter every folder on the way to path."""
    groups = {g for g in os.getgrouplist(pw.pw_name, pw.pw_gid)}
    path = os.path.abspath(path)
    while True:
        st = os.stat(path)
        ok = (st.st_mode & 0o001) or (st.st_uid == pw.pw_uid and st.st_mode & 0o100) or \
             (st.st_gid in groups and st.st_mode & 0o010)
        if not ok:
            return False
        parent = os.path.dirname(path)
        if parent == path:
            return True
        path = parent


def give_to(path, pw):
    if not pw:
        return
    for top, dirs, files in os.walk(path):
        for name in [top] + [os.path.join(top, f) for f in files + dirs]:
            try:
                os.lchown(name, pw.pw_uid, pw.pw_gid)
            except OSError:
                pass


# ---------------------------------------------------------------- running things

def copy_entry(src, dst):
    if os.path.isdir(src) and not os.path.islink(src):
        shutil.copytree(src, dst, symlinks=True)
    else:
        shutil.copy2(src, dst, follow_symlinks=False)


class Result:
    def __init__(self, out=b"", err=b"", code=0, timed_out=False, missing=""):
        self.out, self.err, self.code, self.timed_out, self.missing = out, err, code, timed_out, missing


def limiter(cpu_seconds, pw):
    def setup():
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds + 1))
        resource.setrlimit(resource.RLIMIT_FSIZE, (FILE_LIMIT, FILE_LIMIT))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        if pw:
            os.setgid(pw.pw_gid)
            os.initgroups(pw.pw_name, pw.pw_gid)
            os.setuid(pw.pw_uid)
    return setup


BOOK_ENV = {}   # the book's PLAN.md env: lines, set by Chapter.prepare
HOME_SHOWN = "/home/you"   # what the reader sees where the run's private home folder was printed


def environment(cwd, pw):
    """The same every run: a private HOME (the working folder), fixed locale and time zone, no pager,
    no system-wide git settings, then the book's own env: lines."""
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": cwd, "PS1": "$ ",
           "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TZ": "UTC", "TERM": "dumb", "PAGER": "cat", "GIT_PAGER": "cat",
           "GIT_CONFIG_NOSYSTEM": "1", "PYTHONDONTWRITEBYTECODE": "1", "PYTHON_BASIC_REPL": "1",
           "PYTHONPYCACHEPREFIX": os.path.join(os.path.dirname(cwd), "pycache"), "USER": pw.pw_name if pw else "root"}
    return dict(env, **BOOK_ENV)


def run(argv, cwd, pw, stdin=b"", timeout=5.0, compiler=False, tty=None, extra=None, typed=False, **timing):
    """Run argv in cwd as pw with limits. Never raises for the program's own failures.
    tty="both" (or "out"): standard output and error (or output only) on a pseudo-terminal, as on the
    reader's screen, read in order into out; standard input stays a pipe, or with typed=True is the
    terminal too, and stdin is typed there a line at a time when a command waits for it."""
    if shutil.which(argv[0], path=os.environ.get("PATH")) is None and not os.path.exists(os.path.join(cwd, argv[0])):
        return Result(missing=argv[0])
    env = dict(environment(cwd, pw), **(extra or {}))
    if compiler:
        env["LC_ALL"] = env["LANG"] = "C"   # plain quotes in messages, the same on every machine
    if tty:
        return run_tty(argv, cwd, pw, env, stdin, timeout, tty, typed, **timing)
    try:
        proc = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, start_new_session=True,
                                preexec_fn=limiter(int(timeout) + 1, pw))
    except OSError as e:
        return Result(err=str(e).encode(), code=127)
    try:
        out, err = proc.communicate(stdin, timeout=timeout)
        return Result(out, err, proc.returncode)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            pass
        out, err = proc.communicate()
        return Result(out, err, proc.returncode, timed_out=True)


QUIET = 0.3   # typed input, where /proc cannot tell who waits: after this long with no output


def reading_input(session):
    """True if a process of the session waits in read() on its standard input, False if none does,
    None where /proc cannot tell (not Linux, or not allowed)."""
    seen = None
    for pid in os.listdir("/proc") if os.path.isdir("/proc") else []:
        try:
            with open(f"/proc/{pid}/stat") as f:
                if int(f.read().rsplit(")", 1)[1].split()[3]) != session:
                    continue
            with open(f"/proc/{pid}/syscall") as f:
                seen = False
                if f.read().startswith("0 0x0 "):    # read(0, ...)
                    return True
        except (OSError, ValueError, IndexError):
            pass
    return seen


def wants_input(session, last):
    """True when a typed line should go in now: the session reads, or (where /proc cannot tell) it is quiet."""
    waiting = reading_input(session)
    return waiting or (waiting is None and time.time() - last >= QUIET)


def controlling(slave_fd, setup):
    """The terminal becomes the session's own, as a reader's is: Ctrl-C typed there interrupts the command."""
    def pre():
        fcntl.ioctl(slave_fd, termios.TIOCSCTTY, 0)
        setup()
    return pre


def run_tty(argv, cwd, pw, env, stdin, timeout, tty, typed=False, wait=None, restart=None):
    """With typed=True stdin is typed (us_term.keys: lines, ^C, ^D): with wait=N each item N seconds after
    the command starts or the item before it, else when the session reads. restart: output that marks the
    start of the next command, from which its time limit (and wait) count afresh."""
    master, slave = os.openpty()
    fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 80, 0, 0))   # the reader's 80 columns
    try:
        setup = limiter(int(timeout) + 1, pw)
        proc = subprocess.Popen(argv, cwd=cwd, env=env, stdin=slave if typed else subprocess.PIPE, stdout=slave,
                                stderr=slave if tty == "both" else subprocess.DEVNULL, start_new_session=True,
                                preexec_fn=controlling(1, setup) if typed else setup)
    except OSError as e:
        os.close(master)
        return Result(err=str(e).encode(), code=127)
    finally:
        os.close(slave)
    chunks, pending, deadline, timed_out = [], us_term.keys(stdin) if typed else stdin, time.time() + timeout, False
    if not pending and not typed:
        proc.stdin.close()
    last = clock = time.time()
    while True:
        left = deadline - time.time()
        if left <= 0:
            timed_out = True
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except OSError:
                pass
            left = 1.0                    # what it printed before it was killed
        poll = typed and pending and not timed_out
        pause = left if not poll else min(left, 0.05) if wait is None else min(left, max(0, clock + wait - time.time()))
        ready, writable, _ = select.select([master], [proc.stdin] if pending and not typed else [], [], pause)
        if poll and (time.time() >= clock + wait if wait is not None else not ready and wants_input(proc.pid, last)):
            os.write(master, pending.pop(0))  # the terminal echoes it, as it does a reader's typing
            clock = time.time()
        if poll and not ready:
            continue
        last = time.time()
        if writable:
            try:
                pending = pending[os.write(proc.stdin.fileno(), pending[:4096]):]
            except OSError:
                pending = b""
            if not pending:
                proc.stdin.close()
        if ready:
            try:
                data = os.read(master, 65536)
            except OSError:               # EIO: every writer has closed the terminal
                data = b""
            if not data:
                break
            chunks.append(data)
            if restart and not timed_out and restart in chunks[-1] + (chunks[-2][-64:] if len(chunks) > 1 else b""):
                deadline, clock = time.time() + timeout, time.time()
        elif timed_out:
            break
    os.close(master)
    if pending and not typed:
        proc.stdin.close()
    proc.wait()
    return Result(b"".join(chunks).replace(b"\r\n", b"\n"), b"", proc.returncode, timed_out=timed_out)


_versions = {}


def tool_version(tool):
    if tool not in _versions:
        try:
            p = subprocess.run([tool, "--version"], capture_output=True, timeout=20)
            text = (p.stdout or p.stderr).decode(errors="replace").strip().splitlines()
            _versions[tool] = text[0] if text else tool
        except (OSError, subprocess.TimeoutExpired):
            _versions[tool] = ""
    return _versions[tool]


def text_of(data, work):
    """Bytes to text: newlines normalised; the run's private home folder reads as the reader's (HOME_SHOWN),
    as it does in terminal sessions, so a traceback names /home/you/shop/sales.py as the reader's will."""
    text = data.decode("utf-8", errors="replace").replace("\r\n", "\n")
    for home in sorted({work, os.path.realpath(work)}, key=len, reverse=True):
        text = text.replace(home, HOME_SHOWN)
    return text


def tidy(text):
    """Output as pasted: trailing spaces cut from each line (invisible, and editors strip them),
    and a final newline."""
    text = re.sub(r"[ \t]+$", "", text, flags=re.M)
    return text if not text or text.endswith("\n") else text + "\n"


@functools.lru_cache(maxsize=None)
def sanitizers():
    """True if a program built with -fsanitize=address,undefined runs here; says once if not."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "t.c")
        with open(src, "w") as f:
            f.write("int main(void) { return 0; }\n")
        try:
            ok = subprocess.run(["gcc", src, "-o", src[:-2]] + SAN_FLAGS, capture_output=True, timeout=60).returncode == 0 \
                and subprocess.run([src[:-2]], capture_output=True, timeout=20, env=SAN_ENV).returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            ok = False
    if not ok:
        print("sanitizers not available here: programs not checked for memory faults", file=sys.stderr)
    return ok


SIGNAMES = "|".join(sorted({re.escape(signal.strsignal(s)) for s in signal.valid_signals()
                            if signal.strsignal(s)}, key=len, reverse=True))
SHELL_CRASH = re.compile(r"^(?:/bin/)?bash: line \d+: +\d+ (%s)\b.*$" % SIGNAMES, re.M)


def as_interactive(text):
    """Shell messages as an interactive shell prints them: 'Segmentation fault', not
    'bash: line 2:   919 Segmentation fault      (core dumped) ./prog'; 'bash: x', not 'bash: line 2: x'."""
    text = SHELL_CRASH.sub(r"\1", text)
    return re.sub(r"^((?:/bin/)?bash): line \d+: ", r"\1: ", text, flags=re.M).replace(" (core dumped)", "")


# ---------------------------------------------------------------- one chapter

class Chapter:
    def __init__(self, path, opts, text=None):
        self.path, self.opts = path, opts
        self.name = os.path.basename(path)
        if text is None:
            with open(path, encoding="utf-8", newline="") as f:
                text = f.read()
        self.raw = text
        self.lines = self.raw.splitlines(keepends=True)
        self.blocks, self.errors = parse_chapter(self.lines, answers=getattr(opts, "ids", None) is None)
        self.traces, errors = parse_traces(self.lines)
        self.errors += errors
        self.items = []                  # (line in the chapter as read, rest of the problem line, block id)
        self.outs = {}                   # block id -> its output as pasted (None for nothing)
        self.notes = {}                  # block id -> why it was not run
        self.written = False
        self.counts = {"ran": 0, "compiled": 0, "warns": 0, "errors": 0, "fragments": 0, "skipped": 0,
                       "not run": 0, "traced": 0, "unrun": 0}
        self.missing = set()
        self.state = None                # what the sessions make outside HOME (PLAN.md `state:`), see us_state.py
        self.masks = []                  # text that changes on every run: ignored when outputs are compared
        self.tips = []                   # (line, text, block id): advice, not problems
        self.fixed = {}                  # 0-based line -> marker line rewritten (unrun dropped)
        self.files = {}                  # file name -> first code line of the block that saved it
        self.new_out = {}                # block id -> list of lines for its owned region
        self.work = working_folder(path)
        self.tool = os.path.dirname(self.work)   # the cache, tried/, snapshots and the tool's own builds
        self.pw = None
        self.cache = {}
        self.cwd = self.work             # where the next session starts
        self.hiding = set()
        m = re.match(r"(\d+)-", self.name)
        self.number = int(m.group(1)) if m else 0
        self.start, self.start_key = start_of(path, self.number, opts)
        self.broken = None               # an earlier chapter that could not be run to its end (see rebuild)

    # -- reporting

    def problem(self, line, block, message, hint=""):
        text = (f"id={block.id}  " if block and block.id else "") + message + (f"  ({hint})" if hint else "")
        self.items.append((line, text, block.id if block else ""))

    @property
    def problems(self):
        return [f"{self.name}:{self.where(line)}  {text}" for line, text, _ in self.items]

    def where(self, line):
        """A line number of the chapter as read, moved to where it is after this run's edits."""
        if not self.written:
            return line
        shift = 0
        for b in self.blocks + self.traces:
            if b.id in self.new_out and b.out_end <= line - 1:
                shift += len(self.new_out[b.id]) - (b.out_end - b.out_start)
        return line + shift

    def chapter_line(self, block, diag_file, diag_line):
        """Line in the chapter of a message about line diag_line of diag_file."""
        if diag_file and diag_line:
            base = os.path.basename(diag_file)
            if base == block.src:
                return block.open + 1 + diag_line
            if base in self.files:
                return self.files[base] + diag_line - 1
        return block.marker

    def first_diag(self, block, text, kinds=("error", "warning"), last=False):
        """(chapter line, message) of the first error (or warning) in compiler or interpreter output."""
        lines = [x for x in text.splitlines() if x.strip()]
        found = []
        for k, line in enumerate(lines):
            for pat in DIAG:
                m = pat.match(line)
                if m:
                    msg = m.groupdict().get("msg") or next(
                        (x.strip() for x in lines[k + 1:] if re.match(r"^\w*(Error|Warning|error)\b", x.strip())),
                        lines[-1].strip())
                    found.append((m.group("file"), int(m.group("line")), re.sub(r"\s*\[-W[^\]]*\]$", "", msg)))
                    break
        if last:
            found.reverse()
        for kind in kinds:
            for name, num, msg in found:
                if kind in msg.lower():
                    return self.chapter_line(block, name, num), msg
        if found:
            name, num, msg = found[0]
            return self.chapter_line(block, name, num), msg
        return block.marker, (lines[0].strip() if lines else "no message")

    # -- the main loop

    def go(self):
        if self.errors:
            for line, bid, msg in self.errors:
                self.items.append((line, (f"id={bid}  " if bid else "") + msg, bid))
            return
        broken = self.rebuild()
        if broken and getattr(self.opts, "rebuilding", False):
            self.broken = broken
            return
        if broken:
            print(f"{self.name}:1  starts from an empty home: {os.path.basename(broken)} cannot be run to its end "
                  f"without a problem, so its end state was not rebuilt (run python3 scripts/us_run.py "
                  f"{shown(broken)} and fix it)")
        self.prepare()
        self.hiding = set()              # ids of python blocks whose file would hide a module: never run
        for block in self.blocks:
            if self.hides_module(block):
                self.hiding.add(block.id)
                continue
            self.save_source(block)
        self.begin()
        self.by_id = {b.id: b for b in self.blocks}
        self.full = not self.opts.only     # try too: every block above a tried one runs first
        self.done = set()                # ids of blocks whose files are in the working folder now
        files, above = hashlib.sha256(), hashlib.sha256()
        for block in self.blocks:
            if block.attrs.get("file") is not None:
                files.update(block.code.encode())
            selected = not (self.opts.only and block.id != self.opts.only) and \
                (getattr(self.opts, "ids", None) is None or block.id in self.opts.ids)
            deps = [files.hexdigest(), [[b.code, sorted(b.attrs.items())] for b in self.needs(block, selected)]]
            if block.lang == CONSOLE:
                deps.append(above.hexdigest())
            if block.mode != "fragment":
                above.update(json.dumps([block.code, sorted(block.attrs.items())]).encode())
            if not selected:
                continue
            if block.mode == "fragment":
                self.counts["fragments"] += 1
                continue
            if block.id in self.hiding:
                continue
            self.do_block(block, json.dumps(deps))
        if self.full and getattr(self.opts, "ids", None) is None and not getattr(self.opts, "fresh", False) \
                and self.number and not self.items:
            self.save_end(json.dumps([self.start_key, above.hexdigest(), files.hexdigest(), sorted(BOOK_ENV.items())]))
        for t in self.traces:
            if (not self.opts.only or t.prog == self.opts.only) and t.marker > getattr(self.opts, "trace_from", 0):
                self.do_trace(t, files.hexdigest())
        shutil.rmtree(os.path.join(self.tool, "snap"), ignore_errors=True)
        if self.state:                   # nothing the run made in Docker is left behind (downloads stay)
            self.state.clear()
        self.save_cache()

    def rebuild(self):
        """In a terminal book, a missing snapshot of chapter n-1 is made again: a full run of that chapter,
        quiet and not written back (it rebuilds the ones before it the same way). Returns the chapter
        file that could not be run to its end, or None."""
        if self.start or self.number < 2 or getattr(self.opts, "fresh", False):
            return None
        book = book_of(self.path)
        plan = bf.load_plan(book) if book else None
        prev = bf.chapter_path(book, self.number - 1) if plan and plan.run.strip().lower() == CONSOLE else None
        if not prev:
            return None
        ch = Chapter(prev, argparse.Namespace(only=None, force=False, strict=False, rebuilding=True))
        ch.go()
        if ch.broken:
            return ch.broken
        self.start, self.start_key = start_of(self.path, self.number, self.opts)
        if not self.start:
            return prev
        print(f"rebuilt chapter {ch.number}'s end state (the saved one was missing)", file=sys.stderr)
        return None

    # -- the files programs make

    def needs(self, block, report=False, seen=None):
        """The blocks named in after= (and theirs), in chapter order; an unknown name is a problem."""
        seen = set() if seen is None else seen
        for name in filter(None, (x.strip() for x in block.attrs.get("after", "").split(","))):
            dep = self.by_id.get(name)
            if dep is None or dep.marker >= block.marker:
                if report:
                    self.problem(block.marker, block, f"after={name} names no program above this one",
                                 "try that program first, or fix the id")
            elif name not in seen:
                seen.add(name)
                self.needs(dep, False, seen)
        return sorted((self.by_id[x] for x in seen), key=lambda b: b.marker)

    def data_names(self):
        """Names in the working folder that programs made: all but sources, builds, the cache and tried/."""
        keep = set(KEEP)
        for b in self.blocks:
            stem = os.path.splitext(b.src)[0]
            keep |= {b.src, stem, stem + ".trace"} if b.src else set()
        return [n for n in os.listdir(self.work) if n not in keep and not n.endswith(".class")]

    def clean(self):
        for name in self.data_names():
            path = os.path.join(self.work, name)
            if os.path.isdir(path) and not os.path.islink(path):
                shutil.rmtree(path, ignore_errors=True)
            else:
                try:
                    os.remove(path)
                except OSError:
                    pass

    def begin(self):
        """HOME as the chapter starts: what the chapter before left (its snapshot), else empty."""
        self.restore(self.start) if self.start else self.clean()
        if self.state:                   # and nothing in Docker that the book's runs made before
            self.state.clear()
        self.cwd = self.work

    def save_end(self, key):
        """Keep HOME as this chapter leaves it, for the next chapter to start from (unless kept already)."""
        dest = chapter_snapshot(self.path, self.number)
        try:
            if open(os.path.join(dest, "key")).read() == key:
                return
        except OSError:
            pass
        for b in self.blocks:            # blocks taken from the cache made no files: make them now
            if b.mode != "fragment" and b.id not in self.done:
                self.replay(b)
        shutil.rmtree(dest, ignore_errors=True)
        os.makedirs(os.path.join(dest, "home"))
        for name in self.data_names():
            copy_entry(os.path.join(self.work, name), os.path.join(dest, "home", name))
        with open(os.path.join(dest, "key"), "w") as f:
            f.write(key)

    def snapshot(self):
        """Copy the files programs made, to undo a run with restore()."""
        snap = os.path.join(self.tool, "snap")
        shutil.rmtree(snap, ignore_errors=True)
        os.makedirs(snap)
        for name in self.data_names():
            copy_entry(os.path.join(self.work, name), os.path.join(snap, name))
        return snap

    def restore(self, snap):
        self.clean()
        for name in os.listdir(snap):
            copy_entry(os.path.join(snap, name), os.path.join(self.work, name))
        give_to(self.work, self.pw)

    def ready(self, block):
        """Make the files block reads: in a full run every block above it has run, else its after= blocks."""
        for dep in [b for b in self.blocks if b.marker < block.marker] if self.full else self.needs(block):
            if dep.id not in self.done:
                self.replay(dep)
        self.done.add(block.id)

    def replay(self, block):
        """Run a block once for the files it makes; its output and problems are not used."""
        self.done.add(block.id)
        if block.id in self.hiding:
            return
        before = len(self.items)
        if block.lang != CONSOLE:
            self.settle(block)
        if block.lang == CONSOLE and block.mode == "run" and self.safe(block, self.commands(block)):
            self.tracked(block, self.commands(block))
        elif block.lang in LANGS and block.mode in ("run", "warns", "crash") and \
                (block.lang not in ("bash", "sh") or self.safe(block, [block.code])):
            stem = os.path.splitext(block.src)[0] + (".class" if block.lang == "java" else "")
            built, src = os.path.join(self.place(block), stem), os.path.join(self.place(block), block.src)
            if LANGS[block.lang]["main"] == "build" and \
                    (not os.path.exists(built) or os.path.getmtime(built) < os.path.getmtime(src)):
                self.build(block)
            run(self.command(block, "run") + shlex.split(block.attrs.get("args", "")), self.place(block), self.pw,
                stdin=unescape(block.attrs.get("stdin", "")).encode(), timeout=self.limit(block))
        del self.items[before:]

    def prepare(self):
        os.makedirs(self.work, exist_ok=True)
        book = book_of(self.path)
        BOOK_ENV.clear()
        BOOK_ENV.update(bf.plan_env(book) if book else {})
        self.state = us_state.tracker((bf.plan_meta(book, "state") or [""])[0], os.path.dirname(self.tool)) \
            if book else None
        for pattern in (self.state.masks if self.state else []) + (bf.plan_meta(book, "mask") if book else []):
            try:
                self.masks.append(re.compile(pattern))
            except re.error:
                pass                     # us_plan.py check names a bad pattern
        self.pw, warning = ordinary_user()
        if warning:
            print(warning, file=sys.stderr)
        if self.pw:
            if not can_reach(self.work, self.pw):
                sys.exit(f"{self.name}: user {self.pw.pw_name} cannot reach {self.work}; "
                         "set US_RUN_USER to another user or move the chapter")
            give_to(self.tool, self.pw)
        try:
            with open(os.path.join(self.tool, "cache.json"), encoding="utf-8") as f:
                self.cache = json.load(f)
        except (OSError, ValueError):
            self.cache = {}

    def save_cache(self):
        path = os.path.join(self.tool, "cache.json")
        with open(path + ".tmp", "w", encoding="utf-8") as f:
            json.dump(self.cache, f, indent=0, sort_keys=True)
        os.replace(path + ".tmp", path)

    def hides_module(self, block):
        """True (and a problem) for a python block saved under the name of a module it would hide."""
        if block.lang != "python" or block.mode == "fragment" and block.attrs.get("file") is None:
            return False
        name = os.path.basename(block.attrs.get("file") or block.id + ".py")
        stem = os.path.splitext(name)[0]
        if stem not in HIDDEN_MODULES:
            return False
        said = f"file={name}" if block.attrs.get("file") else f"id={block.id}"
        self.items.append((block.marker, f"{said} would be saved as {name}, which hides Python's own module "
                           f"'{stem}'; rename it, for example " +
                           (f"file={stem}_demo.py" if block.attrs.get("file") else f"id={stem}-demo"), block.id))
        return True

    def place(self, block):
        """Folder a program is saved, built and run in: where the last console session ended when that
        is a folder inside the run's home, else the home itself."""
        return getattr(block, "dir", None) or self.work

    def settle(self, block):
        """Before a program is built or run: put it (and its source) where the reader is now."""
        here = os.path.realpath(self.cwd) if os.path.isdir(self.cwd) else ""
        home = os.path.realpath(self.work)
        block.dir = self.cwd if here and here != home and here.startswith(home + os.sep) else None
        if block.dir and block.src:
            path = os.path.join(block.dir, block.src)
            with open(path, "w", encoding="utf-8") as f:
                f.write(block.code)
            if self.pw:
                os.chown(path, self.pw.pw_uid, self.pw.pw_gid)
            stray = os.path.join(self.work, block.src)      # save_source put a copy in the home: one is enough
            if os.path.isfile(stray) and open(stray, encoding="utf-8", errors="replace").read() == block.code:
                os.remove(stray)

    def text(self, block, data):
        """text_of for a program's messages, wherever under the home it was saved."""
        return text_of(data, self.work)

    def save_source(self, block):
        if block.attrs.get("file") is None and (block.lang not in LANGS or block.mode == "fragment"):
            return
        name = block.attrs.get("file")
        if not name and block.lang == "java":
            m = re.search(r"public\s+(?:final\s+)?class\s+(\w+)", block.code)
            name = (m.group(1) if m else block.id) + ".java"
        block.src = os.path.basename(name or block.id + LANGS[block.lang]["ext"])
        path = os.path.join(self.work, block.src)
        if not os.path.exists(path) or open(path, encoding="utf-8", errors="replace").read() != block.code:
            with open(path, "w", encoding="utf-8") as f:
                f.write(block.code)
            if self.pw:
                os.chown(path, self.pw.pw_uid, self.pw.pw_gid)
        if block.attrs.get("file") is not None:
            self.files.setdefault(block.src, block.open + 2)

    def command(self, block, step):
        spec = LANGS[block.lang]
        template = spec[step]
        if spec["main"] == step:
            template = load_config().get("run." + block.lang, template)
        exe = "./" + os.path.splitext(block.src)[0]
        cls = os.path.splitext(block.src)[0]
        values = {"{src}": block.src, "{exe}": exe, "{cls}": cls, "{name}": block.id, "{dir}": self.place(block),
                  "{posix}": "-D_POSIX_C_SOURCE=200809L" if POSIX_RE.search(block.code) else ""}
        argv = []
        for word in shlex.split(template):
            for key, value in values.items():
                word = word.replace(key, value)
            if word:
                argv.append(word)
        return argv

    def cache_key(self, block, deps):
        tools = []
        if block.lang == CONSOLE:
            tools = ["bash"]
        else:
            for step in ("build", "run"):
                first = self.command(block, step)[0]
                if not first.startswith("./"):
                    tools.append(first)
        for tool in tools:
            if shutil.which(tool) is None:
                return None, tool
        code = self.commands(block) if block.lang == CONSOLE else block.code  # not the pasted output
        data = [VERSION, block.lang, block.mode, code, sorted(block.attrs.items()), deps,
                [tool_version(t) for t in tools], sorted(BOOK_ENV.items()), self.start_key]
        if block.lang == CONSOLE:              # the commands' own programs: a new git is a new result
            data.append([[w, os.stat(w).st_mtime_ns] for w in filter(None, (
                shutil.which(c.split()[0]) for c in re.split(r"[|;&\n]+", "\n".join(code)) if c.split()))])
        if block.lang in LANGS:
            data.append([self.command(block, s) for s in ("build", "run")])
        return hashlib.sha256(json.dumps(data).encode()).hexdigest(), ""

    def do_block(self, block, deps):
        key, missing = self.cache_key(block, deps)
        for cmd in self.commands(block) if self.state and block.lang == CONSOLE else []:
            tip = self.state.note(cmd)
            if tip:
                self.tips.append((block.open + 2 + self.command_line(block, cmd), f"id={block.id}  note: {tip}",
                                  block.id))
        if "unrun" in block.attrs:
            return self.try_unrun(block, key, missing)
        if missing:
            self.counts["not run"] += 1
            self.notes[block.id] = f"not run: no {missing} on this machine"
            if missing not in self.missing:
                self.missing.add(missing)
                print(f"not run: no {missing} on this machine", file=sys.stderr)
                if self.opts.strict:
                    self.problem(block.marker, block, f"not run: no {missing} on this machine")
            return
        hit = self.cache.get(block.id)
        if hit and hit.get("key") == key and not self.opts.force:
            self.counts["skipped"] += 1
            self.set_output(block, hit["out"])
            return
        self.ready(block)
        if block.lang == CONSOLE:
            out = self.do_console(block)
        else:
            self.settle(block)
            out = self.do_program(block)
        if out is not False:
            self.cache[block.id] = {"key": key, "out": out}
            self.set_output(block, out)
        else:
            self.cache.pop(block.id, None)

    def try_unrun(self, block, key, missing):
        """A block marked unrun="why" is tried on every run: when it now runs with no problem its output is
        pasted and unrun= is dropped from its marker; else it stays as it is and no problem is reported."""
        before, counts = len(self.items), dict(self.counts)
        hit = self.cache.get(block.id)
        if missing:
            out = False
        elif hit and hit.get("key") == key and not self.opts.force:
            out = hit["out"]
        else:
            self.ready(block)
            if block.lang != CONSOLE:
                self.settle(block)
            out = self.do_console(block) if block.lang == CONSOLE else self.do_program(block)
        if out is False or len(self.items) > before:
            why = self.items[before][1] if len(self.items) > before else f"no {missing} on this machine"
            del self.items[before:]
            self.counts = dict(counts, unrun=counts["unrun"] + 1)
            self.notes[block.id] = "still not run here (unrun): " + why
            self.cache.pop(block.id, None)
            return
        self.cache[block.id] = {"key": key, "out": out}
        self.set_output(block, out)
        self.fixed[block.marker - 1] = re.sub(r"\s+unrun(?:=(?:\"(?:[^\"\\]|\\.)*\"|'[^']*'|[^\s\"']+))?", "",
                                              self.lines[block.marker - 1], count=1)
        print(f"now run: {block.id}")

    # -- programs

    def build(self, block):
        exe = os.path.join(self.place(block), os.path.splitext(block.src)[0])
        if LANGS[block.lang]["run"] == "{exe}" and os.path.exists(exe):
            os.remove(exe)
        r = run(self.command(block, "build"), self.place(block), self.pw, timeout=BUILD_TIMEOUT, compiler=True)
        msgs = self.text(block, r.out + r.err)
        if r.timed_out:
            return False, "build timed out"
        return r.code == 0, msgs

    def do_program(self, block):
        """Returns the text to paste (None for nothing) or False after a problem."""
        mode = block.mode
        ok, msgs = self.build(block)
        has_msgs = bool(msgs.strip())
        count = {"run": "ran", "crash": "ran", "compile": "compiled", "warns": "warns", "error": "errors"}[mode]
        self.counts[count] += 1
        if mode == "error":
            if ok:
                self.problem(block.marker, block, "builds without errors", "mode=error needs a program that fails to build")
                return False
            if block.lang == "python":       # show what `python3 file.py` prints, not the compile step's wording
                r = run(self.command(block, "run"), self.place(block), self.pw, timeout=self.limit(block), tty="both")
                if r.code and r.out.strip():
                    msgs = tidy(self.text(block, r.out))
            return self.limit_lines(block, msgs)
        if not ok:
            line, msg = self.first_diag(block, msgs)
            hint = "mode=warns needs a program that builds" if mode == "warns" else \
                "fix the program, or set mode=error if the error is the lesson"
            self.problem(line, block, msg, hint)
            return False
        if mode == "warns":
            if not has_msgs:
                self.problem(block.marker, block, "builds without warnings",
                             "set mode=compile or mode=run, or make the warning happen")
                return False
            ran = self.quiet_run(block)
            return self.limit_lines(block, tidy(msgs) + ("\n" + ran if ran else ""))
        if has_msgs:
            line, msg = self.first_diag(block, msgs, kinds=("warning",))
            self.problem(line, block, msg, "fix the program, or set mode=warns if the warning is the lesson")
            return False
        if mode == "compile":
            return None
        return self.run_program(block)

    def quiet_run(self, block):
        """Output of a warns program if it runs as a run block would, else None; no problems recorded."""
        before = len(self.items)
        out = self.run_program(block, limit=False)
        del self.items[before:]
        return tidy(out) if out else None

    def run_program(self, block, limit=True):
        if block.lang in ("bash", "sh") and not self.safe(block, [block.code]):
            return False
        argv = self.command(block, "run") + shlex.split(block.attrs.get("args", ""))
        given = "stdin" in block.attrs
        stdin = unescape(block.attrs.get("stdin", "")).encode()
        timeout = self.limit(block)
        outputs, runs = [], 1 if "varies" in block.attrs else 2
        san = limit and block.mode == "run" and block.lang in ("c", "cpp") and "nosan" not in block.attrs
        snap = self.snapshot() if runs == 2 or san else None
        if san and self.sanitized(block, argv[1:], stdin, timeout) is False:
            return False
        for k in range(runs):
            if k or san:
                self.restore(snap)        # every run sees what the first one saw
            r = run(argv, self.place(block), self.pw, stdin=stdin, timeout=timeout,
                    tty="out" if block.attrs.get("stderr") == "hide" else "both")
            if not self.ran_well(block, r, timeout, given):
                return False
            text = self.text(block, r.out)
            if block.mode == "crash":
                text = tidy(text) + CRASH.get(-r.code, "Killed by " + signal.Signals(-r.code).name) + "\n"
            outputs.append(text)
        if len(outputs) == 2 and self.masked(outputs[0]) != self.masked(outputs[1]):
            self.problem(block.marker, block, "output changes between runs: say 'on this machine' in the text "
                         "or print a comparison instead", "if the text already does, add varies to the marker")
            return False
        return self.limit_lines(block, outputs[0]) if limit else outputs[0]

    def sanitized(self, block, args, stdin, timeout):
        """One unseen run of a build with the address and undefined-behaviour sanitizers: False (and a
        problem) on a sanitizer report, else None."""
        if not sanitizers():
            return None
        exe = os.path.join(self.tool, os.path.splitext(block.src)[0] + ".san")
        argv = [w for w in self.command(block, "build") if w != "-Werror" and not w.startswith("-Werror=")]
        if "-o" not in argv[:-1]:
            return None
        argv[argv.index("-o") + 1] = exe
        if run(argv + SAN_FLAGS, self.place(block), self.pw, timeout=BUILD_TIMEOUT, compiler=True).code != 0:
            return None
        r = run([exe] + args, self.place(block), self.pw, stdin=stdin, timeout=timeout * 3 + 5, extra=SAN_ENV)
        report = [x.strip() for x in self.text(block, r.err).splitlines()]
        first = next((x for x in report if SAN_RE.search(x)), None)
        if first is None:
            return None
        where = next((m for x in report for m in [re.search(r"([\w.+-]+):(\d+)(?::\d+)?(?:: runtime error|$)", x)]
                      if m and (m.group(1) == block.src or m.group(1) in self.files)), None)
        line = self.chapter_line(block, where.group(1), int(where.group(2))) if where else block.marker
        first = re.sub(r" on (?:unknown )?address 0x.*| \(pc 0x.*", "", re.sub(r"^==\d+==|^\S+:\d+:\d+: ", "", first))
        code = block.code.splitlines()
        if where and where.group(1) == block.src and int(where.group(2)) <= len(code):
            first += f", in line {where.group(2)} `{code[int(where.group(2)) - 1].strip()}`"
        self.problem(line, block, first + ": the program has a memory or undefined-behaviour fault: fix it",
                     "or add nosan to the marker if the fault is the lesson")
        return False

    def ran_well(self, block, r, timeout, given):
        want = block.attrs.get("exit", "0")
        if r.missing:
            self.problem(block.marker, block, f"not run: no {r.missing} on this machine")
            return False
        if r.timed_out or r.code in (-signal.SIGXCPU, -signal.SIGKILL):
            hint = ("an endless loop? if it reads input, give it stdin=\"...\"; it got none" if not given else
                    f"an endless loop? or set timeout= above {timeout:g}")
            self.problem(block.marker, block, f"timed out after {timeout:g}s", hint)
            return False
        if block.mode == "crash":
            if r.code >= 0:
                self.problem(block.marker, block, f"exited with code {r.code}, not killed by a signal",
                             "mode=crash needs a program that crashes")
            return r.code < 0
        if r.code < 0:
            name = signal.Signals(-r.code).name if -r.code in signal.valid_signals() else str(-r.code)
            self.problem(block.marker, block, f"crashed: signal {-r.code} ({name})",
                         "fix the program, or set mode=crash if the crash is the lesson")
            return False
        if want != "any" and r.code != int(want):
            err = [x for x in self.text(block, r.err or r.out).splitlines() if x.strip()]
            line, _ = self.first_diag(block, "\n".join(err), last=True) if err else (block.marker, "")
            detail = f": {err[-1].strip()}" if err else ""
            hint = f"or set exit={r.code} if that is the lesson" if want == "0" else ""
            self.problem(line, block, f"exited with code {r.code}, expected {want}{detail}", hint)
            return False
        return True

    def limit_lines(self, block, text):
        text = tidy(text)
        if not text:
            return None
        if not self.printable(block, text):
            return False
        n = text.count("\n")
        if n > MAX_LINES:
            self.too_long(block, text, f"prints {n} lines")
            return False
        if len(text) > MAX_CHARS:
            self.too_long(block, text, f"prints {len(text):,} characters")
            return False
        return text

    def too_long(self, block, text, said):
        """A problem for output over MAX_LINES, and its first lines kept as the block's note (try shows it)."""
        rows = [r if len(r) <= 200 else r[:200] + f" … {len(r) - 200:,} more characters cut"
                for r in text.splitlines()]
        shown = rows[:SHOW_LINES]
        if len(rows) > SHOW_LINES:
            shown.append(f"… {len(rows) - SHOW_LINES} more lines cut")
        self.notes[block.id] = "\n".join(shown)
        self.problem(block.marker, block, said, f"print less: {MAX_LINES} lines and {MAX_CHARS:,} characters "
                                                f"at most; the first {SHOW_LINES} lines are shown")

    def printable(self, block, text):
        """False (and a problem) for text with control bytes or bytes that are not UTF-8."""
        if "\ufffd" in text or re.search(r"[\x00-\x08\x0b-\x1f\x7f]", text):
            self.problem(block.marker, block, UNPRINTABLE)
            return False
        return True

    # -- console transcripts

    def commands(self, block):
        """The '$ ' commands of a console fence (see command_spans)."""
        lines = block.code.splitlines()
        return ["\n".join(lines[a:b + 1])[2:] for a, b in command_spans(lines)]

    def safe(self, block, texts):
        if "danger" in block.attrs:
            return True
        for text in texts:
            for k, line in enumerate(text.splitlines()):
                why = "is dangerous" if any(re.search(p, line) for p in DANGER) else \
                    self.state.danger(line) if self.state else ""
                if why:
                    where = block.open + 2 + k if len(texts) == 1 and block.lang != CONSOLE else block.marker
                    if block.lang == CONSOLE:
                        where = block.open + 2 + self.command_line(block, line)
                    self.problem(where, block, f"refused: '{line.strip()}' {why}" + (
                        "" if why == "is dangerous" else "; show it as mode=fragment instead"),
                                 "add danger=\"why\" to the marker if it must run")
                    return False
        return True

    def tracked(self, block, cmds, *args):
        """session(), noting in the ledger what it made outside HOME (PLAN.md `state:`); a session that
        timed out leaves nothing of the book's running."""
        seen = self.state.look() if self.state else None
        r = self.session(block, cmds, *args)
        if self.state:
            self.state.record(seen)
            if r.timed_out:
                self.state.clear()
        return r

    def masked(self, text):
        """text with what changes on every run (ids, times; PLAN.md `mask:`) blanked, for comparing only."""
        for pattern in self.masks:
            text = pattern.sub("~", text)
        return re.sub(r"[ \t]+", " ", text) if self.masks else text

    def limit(self, block):
        """Seconds a program or session may take: the marker's timeout=, else the plan's `timeout:` line, else 5."""
        if "timeout" in block.attrs:
            return float(block.attrs["timeout"])
        if not hasattr(self, "default_limit"):
            book = book_of(self.path)
            said = bf.plan_meta(book, "timeout") if book else []
            self.default_limit = float(said[-1]) if said and re.fullmatch(r"\d+(\.\d+)?", said[-1]) else 5.0
        return self.default_limit

    def session(self, block, cmds, sep="\x1eUS-RUN-END"):
        """Run a console block's commands in one shell on an 80-column terminal, each followed by a line
        with sep and its exit code; it starts where the session before it ended, and notes where it ends."""
        start = self.cwd if os.path.isdir(self.cwd) else self.work
        script = f"exec 2>&1\ntrap : INT\ncd {shlex.quote(start)}\n" + "".join(   # Ctrl-C ends a command, not all
            f"{c}\nprintf '\\n{sep} %s\\n' \"$?\"\n" for c in cmds) + "printf '\\x1eUS-RUN-CWD %s' \"$PWD\"\n"
        wait = block.attrs.get("wait")
        r = run(["bash", "-c", script], self.work, self.pw, stdin=unescape(block.attrs.get("stdin", "")).encode(),
                timeout=self.limit(block), tty="both", typed="stdin" in block.attrs,
                wait=float(wait) if wait else None, restart=sep.encode())
        out, _, cwd = r.out.partition(b"\x1eUS-RUN-CWD ")
        if cwd:
            r.out, self.cwd = out, cwd.decode("utf-8", errors="replace")
        return r

    def screen(self, text):
        """What the reader's terminal finally shows (us_term.final_screen): no colour, a progress display
        that redraws itself as its last frame, overstruck letters once, tabs as spaces, HOME as HOME_SHOWN."""
        text = us_term.final_screen(text.replace("\r\n", "\n"))
        for home in sorted({self.work, os.path.realpath(self.work)}, key=len, reverse=True):
            text = text.replace(home, HOME_SHOWN)
        return text

    def command_line(self, block, text):
        for k, line in enumerate(block.code.splitlines()):
            if text.strip().split("\n")[0] in line:
                return k
        return -1

    def do_console(self, block):
        cmds = self.commands(block)
        if not cmds:
            self.problem(block.marker, block, "console block has no '$ ' command")
            return False
        if not self.safe(block, cmds):
            return False
        sep = "\x1eUS-RUN-END"
        timeout = self.limit(block)
        r = self.tracked(block, cmds, sep)
        self.counts["ran"] += 1
        text = self.screen(r.out.decode("utf-8", errors="replace"))
        parts = re.split(r"\n?\n" + re.escape(sep) + r" (\d+)\n", "\n" + text)
        outs, codes = parts[0:-1:2], [int(x) for x in parts[1::2]]
        if r.timed_out or len(codes) < len(cmds):
            done = len(codes)
            self.problem(block.marker, block, f"timed out after {timeout:g}s in '{cmds[min(done, len(cmds) - 1)]}'",
                         "a command waiting for input? give stdin=, or set timeout=")
            return False
        want = block.attrs.get("exit", "0")
        for k, (cmd, code) in enumerate(zip(cmds, codes)):
            expect = want if k == len(cmds) - 1 else "0"
            if expect != "any" and code != int(expect):
                said = (outs[k][1:] if k == 0 else outs[k]).splitlines()
                self.notes[block.id] = tidy(as_interactive("\n".join(["$ " + cmd] + said[:15] + (
                    [f"… {len(said) - 15} more lines"] if len(said) > 15 else []))))
                clash = self.state.clash(outs[k]) if self.state else ""
                self.problem(block.open + 2 + self.command_line(block, cmd), block,
                             clash or f"'{cmd}' exited with code {code}, expected {expect}",
                             "" if clash else "fix the command, or set exit= on the marker for the last command")
                return False
        body = ""
        for k, cmd in enumerate(cmds):
            out = outs[k][1:] if k == 0 else outs[k]
            body += "$ " + cmd + "\n"
            body += out + ("\n" if out and not out.endswith("\n") else "")
        body = tidy(as_interactive(body))
        if not self.printable(block, body):
            return False
        if body.count("\n") > MAX_LINES:
            self.too_long(block, body, f"transcript is {body.count(chr(10))} lines")
            return False
        if len(body) > MAX_CHARS:
            self.too_long(block, body, f"transcript is {len(body):,} characters")
            return False
        return body

    # -- traces

    def trace_problem(self, t, message):
        self.items.append((t.marker, f"trace id={t.prog}  {message}", t.prog))

    def do_trace(self, t, deps):
        block = next((b for b in self.blocks if b.id == t.prog), None)
        if block is None:
            return self.trace_problem(t, "no program with this id in the chapter; try it first, or fix the id")
        if block.mode != "run":
            return self.trace_problem(t, f"the program is mode={block.mode}; only a run program can be traced")
        if block.lang not in TRACE_LANGS:
            return self.trace_problem(t, f"trace is not supported for {block.tag or 'untagged'}; write the table by hand")
        at = [int(x) for x in t.attrs["at"].split()]
        code = block.code.splitlines()
        if any(not 0 < x <= len(code) for x in at):
            return self.trace_problem(t, f"at= names a line outside the program (lines 1 to {len(code)})")
        tools = [TRACE_LANGS[block.lang]] + (["gdb"] if block.lang != "python" else [])
        missing = next((x for x in tools if shutil.which(x) is None), None)
        if missing:
            print(f"trace not made: no {missing} on this machine; write the table below the marker by hand",
                  file=sys.stderr)
            return
        key = hashlib.sha256(json.dumps([VERSION, block.code, block.lang, sorted(block.attrs.items()), deps,
                                         [b.code for b in self.needs(block)], sorted(t.attrs.items()),
                                         [tool_version(x) for x in tools], self.start_key]).encode())
        name, key = f"trace:{t.prog}:{t.attrs['at']}:{t.attrs['watch']}", key.hexdigest()
        hit = self.cache.get(name)
        if hit and hit.get("key") == key and not self.opts.force:
            rows = hit["out"]
        else:
            self.begin()                 # the traced run starts where the program's own run did
            self.done = set()
            self.ready(block)
            rows = self.trace_rows(block, t, at)
            if isinstance(rows, str):
                return self.trace_problem(t, rows)
            if not rows:
                return self.trace_problem(t, "no line of at= ran; pick lines the run reaches")
            self.cache[name] = {"key": key, "out": rows}
        self.counts["traced"] += 1
        watch = t.attrs["watch"].split()
        end = self.lines[t.marker - 1][len(strip_end(self.lines[t.marker - 1])):] or "\n"
        cell = lambda x: x.replace("|", "\\|")
        table = ["| Line | Statement | " + " | ".join(f"`{cell(w)}`" for w in watch) + " |",
                 "|---" * (len(watch) + 2) + "|"]
        table += [f"| {line} | `{cell(code[line - 1].strip())}` | " + " | ".join(cell(v) for v in values) + " |"
                  for line, values in rows]
        self.outs[t.id] = "\n".join(table) + "\n"
        self.new_out[t.id] = [x + end for x in table]

    def trace_rows(self, block, t, at):
        """The traced run works in the home folder: lend it the program's source if that now lives elsewhere."""
        src = os.path.join(self.work, block.src)
        lent = not os.path.exists(src)
        if lent:
            with open(src, "w", encoding="utf-8") as f:
                f.write(block.code)
            if self.pw:
                os.chown(src, self.pw.pw_uid, self.pw.pw_gid)
        try:
            return self.traced_rows(block, t, at)
        finally:
            if lent and os.path.exists(src):
                os.remove(src)

    def traced_rows(self, block, t, at):
        """[[line, [values]], ...] from one walked run, or a problem as a string."""
        tool = TRACE_LANGS[block.lang]
        conf = {"src": block.src, "args": [shlex.quote(a) for a in shlex.split(block.attrs.get("args", ""))],
                "at": at, "watch": t.attrs["watch"].split(), "rows": int(t.attrs.get("rows", 12)),
                "first": t.attrs.get("hits") == "first"}
        files = {"trace.json": json.dumps(conf), "trace.stdin": unescape(block.attrs.get("stdin", "")),
                 "us_trace.py": open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "us_trace.py"),
                                     encoding="utf-8").read(), "trace.out": ""}
        for fname, text in files.items():
            with open(os.path.join(self.work, fname), "w", encoding="utf-8") as f:
                f.write(text)
            if self.pw:
                os.chown(os.path.join(self.work, fname), self.pw.pw_uid, self.pw.pw_gid)
        timeout = self.limit(block) + 20
        if tool == "python3":
            r = run(["python3", "us_trace.py"], self.work, self.pw,
                    stdin=files["trace.stdin"].encode(), timeout=timeout)
        else:
            exe = os.path.splitext(block.src)[0] + ".trace"
            r = run([tool, "-g", "-O0", "-w", block.src, "-o", exe, "-lm"], self.work, self.pw,
                    timeout=BUILD_TIMEOUT, compiler=True)
            if r.code != 0:
                return "does not build with -g -O0: " + (text_of(r.err, self.work).strip().splitlines() or [""])[0]
            r = run(["gdb", "-batch", "-nx", "-x", "us_trace.py", "./" + exe], self.work, self.pw, timeout=timeout)
        if r.timed_out:
            return f"the traced run timed out after {timeout:g}s"
        if b"Python Exception" in r.out + r.err:
            return "the tracer failed: " + text_of(r.out + r.err, self.work).strip().splitlines()[-1]
        with open(os.path.join(self.work, "trace.out"), encoding="utf-8") as f:
            rows = [json.loads(x) for x in f if x.strip()]
        if not rows and r.code != 0:
            err = text_of(r.err, self.work).strip().splitlines()
            return "the traced run failed" + (": " + err[-1] if err else "")
        return rows

    # -- writing

    def set_output(self, block, out):
        self.outs[block.id] = out
        end = self.lines[block.close][len(strip_end(self.lines[block.close])):] or "\n"
        if block.lang == CONSOLE and block.details is None:
            self.new_out[block.id] = [x + end for x in (out or "").split("\n")[:-1]]
            return
        if out is None:
            self.new_out[block.id] = []
            return
        longest = max([len(m) for m in re.findall(r"^(`+)", out, re.M)] + [0])
        fence = "`" * max(3, longest + 1)
        tag = "console" if block.lang == CONSOLE else "text"
        lines = [fence + tag + end] + [x + end for x in out.split("\n")[:-1]] + [fence + end]
        if block.details is not None and block.answer_at == block.out_end:
            lines = [end] * block.pad[0] + lines + [end] * block.pad[1]
        if block.lang == CONSOLE:            # under the question the commands only; between, the text as it is
            asked = ["$ " + c + "\n" for c in self.commands(block)]
            lines = [x + end for x in "".join(asked).split("\n")[:-1]] + self.lines[block.close:block.answer_at] + lines
        self.new_out[block.id] = lines

    def result(self):
        """The chapter text with every owned region replaced."""
        lines = list(self.lines)
        no_final = bool(lines) and not lines[-1].endswith("\n")
        if no_final:
            lines[-1] += "\n"
        for i, line in self.fixed.items():
            lines[i] = line
        for block in sorted(self.blocks + self.traces, key=lambda b: b.out_start, reverse=True):
            if block.id in self.new_out and not self.same(block):   # pasted text is never changed for a mask
                lines[block.out_start:block.out_end] = self.new_out[block.id]
        text = "".join(lines)
        if no_final:
            text = text[:-2] if text.endswith("\r\n") else text[:-1]
        return text

    def stale(self):
        """Ids of blocks whose pasted output differs from the new output."""
        out = []
        for block in self.blocks + self.traces:
            if block.id in self.new_out and "varies" not in block.attrs:
                old = [strip_end(x) for x in self.lines[block.out_start:block.out_end]]
                if old != [strip_end(x) for x in self.new_out[block.id]] and not self.same(block):
                    out.append(block)
        return out

    def same(self, block):
        """True when the pasted output and the new one differ only in what the masks ignore."""
        old = "\n".join(strip_end(x) for x in self.lines[block.out_start:block.out_end])
        new = "\n".join(strip_end(x) for x in self.new_out.get(block.id, []))
        return bool(self.masks) and self.masked(old) == self.masked(new)

    def write(self):
        text = self.result()
        if text == self.raw:
            return
        tmp = self.path + ".us-run.tmp"
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        shutil.copymode(self.path, tmp)
        os.replace(tmp, self.path)
        self.written = True


# ---------------------------------------------------------------- the command

def shown(path):
    """A path as a command line beside it should give it: relative when below here."""
    rel = os.path.relpath(path)
    return path if rel.startswith("..") else rel


def list_blocks(ch):
    for line, bid, msg in ch.errors:
        print(f"{ch.name}:{line}  " + (f"id={bid}  " if bid else "") + msg)
    for b in ch.blocks:
        print(f"{b.id}  {b.mode}  {b.tag or '-'}  {b.marker}")


def summary(ch):
    c = ch.counts
    parts = [f"ran {c['ran']}", f"compiled {c['compiled']}", f"warns {c['warns']}"]
    if c["errors"]:
        parts.append(f"errors {c['errors']}")
    parts.append(f"fragments {c['fragments']}")
    if c["not run"]:
        parts.append(f"not run {c['not run']}")
    if c["traced"]:
        parts.append(f"traced {c['traced']}")
    if c["unrun"]:
        parts.append(f"unrun {c['unrun']}")
    parts.append(f"skipped {c['skipped']} unchanged")
    n = len(ch.problems)
    parts.append(f"{n} problem" + ("" if n == 1 else "s"))
    return "  ".join(parts)


# ---------------------------------------------------------------- try: run a section's programs first

def tried_folder(chapter):
    """Where tried programs of a chapter are kept: tried/ID.md in its run folder."""
    return os.path.join(run_folder(chapter), "tried")


def tried_program(chapter, bid):
    """(marker line, fence text) of a tried program, or None."""
    path = os.path.join(tried_folder(chapter), bid + ".md")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", bid) or not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        marker, _, fence = f.read().partition("\n")
    return marker, fence


def try_chapter(book, n):
    """Path of chapter n of a book (existing, or where it will be created), or exit."""
    book = bf.resolve_book(book)
    plan = bf.load_plan(book)
    if plan is None or plan.chapter(n) is None:
        sys.exit(f"chapter {n} is not in the plan of {book}" if plan else f"no PLAN.md in {book}")
    return bf.chapter_path(book, n) or bf.new_chapter_path(book, n, plan.chapter(n).title)


def try_main(argv):
    ap = argparse.ArgumentParser(prog="us_run.py try", description="Run a section's programs before writing it; "
                                 "programs they name in after= run first, silently.")
    ap.add_argument("book")
    ap.add_argument("chapter", type=int)
    ap.add_argument("--file", metavar="PATH", help="read the programs from PATH instead of stdin")
    ap.add_argument("--fresh", action="store_true", help="start in an empty HOME, not where the chapter before ended")
    opts = ap.parse_args(argv)
    chapter = try_chapter(opts.book, opts.chapter)
    if opts.file:
        with open(opts.file, encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()
    label = os.path.basename(opts.file) if opts.file else "input"
    sub = [x if x.endswith("\n") else x + "\n" for x in text.splitlines(keepends=True)]
    blocks, errors = parse_chapter(sub, answers=False)
    errors += [(b.marker, b.id, "id= may use only letters, digits, '.', '_' and '-'") for b in blocks
               if b.id and not re.fullmatch(r"[A-Za-z0-9._-]+", b.id)]
    if not blocks and not errors and not parse_traces(sub)[0]:
        errors.append((1, "", "no program: send each as a <!-- code: id=NAME --> line with its fence below"))
    ids = {b.id for b in blocks}
    # The chapter as it is, then these programs: file= blocks before them are saved, as in a real run.
    # A chapter block with a tried id gives way to the tried one.
    head = []
    if os.path.isfile(chapter):
        with open(chapter, encoding="utf-8") as f:
            head = [x if x.endswith("\n") else x + "\n" for x in f.read().splitlines(keepends=True)]
        for b in parse_chapter(head, answers=False)[0]:
            if b.id in ids:
                head[b.marker - 1] = "\n"
    known = ids | {b.id for b in parse_chapter(head, answers=False)[0]}
    wanted = [t.prog for t in parse_traces(sub)[0]] + [x.strip() for b in blocks for x in b.attrs.get("after", "").split(",")]
    extra = []
    while wanted:
        name = wanted.pop(0)
        tried = None if not name or name in known else tried_program(chapter, name)
        if tried:                         # a program tried earlier, not in the chapter yet: above what needs it
            extra = ["\n", tried[0] + "\n"] + tried[1].splitlines(keepends=True) + extra
            known.add(name)
            wanted += [x.strip() for x in parse_attrs(MARKER.match(tried[0]).group(1)).get("after", "").split(",")]
    head += extra
    offset = len(head) + 1
    ch = Chapter(chapter, argparse.Namespace(only=None, force=False, strict=False, ids=ids, trace_from=offset,
                                                    fresh=opts.fresh),
                 text="".join(head) + "\n" + "".join(sub))
    if errors:
        ch.errors = [(line + offset, bid, msg) for line, bid, msg in errors]
    else:
        folder = tried_folder(chapter)
        os.makedirs(folder, exist_ok=True)
        for b in blocks:
            with open(os.path.join(folder, b.id + ".md"), "w", encoding="utf-8") as f:
                f.write(strip_end(sub[b.marker - 1]).strip() + "\n" + "".join(sub[b.open:b.close + 1]))
    ch.go()

    def where(line):
        return f"{label}:{line - offset}" if line > offset else f"{ch.name}:{line}"
    shown = set()
    for b in blocks if not errors else []:
        print(f"== id={b.id} ({b.mode})")
        for k, (line, msg, bid) in enumerate(ch.items):
            if bid == b.id:
                print(f"{where(line)}  {msg}")
                shown.add(k)
        for line, text, bid in ch.tips:
            if bid == b.id:
                print(f"{where(line)}  {text}")
        if b.id in ch.notes:
            print(ch.notes[b.id])
        rows = (ch.outs.get(b.id) or "").splitlines()
        for row in rows[:TRY_LINES]:
            print(row)
        if len(rows) > TRY_LINES:
            print(f"… {len(rows) - TRY_LINES} more lines")
    for t in ch.traces if not errors else []:
        if t.id in ch.outs:
            print(f"== trace id={t.prog} at {where(t.marker)}")
            print(ch.outs[t.id], end="")
    for k, (line, msg, bid) in enumerate(ch.items):
        if k not in shown:
            print(f"{where(line)}  {msg}")
    print(summary(ch))
    return 1 if ch.items else 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "try":
        return try_main(argv[1:])
    if argv and argv[0] == "--reset":
        return reset_main(argv[1:])
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("chapter")
    ap.add_argument("--only", metavar="ID", help="run one block")
    ap.add_argument("--check", action="store_true", help="change nothing; exit 1 if pasted output is out of date")
    ap.add_argument("--force", action="store_true", help="ignore the cache")
    ap.add_argument("--list", action="store_true", help="one line per block: id, mode, language, line")
    ap.add_argument("--strict", action="store_true", help="a language with no tool here is a problem")
    ap.add_argument("--fresh", action="store_true", help="start in an empty HOME, not where the chapter before ended")
    opts = ap.parse_args(argv)
    if not os.path.isfile(opts.chapter):
        sys.exit(f"no such chapter: {opts.chapter}")
    book = book_of(opts.chapter)
    plan = bf.load_plan(book) if book else None
    if plan and plan.run.strip().lower() == "none":
        print(f"{os.path.basename(opts.chapter)}: run: none in PLAN.md; nothing to run")
        return 0
    ch = Chapter(opts.chapter, opts)
    if opts.list:
        list_blocks(ch)
        return 1 if ch.errors else 0
    if opts.only and opts.only not in {b.id for b in ch.blocks}:
        sys.exit(f"{ch.name}: no block with id={opts.only}")
    ch.go()
    if opts.check:
        for block in ch.stale():
            if isinstance(block, Trace):
                ch.trace_problem(block, f"the table differs from a fresh trace (run python3 scripts/us_run.py "
                                        f"{shown(opts.chapter)})")
                continue
            ch.problem(block.marker, block, "pasted output differs from a fresh run",
                       f"run python3 scripts/us_run.py {shown(opts.chapter)} to paste the real output")
    elif not ch.errors:
        ch.write()
    for line, text, _ in ch.tips:
        print(f"{ch.name}:{ch.where(line)}  {text}")
    for line in ch.problems:
        print(line)
    print(summary(ch))
    return 1 if ch.problems else 0


def reset_main(argv):
    """--reset BOOK: remove everything the book's runs made outside their folders, built images included."""
    if len(argv) != 1:
        sys.exit("usage: python3 scripts/us_run.py --reset BOOK")
    book = bf.resolve_book(argv[0])
    if not os.path.isfile(os.path.join(book, "PLAN.md")):
        sys.exit(f"no PLAN.md in {book}")
    folder = os.path.dirname(run_folder(os.path.join(book, "chapters", "00-reset.md")))
    left = 0
    for kind in us_state.TRACKERS:
        t = us_state.tracker(kind, folder)
        gone = t.clear(images=True)
        left += sum(len(x) for x in t.ledger.values())
        said = ", ".join(f"{n} {k}" for k, n in gone.items() if n)
        print(f"{kind}: removed {said} made by the runs of {os.path.basename(book)}" if said else
              f"{kind}: nothing to remove for {os.path.basename(book)}")
    if left:
        print(f"{left} things could not be removed: is the {kind} service running? then run --reset again")
    return 1 if left else 0


if __name__ == "__main__":
    sys.exit(main())
