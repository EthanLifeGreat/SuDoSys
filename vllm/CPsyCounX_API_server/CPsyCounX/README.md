# README for SuDoSys
Copy all files in [CPsyCounX](https://huggingface.co/CAS-SIAT-XinHai/CPsyCounX) to this folder. (Model files are too large to upload.)
Then run CPsyCounX.sh in the parent folder to start the API server.
Note that you can run model_class.py to test CPsyCounX locally.


# Original README
---
license: apache-2.0
base_model: internlm/internlm2-chat-7b
datasets:
- CAS-SIAT-XinHai/CPsyCoun
language:
- zh
---

# CPsyCounX

This model is a fine-tuned version of [internlm/internlm2-chat-7b](https://huggingface.co/internlm/internlm2-chat-7b) on the [CPsyCounD](https://huggingface.co/datasets/CAS-SIAT-XinHai/CPsyCoun) dataset.

## Model description

**CPsyCounX** is a large language model designed for Chinese Psychological Counseling.

## Training and evaluation data

- Train: [CPsyCounD](https://huggingface.co/datasets/CAS-SIAT-XinHai/CPsyCoun) 
- Evaluate: [CPsyCounE](https://github.com/CAS-SIAT-XinHai/CPsyCoun/tree/main/CPsyCounE)

## Training procedure

### Training hyperparameters

The following hyperparameters were used during training:
- learning_rate: 1e-06
- train_batch_size: 4
- eval_batch_size: 8
- seed: 42
- distributed_type: multi-GPU
- num_devices: 4
- gradient_accumulation_steps: 28
- total_train_batch_size: 448
- total_eval_batch_size: 32
- optimizer: Adam with betas=(0.9,0.999) and epsilon=1e-08
- lr_scheduler_type: cosine
- num_epochs: 9.0
- mixed_precision_training: Native AMP

### Training results



### Framework versions

- Transformers 4.37.1
- Pytorch 2.1.2+cu121
- Datasets 2.16.1
- Tokenizers 0.15.1