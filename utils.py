"""
Shared helpers: call models, extract answers, score results.
"""

import json
import os
import re
from openai import OpenAI


def get_qwen_client():
    """Client pointed at the local vLLM server."""
    endpoint = open("vllm_endpoint.txt").read().strip()
    return OpenAI(base_url=f"http://{endpoint}/v1", api_key="unused")


def get_openai_client():
    """Client for GPT-5.2 via OpenAI API."""
    return OpenAI()  # uses OPENAI_API_KEY env var


QWEN_MODEL = "Qwen/Qwen2.5-7B-Instruct"


def call_qwen(client, prompt, system="You are a helpful assistant.", n=1, temperature=0.7, max_tokens=2048):
    """Call Qwen via vLLM. Returns list of completion strings."""
    response = client.chat.completions.create(
        model=QWEN_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        n=n,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return [choice.message.content for choice in response.choices]


def call_gpt(client, messages, model="gpt-5.2", max_tokens=16384):
    """Call GPT-5.2 via OpenAI API. Returns the response string."""
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_completion_tokens=max_tokens,
    )
    return response.choices[0].message.content


def extract_answer(text):
    """Pull integer from <answer>...</answer> tags. Returns int or None."""
    match = re.search(r"<answer>\s*(\d+)\s*</answer>", text)
    if match:
        return int(match.group(1))
    return None


def score_completions(completions, correct_answer):
    """
    Given a list of completion strings and the correct answer,
    return pass@1: fraction of completions that got the right answer.
    """
    extracted = [extract_answer(c) for c in completions]
    correct = sum(1 for a in extracted if a == correct_answer)
    return correct / len(completions)


def save_results(results, path):
    """Save results dict to JSON."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(results, f, indent=2)


def print_scores(stage_name, results):
    """Print a nice summary table."""
    print(f"\n{'=' * 60}")
    print(f"  {stage_name}")
    print(f"{'=' * 60}")
    for r in results:
        status = "✓" if r["pass_at_1"] > 0 else "✗"
        print(f"  {status} {r['id']:>12s}  pass@1={r['pass_at_1']:.2f}  "
              f"(correct={r['correct']}/{r['total']})  answer={r['expected']}")
    avg = sum(r["pass_at_1"] for r in results) / len(results)
    print(f"{'─' * 60}")
    print(f"  Average pass@1: {avg:.3f}")
    print(f"{'=' * 60}")
    return avg
