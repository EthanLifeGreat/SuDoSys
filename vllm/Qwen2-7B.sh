#!/usr/bin/bash -x
echo "which python: $(which python)"

# Set model path to the path containing config.json et. al.
export MODEL_PATH=/mnt/shareEEx/chenyixiang/.cache/modelscope/hub/qwen/Qwen2-7B-Instruct
echo "MODEL_PATH: $MODEL_PATH"

# Set NCCL path to the .so file
export VLLM_NCCL_SO_PATH=/mnt/shareEEx/chenyixiang/Qwen/nccl_2.22.3-1+cuda12.2_x86_64/lib/libnccl.so
echo "VLLM_NCCL_SO_PATH: $VLLM_NCCL_SO_PATH"

# Start the API server on local IP:8007 with 4 GPUs.
CUDA_VISIBLE_DEVICES=0,1,2,3 python -m vllm.entrypoints.openai.api_server \
--model "$MODEL_PATH" \
--served-model-name Qwen2-7B-Instruct \
--tensor-parallel-size 4 \
--host 0.0.0.0 --port 8007 \
--gpu-memory-utilization 0.99 \
--max-model-len 8192
