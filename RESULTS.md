# Can a meta-system make a small LLM solve hard math?

An experiment inspired by [Poetiq](https://poetiq.ai/), a startup that builds
"AI meta-systems" on top of frontier models. Their claim: you can get dramatically
better results by building intelligence *on top of* LLMs rather than *into* them.

We tested this with **Qwen 2.5 7B** on **AIME 2024** (30 competition math problems),
progressively adding layers of meta-optimization.

## Setup

- **Model**: Qwen 2.5 7B Instruct, served via vLLM on a single H100
- **Problems**: 30 AIME 2024 problems (15 from AIME I = train, 15 from AIME II = test)
- **Meta-optimizer**: GPT-5.2 (used only during training/design, never at test time)

## Three stages

### Stage 1: Baseline

Raw Qwen 7B with a simple prompt ("Solve this AIME problem, reason step by step,
give your answer in \<answer\> tags"). 20 completions per problem, temperature 0.7.

### Stage 2: Meta-prompt optimization

GPT-5.2 sees Qwen's failures on train and iteratively rewrites the prompt. It produced
a structured prompt with specific instructions: restate the problem, name the math
topic, define variables before doing algebra, switch approach if stuck after 12 lines,
verify by plugging back in. Best prompt is frozen and evaluated on test.

### Stage 3: GPT-designed solving strategy

GPT-5.2 designs a complete `solve()` function that can call Qwen multiple times with
different prompts. The function uses the optimized stage 2 system prompt (locked in, can't
be overridden) and adds its own logic on top. Best strategy is frozen and evaluated on test.

GPT-5.2 is **not in the loop at test time** -- it only designs the strategy, which then
runs autonomously with Qwen alone.

## Results

All scores on the held-out test set (AIME 2024 II, 15 problems):

| Stage | Method | Test Score |
|-------|--------|-----------|
| 1 | Baseline (raw prompt, pass@1) | 0.0% (0/15) |
| 2 | GPT-optimized prompt (pass@1) | 1.7% (5/300 completions correct) |
| 3 | GPT-designed strategy | **13.3% (2/15 problems solved)** |

Stage 3 correctly solved:
- **2024 II Problem 2** (answer: 236) -- list properties / sum of squares
- **2024 II Problem 4** (answer: 33) -- logarithmic system of equations

On the train set (AIME 2024 I), stage 3 solved 4/15 (problems 1, 2, 4, 7).

## What GPT-5.2 designed (the winning strategy)

The strategy is a multi-phase pipeline with ~40 model calls per problem:

**Phase 1 -- Batch sampling (20 calls):** Generate 20 candidate answers using the
optimized prompt. Extract answers, count votes.

**Phase 2 -- Confidence check:** If there's a strong majority (11+ votes, or 60%+),
go straight to verification. If weak, continue to phase 3.

**Phase 3 -- Diversified reprompting (8 calls):** If no clear winner, reprompt with
four different "angles" (2 calls each):
- Algebraic: "keep expressions symbolic, only do arithmetic at the end"
- Counting: "define sample space, use complementary counting, check small cases"
- Geometry: "introduce coordinates or vectors, verify with consistency check"
- Checklist: "restate variables, derive equations, solve, check constraints, re-check arithmetic"

Combine votes from both rounds with the diversified prompts weighted 2x.

**Phase 4 -- Forced-choice tournament (6 calls):** Present the top candidates to the
model: "which of [X, Y, Z] is correct? Check each by plugging in." Merge tournament
votes with 3x weight.

**Phase 5 -- Final verification (3 calls):** Take the overall winner, ask the model to
verify it by re-solving cleanly. Accept if 2+ verifications agree.

**Fallback:** Lightweight sympy-based salvage for gcd/lcm-type problems (rarely fires).

## What's interesting

### The layering effect is real but modest

Each layer provides genuine improvement:
- Raw model: 0%
- Better prompt: ~2%
- Prompt + multi-phase aggregation: ~13%

The gains are multiplicative -- the strategy only works *because* the optimized prompt
gives the model enough signal to occasionally produce correct answers. When we accidentally
ran stage 3 with a generic prompt (bypassing stage 2), it got 0% everywhere.

### The capability floor matters

Qwen 7B is near the floor for AIME. With 20 completions on the basic prompt, it produced
0 correct answers on any test problem. The meta-prompt squeezed out 5/300 correct, and
the reprompting strategy was able to surface correctness on 2 problems where weak signal
existed.

For the 13 unsolved test problems, the model simply doesn't have the mathematical reasoning
capacity. No amount of scaffolding can create capability that isn't there. This suggests
Poetiq's approach works best with stronger base models where there's more latent signal
to amplify.

### Reprompting > selection

The key insight from stage 3: reprompting with different angles (algebraic, counting,
geometry, checklist) generates *new* completions that may be correct even when the
original 20 weren't. This is fundamentally different from just selecting among existing
completions. The diversified prompts break the model out of its default failure modes.

### Verification catches errors

The verify-then-accept pattern (ask the model to re-solve given a candidate answer)
acts as a filter. Even a 7B model can sometimes recognize a wrong answer when shown it,
even if it couldn't find the right answer from scratch. This is cheaper than generating
more solutions.

### What Poetiq probably does differently

This experiment was intentionally minimal (3 iterations, 15 train problems, one model).
The real system likely:
- Runs hundreds of refinement cycles, not 3
- Learns problem-type-specific strategies, not one universal pipeline
- Uses code execution as a first-class tool (sympy, brute force, numerical verification)
- Routes between different base models depending on the problem
- Accumulates a growing library of strategies that compound over time

The gap between our 13% and their 54% on ARC-AGI-2 likely comes from this depth of
iteration and specialization -- the same basic ideas (reprompt, verify, aggregate,
use code) but refined over thousands of cycles rather than 3.

## Reproducing

```bash
cd ~/aime_meta
sbatch start_vllm.sh                     # start Qwen on GPU
export OPENAI_API_KEY=...                 # for GPT-5.2
PYTHONUNBUFFERED=1 uv run python run_all.py
```

Requires: 1x H100, OpenAI API access, ~30 minutes.
