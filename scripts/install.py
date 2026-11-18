#!/usr/bin/env python3
"""Make the same skills and system prompt visible to Codex and Gemini CLI.

    python3 scripts/install.py

Claude Code needs nothing: it reads .claude/skills/ and CLAUDE.md as they are.
This script (1) makes sure CLAUDE.md and GEMINI.md each hold the one-line import of
AGENTS.md, so all three harnesses read the same prompt with no second copy, and
(2) exposes .claude/skills/ as .agents/skills/, the folder Codex and Gemini CLI both
read. It links where the system allows and copies otherwise (pass --copy to force a copy).
"""
import os
import shutil
import sys

from us_lib import ROOT


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return
    for name, line in (("CLAUDE.md", "@AGENTS.md"), ("GEMINI.md", "@./AGENTS.md")):
        path = os.path.join(ROOT, name)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(line + "\n")
            print("wrote", name)
    source = os.path.join(ROOT, ".claude", "skills")
    agents = os.path.join(ROOT, ".agents")
    target = os.path.join(agents, "skills")
    os.makedirs(agents, exist_ok=True)
    if os.path.islink(target):
        os.unlink(target)
    elif os.path.isdir(target):
        shutil.rmtree(target)
    try:
        if "--copy" in sys.argv:
            raise OSError("copy requested")
        os.symlink(os.path.join("..", ".claude", "skills"), target, target_is_directory=True)
        print("linked .agents/skills -> .claude/skills")
    except OSError:
        shutil.copytree(source, target)
        print("copied .claude/skills to .agents/skills (links not available; rerun after editing skills)")


if __name__ == "__main__":
    main()
