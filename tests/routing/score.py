#!/usr/bin/env python3
"""Score routing runs.  python3 tests/routing/score.py tests/routing/run_*.json"""
import json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
for path in sys.argv[1:]:
    scenarios = json.load(open(os.path.join(here, "scenarios_b.json" if "_b_" in os.path.basename(path) else "scenarios.json")))
    got = json.load(open(path))
    wrong, missed, false_act = [], 0, 0
    for s in scenarios:
        answer = got.get(str(s["id"]), "missing")
        if answer in s["accept"]:
            continue
        wrong.append((s["id"], s["message"], answer, s["accept"]))
        if answer == "none":
            missed += 1
        elif s["accept"] == ["none"]:
            false_act += 1
    n = len(scenarios)
    print(f"{os.path.basename(path)}: {n - len(wrong)}/{n} correct ({100 * (n - len(wrong)) / n:.1f}%), "
          f"missed triggers {missed}, false activations {false_act}, wrong skill {len(wrong) - missed - false_act}")
    for item in wrong:
        print("   #%d %r -> %s (accepted: %s)" % item)
