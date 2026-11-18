#!/usr/bin/env python3
"""Rebuild the four routing prompts from AGENTS.md, the skill descriptions and the scenario files.

    python3 tests/routing/build.py

Run it after any change to AGENTS.md or a skill description. "full" gives the model the project
instructions and the skill list; "bare" gives it the skill list only (what a harness shows when the
project instructions are not loaded). Give one prompt file to a fresh small-model agent, tell it where
to save its JSON answer (tests/routing/run_<set>_<model>_<full|bare>.json), then run score.py on it.
"""
import json
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(os.path.dirname(here))
sys.path.insert(0, os.path.join(root, "scripts"))
from us_lib import parse_front  # noqa: E402

HEAD = """You are simulating ONE step of a coding-agent harness: deciding which skill to load first for a user message.
Below is everything the harness puts in front of the model before any skill is loaded. Do not read any files; decide only from this text.
For each numbered user message, choose the ONE skill that should be loaded first, or "none" if no skill should be loaded.
Treat each message as the first message of its own session.
Write your answer as a JSON object mapping the message number (as a string) to the skill name or "none", and save it to the file path given at the end. Reply with only the word DONE.
"""

skills = []
for name in sorted(os.listdir(os.path.join(root, ".claude", "skills"))):
    front, _ = parse_front(os.path.join(root, ".claude", "skills", name, "SKILL.md"))
    skills.append(f"- {front['name']}: {front['description']}")
agents = open(os.path.join(root, "AGENTS.md"), encoding="utf-8").read()
for tag, source in (("", "scenarios.json"), ("b_", "scenarios_b.json")):
    scenarios = json.load(open(os.path.join(here, source), encoding="utf-8"))
    messages = "\n".join(f"{s['id']}. {s['message']}" for s in scenarios)
    for kind in ("full", "bare"):
        text = HEAD
        if kind == "full":
            text += "\n=== PROJECT INSTRUCTIONS ===\n" + agents
        text += "\n=== AVAILABLE SKILLS (name: description) ===\n" + "\n".join(skills)
        text += "\n\n=== USER MESSAGES ===\n" + messages + "\n"
        open(os.path.join(here, f"prompt_{tag}{kind}.txt"), "w", encoding="utf-8").write(text)
        print(f"prompt_{tag}{kind}.txt: {len(scenarios)} messages, {len(text) // 4} tokens")
