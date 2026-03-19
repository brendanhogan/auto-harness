"""
Stage 2: Meta-prompt optimization.
GPT-5.2 looks at Qwen's failures on the train set and iterates on the prompt.
Best prompt is frozen, then evaluated on the test set.
"""

import json
from problems import TRAIN, TEST
from utils import (
    get_qwen_client, get_openai_client, call_qwen, call_gpt,
    extract_answer, score_completions, save_results, print_scores,
)

N_COMPLETIONS = 20
N_ITERATIONS = 3
# During optimization, use fewer completions to save time
N_OPT_COMPLETIONS = 3

META_PROMPT = """You are an expert prompt engineer. A 7-billion-parameter language model (Qwen 2.5 7B) is being used to solve AIME math competition problems.

Below is the current system prompt and user prompt template being used, followed by the model's results on 15 training problems. Your job: improve the prompts to help this small model solve more problems correctly.

You can change:
- The system prompt (persona, instructions, strategies)
- The user prompt template (must keep {{problem}} placeholder and <answer> tags for the final integer)
- Add few-shot examples, chain-of-thought instructions, specific math strategies, etc.

Keep in mind this is a SMALL model. It benefits from:
- Very explicit step-by-step instructions
- Reminders to check its work
- Specific strategies for different problem types
- Being told to try multiple approaches if stuck

CURRENT SYSTEM PROMPT:
```
{system_prompt}
```

CURRENT USER PROMPT TEMPLATE:
```
{user_prompt}
```

RESULTS (pass@1 over {n_opt} completions):
{results_summary}

Return your improved prompts in this exact format:

<system_prompt>
Your improved system prompt here
</system_prompt>

<user_prompt>
Your improved user prompt template here (must contain {{problem}} and <answer> tags)
</user_prompt>

Brief explanation of what you changed and why:"""


def summarize_results(results, problems):
    """Create a summary of what the model got right/wrong."""
    lines = []
    for r, p in zip(results, problems):
        extracted = [extract_answer(c) for c in r["completions"]]
        lines.append(
            f"Problem {p['id']}: correct_answer={p['answer']}, "
            f"pass@1={r['pass_at_1']:.2f}, "
            f"model_answers={extracted}"
        )
        # Show one failed attempt if it got it wrong
        if r["pass_at_1"] < 1.0:
            for c in r["completions"]:
                if extract_answer(c) != p["answer"]:
                    # Truncate to first 500 chars to keep context manageable
                    lines.append(f"  Example failed reasoning: {c[:500]}...")
                    break
    return "\n".join(lines)


def extract_prompts(response):
    """Parse GPT's response for the new prompts."""
    import re
    sys_match = re.search(r"<system_prompt>\s*(.*?)\s*</system_prompt>", response, re.DOTALL)
    usr_match = re.search(r"<user_prompt>\s*(.*?)\s*</user_prompt>", response, re.DOTALL)
    if not sys_match or not usr_match:
        return None, None
    return sys_match.group(1), usr_match.group(1)


def evaluate(qwen_client, system_prompt, user_prompt_template, problems, n_completions):
    """Run Qwen on a set of problems with given prompts."""
    results = []
    for prob in problems:
        prompt = user_prompt_template.replace("{problem}", prob["text"])
        completions = call_qwen(
            qwen_client, prompt, system=system_prompt, n=n_completions
        )
        p1 = score_completions(completions, prob["answer"])
        results.append({
            "id": prob["id"],
            "expected": prob["answer"],
            "pass_at_1": p1,
            "correct": sum(1 for c in completions if extract_answer(c) == prob["answer"]),
            "total": n_completions,
            "completions": completions,
        })
    return results


def run(stage1_results=None):
    qwen = get_qwen_client()
    gpt = get_openai_client()

    # Start with the baseline prompt
    best_system = "You are a math competition solver."
    best_user = (
        "Solve this AIME problem. Think step by step inside <reason> tags, "
        "then give your final integer answer (0-999) inside <answer> tags.\n\n"
        "Problem: {problem}\n\n<reason>"
    )

    # If we have stage 1 results, use them; otherwise run baseline
    if stage1_results:
        current_results = stage1_results
    else:
        print("Running initial evaluation on train set...")
        current_results = evaluate(qwen, best_system, best_user, TRAIN, N_OPT_COMPLETIONS)

    best_score = sum(r["pass_at_1"] for r in current_results) / len(current_results)
    print(f"Starting score: {best_score:.3f}")

    all_iterations = []

    for iteration in range(N_ITERATIONS):
        print(f"\n--- Iteration {iteration + 1}/{N_ITERATIONS} ---")

        # Ask GPT to improve the prompt
        summary = summarize_results(current_results, TRAIN)
        meta = META_PROMPT.format(
            system_prompt=best_system,
            user_prompt=best_user,
            n_opt=N_OPT_COMPLETIONS,
            results_summary=summary,
        )

        gpt_response = call_gpt(gpt, [{"role": "user", "content": meta}])
        new_system, new_user = extract_prompts(gpt_response)

        if not new_system or not new_user:
            print("  Failed to parse GPT response, skipping iteration")
            continue

        # Test the new prompt on train set (quick eval)
        print("  Evaluating new prompt on train set...")
        new_results = evaluate(qwen, new_system, new_user, TRAIN, N_OPT_COMPLETIONS)
        new_score = sum(r["pass_at_1"] for r in new_results) / len(new_results)
        print(f"  New score: {new_score:.3f} (best: {best_score:.3f})")

        all_iterations.append({
            "iteration": iteration + 1,
            "system_prompt": new_system,
            "user_prompt": new_user,
            "train_score": new_score,
            "gpt_explanation": gpt_response.split("Brief explanation")[-1] if "Brief explanation" in gpt_response else "",
        })

        if new_score >= best_score:
            print("  -> New best! Keeping this prompt.")
            best_system = new_system
            best_user = new_user
            best_score = new_score
            current_results = new_results

    # Final evaluation: test set with full completions
    print(f"\n{'=' * 60}")
    print(f"Best train score: {best_score:.3f}")
    print(f"Best system prompt: {best_system[:100]}...")
    print(f"Evaluating on TEST set with {N_COMPLETIONS} completions...")

    test_results = evaluate(qwen, best_system, best_user, TEST, N_COMPLETIONS)
    test_avg = print_scores("Stage 2: Meta-prompt (test set)", test_results)

    save_results({
        "best_system_prompt": best_system,
        "best_user_prompt": best_user,
        "best_train_score": best_score,
        "iterations": all_iterations,
        "test_results": test_results,
        "test_avg": test_avg,
    }, "results/stage2.json")

    return test_results, test_avg


if __name__ == "__main__":
    run()
