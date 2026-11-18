#!/usr/bin/env python3
"""Tests for scripts/us_run.py. Prints one line per test and "N passed, M failed"; exit 1 on failure.

    python3 tests/run/run.py
"""
import os
import pwd
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPT = os.path.join(ROOT, "scripts", "us_run.py")
FIXTURE = os.path.join(HERE, "fixture.md")
HAS_NODE = shutil.which("node") is not None
RESULTS = []
RESULTS_TRY = []


def ordinary_user():
    if os.geteuid() != 0:
        return None
    try:
        return pwd.getpwnam(os.environ.get("US_RUN_USER", "ubuntu")).pw_name
    except KeyError:
        return None


USER = ordinary_user()
TMP = tempfile.mkdtemp(prefix="us-run-tests-")
os.chmod(TMP, 0o755)
os.environ["TMPDIR"] = tempfile.tempdir = TMP  # run folders go in TMP too, and leave with it
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from us_run import run_folder, tried_folder  # noqa: E402


def env(**extra):
    e = dict(os.environ)
    if USER:
        e["US_RUN_USER"] = USER
    e.update(extra)
    return {k: v for k, v in e.items() if v is not None}


def us_run(path, *args, environ=None):
    p = subprocess.run([sys.executable, SCRIPT, path] + list(args), capture_output=True, text=True,
                       env=environ or env())
    return p.returncode, p.stdout, p.stderr


def test(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else f": {detail}"))


def workspace(text=None, name="fixture.md"):
    """A fresh temp folder (reachable by the ordinary user) holding a copy of the fixture."""
    d = tempfile.mkdtemp(prefix="us-run-test-")
    os.chmod(d, 0o755)
    path = os.path.join(d, name)
    if text is None:
        shutil.copy(FIXTURE, path)
    else:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)
    return path


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def problems(stdout):
    """{id: problem line} from the script's output."""
    out = {}
    for line in stdout.splitlines():
        m = re.search(r"id=(\S+)", line)
        if m:
            out[m.group(1)] = line
    return out


def fence_after(text, bid):
    """The text of the ```text fence directly below block bid's code fence, or None."""
    lines = text.splitlines()
    i = next(k for k, x in enumerate(lines) if re.search(rf"code: id={re.escape(bid)}(?=\s|-->)", x))
    j = i + 1
    while not lines[j].startswith("```"):
        j += 1
    j += 1
    while not lines[j].startswith("```"):
        j += 1
    if j + 1 < len(lines) and lines[j + 1].startswith("```text"):
        k = j + 2
        while not lines[k].startswith("```"):
            k += 1
        return "\n".join(lines[j + 2:k])
    return None


def console_body(text, bid):
    lines = text.splitlines()
    i = next(k for k, x in enumerate(lines) if re.search(rf"code: id={re.escape(bid)}(?=\s|-->)", x))
    j = i + 2
    k = j
    while not lines[k].startswith("```"):
        k += 1
    return "\n".join(lines[j:k])


def strip_owned(text):
    """Remove what the script owns: text fences right below a marked code fence, and the
    output lines of console fences. Written independently of the script's own parser."""
    lines = text.splitlines(keepends=True)
    out, i, marked, mode = [], 0, False, ""
    while i < len(lines):
        line = lines[i]
        m = re.match(r"\s*<!-- code:(.*)-->", line)
        if m:
            marked, mode = True, ("fragment" if "mode=fragment" in m.group(1) else "run")
            out.append(line)
            i += 1
            continue
        if marked and line.startswith("```"):
            tag = line.strip()[3:]
            out.append(line)
            i += 1
            while not lines[i].startswith("```"):
                if tag != "console" or lines[i].startswith("$ ") or mode == "fragment":
                    out.append(lines[i])
                i += 1
            out.append(lines[i])
            i += 1
            if mode != "fragment" and i < len(lines) and lines[i].startswith("```text"):
                i += 1
                while not lines[i].startswith("```"):
                    i += 1
                i += 1
            marked = False
            continue
        if line.strip():
            marked = False
        out.append(line)
        i += 1
    return "".join(out)


def remove_blocks(text, ids):
    """The fixture without the given blocks (marker, code fence and output fence)."""
    for bid in ids:
        pattern = rf"<!-- code: id={re.escape(bid)}(?=\s|-->)[^\n]*-->\n(`{{3}}|~{{3}})[^\n]*\n.*?\n\1\n(```text\n.*?\n```\n)?"
        text, n = re.subn(pattern, "", text, flags=re.S)
        assert n == 1, bid
    return text


PROBLEM_IDS = ["show-address", "unused-in-run", "forever", "waits-for-input", "too-long", "clean-up-refused"]


GIT_CHAPTER = """# Chapter 1: One

## 1.1 A

<!-- code: id=setup -->
```console
$ git config --global user.name 'Sam Rivera'
$ git config --global user.email sam@example.com
$ git config --global init.defaultBranch main
$ mkdir proj
$ cd proj
$ touch a b c d e f g h i j k l
$ git init --quiet
$ git add .
$ git commit --quiet -m First
$ git rev-parse --short HEAD
```

<!-- code: id=where exit=128 -->
```console
$ cd
$ pwd
$ ls -a
$ echo $HOME $TZ $LC_ALL $PAGER $GIT_PAGER
$ python3 -c 'import os; print(os.get_terminal_size().columns)'
$ printf 'red\\033[31m!\\033[0m\\rR\\n'
$ git status
```

## 1.2 B

<!-- code: id=log -->
```console
$ cd proj
$ ls
$ git log --oneline
```

<!-- code: id=quiz answer -->
```console
$ git log --oneline
```

<details>
<summary>Answer</summary>

One commit.

</details>
"""


