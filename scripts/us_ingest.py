#!/usr/bin/env python3
"""Copy the text of the learner's own lectures, slides or notes into private/sources/, page by page.

    python3 scripts/us_ingest.py FILE_OR_FOLDER [NAME]

Reads .pdf (needs the `pdftotext` program or the `pypdf` module), .pptx (no extra software),
.md and .txt. Writes private/sources/NAME/pages.md, with a "## <file> p.<N>" heading before every
page or slide, and index.md: one line per page with its first line and word count, and a mark on
pages that hold almost no text (maybe a picture or a scan: look at the page itself). No model is used and
nothing is summarised: the pages hold the source's own words, for the writer to read on demand.
Everything stays in private/, which is never pushed.
"""
import os
import re
import shutil
import subprocess
import sys
import zipfile
from xml.etree import ElementTree

from us_lib import ROOT, load_config


def pdf_pages(path):
    if shutil.which("pdftotext"):
        text = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True).stdout
        return text.split("\f")[:-1] or [text]
    try:
        import pypdf
    except ImportError:
        sys.exit(f"cannot read {path}: install poppler (for pdftotext) or `pip install pypdf`")
    return [(page.extract_text() or "") for page in pypdf.PdfReader(path).pages]


def pptx_pages(path):
    ns = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
    pages = []
    with zipfile.ZipFile(path) as z:
        slides = sorted((n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                        key=lambda n: int(re.findall(r"\d+", n)[-1]))
        for name in slides:
            root = ElementTree.fromstring(z.read(name))
            lines = ["".join(t.text or "" for t in p.iter(ns + "t")) for p in root.iter(ns + "p")]
            notes = name.replace("slides/slide", "notesSlides/notesSlide")
            if notes in z.namelist():
                said = ["".join(t.text or "" for t in p.iter(ns + "t")) for p in ElementTree.fromstring(z.read(notes)).iter(ns + "p")]
                said = [s for s in said if s.strip() and not s.strip().isdigit()]
                if said:
                    lines += ["", "Speaker notes:"] + said
            pages.append("\n".join(l for l in lines if l.strip() or l == ""))
    return pages


def pages_of(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return pdf_pages(path)
    if ext == ".pptx":
        return pptx_pages(path)
    if ext in (".md", ".txt"):
        return [open(path, encoding="utf-8", errors="replace").read()]
    return None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args or "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return
    source = os.path.abspath(args[0])
    files = [source] if os.path.isfile(source) else sorted(
        os.path.join(d, f) for d, _, fs in os.walk(source) for f in fs)
    name = args[1] if len(args) > 1 else re.sub(r"[^a-z0-9]+", "-", os.path.splitext(os.path.basename(source))[0].lower()).strip("-")
    out = os.path.join(ROOT, load_config()["private"], "sources", name)
    os.makedirs(out, exist_ok=True)
    body, index, skipped, total = [], [f"# {name}: what is on each page", "",
                                        "Read `pages.md` only at the pages you need. `[little text]` pages may be a picture or a scan: look at the original.", ""], [], 0
    for path in files:
        pages = pages_of(path)
        label = os.path.relpath(path, os.path.dirname(source) if os.path.isfile(source) else source)
        if pages is None:
            skipped.append(label)
            continue
        for n, text in enumerate(pages, 1):
            text = re.sub(r"\n{3,}", "\n\n", text.replace("\r", "")).strip()
            words = len(text.split())
            first = next((l.strip() for l in text.splitlines() if l.strip()), "")
            total += words
            body.append(f"## {label} p.{n}\n\n{text}\n")
            index.append(f"- {label} p.{n}: {first[:70]} ({words} words){' [little text]' if words < 6 else ''}")
    if skipped:
        index += ["", "Not read (kind of file not supported): " + ", ".join(skipped)]
    open(os.path.join(out, "pages.md"), "w", encoding="utf-8").write("\n".join(body))
    open(os.path.join(out, "index.md"), "w", encoding="utf-8").write("\n".join(index) + "\n")
    print(f"{len(body)} pages, {total} words -> {os.path.relpath(out, ROOT)}/ (index.md, pages.md)"
          + (f"; {len(skipped)} file(s) not read" if skipped else ""))


if __name__ == "__main__":
    main()
