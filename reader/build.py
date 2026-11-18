#!/usr/bin/env python3
"""Build reader/index.html from src/ and vendor/. Maintainers only; learners never run this.

    python3 reader/build.py

Everything is inlined (styles, scripts, the Markdown renderer, the highlighter), so the result is
one file with no network requests of its own. Fonts are the reader's own system fonts. Comments and
indentation are stripped from our own sources to keep the file small; the vendored libraries are
already minified.
"""
import os
import re

here = os.path.dirname(os.path.abspath(__file__))
SOURCES = ["core.js", "map.js", "read.js", "app.js"]
VERSION = "2"


def read(*parts):
    with open(os.path.join(here, *parts), encoding="utf-8") as f:
        return f.read()


def squeeze_css(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"\s+", " ", text)
    return re.sub(r" ?([{};,>]) ?", r"\1", text).replace(";}", "}").strip()


def squeeze_js(text):
    """Drop whole-line comments, blank lines and indentation. Nothing inside a line is touched."""
    out, block = [], False
    for line in text.split("\n"):
        t = line.strip()
        if block:
            block = "*/" not in t
            continue
        if t.startswith("/*"):
            block = "*/" not in t
            continue
        if not t or t.startswith("//"):
            continue
        out.append(t)
    return "\n".join(out)


def main():
    page = read("src", "template.html")
    js = "\n".join(squeeze_js(read("src", name)) for name in SOURCES)
    for key, value in (("__CSS__", squeeze_css(read("src", "reader.css"))), ("__MARKED__", read("vendor", "marked.umd.js")),
                       ("__HLJS__", read("vendor", "hljs.min.js")), ("__JS__", js), ("__VERSION__", VERSION)):
        if key in ("__MARKED__", "__HLJS__", "__JS__"):
            value = value.replace("</script>", "<\\/script>")
        page = page.replace(key, value)
    with open(os.path.join(here, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print("reader/index.html: %d bytes (%d KB)" % (len(page.encode("utf-8")), len(page.encode("utf-8")) // 1024))


if __name__ == "__main__":
    main()
