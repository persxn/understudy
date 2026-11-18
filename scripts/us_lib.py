"""Shared helpers for the understudy scripts. Standard library only."""
import os
import signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


if hasattr(signal, "SIGPIPE"):          # `... | head` closes the pipe early: end quietly, no traceback
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def load_config():
    cfg = {"book": "book", "private": "private"}
    path = os.path.join(ROOT, "understudy.yaml")
    if os.path.exists(path):
        for raw in open(path, encoding="utf-8"):
            line = raw.split("#", 1)[0].strip()
            if ":" in line:
                key, value = line.split(":", 1)
                cfg[key.strip()] = value.strip()
    return cfg


def book_dir(arg=None):
    path = arg or load_config()["book"]
    return path if os.path.isabs(path) else os.path.join(ROOT, path)


def _value(text):
    text = text.split(" #", 1)[0].strip()
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        return [item.strip() for item in inner.split(",") if item.strip()] if inner else []
    return text.strip("\"'")


def parse_front(path):
    """Return (front dict, body text). Front is {} when the file has no front block."""
    text = open(path, encoding="utf-8").read()
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    front = {}
    for raw in text[4:end].splitlines():
        if ":" in raw and not raw.lstrip().startswith("#"):
            key, value = raw.split(":", 1)
            front[key.strip()] = _value(value)
    body = text[end + 4:].lstrip("\n")
    return front, body


def tokens(text):
    """Rough token estimate: four characters per token."""
    return (len(text) + 3) // 4
