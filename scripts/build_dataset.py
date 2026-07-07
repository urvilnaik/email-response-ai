#!/usr/bin/env python3
"""Expand seed dataset with LLM paraphrases, split train/holdout, export negatives."""

from __future__ import annotations

import json
import logging
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import (  # noqa: E402
    DATASET_FILE,
    DATA_DIR,
    GEMINI_API_KEY,
    GROQ_API_KEY,
    HOLDOUT_FILE,
    MOCK_LLM,
    NEGATIVE_FILE,
    SANITY_FILE,
    SEED_FILE,
    STATS_FILE,
)
from src.generator.llm import complete_text  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

NEGATIVE_TEMPLATES = [
    {
        "suffix": "a",
        "failure_mode": "ignores_intent",
        "why_bad": "Generic acknowledgment with no answer to the customer's question.",
        "body": "Thanks for reaching out! We appreciate your message and will get back to you soon.",
    },
    {
        "suffix": "b",
        "failure_mode": "missing_actions",
        "why_bad": "Acknowledges the issue but omits required next steps and timelines.",
        "body": "Hi,\n\nSorry to hear about this. We'll look into it and take care of it for you.\n\nBest,\nSupport",
    },
    {
        "suffix": "c",
        "failure_mode": "wrong_tone",
        "why_bad": "Dismissive or overly casual tone inappropriate for the situation.",
        "body": "Hey,\n\nNot a big deal — these things happen. Just wait a bit and it should sort itself out.\n\nCheers",
    },
    {
        "suffix": "d",
        "failure_mode": "hallucinated_policy",
        "why_bad": "Invents refund terms, features, or policies not supported by the gold reply.",
        "body": "Hi,\n\nPer our lifetime refund guarantee, we'll process a full refund within 24 hours and add a free year of premium service.\n\nBest,\nSupport",
    },
    {
        "suffix": "e",
        "failure_mode": "off_topic",
        "why_bad": "Answers a completely different question than the one asked.",
        "body": "Hi,\n\nTo update your billing address, go to Settings > Billing > Address. Let me know if you need help with that.\n\nBest,\nSupport",
    },
]


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _manual_paraphrase(seed: dict, variant_idx: int, messy: bool) -> dict:
    """Offline paraphrase when no LLM key available."""
    inc = seed["incoming_email"]
    body = inc["body"]
    subject = inc["subject"]

    if messy:
        body = body.lower().replace("please", "pls").replace("?", "??")
        if "!" not in body:
            body = body.rstrip(".") + "!!!"
        subject = subject.lower()
    else:
        prefixes = ["Follow-up: ", "Re: ", "Quick question — ", "Regarding: "]
        subject = prefixes[variant_idx % len(prefixes)] + subject

    new_id = f"var_{seed['id']}_{variant_idx:02d}"
    record = json.loads(json.dumps(seed))
    record["id"] = new_id
    record["incoming_email"] = {
        "subject": subject,
        "body": body,
        "from": inc.get("from", "customer@example.com"),
    }
    if messy:
        record.setdefault("metadata", {})["quality"] = "messy"
    return record


def llm_paraphrase(seed: dict, variant_idx: int, messy: bool) -> dict | None:
    if MOCK_LLM or (not GROQ_API_KEY and not GEMINI_API_KEY):
        return _manual_paraphrase(seed, variant_idx, messy)

    inc = seed["incoming_email"]
    style = "messy with typos, bad grammar, and frustrated tone" if messy else "clean professional"
    prompt = f"""Paraphrase this customer email in a {style} style. Keep the same intent and facts.
Return JSON: {{"subject": "...", "body": "..."}}

Original subject: {inc['subject']}
Original body: {inc['body']}"""

    try:
        text = complete_text(prompt, system="Return valid JSON only.")
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        parsed = json.loads(text.strip())
        new_id = f"var_{seed['id']}_{variant_idx:02d}"
        record = json.loads(json.dumps(seed))
        record["id"] = new_id
        record["incoming_email"]["subject"] = parsed.get("subject", inc["subject"])
        record["incoming_email"]["body"] = parsed.get("body", inc["body"])
        if messy:
            record.setdefault("metadata", {})["quality"] = "messy"
        return record
    except Exception as exc:
        log.warning("LLM paraphrase failed for %s: %s", seed["id"], exc)
        return _manual_paraphrase(seed, variant_idx, messy)


