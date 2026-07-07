# AI Email Suggested-Response System

A Python CLI pipeline that generates suggested email replies using **hybrid RAG** (retrieval-augmented generation) and evaluates them with a **cascade multi-metric framework** — embedding similarity, action coverage, and a 4-dimension LLM judge — validated by negative examples and cross-pair sanity checks.

## Problem & Approach

Customer support and workplace inboxes contain messy, vague, emotional emails — not polished test prompts. This system:

1. **Retrieves** the top-3 most similar past (incoming, reply) pairs from a vector index
2. **Generates** a suggested reply via few-shot prompting with a free-tier LLM (Groq or Gemini)
3. **Evaluates** replies with a cascade of deterministic + LLM metrics, calibrated against deliberately bad replies and cross-mismatch sanity pairs

We chose **RAG over fine-tuning** because fine-tuning is expensive, prone to catastrophic forgetting, and cannot easily be updated. RAG allows instant knowledge-base updates by adding rows to the vector index — no retraining required.

## Dataset

The dataset is a **hybrid** of hand-authored seed pairs and LLM-generated paraphrases:

| File | Purpose | Count |
|---|---|---|
| `data/seed_emails.jsonl` | Hand-authored seed pairs (~30% intentionally messy) | 25 |
| `data/dataset.jsonl` | Train/RAG pool (80% split) | 60 |
| `data/holdout.jsonl` | Evaluation-only (never indexed) | 15 |
| `data/negative_examples.jsonl` | Deliberately bad replies for calibration | 30 |
| `data/sanity_check_pairs.jsonl` | Cross-mismatch pairs (metric validation gate) | 10 |

Each record includes rich metadata: `category`, `urgency`, `tone`, `quality` (clean/messy), `intent`, and `actions` (required next steps for action-coverage scoring).

**Limitations:** This is synthetic data, not real organizational email. It provides controlled coverage and linguistic diversity but does not capture a specific company's voice.

**Rebuild the dataset:**

```bash
python scripts/build_dataset.py
```

If no API key is set, the script falls back to seed-only mode and logs a warning.

## Generation (Hybrid RAG)

```
Incoming email → Embed (all-MiniLM-L6-v2) → ChromaDB top-3 search
  → Few-shot prompt with retrieved pairs → Groq/Gemini LLM → Suggested reply
```

1. Embed the incoming email (`subject + body`) with `sentence-transformers/all-MiniLM-L6-v2`
2. Search ChromaDB for the top-3 similar past pairs, with optional same-`category` boost (+0.1 rerank)
3. Build a few-shot prompt with system rules, retrieved examples, and metadata hints
4. Generate via Groq (`llama-3.3-70b-versatile`) or Gemini (`gemini-2.0-flash`) free tier

**Why not fine-tuning?** Fine-tuning requires GPU resources, risks catastrophic forgetting, and makes KB updates slow. RAG is interpretable (you can inspect retrieved examples), free-tier friendly, and updatable by adding JSONL rows.

**Why not prompt-only?** Without retrieval grounding, replies drift from organizational style and miss domain-specific action items.

```bash
python -m src.pipeline generate --subject "Refund request" --body "I was charged twice for order #12345"
# or
python -m src.pipeline generate --file path/to/email.txt
```

## Evaluation

### Cascade logic

| Zone | Cosine similarity | Behavior |
|---|---|---|
| **High confidence** | ≥ 0.85 | Trust embedding; LLM judge skipped (unless `always_judge`) |
| **Gray zone** | 0.55 – 0.85 | Always invoke LLM judge |
| **Low confidence** | < 0.55 | Cap composite at 0.4; still run judge for rationale |

### 4-dimension LLM judge (1–5 each)

| Dimension | Weight | Question |
|---|---|---|
| Intent alignment | 0.35 | Did the reply answer the sender's core request? |
| Tone & brand consistency | 0.20 | Is tone appropriate for the situation? |
| Hallucination / factuality | 0.25 | Does the reply invent policies or facts? |
| Completeness | 0.20 | Are all required next steps included? |

### Composite formula

| Component | Weight |
|---|---|
| Semantic similarity (cosine) | 0.20 |
| Action coverage (keyword heuristics) | 0.25 |
| Multi-dim LLM judge sub-score | 0.55 |

### Sanity-check gate

Cross-mismatch pairs (billing email + password-reset reply) must score composite **< 0.25** with mean **< 0.15**, or metrics are declared broken.

```bash
python scripts/sanity_check_eval.py   # must pass before trusting eval
python scripts/run_eval.py            # full holdout eval + calibration
```

### Negative calibration & adjusted score

```
adjusted_score = positive_mean × rank_accuracy × min(1, separation_gap / 0.30)
```

This prevents reporting high "accuracy" when bad replies also score well (meaning the metric is broken).

## How to Run

