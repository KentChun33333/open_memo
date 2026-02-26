# EvalAgt: Agent Evaluator Framework

This directory contains the testing and evaluation framework for benchmarking the `nanobot` agents using the GAIA dataset. It currently compares the performance of the original `nanobot` against the advanced, orchestration-focused `nanobot-2`.

## Architecture

Because both agents use the same python module namespace (`nanobot.*`), attempting to run them in the exact same process leads to caching and import conflicts. To solve this, the framework uses an isolated runner approach:

- `main.py`: The root orchestrator. It downloads the GAIA benchmark dataset, extracts the challenges, spawns the runners, and passes the results to an LLM evaluator (GPT-4o) to determine the winner based on reasoning and task completion.
- `runner.py`: A lightweight CLI utility that accepts an `--agent-dir` path. It prepends that exact directory to `sys.path`, loads the local configuration (`~/.nanobot/config`), and executes the agent synchronously, dumping out its internal trajectory (thoughts and tool calls) alongside its final answer as JSON.

## Prerequisites

1. **Hugging Face Token**: The GAIA dataset is gated. If you have not cached it locally, make sure you have authenticated via `huggingface-cli login` or exported your `HUGGING_FACE_HUB_TOKEN`.
2. **LLM Judge Setup**: The `-main.py` script currently leverages `OpenAIProvider(model="gpt-4o")` to act as the AI Judge. Ensure `OPENAI_API_KEY` is present in your environment. (This is distinct from the runner config, which uses whatever local `nanobot` settings you have configured via `onboard`).

## Usage

From the root `openmemo` workspace directory, run:

```bash
python evalagt/main.py
```

The script will:
1. Fetch the first 5 test queries from the GAIA Validation (Level 1) set.
2. Spin up `nanobot` to solve it.
3. Spin up `nanobot-2` to solve it.
4. Pass both execution traces to the LLM Judge.
5. Print the verdict to the console and save full logs to `evalagt/benchmark_results.json`.
