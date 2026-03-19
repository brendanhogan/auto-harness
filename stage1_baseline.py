"""
Stage 1: Baseline. Raw Qwen 7B on the train set (AIME 2024 I).
Simple prompt, 20 completions per problem, report pass@1.
"""

from problems import TRAIN
from utils import get_qwen_client, call_qwen, extract_answer, score_completions, save_results, print_scores

SYSTEM_PROMPT = "You are a math competition solver."

USER_PROMPT_TEMPLATE = """Solve this AIME problem. Think step by step inside <reason> tags, then give your final integer answer (0-999) inside <answer> tags.

Problem: {problem}

<reason>
"""

N_COMPLETIONS = 20


def run():
    client = get_qwen_client()
    results = []

    for prob in TRAIN:
        print(f"Running {prob['id']}...")
        prompt = USER_PROMPT_TEMPLATE.format(problem=prob["text"])
        completions = call_qwen(client, prompt, system=SYSTEM_PROMPT, n=N_COMPLETIONS)

        p1 = score_completions(completions, prob["answer"])
        results.append({
            "id": prob["id"],
            "expected": prob["answer"],
            "pass_at_1": p1,
            "correct": sum(1 for c in completions if extract_answer(c) == prob["answer"]),
            "total": N_COMPLETIONS,
            "completions": completions,
        })

    save_results(results, "results/stage1.json")
    avg = print_scores("Stage 1: Baseline (train set)", results)
    return results, avg


if __name__ == "__main__":
    run()