```bash
cd ~/email-response-ai
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add at least one API key

python scripts/build_dataset.py
python -m src.pipeline index
python scripts/sanity_check_eval.py   # gate: fail fast if metrics broken
python scripts/run_eval.py
pytest tests/ -v
```

**First run** downloads the ~90MB `all-MiniLM-L6-v2` embedding model from Hugging Face.

## Free API Setup

Add keys to `.env`:

```
GROQ_API_KEY=           # https://console.groq.com (free tier)
GEMINI_API_KEY=         # https://aistudio.google.com (free fallback)
MOCK_LLM=0              # set to 1 for offline demo without API keys
```

With `MOCK_LLM=1`, generation and judging use templated/heuristic responses so the full pipeline runs without keys. **Eval scores in mock mode are not representative** — use real API keys for meaningful generation and judge results.

## AI Tools Disclosure

- **Cursor** — project scaffolding, code generation, and iteration
- **Groq / Gemini** — reply generation, dataset expansion, and LLM-as-judge evaluation (free tiers)
- **sentence-transformers** — local embedding model (`all-MiniLM-L6-v2`), no API cost

## Results

> Results below were captured with `MOCK_LLM=1` (offline demo). With real Groq/Gemini keys, generation quality and judge scores will differ substantially. The sanity-check gate validates metric behavior regardless of LLM provider.

### Sanity-check proof table

All 10 cross-mismatch pairs passed the gate (composite < 0.25, mean = 0.150):

| Email topic | Mismatched reply topic | Composite | Intent | Hallucination |
|---|---|---|---|---|
| billing | account_access | 0.150 | 1/5 | 1/5 |
| scheduling | billing | 0.150 | 1/5 | 1/5 |
| sales | complaints | 0.150 | 1/5 | 1/5 |
| support | billing | 0.150 | 1/5 | 1/5 |
| complaints | sales | 0.150 | 1/5 | 1/5 |
| account_access | feature_request | 0.150 | 1/5 | 1/5 |
| feature_request | account_access | 0.150 | 1/5 | 1/5 |
| scheduling | support | 0.150 | 1/5 | 1/5 |
| support | sales | 0.150 | 1/5 | 1/5 |
| onboarding | complaints | 0.150 | 1/5 | 1/5 |

### Eval summary (mock mode)

| Metric | Value |
|---|---|
| Positive mean (generated) | 0.288 |
| Negative mean (bad replies) | 0.286 |
| Separation gap | 0.002 |
| Rank accuracy | 47% |
| Adjusted score | 0.001 |

The low separation gap in mock mode is expected: the mock generator returns a generic template that scores similarly to deliberately bad replies. With real LLM generation, positive scores should rise while negatives stay low.

### Messy vs clean breakdown

| Quality | Mean composite |
|---|---|
| messy | 0.298 |
| clean | 0.273 |

### Negative calibration examples

| Bad reply | Failure mode | Composite |
|---|---|---|
| "Thanks for reaching out! We appreciate your message..." | ignores_intent | 0.284 |
| "Sorry to hear about this. We'll look into it..." | missing_actions | 0.288 |

### Judge dimension example (holdout_001)

A case where intent is partially addressed but completeness is poor:

| Dimension | Score | Rationale |
|---|---|---|
| Intent alignment | 2/5 | Mock: based on lexical overlap with gold reply |
| Tone consistency | 4/5 | Mock: professional tone assumed |
| Hallucination | 4/5 | Mock: no obvious fabrications detected |
| Completeness | 1/5 | Mock: action coverage 0% |

### Cascade zones (mock mode)

| Email | Semantic sim | Zone | Judge invoked |
|---|---|---|---|
| holdout_001 | 0.112 | low | yes (composite capped at 0.4) |
| holdout_003 | 0.551 | gray | yes |
| (high-sim example) | ≥ 0.85 | high | skipped in live mode |

### Ablation note

Without the LLM judge, composite relies on semantic similarity (0.20) and action coverage (0.25) only — roughly 45% of the total weight. The judge (0.55 weight) captures nuance that embeddings miss, especially for paraphrased but semantically equivalent replies.

## Project Structure

```
email-response-ai/
├── data/           # seed, dataset, holdout, negatives, sanity pairs
├── scripts/        # build_dataset, run_eval, sanity_check_eval
├── src/
│   ├── retrieval/  # ChromaDB index + semantic search
│   ├── generator/  # RAG prompt builder + LLM client
│   └── evaluator/  # cascade metrics, judge, calibration
├── tests/          # test_metrics.py
└── reports/        # generated eval outputs (gitignored)
```

## GitHub Publication

To publish this repository:

```bash
# Create an empty public repo on GitHub, then:
git remote add origin git@github.com:YOUR_USER/email-response-ai.git
git push -u origin main
```

Replace `YOUR_USER` with your GitHub username and update this README with the public URL.
