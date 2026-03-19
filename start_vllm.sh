#!/bin/bash
#SBATCH --job-name=vllm-qwen
#SBATCH --partition=h100
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=4:00:00
#SBATCH --output=slurm_vllm_%j.log

cd /mnt/home/brendan/aime_meta

# Write endpoint file so experiment scripts can find us
HOSTNAME=$(hostname)
PORT=8234
echo "${HOSTNAME}:${PORT}" > vllm_endpoint.txt
echo "vLLM starting on ${HOSTNAME}:${PORT}"

# Start vLLM server (uv will create venv and install deps from pyproject.toml)
uv run python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --host 0.0.0.0 \
    --port ${PORT} \
    --max-model-len 4096
