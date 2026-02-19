# LLM Basics

A foundational overview of Large Language Models and their architecture.

## Core Concepts

### What is an LLM?
- Statistical language models trained on massive text corpora
- Predict the next token in a sequence based on context
- No explicit programming - learns patterns from data

### Transformer Architecture
- Introduced in "Attention Is All You Need" (Vaswani et al., 2017)
- Self-attention机制 -每个词关注序列中其他词
- Feed-forward networks process context

### Key Components
- Embeddings: Convert tokens to vectors
- Attention mechanisms: Weight relationships between tokens
- Layers: Multiple transformer blocks stacked
- Output projection: Translate hidden states to token probabilities

## Types of LLMs

### Encoder-Only
- BERT-style models
- Best for classification, extraction tasks
- Bidirectional context

### Decoder-Only
- GPT-style models
- Best for generation, conversation
- Causal (left-to-right) attention

### Encoder-Decoder
- T5-style models
- Best for translation, summarization
- Bidirectional input, causal output

## Training Process

### Pre-training
- Masked language modeling (BERT)
- Causal language modeling (GPT)
- Self-supervised from web-scale corpora

### Fine-tuning
- Supervised learning on labeled data
- Reinforcement learning from human feedback (RLHF)
- Direct preference optimization (DPO)

## Limitations

- No true understanding - pattern matching only
-hallucinations - confident but incorrect outputs
- Context window limits
- Biases from training data