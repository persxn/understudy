#!/usr/bin/env python3
"""Real-world check of scripts/us_run.py on chapters of a finished book.

    python3 tests/run/realworld.py CHAPTER.md [CHAPTER.md ...] [--diffs]

Copies each chapter to a temp folder, compares every block's pasted output with a fresh run
on this machine (one line per block), then runs the script for real on the copy and checks
that only output fences changed. Prints how long a chapter takes cold and cached.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, HERE)
import us_run  # noqa: E402
from run import strip_owned  # noqa: E402


def answer_fence(lines, start):
    """The ```text fence inside a <details> that follows the block, where the book hides an answer."""
    i = start
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines) or not lines[i].startswith("<details>"):
        return None
    while i < len(lines) and not lines[i].startswith("</details>"):
        if lines[i].startswith("```text"):
            j = i + 1
            while not lines[j].startswith("```"):
                j += 1
            return "".join(lines[i:j + 1])
        i += 1
    return None


def compare(path):
    """[(block, status, old, new, problem)] for every block of the chapter, from a fresh run."""
    opts = argparse.Namespace(only=None, check=True, force=True, list=False, strict=False)
    ch = us_run.Chapter(path, opts)
    ch.go()
    by_id = {}
    for line in ch.problems:
        m = re.search(r"id=(\S+)\s+(.*)", line)
        if m:
            by_id.setdefault(m.group(1), m.group(2))
    rows = []
    for b in ch.blocks:
        old = "".join(ch.lines[b.out_start:b.out_end])
        new = "".join(ch.new_out.get(b.id, []))
        if b.mode == "fragment":
            status = "fragment"
        elif b.id in by_id:
            status = "problem"
        elif b.id not in ch.new_out:
            status = "not run"
        else:
            status = "same" if old.replace("\r\n", "\n") == new.replace("\r\n", "\n") else "differs"
            answer = answer_fence(ch.lines, b.out_end) if not old and new else None
            if answer is not None:
                old, status = answer, ("same" if answer == new else "differs") + "(answer)"
        rows.append((b, status, old, new, by_id.get(b.id, "")))
    return ch, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chapters", nargs="+")
    ap.add_argument("--diffs", action="store_true", help="print old and new output of differing blocks")
    args = ap.parse_args()
    for src in args.chapters:
        d = tempfile.mkdtemp(prefix="us-run-real-")
        os.chmod(d, 0o755)
        path = os.path.join(d, os.path.basename(src))
        shutil.copy(src, path)
        ch, rows = compare(path)
        print(f"== {ch.name}")
        for b, status, old, new, prob in rows:
            print(f"{b.marker:5d}  {b.id:28s} {b.mode:9s} {status:8s} {prob}")
            if args.diffs and status in ("differs", "problem"):
                print("   book:\n" + "".join("     | " + x for x in old.splitlines(True)))
                print("   here:\n" + "".join("     | " + x for x in new.splitlines(True)))
        counts = {}
        for row in rows:
            counts[row[1]] = counts.get(row[1], 0) + 1
        print("   " + "  ".join(f"{k} {v}" for k, v in sorted(counts.items())))
        shutil.rmtree(os.path.join(d, ".us-run"), ignore_errors=True)
        before = open(path, encoding="utf-8", newline="").read()
        script = os.path.join(ROOT, "scripts", "us_run.py")
        t0 = time.time()
        subprocess.run([sys.executable, script, path], capture_output=True)
        cold = time.time() - t0
        after = open(path, encoding="utf-8", newline="").read()
        t0 = time.time()
        subprocess.run([sys.executable, script, path], capture_output=True)
        cached = time.time() - t0
        again = open(path, encoding="utf-8", newline="").read()
        print(f"   surgical: {strip_owned(before) == strip_owned(after)}   idempotent: {after == again}   "
              f"cold {cold:.1f}s  cached {cached:.1f}s")
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    main()