def expand_seeds(seeds: list[dict], variations_per_seed: int = 2) -> list[dict]:
    expanded = list(seeds)
    var_idx = 0
    for seed in seeds:
        for i in range(variations_per_seed):
            messy = seed.get("metadata", {}).get("quality") == "messy" or i == 1
            variant = llm_paraphrase(seed, var_idx, messy=messy)
            if variant:
                expanded.append(variant)
            var_idx += 1
    return expanded


def split_dataset(rows: list[dict], holdout_ratio: float = 0.2, seed: int = 42) -> tuple[list[dict], list[dict]]:
    rng = random.Random(seed)
    shuffled = rows.copy()
    rng.shuffle(shuffled)
    n_holdout = max(1, int(len(shuffled) * holdout_ratio))
    holdout = shuffled[:n_holdout]
    train = shuffled[n_holdout:]

    # Rename holdout IDs for clarity
    for i, row in enumerate(holdout):
        row["id"] = f"holdout_{i+1:03d}"
        row["_source_id"] = row.get("_source_id", row["id"])

    return train, holdout


def build_negatives(holdout: list[dict]) -> list[dict]:
    negatives = []
    for row in holdout:
        for tmpl in NEGATIVE_TEMPLATES[:2]:
            negatives.append(
                {
                    "id": f"neg_{row['id']}{tmpl['suffix']}",
                    "paired_email_id": row["id"],
                    "bad_reply": {"body": tmpl["body"], "tone": "unprofessional"},
                    "failure_mode": tmpl["failure_mode"],
                    "why_bad": tmpl["why_bad"],
                }
            )
    return negatives


def compute_stats(
    dataset: list[dict],
    holdout: list[dict],
    negatives: list[dict],
) -> dict:
    def count_field(rows: list[dict], field: str, subfield: str | None = None) -> dict:
        c: Counter = Counter()
        for r in rows:
            if subfield:
                val = r.get(field, {}).get(subfield, "unknown")
            else:
                val = r.get(field, "unknown")
            c[val] += 1
        return dict(c)

    return {
        "seed_count": len(load_jsonl(SEED_FILE)),
        "dataset_count": len(dataset),
        "holdout_count": len(holdout),
        "negative_count": len(negatives),
        "sanity_count": len(load_jsonl(SANITY_FILE)) if SANITY_FILE.exists() else 0,
        "dataset_by_category": count_field(dataset, "category"),
        "dataset_by_quality": count_field(dataset, "metadata", "quality"),
        "holdout_by_category": count_field(holdout, "category"),
        "negative_by_failure_mode": count_field(negatives, "failure_mode"),
    }


def main() -> None:
    if not SEED_FILE.exists():
        log.error("Seed file not found: %s", SEED_FILE)
        sys.exit(1)

    seeds = load_jsonl(SEED_FILE)
    log.info("Loaded %d seed pairs", len(seeds))

    if MOCK_LLM or (not GROQ_API_KEY and not GEMINI_API_KEY):
        log.warning("No API keys / MOCK_LLM=1 — using seed + manual paraphrases only")

    expanded = expand_seeds(seeds, variations_per_seed=2)
    log.info("Expanded to %d total pairs", len(expanded))

    dataset, holdout = split_dataset(expanded, holdout_ratio=0.2)
    negatives = build_negatives(holdout)

    write_jsonl(DATASET_FILE, dataset)
    write_jsonl(HOLDOUT_FILE, holdout)
    write_jsonl(NEGATIVE_FILE, negatives)

    stats = compute_stats(dataset, holdout, negatives)
    STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with STATS_FILE.open("w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    log.info("Wrote %s (%d rows)", DATASET_FILE, len(dataset))
    log.info("Wrote %s (%d rows)", HOLDOUT_FILE, len(holdout))
    log.info("Wrote %s (%d rows)", NEGATIVE_FILE, len(negatives))
    log.info("Wrote %s", STATS_FILE)


if __name__ == "__main__":
    main()