def sessions():
    """Console fences of a chapter: one continuing story, from a clean private HOME, on an 80-column
    terminal, with the book's env: lines; try replays the chapter first."""
    gb = os.path.join(TMP, "sessions", "gitbook")
    os.makedirs(os.path.join(gb, "chapters"))
    write(os.path.join(gb, "PLAN.md"), "# G\nfor: x\nrun: console\nenv: GIT_AUTHOR_DATE=2026-01-05T10:00:00 "
          "GIT_COMMITTER_DATE=2026-01-05T10:00:00\n\n### 1 One\n1.1 A\n1.2 B\n1.3 C\n\n### 2 Two\n2.1 D\n")
    gch = os.path.join(gb, "chapters", "01-one.md")
    write(gch, GIT_CHAPTER)
    mine = os.path.expanduser("~/.gitconfig")
    before = read(mine) if os.path.exists(mine) else None
    code, out, err = us_run(gch)
    first = read(gch)
    test("sessions: the chapter runs", code == 0, out + err)
    head = console_body(first, "setup").splitlines()[-1]
    test("sessions: later fences find what earlier ones made (repository, settings), each starting where the "
         "one before ended",
         console_body(first, "log") == f"$ cd proj\n$ ls\na  b  c  d  e  f  g  h  i  j  k  l\n$ git log --oneline\n"
         f"{head} (HEAD -> main) First", first)
    test("sessions: HOME is private and shown as /home/you, with a fixed locale, time zone and no pager; 80 columns; "
         "colour codes and overwritten text dropped; not inside any git repository",
         console_body(first, "where") == "$ cd\n$ pwd\n/home/you\n$ ls -a\n.  ..  .gitconfig  proj\n"
         "$ echo $HOME $TZ $LC_ALL $PAGER $GIT_PAGER\n/home/you UTC C.UTF-8 cat cat\n"
         "$ python3 -c 'import os; print(os.get_terminal_size().columns)'\n80\n"
         "$ printf 'red\\033[31m!\\033[0m\\rR\\n'\nRed!\n"
         "$ git status\nfatal: not a git repository (or any of the parent directories): .git", first)
    test("sessions: the machine's own ~/.gitconfig is neither read nor written",
         (read(mine) if os.path.exists(mine) else None) == before)
    test("sessions: run folders sit under the system temp folder, apart from the product",
         run_folder(gch).startswith(os.path.join(TMP, "understudy-run") + os.sep) and not
         run_folder(gch).startswith(ROOT), run_folder(gch))
    code, out, err = us_run(gch, "--force")
    test("sessions: a second full run is byte for byte the same, commit hashes included (fixed dates from env:)",
         code == 0 and read(gch) == first, out + err)
    write(gch, GIT_CHAPTER)
    code, out, err = us_run(gch)
    test("sessions: the same hash from a fresh run", code == 0 and read(gch) == first, out + err)
    test("answer on a session: the commands under the question, the whole session in the hidden answer",
         "<!-- code: id=quiz answer -->\n```console\n$ git log --oneline\n```\n\n<details>\n"
         f"<summary>Answer</summary>\n\n```console\n$ git log --oneline\n{head} (HEAD -> main) First\n```\n\n"
         "One commit." in first, first)
    p = subprocess.run([sys.executable, SCRIPT, "try", gb, "1"], capture_output=True, text=True, env=env(),
                       input="<!-- code: id=later -->\n```console\n$ git log --oneline\n```\n")
    test("try: every session already in the chapter runs first, so the tried one sees what the real run will",
         p.returncode == 0 and p.stdout.startswith(f"== id=later (run)\n$ git log --oneline\n{head} (HEAD -> main) "
                                                   "First\n"), p.stdout + p.stderr)
    test("try: the tool's own files stay out of HOME",
         sorted(os.listdir(os.path.dirname(tried_folder(gch)))) == ["cache.json", "home", "tried"]
         and ".gitconfig" in os.listdir(os.path.join(run_folder(gch), "home")), os.listdir(run_folder(gch)))
    book_story(gb, gch)
    bin_dir = os.path.join(TMP, "sessions", "bin")
    os.makedirs(bin_dir)
    tool = os.path.join(bin_dir, "greet")
    tenv = env(PATH=bin_dir + os.pathsep + os.environ["PATH"])
    said, tch = [], workspace("<!-- code: id=greet -->\n```console\n$ greet\n```\n", name="greet.md")
    for word in ("hello", "goodbye"):
        write(tool, "#!/bin/sh\necho %s\n" % word)
        os.chmod(tool, 0o755)
        os.utime(tool, ns=(len(said) * 10 ** 9, len(said) * 10 ** 9))
        us_run(tch, environ=tenv)
        said.append(console_body(read(tch), "greet"))
    test("sessions: a changed command is run again, not taken from the cache", said == ["$ greet\nhello", "$ greet\ngoodbye"], said)


CHAPTER_TWO = """# Chapter 2: Two

## 2.1 D

<!-- code: id=again -->
```console
$ pwd
$ ls
$ cd proj
```

<!-- code: id=here-doc -->
```console
$ cat > notes.txt <<'EOF'
first line
$ not a command
EOF
$ printf '%s\\n' one \\
  two
$ wc -l notes.txt
```

<!-- code: id=typed stdin="Sam\\ny\\n" -->
```console
$ python3 -c 'n = input("Name? "); a = input("Sure [y,n]? "); print("hi", n, a)'
```
"""


