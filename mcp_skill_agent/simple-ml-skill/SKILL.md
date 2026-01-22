---
name: simple-ml-skill
description: |
  Enables creation of simple ML workflows (data split, model training,
  evaluation). Used when an agent needs to train a quick scikit‑learn
  model on a tabular CSV without writing boilerplate Python code.
---

# Simple ML Skill Overview

This skill provides:

1. **One‑click trainer** (`scripts/train_iris.py`) – trains a Logistic Regression
   classifier on the Iris example dataset (or any small CSV you point it at).  
2. **Reference guide** (`references/README.md`) – explains how to adapt the script,
   supply your own data, and retrieve results.  
3. **Minimal schema** (`references/data_schema.json`) – shows expected column
   layout for the training script.

# When to use this skill

- You need to generate a quick ML model from a CSV without leaving the chat.  
- The task can be expressed as “train a classifier/regressor on a tabular file”.  
- You want reproducible results with deterministic splits (default 80/20).

# How it works internally (for maintainers)

The trainer script executes a scikit‑learn pipeline, saves the trained model as
`model.pkl`, and prints evaluation metrics. All heavy lifting stays inside the
skill; Claude only needs to reference `references/README.md` when details are
requested.

---  

## Scripts (`scripts/`)

| Script | Purpose |
|--------|---------|
| `train_iris.py` | Trains a simple model on `assets/iris_example.csv`. |

---

## References (`references/`)

- **README.md** – step‑by‑step usage instructions (loaded only when requested).  
- **data_schema.json** – example column schema for CSV input.

---

## Assets (`assets/`)

- **iris_example.csv** – tiny dataset bundled with the skill; used as a demo
  when no external file is provided.