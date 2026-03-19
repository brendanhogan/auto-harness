"""
Run all three stages of the experiment.

Usage:
    1. Start vLLM:  sbatch start_vllm.sh
    2. Wait for vllm_endpoint.txt to appear
    3. Run:         uv run python run_all.py
"""

import json
import os
import sys
import time
from collections import Counter


def wait_for_vllm():
    """Wait until the vLLM server is ready."""
    endpoint_file = os.path.join(os.path.dirname(__file__), "vllm_endpoint.txt")
    print("Waiting for vllm_endpoint.txt...")
    while not os.path.exists(endpoint_file):
        time.sleep(2)
    endpoint = open(endpoint_file).read().strip()
    print(f"Found endpoint: {endpoint}")
    print("Checking if vLLM is ready...")
    from openai import OpenAI
    client = OpenAI(base_url=f"http://{endpoint}/v1", api_key="unused")
    for attempt in range(60):
        try:
            client.models.list()
            print("vLLM is ready!")
            return
        except Exception:
            time.sleep(5)
    print("ERROR: vLLM did not start within 5 minutes")
    sys.exit(1)


def baseline_majority_vote(problems, completions_dict):
    """Simple majority vote over raw completions."""
    from utils import extract_answer
    results = []
    for prob in problems:
        comps = completions_dict[prob["id"]]
        answers = [extract_answer(c) for c in comps]
        valid = [a for a in answers if a is not None]
        selected = Counter(valid).most_common(1)[0][0] if valid else None
        correct = 1 if selected == prob["answer"] else 0
        results.append({"id": prob["id"], "selected": selected, "expected": prob["answer"], "correct": correct})
    return results


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    wait_for_vllm()

    # Stage 1: Baseline pass@1
    stage1_path = "results/stage1.json"
    if os.path.exists(stage1_path):
        print("\n" + "=" * 60)
        print("  STAGE 1: BASELINE (cached)")
        print("=" * 60)
        stage1_results = json.load(open(stage1_path))
        stage1_avg = sum(r["pass_at_1"] for r in stage1_results) / len(stage1_results)
        print(f"  Train pass@1: {stage1_avg:.3f}")
    else:
        print("\n" + "=" * 60)
        print("  STAGE 1: BASELINE")
        print("=" * 60)
        import stage1_baseline
        stage1_results, stage1_avg = stage1_baseline.run()

    # Baseline on TEST too (majority vote over 20 completions with basic prompt)
    from problems import TEST
    from utils import get_qwen_client, call_qwen, extract_answer
    baseline_test_cache = "results/baseline_test_completions.json"
    if os.path.exists(baseline_test_cache):
        print("  Loading cached baseline test completions...")
        baseline_test_comps = json.load(open(baseline_test_cache))
    else:
        print("  Generating baseline test completions...")
        qwen = get_qwen_client()
        system = "You are a math competition solver."
        user_tmpl = (
            "Solve this AIME problem. Think step by step inside <reason> tags, "
            "then give your final integer answer (0-999) inside <answer> tags.\n\n"
            "Problem: {problem}\n\n<reason>"
        )
        baseline_test_comps = {}
        for prob in TEST:
            print(f"    {prob['id']}...", flush=True)
            prompt = user_tmpl.replace("{problem}", prob["text"])
            comps = call_qwen(qwen, prompt, system=system, n=20)
            baseline_test_comps[prob["id"]] = comps
        from utils import save_results
        save_results(baseline_test_comps, baseline_test_cache)

    # Compute baseline test metrics
    baseline_test_pass1 = []
    for prob in TEST:
        comps = baseline_test_comps[prob["id"]]
        answers = [extract_answer(c) for c in comps]
        correct = sum(1 for a in answers if a == prob["answer"])
        baseline_test_pass1.append(correct / len(comps))
    baseline_test_avg = sum(baseline_test_pass1) / len(baseline_test_pass1)

    baseline_mv = baseline_majority_vote(TEST, baseline_test_comps)
    baseline_mv_score = sum(r["correct"] for r in baseline_mv) / len(baseline_mv)
    print(f"  Baseline test pass@1: {baseline_test_avg:.3f}")
    print(f"  Baseline test maj.vote: {baseline_mv_score:.3f} ({sum(r['correct'] for r in baseline_mv)}/15)")

    # Stage 2: Meta-prompt (cached)
    stage2_path = "results/stage2.json"
    if os.path.exists(stage2_path):
        print("\n" + "=" * 60)
        print("  STAGE 2: META-PROMPT (cached)")
        print("=" * 60)
        s2 = json.load(open(stage2_path))
        stage2_avg = s2["test_avg"]
        print(f"  Test pass@1: {stage2_avg:.3f}")
    else:
        print("\n" + "=" * 60)
        print("  STAGE 2: META-PROMPT OPTIMIZATION")
        print("=" * 60)
        import stage2_metaprompt
        _, stage2_avg = stage2_metaprompt.run(stage1_results)

    # Stage 2 majority vote on test
    s2_test_cache = "results/stage3_test_completions.json"
    if os.path.exists(s2_test_cache):
        s2_test_comps = json.load(open(s2_test_cache))
        s2_mv = baseline_majority_vote(TEST, s2_test_comps)
        s2_mv_score = sum(r["correct"] for r in s2_mv) / len(s2_mv)
        print(f"  Meta-prompt test maj.vote: {s2_mv_score:.3f} ({sum(r['correct'] for r in s2_mv)}/15)")
    else:
        s2_mv_score = None

    # Stage 3: Code harness
    print("\n" + "=" * 60)
    print("  STAGE 3: CODE HARNESS")
    print("=" * 60)
    import stage3_harness
    stage3_results, stage3_avg = stage3_harness.run(stage1_results)

    # Final summary
    print("\n" + "=" * 60)
    print("  FINAL RESULTS (all on test set, AIME 2024 II)")
    print("=" * 60)
    print(f"{'Stage':<35s} | {'Score':>7s}")
    print("-" * 50)
    print(f"{'1. Baseline pass@1':<35s} | {baseline_test_avg:>7.3f}")
    print(f"{'1. Baseline maj. vote':<35s} | {baseline_mv_score:>7.3f}")
    print(f"{'2. Meta-prompt pass@1':<35s} | {stage2_avg:>7.3f}")
    if s2_mv_score is not None:
        print(f"{'2. Meta-prompt maj. vote':<35s} | {s2_mv_score:>7.3f}")
    print(f"{'3. GPT-designed strategy':<35s} | {stage3_avg:>7.3f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
