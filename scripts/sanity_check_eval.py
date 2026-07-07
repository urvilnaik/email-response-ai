#!/usr/bin/env python3
"""Run sanity-check evaluation gate on cross-mismatch pairs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import REPORTS_DIR, SANITY_FILE  # noqa: E402
from src.evaluator.cascade import evaluate_reply  # noqa: E402
from src.evaluator.report import write_json, write_sanity_markdown  # noqa: E402

PASS_THRESHOLD = 0.25
MEAN_THRESHOLD = 0.15


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> int:
    pairs = load_jsonl(SANITY_FILE)
    print(f"Running sanity check on {len(pairs)} cross-mismatch pairs...")

    results = []
    composites = []

    for pair in pairs:
        incoming = pair["incoming_email"]
        bad_reply = pair["mismatched_reply"]["body"]
        scores = evaluate_reply(
            incoming,
            bad_reply,
            gold=bad_reply,
            actions=[],
            always_judge=True,
            is_mismatch=True,
        )
        result = {
            "id": pair["id"],
            "source_categories": pair["source_categories"],
            "why_mismatched": pair["why_mismatched"],
            "scores": scores.model_dump(),
        }
        results.append(result)
        composites.append(scores.composite)
        status = "PASS" if scores.composite < PASS_THRESHOLD else "FAIL"
        print(f"  {pair['id']}: composite={scores.composite:.3f} [{status}]")

    mean_score = sum(composites) / len(composites) if composites else 0.0
    failures = [r for r in results if r["scores"]["composite"] >= PASS_THRESHOLD]
    passed = not failures and mean_score < MEAN_THRESHOLD

    output = {
        "passed": passed,
        "mean_composite": round(mean_score, 4),
        "threshold_per_pair": PASS_THRESHOLD,
        "threshold_mean": MEAN_THRESHOLD,
        "failures": [f["id"] for f in failures],
        "results": results,
    }

    write_json(REPORTS_DIR / "sanity_check_results.json", output)
    write_sanity_markdown(REPORTS_DIR / "sanity_check_results.md", results, passed)

    if not passed:
        print("\nMETRIC SANITY CHECK FAILED")
        for f in failures:
            print(f"  {f['id']}: composite={f['scores']['composite']:.3f} (>= {PASS_THRESHOLD})")
        if mean_score >= MEAN_THRESHOLD:
            print(f"  Mean composite {mean_score:.3f} >= {MEAN_THRESHOLD}")
        return 1

    print(f"\nSanity check PASSED (mean={mean_score:.3f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