def book_story(gb, gch):
    """A book is one story: chapter 2 starts with what chapter 1 left; inside a chapter each session starts
    where the last ended; here-documents and backslash lines; stdin typed at the terminal; a failed try
    shows what the command printed."""
    two = os.path.join(gb, "chapters", "02-two.md")
    write(two, CHAPTER_TWO)
    code, out, err = us_run(two)
    text = read(two)
    test("story: chapter 2 starts in HOME, with chapter 1's files there (its snapshot)",
         code == 0 and console_body(text, "again") == "$ pwd\n/home/you\n$ ls\nproj\n$ cd proj"
         and os.path.isfile(os.path.join(os.path.dirname(run_folder(gch)), "snapshot-1", "home", "proj", "a")),
         out + err + text)
    test("story: a here-document and a backslash line run as one command each, shown with no prompt",
         console_body(text, "here-doc") == "$ cat > notes.txt <<'EOF'\nfirst line\n$ not a command\nEOF\n"
         "$ printf '%s\\n' one \\\n  two\none\ntwo\n$ wc -l notes.txt\n2 notes.txt", text)
    test("story: stdin is typed at the terminal, each answer shown after its prompt",
         console_body(text, "typed").endswith("\nName? Sam\nSure [y,n]? y\nhi Sam y"), console_body(text, "typed"))
    code, out, err = us_run(two, "--check")
    test("story: a second run agrees byte for byte", code == 0, out + err)
    code, out, err = us_run(two, "--fresh")
    test("story: --fresh starts chapter 2 in an empty HOME",
         code == 1 and "'cd proj' exited with code 1" in out, out)
    write(two, text)
    write(gch, GIT_CHAPTER.replace("$ touch a b c", "$ touch extra a b c"))
    us_run(gch)
    code, out, err = us_run(two)
    test("story: chapter 1 changed, so chapter 2's sessions run again from its new snapshot",
         code == 0 and "skipped 0 unchanged" in out and
         os.path.isfile(os.path.join(os.path.dirname(run_folder(gch)), "snapshot-1", "home", "proj", "extra")),
         out + err)
    p = subprocess.run([sys.executable, SCRIPT, "try", gb, "2"], capture_output=True, text=True, env=env(),
                       input="<!-- code: id=seen -->\n```console\n$ ls a extra nosuch\n```\n")
    test("try: replays from chapter 1's snapshot and starts where the chapter's last session ended; a failed "
         "command shows what it printed",
         p.returncode == 1 and "$ ls a extra nosuch\nls: cannot access 'nosuch': No such file or directory\n"
         "a  extra\n" in p.stdout and "exited with code 2" in p.stdout, p.stdout + p.stderr)
    write(gch, GIT_CHAPTER)
    us_run(gch)


def rebuilt_story():
    """A missing snapshot of the chapter before (a reboot emptied the temp folder) is made again by a quiet
    full run of that chapter, back to chapter 1, without rewriting it; a broken one is said in one line."""
    sb = os.path.join(TMP, "rebuild", "shellbook")
    os.makedirs(os.path.join(sb, "chapters"))
    write(os.path.join(sb, "PLAN.md"), "# S\nfor: x\nrun: console\n\n### 1 One\n1.1 A\n\n### 2 Two\n2.1 B\n\n"
          "### 3 Three\n3.1 C\n")
    paths = [os.path.join(sb, "chapters", n) for n in ("01-one.md", "02-two.md", "03-three.md")]
    write(paths[0], "# Chapter 1: One\n\n## 1.1 A\n\n<!-- code: id=make -->\n```console\n$ mkdir proj\n"
          "$ echo hi > proj/a\n$ cat proj/a\n```\n")
    write(paths[1], "# Chapter 2: Two\n\n## 2.1 B\n\n<!-- code: id=more -->\n```console\n$ cat proj/a\n"
          "$ echo there > proj/b\n```\n")
    write(paths[2], "# Chapter 3: Three\n\n## 3.1 C\n\n<!-- code: id=look -->\n```console\n$ ls proj\n```\n")
    for p in paths:
        us_run(p)
    texts = [read(p) for p in paths]
    test("rebuild: a three-chapter story runs in order",
         console_body(texts[2], "look") == "$ ls proj\na  b", texts)
    write(paths[0], texts[0].replace("$ cat proj/a\nhi", "$ cat proj/a\nstale"))
    one = read(paths[0])
    folder = os.path.dirname(run_folder(paths[0]))

    def drop():
        for name in os.listdir(folder):
            if name.startswith("snapshot-"):
                shutil.rmtree(os.path.join(folder, name))
    drop()
    code, out, err = us_run(paths[2], "--check")
    test("rebuild: snapshots gone, chapter 3 rebuilds chapters 1 and 2 first and agrees with what is pasted",
         code == 0 and read(paths[2]) == texts[2] and err.count("rebuilt chapter") == 2 and
         "rebuilt chapter 1's end state (the saved one was missing)\n"
         "rebuilt chapter 2's end state (the saved one was missing)" in err, out + err)
    test("rebuild: the earlier chapters' files are not touched (stale pasted output stays stale)",
         read(paths[0]) == one and read(paths[1]) == texts[1])
    code, out, err = us_run(paths[2], "--check")
    test("rebuild: once rebuilt, nothing is rebuilt again", code == 0 and "rebuilt" not in err, out + err)
    drop()
    code, out, err = us_run(paths[1], "--fresh")
    test("rebuild: --fresh starts in an empty HOME and rebuilds nothing",
         code == 1 and "rebuilt" not in out + err and not os.path.exists(os.path.join(folder, "snapshot-1")),
         out + err)
    write(paths[0], one.replace("$ mkdir proj\n", "$ mkdir proj\n$ false\n"))
    drop()
    for k in (1, 2):
        code, out, err = us_run(paths[k])
        said = [x for x in (out + err).splitlines() if "starts from an empty home" in x]
        test(f"rebuild: chapter 1 broken, chapter {k + 1} says so in one line, then starts from an empty home",
             code == 1 and len(said) == 1 and "01-one.md cannot be run to its end" in said[0] and
             "run python3 scripts/us_run.py" in said[0] and "rebuilt" not in err and
             not os.path.exists(os.path.join(folder, "snapshot-1")), out + err)
    write(paths[0], one)


