#!/usr/bin/env python3
"""What a book's sessions make outside their HOME, kept and removed by us_run.py.

A book whose PLAN.md says `state: docker` makes containers, networks, volumes and images in the Docker
service, not in its folder. A ledger (state.json in the book's run folder) holds exactly what the
book's runs made there; only those things are ever removed. The interface, for another tool later:

    t = tracker(kind, folder)    # None for a kind not known here
    seen = t.look()              # what exists now (None where the tool cannot be asked)
    t.record(seen)               # add what is new since `seen` to the ledger
    t.clear(images=False)        # remove what the ledger holds (images only with images=True)
    t.clash(text)                # one plain line when text is a clash with something the book did not make
    t.danger(line)               # why a command line must not run on the learner's own machine, or ""
    t.note(line)                 # advice (not a problem) about a command line, or ""
    t.masks                      # patterns of text that changes on every run
"""
import json
import os
import re
import subprocess

DOCKER_KINDS = (("containers", ["ps", "-aq", "--no-trunc"]), ("networks", ["network", "ls", "-q", "--no-trunc"]),
                ("volumes", ["volume", "ls", "-q"]), ("images", ["images", "-q", "--no-trunc"]))
DOCKER_RM = {"containers": ["rm", "-f"], "networks": ["network", "rm"], "volumes": ["volume", "rm", "-f"],
             "images": ["rmi", "-f"]}
DOCKER_DANGER = [r"\bdocker\s+system\s+prune\b", r"\bdocker\s+(container|image|volume|network|builder)\s+prune\b",
                 r"\bdocker\s+(rm|rmi|stop|kill|volume\s+rm|container\s+(rm|stop|kill)|image\s+rm)\b.*"
                 r"(\$\(\s*docker\b|`)", r"\|\s*xargs\s+(-\S+\s+)*docker\s+(rm|rmi|stop|kill)\b",
                 r"\bdocker\s+swarm\s+leave\b"]
DOCKER_MASKS = [
    r"\bsha256:[0-9a-f]+", r"\b[0-9a-f]{12,64}\b",
    r"\b\d{4}-\d\d-\d\d(?:[T ]\d\d:\d\d(?::\d\d(?:\.\d+)?)?(?:Z|\s?[+-]\d\d:?\d\d)?(?: [A-Z]{2,5})?)?",
    r"\b\d{1,2}:\d\d:\d\d\b",
    r"\bUp (?:Less than a second|About an? \w+|\d+ \w+)(?: \((?:healthy|unhealthy|health: starting|Paused)\))?",
    r"\b(?:Less than a second|About an? \w+|\d+ \w+) ago\b",
    r"\b\d+(?:\.\d+)?m?s\b",
]
PUBLISH = re.compile(r"(?:^|\s)(?:-p|--publish)(?:\s+|=)(\S+)")


def docker(args, timeout=60):
    """(exit code, output) of a docker command; (None, "") when docker cannot be started."""
    try:
        p = subprocess.run(["docker"] + args, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None, ""
    return p.returncode, p.stdout + p.stderr


class Docker:
    masks = DOCKER_MASKS

    def __init__(self, folder):
        self.path = os.path.join(folder, "state.json")
        try:
            with open(self.path, encoding="utf-8") as f:
                self.ledger = {k: list(v) for k, v in json.load(f).items()}
        except (OSError, ValueError, AttributeError):
            self.ledger = {}

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path + ".tmp", "w", encoding="utf-8") as f:
            json.dump(self.ledger, f, indent=0, sort_keys=True)
        os.replace(self.path + ".tmp", self.path)

    def look(self):
        seen = {}
        for kind, args in DOCKER_KINDS:
            code, out = docker(args)
            if code != 0:
                return None
            seen[kind] = set(out.split())
        return seen

    def record(self, before):
        after = self.look() if before is not None else None
        if after is None:
            return
        for kind, _ in DOCKER_KINDS:
            new = after[kind] - before[kind] - set(self.ledger.get(kind, []))
            if new:
                self.ledger[kind] = self.ledger.get(kind, []) + sorted(new)
        self.save()

    def clear(self, images=False):
        """Remove what the ledger holds: containers (forced), then networks, then volumes (then images).
        Returns {kind: number removed}."""
        if not any(self.ledger.values()):
            return {}
        kinds = [k for k, _ in DOCKER_KINDS if images or k != "images"]
        for kind in kinds:
            if self.ledger.get(kind):
                docker(DOCKER_RM[kind] + self.ledger[kind], timeout=120)
        now, gone = self.look(), {}
        if now is None:
            return {}
        for kind in kinds:
            left = [x for x in self.ledger.get(kind, []) if x in now[kind]]
            gone[kind] = len(self.ledger.get(kind, [])) - len(left)
            self.ledger[kind] = left
        self.save()
        return gone

    def mine(self, kind, ident):
        return any(x.startswith(ident) or ident.startswith(x) for x in self.ledger.get(kind, []))

    def clash(self, text):
        m = re.search(r'name "/?([^"]+)" is already in use by container "([0-9a-f]+)"', text)
        if m and not self.mine("containers", m.group(2)):
            return (f"a container named {m.group(1)} already exists on this machine and was not made by the book's "
                    f"runs: remove it (docker rm -f {m.group(1)}) or rename it, then run again")
        m = re.search(r"(?:Bind for \S*?:(\d+) failed: port is already allocated|"
                      r"listen tcp\S* \S*?:(\d+): bind: address already in use)", text)
        if m:
            port = m.group(1) or m.group(2)
            code, out = docker(["ps", "-q", "--no-trunc", "--filter", "publish=" + port])
            if not any(self.mine("containers", x) for x in out.split()):
                return (f"port {port} is already in use on this machine by something the book's runs did not "
                        f"make: stop it or free the port, or use another port, then run again")
        return ""

    def danger(self, line):
        if any(re.search(p, line) for p in DOCKER_DANGER):
            return "would touch things the book did not make on the learner's own Docker"
        return ""

    def note(self, line):
        if not re.search(r"\bdocker\b", line):
            return ""
        for value in PUBLISH.findall(line):
            if not re.match(r"(127\.0\.0\.1|localhost|\[::1\]):", value):
                value = re.sub(r"^0\.0\.0\.0:", "", value)
                return f"publishes the port to the whole network; write -p 127.0.0.1:{value}"
        return ""


TRACKERS = {"docker": Docker}


def tracker(kind, folder):
    """The tracker for a plan's `state:` value (docker), or None."""
    cls = TRACKERS.get((kind or "").strip().lower())
    return cls(folder) if cls else None
