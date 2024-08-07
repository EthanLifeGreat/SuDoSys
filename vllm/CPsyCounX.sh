#!/usr/bin/bash -x

#
# Before running, make sure you have read the README in CPsyCounX_API_server.
#

# Change directory so that the transformer package can find the correct path of the fine-tuned model.
cd vllm/CPsyCounX_API_server || exit

# Start the server at local IP:8010 with GPU 0.
/mnt/shareEEx/chenyixiang/miniconda3/envs/AuPC/bin/python web-backend.py --port 8010 --device cuda:0
