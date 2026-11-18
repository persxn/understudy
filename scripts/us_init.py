#!/usr/bin/env python3
"""First-run setup: the book root (its own git repository) and the private folder.

    python3 scripts/us_init.py

Creates <book root>/ with .nojekyll and the reading page, makes it a git repository, and writes <private>/now.md
and <private>/machine.md (filled in by us_doctor.py).
Books are added later, one folder per subject (book/<slug>/PLAN.md). Safe to run again: nothing that exists is overwritten.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import us_bookfmt as bf  # noqa: E402
from us_lib import ROOT  # noqa: E402
from us_doctor import EMPTY  # noqa: E402


def put(path, text):
    """Create a file unless it exists."""
    if not os.path.exists(path):
        bf.write_text(path, text)
        print("created", os.path.relpath(path, ROOT))


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__.strip())
        return 0
    root, private = bf.book_root(), bf.private_dir()
    os.makedirs(root, exist_ok=True)
    put(os.path.join(root, ".nojekyll"), "")
    put(os.path.join(private, "now.md"), "First session. No goal recorded yet.\n")
    put(os.path.join(private, "machine.md"), EMPTY)
    if not os.path.isdir(os.path.join(root, ".git")):
        try:
            subprocess.run(["git", "init", "-q", root], check=True)
            print("%s is now its own git repository" % os.path.relpath(root, ROOT))
        except (OSError, subprocess.CalledProcessError):
            print("git not available: %s created without a repository" % os.path.relpath(root, ROOT))
    if not os.path.exists(os.path.join(root, "index.html")):
        res = bf.run_helper("us_reader.py", [])
        if res is None or res[0] != 0 or not os.path.exists(os.path.join(root, "index.html")):
            print("reading page not copied (run python3 scripts/us_reader.py later)")
        else:
            print("created %s (the reading page; never open or edit it)" % os.path.relpath(os.path.join(root, "index.html"), ROOT))
    print("done. %s/ is never pushed; %s/ is yours to publish." % (os.path.relpath(private, ROOT), os.path.relpath(root, ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
