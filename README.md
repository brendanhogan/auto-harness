# auto-harness

Can you automatically build a "harness" around a small language model that makes it solve problems it can't solve alone?

This repo is a minimal experiment testing that idea. We take **Qwen 2.5 7B** (a small open model) and try to solve **AIME 2024** math competition problems — problems the model essentially can't solve on its own. We progressively layer meta-optimization on top:

1. **Baseline** — raw model, simple prompt
2. **Meta-prompt** — a frontier model (GPT-5.2) iteratively optimizes the prompt
3. **Auto-harness** — GPT-5.2 designs a multi-phase solving strategy (reprompting, verification, aggregation) that wraps around the small model

The frontier model is only used during *design time*. At test time, only the small model runs — the harness is frozen.

## Results

All scores on the held-out test set (AIME 2024 II, 15 problems):

| Stage | Method | Test Score |
|-------|--------|-----------|
| 1 | Baseline (raw prompt) | 0.0% (0/15) |
| 2 | GPT-optimized prompt | 1.7% (5/300 individual completions correct) |
| 3 | Auto-harness | **13.3% (2/15 problems solved)** |

From zero to two solved problems — not by making the model smarter, but by building smarter infrastructure around it.

## What the auto-harness does

GPT-5.2 designed a five-phase pipeline that uses ~40 small-model calls per problem:

**Phase 1 — Batch sampling (20 calls).** Generate 20 candidate answers with the optimized prompt. Count votes.

**Phase 2 — Confidence check.** If one answer has strong majority (11+ votes or 60%+), skip to verification. Otherwise continue.

**Phase 3 — Diversified reprompting (8 calls).** This is the key innovation. When there's no consensus, reprompt from four different angles (2 calls each):
- *Algebraic*: "keep expressions symbolic, only do arithmetic at the end"
- *Counting*: "define sample space, use complementary counting, check small cases"
- *Geometry*: "introduce coordinates or vectors, verify with consistency check"
- *Checklist*: "restate variables, derive equations, solve, check constraints, re-check arithmetic"

These diversified prompts break the model out of whatever failure mode it's stuck in.

**Phase 4 — Forced-choice tournament (6 calls).** Present the top candidates: "which of [X, Y, Z] is correct? Check each by plugging in." Weighted 3x in the final tally.

**Phase 5 — Verification (3 calls).** Ask the model to re-solve given the winning candidate. Accept if 2+ verifications agree.

## Why this is interesting

### The layering effect

Each layer provides genuine improvement, and they're multiplicative — the auto-harness only works *because* the optimized prompt gives the model enough signal to occasionally produce correct answers. When we accidentally ran the harness with a generic system prompt (bypassing the optimized one), it scored 0% — worse than the prompt-only stage.

### Reprompting > selection

The critical insight: reprompting with different angles generates *new* completions that may be correct even when the original 20 weren't. This is fundamentally different from just selecting among existing completions (majority vote, weighted vote, etc.). The diversified prompts help the model escape its default failure modes.

### The capability floor

For 13 of the 15 test problems, the model simply doesn't have the mathematical capacity. No scaffolding can create reasoning ability that isn't there. This suggests auto-harness approaches work best when the base model has *some* latent signal to amplify — and become more powerful with stronger base models.

### Inspiration: Poetiq

This experiment was inspired by [Poetiq](https://poetiq.ai/), a startup that builds AI meta-systems on top of frontier LLMs. Their system achieved 54% on ARC-AGI-2 at half the cost of the previous SOTA. The gap between our 13% on AIME and their results likely comes from depth of iteration (hundreds of refinement cycles vs. our 3), problem-type specialization, code execution as a first-class tool, and accumulated strategy libraries that compound over time.

## Repo structure

```
auto-harness/
  problems.py            # 30 AIME 2024 problems with answers (train/test split)
  utils.py               # Model calling helpers, answer extraction, scoring
  stage1_baseline.py     # Raw Qwen, simple prompt, 20 completions
  stage2_metaprompt.py   # GPT-5.2 iteratively optimizes the prompt
  stage3_harness.py      # GPT-5.2 designs a multi-phase solve() function
  run_all.py             # Orchestrator: runs all three stages
  start_vllm.sh          # Slurm script to serve Qwen on a GPU node
  results/               # Saved completions and scores (JSON)
  pyproject.toml         # Dependencies: openai, sympy, vllm
```

## Running it

```bash
# 1. Start Qwen on a GPU node
sbatch start_vllm.sh

# 2. Run the experiment
export OPENAI_API_KEY=...
PYTHONUNBUFFERED=1 uv run python run_all.py
```

Requires one H100 GPU (for vLLM), an OpenAI API key (for GPT-5.2), and ~30 minutes.

Results are cached between runs — stages that have already completed will be skipped.
