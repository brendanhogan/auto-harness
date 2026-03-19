"""
Stage 3: GPT-5.2 designs a solve() function that can call Qwen and run code.
Unlike stages 1-2 which just prompt Qwen once, this can reprompt, verify, aggregate, etc.
"""

import json
import os
import re
import traceback
from collections import Counter
from problems import TRAIN, TEST
from utils import (
    get_qwen_client, get_openai_client, call_qwen, call_gpt,
    extract_answer, save_results, print_scores,
)

N_COMPLETIONS = 20
N_ITERATIONS = 3

STRATEGY_SPEC = """You are designing a solving strategy for AIME math competition problems using a small 7B model (Qwen 2.5 7B).

Write a Python function:

    def solve(problem_text: str, call_model, call_model_n) -> int | None

Where:
- problem_text: the AIME problem (may contain LaTeX like $x^2$)
- call_model(prompt) -> str
    Calls Qwen once, returns one completion string.
- call_model_n(prompt, n=20) -> list[str]
    Calls Qwen n times in one batch, returns list of completions.
- Returns: an integer 0-999

CRITICAL: call_model and call_model_n already have an optimized system prompt baked in.
DO NOT pass a system= argument. Just pass the user prompt string. The optimized prompt
tells the model to reason in <reason> tags and answer in <answer>N</answer> tags.
Your user prompts should include the problem text and any additional instructions.

The base prompt template that's already working is:
  "Solve the following AIME problem. [step-by-step instructions] Problem: {{problem}}"
So your prompts should follow a similar style — give the problem and any extra guidance.

IMPORTANT CONSTRAINTS:
- You get at most ~40 total model calls per problem (budget matters)
- Each completion is max 2048 tokens
- The model is SMALL (7B) - it can do basic reasoning but makes arithmetic errors
- Answers are extracted from <answer>N</answer> tags

Your function should be SELF-CONTAINED. You can import: re, math, sympy, collections, itertools, fractions, statistics.

STRATEGIES TO CONSIDER:
- Generate 20 answers with the base prompt, take majority vote, then reprompt asking the model to verify that specific answer
- If there's no clear majority, reprompt with "Here are several candidate answers: [X, Y, Z]. Verify each one and pick the best."
- Try reprompting from different angles (algebraic vs. computational vs. step-by-step)
- Extract equations from completions and solve with sympy
- If there's no clear majority, reprompt asking the model to choose between top candidates

Here are the training problems and what the model produces with the optimized prompt (20 completions each):

{train_data}

{previous_attempt}

Write your function inside <code> tags:
<code>
import re
from collections import Counter
# any other imports...

def solve(problem_text: str, call_model, call_model_n) -> int | None:
    ...
</code>"""


def get_stage2_prompt():
    """Load the best prompt from stage 2."""
    s2_path = "results/stage2.json"
    if os.path.exists(s2_path):
        s2 = json.load(open(s2_path))
        return s2["best_system_prompt"], s2["best_user_prompt"]
    return (
        "You are a math competition solver.",
        "Solve this AIME problem. Think step by step inside <reason> tags, "
        "then give your final integer answer (0-999) inside <answer> tags.\n\n"
        "Problem: {problem}\n\n<reason>",
    )


def make_train_data(qwen_client, system_prompt, user_prompt_template):
    """Get train completions and summarize them."""
    cache_path = "results/stage3_train_completions.json"
    if os.path.exists(cache_path):
        print("  Loading cached train completions...")
        all_completions = json.load(open(cache_path))
    else:
        print("  Generating train completions (20 per problem)...")
        all_completions = {}
        for prob in TRAIN:
            print(f"    {prob['id']}...", flush=True)
            prompt = user_prompt_template.replace("{problem}", prob["text"])
            comps = call_qwen(qwen_client, prompt, system=system_prompt, n=N_COMPLETIONS)
            all_completions[prob["id"]] = comps
        save_results(all_completions, cache_path)

    lines = []
    for prob in TRAIN:
        comps = all_completions[prob["id"]]
        answers = [extract_answer(c) for c in comps]
        counter = Counter(a for a in answers if a is not None)
        top = counter.most_common(5)
        lines.append(
            f"Problem {prob['id']} (correct_answer={prob['answer']}): "
            f"model_answers={answers}, top_votes={top}"
        )
    return "\n".join(lines), all_completions


