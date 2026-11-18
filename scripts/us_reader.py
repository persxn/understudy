#!/usr/bin/env python3
"""Put the reading page into the book, and optionally show it.

    python3 scripts/us_reader.py            copy reader/index.html to book/index.html (and refresh the index)
    python3 scripts/us_reader.py --serve    the same, then serve the books at http://localhost:8765 until Ctrl+C

The page is one file with no build step. It reads manifest.json, search.json and the chapters of every
book beside it, changes nothing, needs no internet, and works the same when the folder is published
with GitHub Pages. Opened by double-click it cannot read the files beside it, and says to run --serve.
Never open or edit book/index.html by hand or with a model: it is about 400 KB of bundled code.
"""
import functools
import http.server
import os
import shutil
import subprocess
import sys

from us_lib import ROOT, book_dir


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return
    book = book_dir(None)
    source = os.path.join(ROOT, "reader", "index.html")
    if not os.path.exists(source):
        sys.exit("reader/index.html is missing from the control folder")
    os.makedirs(book, exist_ok=True)
    shutil.copy(source, os.path.join(book, "index.html"))
    open(os.path.join(book, ".nojekyll"), "a").close()          # GitHub Pages: serve every file as it is
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "us_index.py")], check=True)
    print(f"reader copied to {os.path.relpath(os.path.join(book, 'index.html'), ROOT)}")
    if "--serve" in sys.argv:
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=book)
        http.server.SimpleHTTPRequestHandler.log_message = lambda *a: None
        server = None
        for port in range(8765, 8775):                           # the next free port if 8765 is taken
            try:
                server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
                break
            except OSError:
                continue
        if server is None:
            sys.exit("ports 8765 to 8774 are all in use; stop another reader and try again")
        print(f"open http://localhost:{port}  (Ctrl+C to stop)")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