def first_round():
    """Fixes from the first validation round: an output fence after a blank line, a block that would hide
    a module, a program saved where the last session ended."""
    F = "```"
    path = workspace(f"""# Blank line

<!-- code: id=spaced -->
{F}python
print("real output")
{F}

{F}text
wrong output
{F}

<!-- code: id=para -->
{F}python
print("para")
{F}

Some words in between.

{F}text
the writer's own fence
{F}
""", "blank.md")
    code, out, err = us_run(path)
    text = read(path)
    test("an output fence after a blank line is the block's output: one output block, the real one",
         code == 0 and text.count("```text") == 3 and "wrong output" not in text
         and fence_after(text, "spaced") == "real output", (out, err, text))
    test("a paragraph between program and a text fence: that fence is not the output",
         "the writer's own fence" in text and fence_after(text, "para") == "para", text)

    path = workspace(f"""# Hiding

<!-- code: id=types -->
{F}python
print("hidden")
{F}

<!-- code: id=after-types -->
{F}python
import types
print(types.ModuleType.__name__)
{F}

<!-- code: id=json-file file=json.py -->
{F}python
print(1)
{F}
""", "hide.md")
    code, out, err = us_run(path)
    found = problems(out)
    text = read(path)
    test("a python block saved under a standard module's name is a problem, with a new name to use",
         code == 1 and "id=types would be saved as types.py, which hides Python's own module 'types'; "
         "rename it, for example id=types-demo" in found.get("types", "")
         and "file=json.py would be saved as json.py" in out, out)
    test("the other blocks still run", fence_after(text, "after-types") == "module"
         and fence_after(text, "types") is None, (out, err))
    test("the hiding file is never saved", not os.path.exists(os.path.join(run_folder(path), "types.py")))

    path = workspace(f"""# Shop

<!-- code: id=make-shop -->
{F}console
$ mkdir shop
$ cd shop
{F}

<!-- code: id=sales file=sales.py -->
{F}python
print(200 + 45)
{F}

<!-- code: id=run-sales -->
{F}console
$ python3 sales.py
{F}

<!-- code: id=broken file=broken.py exit=1 -->
{F}python
raise ValueError("no sales")
{F}
""", "shop.md")
    code, out, err = us_run(path)
    text = read(path)
    test("a program is saved and run where the last session ended",
         code == 0 and console_body(text, "run-sales") == "$ python3 sales.py\n245"
         and fence_after(text, "sales") == "245", (out, err, text))
    tb = fence_after(text, "broken") or ""
    test("a traceback from a program in a sub-folder names the reader's folder, never the run's",
         'File "/home/you/shop/broken.py", line 1' in tb and "understudy-run" not in tb and "/tmp" not in tb, tb)


