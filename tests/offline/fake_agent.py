"""A stand-in for a headless agent, for tests/offline/run.py.

    fake_agent.py "Use the us-writer agent for book BOOK chapter N."

Writer: appends the next unwritten section of chapter N from $FAKE_SOURCE/N.M.md through us_section.py.
Reviewer: marks chapter N reviewed. FAKE_MODE=noop does nothing; FAKE_SLEEP=S waits S seconds first.
"""
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import us_bookfmt as bf  # noqa: E402
import us_plan  # noqa: E402

role, book, n = re.match(r"Use the us-(\w+) agent for book (.+) chapter (\d+)\.", sys.argv[1]).groups()
time.sleep(float(os.environ.get("FAKE_SLEEP", 0)))
if os.environ.get("FAKE_MODE") == "noop":
    sys.exit(0)
book, n = bf.resolve_book(book), int(n)
script = os.path.join(ROOT, "scripts", "us_section.py" if role == "writer" else "us_plan.py")
if role == "writer":
    done = us_plan.written_sections(book, bf.load_plan(book).chapter(n))[0]
    sec = next(s for s in bf.load_plan(book).chapter(n).sections if s.number not in done)
    args = ["append", book, str(n), "--file", os.path.join(os.environ["FAKE_SOURCE"], sec.number + ".md")]
else:
    args = ["mark", book, str(n), "reviewed"]
sys.exit(subprocess.run([sys.executable, script] + args, capture_output=True).returncode)