def extract_code(response):
    match = re.search(r"<code>\s*(.*?)\s*</code>", response, re.DOTALL)
    return match.group(1) if match else None


def make_solve_wrapper(solve_fn, qwen_client, system_prompt, user_prompt_template):
    """Wrap the solve function with concrete model-calling functions.
    System prompt is locked to the optimized stage 2 prompt — can't be overridden."""

    def call_model(prompt, **kwargs):
        # Ignore any system= override from GPT's code
        results = call_qwen(qwen_client, prompt, system=system_prompt, n=1)
        return results[0]

    def call_model_n(prompt, n=20, **kwargs):
        # Ignore any system= override from GPT's code
        return call_qwen(qwen_client, prompt, system=system_prompt, n=n)

    def wrapped_solve(problem_text):
        return solve_fn(problem_text, call_model, call_model_n)

    return wrapped_solve


def evaluate(solve_wrapped, problems):
    results = []
    for prob in problems:
        print(f"  {prob['id']}...", end=" ", flush=True)
        try:
            answer = solve_wrapped(prob["text"])
        except Exception as e:
            print(f"ERROR: {e}")
            answer = None

        correct = 1 if answer == prob["answer"] else 0
        print(f"got={answer}, expected={prob['answer']} {'OK' if correct else 'WRONG'}")
        results.append({
            "id": prob["id"],
            "expected": prob["answer"],
            "selected": answer,
            "pass_at_1": float(correct),
            "correct": correct,
            "total": 1,
        })
    return results


def run(stage1_results=None):
    qwen = get_qwen_client()
    gpt = get_openai_client()

    system_prompt, user_prompt_template = get_stage2_prompt()
    print(f"Using stage 2 prompt: {system_prompt[:80]}...")

    # Get train data
    train_data_str, train_completions = make_train_data(qwen, system_prompt, user_prompt_template)

    # Iterate: GPT-5.2 designs the solve function
    best_fn = None
    best_code = None
    best_score = -1
    previous_attempt = ""

    for iteration in range(N_ITERATIONS):
        print(f"\n--- Strategy iteration {iteration + 1}/{N_ITERATIONS} ---")

        prompt = STRATEGY_SPEC.format(
            train_data=train_data_str,
            previous_attempt=previous_attempt,
        )
        response = call_gpt(gpt, [{"role": "user", "content": prompt}])
        code = extract_code(response)

        if not code:
            print("  Failed to extract code from GPT response")
            continue

        try:
            namespace = {}
            exec(code, namespace)
            solve_fn = namespace["solve"]
        except Exception as e:
            print(f"  Failed to load solve function: {e}")
            traceback.print_exc()
            continue

        solve_wrapped = make_solve_wrapper(solve_fn, qwen, system_prompt, user_prompt_template)

        print("  Testing on train set...")
        train_results = evaluate(solve_wrapped, TRAIN)
        train_score = sum(r["pass_at_1"] for r in train_results) / len(train_results)
        correct_ids = [r["id"] for r in train_results if r["correct"]]
        wrong = [(r["id"], r["selected"], r["expected"]) for r in train_results if not r["correct"]]
        print(f"  Train: {len(correct_ids)}/15 = {train_score:.3f}")

        previous_attempt = (
            f"PREVIOUS ATTEMPT (iteration {iteration + 1}, score={train_score:.3f}):\n"
            f"Correct: {correct_ids}\n"
            f"Wrong (id, got, expected): {wrong}\n\n"
            f"Previous code:\n```python\n{code}\n```"
        )

        if train_score >= best_score:
            best_fn = solve_fn
            best_code = code
            best_score = train_score
            print("  -> New best!")

    if not best_fn:
        print("No working strategy produced!")
        return [], 0.0

    # Final test evaluation
    print(f"\n{'=' * 60}")
    print(f"Best strategy (train: {best_score:.3f})")
    solve_wrapped = make_solve_wrapper(best_fn, qwen, system_prompt, user_prompt_template)
    test_results = evaluate(solve_wrapped, TEST)
    test_avg = print_scores("Stage 3: Code harness (test set)", test_results)

    save_results({
        "best_code": best_code,
        "best_train_score": best_score,
        "test_results": test_results,
        "test_avg": test_avg,
    }, "results/stage3.json")

    return test_results, test_avg


if __name__ == "__main__":
    run()