def main():
    original = read(FIXTURE)
    path = workspace()
    code, out, err = us_run(path)
    first = read(path)
    found = problems(out)
    lines = out.strip().splitlines()

    # -- the first run
    test("exits 1 when there are problems", code == 1, code)
    test("one line per problem plus one summary line", len(lines) == len(PROBLEM_IDS) + 1, out)
    test("summary line counts", re.fullmatch(r"ran \d+  compiled 1  warns 1  errors 1  fragments 2  "
                                             r"skipped 0 unchanged  6 problems", lines[-1]), lines[-1])
    test("exactly the expected problems", sorted(found) == sorted(PROBLEM_IDS), sorted(found))
    test("run program output pasted", fence_after(first, "hello") == "Hello, reader!")
    test("hand-typed wrong output replaced", fence_after(first, "stale-output") == "42")
    test("stdin= is fed to the program", fence_after(first, "add-stdin") == "3 + 4 = 7")
    test("args= are passed, quotes respected",
         fence_after(first, "echo-args") == "argument 1: a\nargument 2: b\nargument 3: c d")
    test("file= header saved and included by a later block", fence_after(first, "use-header") == "twice 21 is 42")
    test("address flagged as changing between runs", "output changes between runs" in found.get("show-address", ""))
    test("warning in run mode is a problem", "warning: unused variable 'temp'" in found.get("unused-in-run", "")
         and "set mode=warns" in found.get("unused-in-run", ""), found.get("unused-in-run"))
    flines = first.splitlines()
    marker = next(k for k, x in enumerate(flines) if "id=unused-in-run" in x)
    warn_line = next(k + 1 for k in range(marker, len(flines)) if flines[k].strip() == "int temp;")
    test("problem line number is the line of the warning in the chapter as written",
         found.get("unused-in-run", "").startswith(f"fixture.md:{warn_line}  "), (warn_line, found.get("unused-in-run")))
    tl = int(re.match(r"fixture.md:(\d+)", found.get("too-long", "x:0")).group(1)) if "too-long" in found else 0
    test("problem line of a block points at its marker", "id=too-long" in flines[tl - 1], tl)
    _, ocheck, _ = us_run(path, "--check")
    test("--check reports the same line numbers", found["unused-in-run"] in ocheck, ocheck)
    warns = fence_after(first, "unused-lesson") or ""
    test("mode=warns pastes the compiler messages with bare file names",
         "unused-lesson.c:4:9: warning: unused variable 'temp'" in warns and "/" not in warns, warns)
    errors = fence_after(first, "not-assignable") or ""
    test("mode=error pastes the compiler messages", "not-assignable.c:4:7: error:" in errors, errors)
    test("mode=compile pastes nothing", fence_after(first, "builds-only") is None)
    test("endless loop times out", "timed out after 1s" in found.get("forever", ""))
    test("program waiting for input gets empty stdin and a hint",
         "timed out" in found.get("waits-for-input", "") and "stdin=" in found.get("waits-for-input", ""))
    test("over 60 lines is a problem", "prints 100 lines" in found.get("too-long", "")
         and "print less" in found.get("too-long", ""))
    test("problem blocks keep their fence untouched", fence_after(first, "too-long") is None)
    test("exit=3 accepted", fence_after(first, "exit-three") == "leaving with 3")
    test("python with stdin", fence_after(first, "py-sum") == "sum: 6")
    test("stderr=show puts standard error after standard output",
         fence_after(first, "py-stderr") == "to standard output\nto standard error")
    test("bash block runs", fence_after(first, "bash-loop") == "word: one\nword: two\nword: three")
    if HAS_NODE:
        test("javascript block runs", fence_after(first, "js-hello") == "1 4 9")
    test("console rewritten with real output; files from earlier programs stay",
         console_body(first, "look-around") == "$ cat notes.txt\nkept for later\n$ mkdir -p demo\n"
                                               "$ echo hello > demo/a.txt\n$ ls demo\na.txt",
         console_body(first, "look-around"))
    test("dangerous console command refused", "refused: 'rm -rf demo'" in found.get("clean-up-refused", ""))
    test("refused console block left as it was", console_body(first, "clean-up-refused") == "$ rm -rf demo")
    test("danger=\"why\" lets it run", console_body(first, "clean-up") ==
         "$ rm -r demo\n$ test -e demo || echo \"demo is gone\"\ndemo is gone")
    test("fragment and its following text fence untouched",
         "This fence belongs to the author and is never touched." in first)
    test("surgical: everything but owned output is byte-identical", strip_owned(original) == strip_owned(first))

    # -- second run: idempotent and cached
    code2, out2, _ = us_run(path)
    second = read(path)
    test("second run changes nothing", second == first)
    m = re.search(r"skipped (\d+) unchanged", out2)
    good = 16 if HAS_NODE else 15
    test("cache skips unchanged blocks", m and int(m.group(1)) == good, out2.strip().splitlines()[-1])
    code3, out3, _ = us_run(path, "--force")
    test("--force ignores the cache", "skipped 0 unchanged" in out3 and read(path) == first, out3[-80:])

    # -- varies
    write(path, first.replace("<!-- code: id=show-address -->", "<!-- code: id=show-address varies -->"))
    _, out4, _ = us_run(path)
    test("varies accepts the changing address", "show-address" not in problems(out4)
         and re.fullmatch(r"x is at 0x[0-9a-f]+", fence_after(read(path), "show-address") or ""),
         fence_after(read(path), "show-address"))

    # -- a clean chapter: --check
    clean = workspace(remove_blocks(original, PROBLEM_IDS))
    c1, o1, _ = us_run(clean)
    test("clean chapter: exit 0 and only the summary line", c1 == 0 and len(o1.strip().splitlines()) == 1, o1)
    ran = read(clean)
    c2, o2, _ = us_run(clean, "--check")
    test("--check passes after a run", c2 == 0, o2)
    c2f, o2f, _ = us_run(clean, "--check", "--force")
    test("--check --force passes after a run", c2f == 0, o2f)
    write(clean, ran.replace("3 + 4 = 7", "3 + 4 = 8"))
    edited = read(clean)
    c3, o3, _ = us_run(clean, "--check")
    test("--check fails after a hand edit of an output fence, naming the command", c3 == 1 and "id=add-stdin" in o3 and "run python3 scripts/us_run.py " in o3
         and "differs" in o3, o3)
    test("--check changes nothing", read(clean) == edited)
    us_run(clean)
    test("a run repairs the hand edit", read(clean) == ran)

    # -- --only and --list
    only = workspace()
    c4, o4, _ = us_run(only, "--only", "add-stdin")
    after = read(only)
    test("--only runs one block", c4 == 0 and o4.startswith("ran 1  compiled 0  warns 0  fragments 0")
         and fence_after(after, "add-stdin") == "3 + 4 = 7" and fence_after(after, "hello") is None, o4)
    c5, o5, _ = us_run(only, "--only", "use-header")
    test("--only still saves file= blocks it depends on", c5 == 0 and fence_after(read(only), "use-header"), o5)
    c6, o6, _ = us_run(only, "--list")
    rows = o6.strip().splitlines()
    test("--list: one line per block with id, mode, language, line",
         len(rows) == original.count("<!-- code:") and rows[0] == "hello  run  c  5"
         and "look-around  run  console  " in o6 and read(only) == read(only), rows[:2])

    # -- structural errors
    broken = original.replace("<!-- code: id=add-stdin", "<!-- code: id=hello", 1)
    broken = broken.replace("The end.", "<!-- code: id=lonely -->\n\nThe end.\n\n<!-- code: id=pascal -->\n"
                            "```pascal\nbegin end.\n```")
    bpath = workspace(broken)
    c7, o7, _ = us_run(bpath)
    test("duplicate id is an error", c7 == 1 and "id=hello  duplicate id" in o7, o7)
    test("marker with no fence is an error", "id=lonely  marker with no fenced block" in o7, o7)
    test("unknown language names the supported tags", "cannot run a 'pascal' fence; supported tags: c cpp" in o7, o7)
    test("structural errors change nothing", read(bpath) == broken)

    # -- line endings
    crlf = workspace(remove_blocks(original, PROBLEM_IDS).replace("\n", "\r\n"))
    c8, o8, _ = us_run(crlf)
    data = open(crlf, "rb").read()
    test("CRLF line endings preserved", c8 == 0 and b"\n" not in data.replace(b"\r\n", b"")
         and b"3 + 4 = 7\r\n" in data, o8)
    us_run(crlf)
    test("CRLF second run byte-identical", open(crlf, "rb").read() == data)
    noeol = workspace("<!-- code: id=last -->\n```python\nprint('x')\n```")
    us_run(noeol)
    once = read(noeol)
    us_run(noeol, "--force")
    test("file without a final newline stays without one", once == "<!-- code: id=last -->\n```python\n"
         "print('x')\n```\n```text\nx\n```" and read(noeol) == once, repr(once))

    # -- a missing tool
    nojs = workspace("<!-- code: id=js -->\n```javascript\nconsole.log(1)\n```\n"
                     "<!-- code: id=js2 -->\n```javascript\nconsole.log(2)\n```\n")
    path_no_node = os.pathsep.join(p for p in os.environ["PATH"].split(os.pathsep)
                                   if not os.path.exists(os.path.join(p, "node")))
    c9, o9, e9 = us_run(nojs, environ=env(PATH=path_no_node))
    test("missing tool reported once, plainly, not a problem",
         c9 == 0 and e9.count("not run: no node on this machine") == 1 and "not run 2" in o9, (o9, e9))
    c10, o10, _ = us_run(nojs, "--strict", environ=env(PATH=path_no_node))
    test("missing tool is a problem with --strict", c10 == 1 and "not run: no node" in o10, o10)

    # -- more languages, aliases and dependencies
    extras = workspace("""<!-- code: id=spaces -->
```c
#include <stdio.h>
int main(void) { for (int i = 1; i <= 3; i++) printf("%d ", i); printf("\\n"); return 0; }
```

<!-- code: id=old-name mode=compile-error -->
```c
int main(void) { return x; }
```

<!-- code: id=greet file=greet.h mode=fragment -->
```c
#define GREETING "hi"
```

<!-- code: id=uses-greet -->
```cpp
#include <iostream>
#include "greet.h"
int main() { std::cout << GREETING << std::endl; return 0; }
```

<!-- code: id=Hello -->
```java
public class Hello {
    public static void main(String[] args) { System.out.println("from java"); }
}
```

<!-- code: id=fails -->
```console
$ echo before
$ false
$ echo after
```
""")
    c12, o12, _ = us_run(extras)
    text = read(extras)
    test("trailing spaces cut from output lines", fence_after(text, "spaces") == "1 2 3", fence_after(text, "spaces"))
    test("mode=compile-error is read as mode=error", "old-name.c:1:25: error: 'x' undeclared" in
         (fence_after(text, "old-name") or ""), fence_after(text, "old-name"))
    test("c++ block includes a file= header", fence_after(text, "uses-greet") == "hi", o12)
    if shutil.which("javac"):
        test("java block runs", fence_after(text, "Hello") == "from java", o12)
    test("a failing console command is a problem at its line",
         re.search(r"fixture.md:(\d+)  id=fails  'false' exited with code 1", o12) and
         text.splitlines()[int(re.search(r"fixture.md:(\d+)  id=fails", o12).group(1)) - 1] == "$ false", o12)
    write(extras, text.replace('"hi"', '"hello"'))
    _, o13, _ = us_run(extras)
    test("changing a file= block reruns the blocks after it", fence_after(read(extras), "uses-greet") == "hello"
         and "skipped 2 unchanged" in o13, o13)

    # -- answer: the output goes in the hidden answer that follows
    answer_text = """<!-- code: id=q1 answer -->
```python
print(6 * 7)
```

1. What does it print?

<details>
<summary>Answer</summary>

It prints the number.

</details>

<!-- code: id=q2 answer -->
```python
print("tight")
```
<details>
<summary>Answer</summary>
Tight.
</details>
"""
    ans = workspace(answer_text)
    c14, o14, _ = us_run(ans)
    a1 = read(ans)
    test("answer: output is the first text fence in the next <details>, nothing under the program",
         c14 == 0 and "<summary>Answer</summary>\n\n```text\n42\n```\n\nIt prints the number." in a1
         and fence_after(a1, "q1") is None, a1)
    test("answer: a blank line is added after </summary> when there is none",
         "<summary>Answer</summary>\n\n```text\ntight\n```\n\nTight.\n</details>" in a1, a1)
    us_run(ans, "--force")
    c15, o15, _ = us_run(ans, "--check")
    test("answer: idempotent, and --check passes", read(ans) == a1 and c15 == 0, o15)
    write(ans, a1.replace("\n42\n", "\n41\n"))
    c16, o16, _ = us_run(ans, "--check")
    test("answer: --check sees a hand edit inside the answer", c16 == 1 and "id=q1  pasted output differs" in o16, o16)
    us_run(ans)
    test("answer: a run repairs it", read(ans) == a1)
    inside = workspace("1. Print six.\n\n<details>\n<summary>Answer</summary>\n\n<!-- code: id=in1 answer -->\n"
                       "```python\nprint(6)\n```\n\n</details>\n\n2. Print seven.\n\n<details>\n"
                       "<summary>Answer</summary>\n\n<!-- code: id=in2 answer -->\n```python\nprint(7)\n```\n\n"
                       "</details>\n")
    c18, o18, _ = us_run(inside)
    a2 = read(inside)
    test("answer on a program already inside a hidden answer: its output stays under it, not in the next answer",
         c18 == 0 and fence_after(a2, "in1") == "6" and fence_after(a2, "in2") == "7"
         and a2.index("\n6\n") < a2.index("2. Print seven"), o18 + a2)
    lonely = workspace("<!-- code: id=lost answer -->\n```python\nprint(1)\n```\n\n## 1.2 Next\n\n"
                       "<details>\n<summary>Answer</summary>\n\nx\n</details>\n")
    c17, o17, _ = us_run(lonely)
    test("answer with no <details> in its section is an error", c17 == 1 and "id=lost  answer: no <details>" in o17, o17)

    # -- warns pastes messages, a blank line, then the output; C build flags
    wtext = """<!-- code: id=warn-runs mode=warns -->
```c
#include <stdio.h>
int main(void) { int unused; printf("still runs\\n"); return 0; }
```

<!-- code: id=warn-crashes mode=warns -->
```c
int main(void) { int unused; return 3; }
```

<!-- code: id=implicit mode=error -->
```c
int main(void) { shout(); return 0; }
```

<!-- code: id=implicit-run -->
```c
int main(void) { int *p = 5; return 0; }
```
"""
    wpath = workspace(wtext)
    c18, o18, _ = us_run(wpath)
    w1 = read(wpath)
    wr = fence_after(w1, "warn-runs") or ""
    test("mode=warns: messages, a blank line, then the program's output",
         "warning: unused variable 'unused'" in wr and wr.endswith("\n\nstill runs"), wr)
    wc = fence_after(w1, "warn-crashes") or ""
    test("mode=warns: a program that does not run cleanly shows only the messages",
         "warning: unused variable" in wc and not wc.endswith("\n") and "warn-crashes" not in problems(o18), (wc, o18))
    test("C: implicit declaration is an error (as in gcc 14)",
         "error: implicit declaration of function 'shout'" in (fence_after(w1, "implicit") or ""), fence_after(w1, "implicit"))
    test("C: int to pointer is an error, not a warning", "error:" in problems(o18).get("implicit-run", "")
         and "int-conversion" not in problems(o18).get("implicit-run", "x"), o18)

    # -- try: a section's programs, run before the section is written
    tbook = os.path.dirname(workspace("x"))
    os.makedirs(os.path.join(tbook, "book", "chapters"))
    tb = os.path.join(tbook, "book")
    write(os.path.join(tb, "PLAN.md"), "# T\nfor: x\nrun: c\n\n### 1 One\n1.1 A\n1.2 B\n")
    write(os.path.join(tb, "chapters", "01-one.md"), "# Chapter 1: One\n\n## 1.1 A\n\n"
          "<!-- code: id=twice-h file=twice.h mode=fragment -->\n```c\n#define TWICE(x) (2 * (x))\n```\n")
    tenv = env(UNDERSTUDY_PRIVATE=os.path.join(tbook, "private"))
    tried = """Two programs:

<!-- code: id=t-one stdin="5\\n" -->
```c
#include <stdio.h>
#include "twice.h"
int main(void) { int n; scanf("%d", &n); printf("%d\\n", TWICE(n)); return 0; }
```

<!-- code: id=t-two mode=warns -->
```python
for i in range(45):
    print(i)
```
"""
    def try_(text, *extra):
        p = subprocess.run([sys.executable, SCRIPT, "try", tb, "1"] + list(extra), input=text, capture_output=True,
                           text=True, env=tenv)
        return p.returncode, p.stdout, p.stderr
    c19, o19, e19 = try_(tried)
    RESULTS_TRY.append(o19)
    lines19 = o19.splitlines()
    test("try: a header per program, then what it printed; file= blocks of the chapter are there",
         c19 == 1 and lines19[:2] == ["== id=t-one (run)", "10"] and "== id=t-two (warns)" in lines19, o19)
    test("try: problems under their program's header, with input line numbers",
         re.match(r"input:10  id=t-two  builds without warnings", lines19[lines19.index("== id=t-two (warns)") + 1]), o19)
    store = tried_folder(os.path.join(tb, "chapters", "01-one.md"))
    one = read(os.path.join(store, "t-one.md")) if os.path.exists(os.path.join(store, "t-one.md")) else ""
    test("try: the marker line and fence are kept in tried/ID.md", one.startswith(
        '<!-- code: id=t-one stdin="5\\n" -->\n```c\n#include <stdio.h>') and one.endswith("}\n```\n"), one)
    c20, o20, _ = try_(tried.replace("mode=warns", ""))
    lines20 = o20.splitlines()
    test("try: output capped at 40 lines", c20 == 0 and lines20[-2] == "… 5 more lines" and len(lines20) == 2 + 1 + 40 + 1 + 1,
         o20)
    test("try: one summary line at the end", lines20[-1] == "ran 1  compiled 0  warns 0  fragments 0  skipped 1 unchanged  0 problems",
         lines20[-1])
    try_("<!-- code: id=t-one -->\n```python\nprint('again')\n```\n")
    test("try: trying an id again replaces it", "print('again')" in read(os.path.join(store, "t-one.md")))
    c21, o21, _ = try_("no programs here\n")
    test("try: input with no program is a problem", c21 == 1 and "no program" in o21, o21)
    test("try: the chapter file is never changed", "t-one" not in read(os.path.join(tb, "chapters", "01-one.md")))

    # -- reproducible runs: a clean start, after=, dependencies in the cache key
    log_writer = ("<!-- code: id=add-line -->\n```python\nopen('log.txt', 'a').write('entry\\n')\n"
                  "print(len(open('log.txt').read().splitlines()), 'lines')\n```\n")
    log_reader = ("<!-- code: id=show-log after=add-line -->\n```python\nprint(open('log.txt').read(), end='')\n```\n")
    outs = []
    for k in range(3):
        _, o, _ = try_(log_writer.replace("lines')", "lines')" + " " * k))   # changed, so not from the cache
        outs.append(o)
    test("try: the same output however often it is tried (data files removed first, second run undone)",
         outs[0] == outs[1] == outs[2] and outs[0].startswith("== id=add-line (run)\n1 lines\nran 1  "), outs)
    c22, o22, _ = try_(log_reader)
    test("try: after= runs the named tried program first, silently",
         c22 == 0 and o22.splitlines()[:2] == ["== id=show-log (run)", "entry"] and "add-line" not in o22.split("\n", 1)[1],
         o22)
    c23, o23, _ = try_("<!-- code: id=lost-dep after=nowhere -->\n```python\nprint(1)\n```\n")
    test("try: after= naming no program above is a problem", c23 == 1 and "after=nowhere names no program" in o23, o23)
    chain = workspace(log_writer + "\n" + log_reader + "\n<!-- code: id=look -->\n```console\n$ cat log.txt\n```\n")
    us_run(chain)
    once = read(chain)
    write(chain, once.replace("end='')", "end='')  # changed"))
    c24, o24, _ = us_run(chain)
    test("full run: a changed block finds the files of cached blocks above it, made once",
         c24 == 0 and fence_after(read(chain), "show-log") == "entry" and console_body(read(chain), "look").endswith(
             "$ cat log.txt\nentry"), (o24, read(chain)))
    write(chain, read(chain).replace("'entry\\n'", "'changed\\n'"))
    us_run(chain)
    test("full run: a console block reruns when a program above it changes",
         console_body(read(chain), "look") == "$ cat log.txt\nchanged", read(chain))
    raw = workspace("<!-- code: id=ctl -->\n```python\nprint('a\\x01b')\n```\n\n<!-- code: id=bad-utf8 -->\n"
                    "```python\nimport sys; sys.stdout.buffer.write(b'\\xff\\n')\n```\n\n<!-- code: id=con -->\n"
                    "```console\n$ printf 'x\\033[0m\\n'\n```\n")
    c25, o25, _ = us_run(raw)
    found25 = problems(o25)
    msg = "output has unprintable bytes: show them with `od -c` or `xxd` instead of printing them"
    test("control bytes or invalid UTF-8 are never pasted: one problem line each",
         c25 == 1 and all(msg in found25.get(b, "") for b in ("ctl", "bad-utf8"))
         and fence_after(read(raw), "ctl") is None, o25)
    test("console: colour codes are dropped, as the reader's screen shows no codes",
         "con" not in found25 and console_body(read(raw), "con") == "$ printf 'x\\033[0m\\n'\nx", read(raw))

    # -- terminal sessions: one story a chapter, the same every run, as the reader's screen shows it
    if shutil.which("git"):
        sessions()

    rebuilt_story()

    # -- mode=crash
    crash = workspace("<!-- code: id=boom mode=crash -->\n```c\n#include <stdio.h>\nint main(void) {\n"
                      "    int *p = NULL;\n    printf(\"before\\n\");\n    return *p;\n}\n```\n\n"
                      "<!-- code: id=no-boom mode=crash -->\n```c\nint main(void) { return 0; }\n```\n")
    c26, o26, _ = us_run(crash)
    test("mode=crash: output so far, then one plain line naming the signal",
         fence_after(read(crash), "boom") == "before\nSegmentation fault", fence_after(read(crash), "boom"))
    test("mode=crash: a program that does not crash is a problem",
         c26 == 1 and "not killed by a signal" in problems(o26).get("no-boom", ""), o26)
    # -- as on the reader's terminal: strict builds, real order, sanitizers, shell lines
    term = workspace(
        "<!-- code: id=order -->\n```c\n#include <stdio.h>\nint main(void) {\n    printf(\"first\\n\");\n"
        "    fprintf(stderr, \"second\\n\");\n    printf(\"third\\n\");\n    return 0;\n}\n```\n\n"
        "<!-- code: id=hidden stderr=hide -->\n```c\n#include <stdio.h>\nint main(void) {\n    printf(\"out\\n\");\n"
        "    fprintf(stderr, \"err\\n\");\n    return 0;\n}\n```\n\n"
        "<!-- code: id=pedantic -->\n```c\nint main(void) {\n    int a[0];\n    (void)a;\n    return 0;\n}\n```\n\n"
        "<!-- code: id=posix -->\n```c\n#include <stdio.h>\n#include <unistd.h>\nint main(void) {\n"
        "    printf(\"%d\\n\", isatty(1));\n    return 0;\n}\n```\n\n"
        "<!-- code: id=overflow -->\n```c\n#include <stdio.h>\nint main(void) {\n    int a[4] = {0};\n"
        "    volatile int i = 4;\n    a[i] = 1;\n    printf(\"%d\\n\", a[0]);\n    return 0;\n}\n```\n\n"
        "<!-- code: id=overflow-shown nosan -->\n```c\n#include <stdio.h>\nint main(void) {\n    int a[4] = {0};\n"
        "    volatile int i = 4;\n    a[i] = 1;\n    printf(\"%d\\n\", a[0]);\n    return 0;\n}\n```\n\n"
        "<!-- code: id=cpp-ok -->\n```cpp\n#include <iostream>\nint main() {\n    std::cout << \"c++\\n\";\n}\n```\n\n"
        "<!-- code: id=segv mode=compile -->\n```c\n#include <stdio.h>\nint main(void) {\n    int *p = NULL;\n"
        "    return *p;\n}\n```\n\n<!-- code: id=segv-shell exit=139 -->\n```console\n$ nosuchcmd || true\n$ ./segv\n```\n")
    c27, o27, _ = us_run(term)
    t27, f27 = read(term), problems(o27)
    test("standard error appears where it really happened", fence_after(t27, "order") == "first\nsecond\nthird",
         fence_after(t27, "order"))
    test("stderr=hide drops the error stream", fence_after(t27, "hidden") == "out", fence_after(t27, "hidden"))
    test("C builds with -std=c17 -Wextra -pedantic", "ISO C forbids zero-size array" in f27.get("pedantic", ""), o27)
    test("a POSIX header builds cleanly, and output is a terminal", fence_after(t27, "posix") == "1", o27)
    sanitized = f27.get("overflow", "")
    test("a sanitizer report is a problem at the faulting line",
         "out of bounds for type 'int [4]', in line 5 `a[i] = 1;`: the program" in sanitized and
         "memory or undefined-behaviour fault: fix it" in sanitized and "0x" not in sanitized and
         fence_after(t27, "overflow") is None, o27)
    test("nosan: a fault shown on purpose is not checked", "overflow-shown" not in f27 and
         fence_after(t27, "overflow-shown") == "0", o27)
    test("C++ builds strictly and runs", fence_after(t27, "cpp-ok") == "c++", o27)
    test("console: crash and shell errors as an interactive shell prints them",
         console_body(t27, "segv-shell") == "$ nosuchcmd || true\nbash: nosuchcmd: command not found\n"
                                            "$ ./segv\nSegmentation fault", console_body(t27, "segv-shell"))
    test("only the expected problems", sorted(f27) == ["overflow", "pedantic"], o27)
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import contextlib
    import io
    import us_run as ur
    saved_flags, ur.SAN_FLAGS = ur.SAN_FLAGS, ["-fsanitize=no-such-sanitizer"]
    ur.sanitizers.cache_clear()
    with contextlib.redirect_stderr(io.StringIO()) as said:
        missing = (ur.sanitizers(), ur.sanitizers())
    ur.SAN_FLAGS = saved_flags
    ur.sanitizers.cache_clear()
    test("no sanitizer libraries: skipped, said once", missing == (False, False) and
         said.getvalue().count("sanitizers not available here") == 1, said.getvalue())
    p = subprocess.run([sys.executable, SCRIPT, "--help"], capture_output=True, text=True)
    test("--help documents exit=, args= and try", all(x in p.stdout for x in ('exit=1 ', 'args="', "\n`try` runs",
                                                                             "after=")), p.stdout)

    # -- never as root
    if os.geteuid() == 0:
        who = workspace("<!-- code: id=who -->\n```bash\nid -u\n```\n")
        us_run(who)
        uid = fence_after(read(who), "who")
        test("started as root, programs run as the ordinary user", USER is None or uid not in (None, "0"), uid)
        _, _, e11 = us_run(who, "--force", environ=env(US_RUN_USER=None, SUDO_USER=None))
        if USER == "ubuntu":
            test("root with no US_RUN_USER or SUDO_USER falls back to ubuntu, silently",
                 e11.strip() == "" and fence_after(read(who), "who") == str(pwd.getpwnam("ubuntu").pw_uid), e11)
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import us_run as ur
        saved = (ur.FALLBACK_USER, ur.load_config, dict(os.environ))
        try:
            os.environ.pop("SUDO_USER", None)
            os.environ.pop("US_RUN_USER", None)
            ur.FALLBACK_USER = "no-such-user-here"
            pw, warning = ur.ordinary_user()
            test("root with no ordinary user at all: one-line warning", pw is None and "\n" not in warning
                 and "running as root" in warning, warning)
            if USER:
                ur.load_config = lambda: dict(saved[1](), **{"run.user": USER})
                pw, warning = ur.ordinary_user()
                test("run.user in understudy.yaml is used", pw and pw.pw_name == USER and not warning, warning)
                os.environ["US_RUN_USER"] = "no-such-user-here"
                pw, warning = ur.ordinary_user()
                test("a wrong US_RUN_USER is named, and the next user in line is used",
                     pw and pw.pw_name == USER and "US_RUN_USER=no-such-user-here is not a user here" in warning,
                     warning)
                os.environ["SUDO_USER"] = USER
                os.environ["US_RUN_USER"] = "root"
                pw, warning = ur.ordinary_user()
                test("SUDO_USER comes after US_RUN_USER", pw and pw.pw_name == USER, warning)
        finally:
            ur.FALLBACK_USER, ur.load_config = saved[0], saved[1]
            os.environ.clear()
            os.environ.update(saved[2])

    first_round()
    shutil.rmtree(TMP, ignore_errors=True)
    passed = sum(RESULTS)
    failed = len(RESULTS) - passed
    print(f"{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
