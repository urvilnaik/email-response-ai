#!/usr/bin/env python3
"""Full holdout evaluation with negative calibration."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import HOLDOUT_FILE, NEGATIVE_FILE, REPORTS_DIR  # noqa: E402
from src.evaluator.calibration import (  # noqa: E402
    compute_calibration,
    failure_mode_breakdown,
    quality_breakdown,
)
from src.evaluator.cascade import evaluate_reply  # noqa: E402
from src.evaluator.report import build_eval_report, write_json, write_markdown_summary  # noqa: E402
from src.pipeline import generate_for_record  # noqa: E402


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> None:
    if not HOLDOUT_FILE.exists():
        print(f"Holdout not found: {HOLDOUT_FILE}. Run build_dataset.py first.", file=sys.stderr)
        sys.exit(1)

    holdout = load_jsonl(HOLDOUT_FILE)
    negatives = load_jsonl(NEGATIVE_FILE) if NEGATIVE_FILE.exists() else []
    neg_by_email: dict[str, list[dict]] = {}
    for neg in negatives:
        neg_by_email.setdefault(neg["paired_email_id"], []).append(neg)

    reports = []
    positive_scores = []
    all_negative_scores = []
    rank_results = []
    negative_records = []

    for record in holdout:
        inc = record["incoming_email"]
        gold = record["reply"]["body"]
        meta = {
            "category": record.get("category"),
            "quality": record.get("metadata", {}).get("quality", "clean"),
            "intent": record.get("metadata", {}).get("intent", []),
            "actions": record.get("metadata", {}).get("actions", []),
        }
        actions = record.get("metadata", {}).get("actions", [])

        gen_result = generate_for_record(record)
        generated = gen_result["suggested_reply"]

        scores = evaluate_reply(
            inc,
            generated,
            gold,
            actions=actions,
            context_snippets=[gold],
            always_judge=True,
        )

        neg_scores = []
        for neg in neg_by_email.get(record["id"], []):
            ns = evaluate_reply(
                inc,
                neg["bad_reply"]["body"],
                gold,
                actions=actions,
                always_judge=False,
            )
            neg_entry = {
                "id": neg["id"],
                "failure_mode": neg["failure_mode"],
                "composite": ns.composite,
            }
            neg_scores.append(neg_entry)
            all_negative_scores.append(ns.composite)
            negative_records.append(neg_entry)

        beats = all(n["composite"] < scores.composite for n in neg_scores) if neg_scores else True
        rank_results.append(beats)
        positive_scores.append(scores.composite)

        report = build_eval_report(
            email_id=record["id"],
            metadata=meta,
            generated=generated,
            gold=gold,
            scores=scores,
            negative_scores=neg_scores,
            beats_all=beats,
            retrieved=gen_result["retrieved_examples"],
        )
        reports.append(report)

    calibration = compute_calibration(positive_scores, all_negative_scores, rank_results)
    quality = quality_breakdown(reports)
    failure_modes = failure_mode_breakdown(negative_records)

    summary = {
        "holdout_count": len(holdout),
        **calibration,
        "quality_breakdown": quality,
        "failure_mode_breakdown": failure_modes,
    }

    write_json(REPORTS_DIR / "eval_results.json", reports)
    write_json(REPORTS_DIR / "eval_summary.json", summary)
    write_json(REPORTS_DIR / "calibration_by_failure_mode.json", failure_modes)
    write_markdown_summary(REPORTS_DIR / "eval_summary.md", summary, reports)

    print(f"Evaluated {len(holdout)} holdout emails")
    print(f"Positive mean: {calibration['positive_mean']:.3f}")
    print(f"Negative mean: {calibration['negative_mean']:.3f}")
    print(f"Separation gap: {calibration['separation_gap']:.3f}")
    print(f"Adjusted score: {calibration['adjusted_score']:.3f}")
    print(f"Wrote reports to {REPORTS_DIR}/")


if __name__ == "__main__":
    main()
