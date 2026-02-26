import os
import sys
import json
import subprocess
import argparse
from datasets import load_dataset
from huggingface_hub import snapshot_download

def setup_realkie_data():
    """Downloads the RealKIE FCC Invoices dataset."""
    dataset = load_dataset("amazon-agi/RealKIE-FCC-Verified", split="test")
    return dataset, None

def setup_gaia_data():
    """Downloads GAIA metadata and attachments."""
    # GAIA is a gated dataset; ensure you've run `huggingface-cli login`
    # or set HUGGING_FACE_HUB_TOKEN in your env.
    repo_id = "gaia-benchmark/GAIA"
    data_dir = snapshot_download(repo_id=repo_id, repo_type="dataset")
    
    # Load the 2023 Validation set (Level 1 & 2 are best for initial benchmarks)
    # Choices: "2023_level1", "2023_level2", "2023_level3"
    dataset = load_dataset(data_dir, "2023_level3", split="validation")
    return dataset, data_dir

def run_agent_architecture(agent_dir, question, file_path):
    """
    Spawns the agent runner in a subprocess to prevent module caching conflicts
    between nanobot and nanobot-2.
    """
    runner_script = os.path.join(os.path.dirname(__file__), 'runner.py')
    
    # Build the prompt
    prompt = question
    if file_path:
         prompt += f"\n\nPlease utilize the attached file located here: {file_path}"
    
    workspace_dir = f"/tmp/eval_workspace_{os.path.basename(agent_dir)}"
    
    cmd = [
        "python", runner_script,
        "--agent-dir", agent_dir,
        "--query", prompt,
        "--workspace", workspace_dir
    ]
    
    try:
        # Run subprocess and capture stdout
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        # The runner script prints the JSON result to the last line of stdout
        lines = result.stdout.strip().split('\n')
        for line in reversed(lines):
            if line.startswith('{'):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue
                    
        return {
            "final_answer": "Failed to parse runner output",
            "trajectory": [],
            "raw_output": result.stdout[-500:] # Last 500 chars 
        }
        
    except subprocess.TimeoutExpired:
        return {
            "final_answer": "TIMEOUT EXPIRED (5 minutes)",
            "trajectory": []
        }
    except Exception as e:
         return {
            "final_answer": f"RUNNER EXCEPTION: {str(e)}",
            "trajectory": []
        }

async def llm_judge(dataset_name, gold_answer, res_a, res_b):
    """Uses LLM to evaluate which agent performed better."""
    # Inject nanobot-2 into sys.path to access its local config provider
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(base_dir, "nanobot-2"))
    
    from nanobot.config.loader import load_config
    from nanobot.cli.commands import _make_provider
    config = load_config()
    provider = _make_provider(config)

    sys_prompt = f"You are an expert AI evaluator grading two AI Agents on their execution traces on the {dataset_name} benchmark."
    
    human_prompt = f"""

### Correct Gold Answer:
{gold_answer}

---
### Agent A (Original Nanobot) Output:
Final Answer: {res_a.get('final_answer')}
Trajectory length: {len(res_a.get('trajectory', []))} steps.

### Agent B (Advanced Nanobot-2) Output:
Final Answer: {res_b.get('final_answer')}
Trajectory length: {len(res_b.get('trajectory', []))} steps.
---

Evaluate both agents on a scale of 1-10 based on:
1. Did they arrive at the correct gold answer?
2. Did they display strong workflow orchestration (planning, checking work, avoiding infinite loops)?

Output your evaluation in this exact JSON format:
{{
  "agent_a_score": 0,
  "agent_b_score": 0,
  "winner": "A or B or Tie",
  "reasoning": "brief explanation..."
}}
"""
    try:
        response = await provider.chat(
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": human_prompt}
            ]
        )
        content = response.content.strip()
        if content.startswith("```json"):
             content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        return {"error": str(e), "winner": "Unknown"}

async def async_main(dataset_name: str):
    if dataset_name == "gaia":
        dataset, root_dir = setup_gaia_data()
    else:
        dataset, root_dir = setup_realkie_data()
        
    results = []
    
    # We'll take the first 5 tasks to keep testing realistic time-wise
    test_subset = dataset.select(range(5))

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    agent_a_dir = os.path.join(base_dir, "nanobot")
    agent_b_dir = os.path.join(base_dir, "nanobot-2")

    for item in test_subset:
        if dataset_name == "gaia":
            task_id = item['task_id']
            question = item['Question']
            gold_answer = item['Final answer']
            
            # Handle file attachments if they exist
            attachment = None
            if item.get('file_path'):
                attachment = os.path.join(root_dir, item['file_path'])
        else:
            task_id = str(item['id'])
            question = f"Extract the key information according to this JSON schema:\n{item['json_schema']}\n\nDocument Text:\n{item['text'][:2000]}"
            gold_answer = item['json_response']
            attachment = None
            
        print(f"\nTask: {task_id}")
        print(f"Question: {question}")
        print(f"Gold Answer: {gold_answer}")
        
        print(f"\n==============================")
        print(f"Running Task: {task_id}")
        print(f"==============================")

        print("Running Agent A (Original)...")
        res_a = run_agent_architecture(agent_a_dir, question, attachment)
        
        print("Running Agent B (Advanced)...")
        res_b = run_agent_architecture(agent_b_dir, question, attachment)
        
        print("Running LLM Judge...")
        judge_res = await llm_judge(dataset_name, gold_answer, res_a, res_b)
        
        print(f"Judge Verdict: {judge_res.get('winner')} - A:{judge_res.get('agent_a_score')} B:{judge_res.get('agent_b_score')}")

        results.append({
            "task_id": task_id,
            "question": question,
            "gold_answer": gold_answer,
            "arch_a": res_a,
            "arch_b": res_b,
            "evaluation": judge_res
        })

    # Save for LLM-as-a-Judge analysis
    with open(os.path.join(base_dir, "evalagt", f"benchmark_results_{dataset_name}.json"), "w") as f:
        json.dump(results, f, indent=2)
        
    print("\nBenchmark complete! Results saved to benchmark_results.json")

def main():
    parser = argparse.ArgumentParser(description="Run the evaluation framework.")
    parser.add_argument(
        "--dataset",
        choices=["gaia", "realkie"],
        default="gaia",
        help="Choose the dataset to evaluate against."
    )
    args = parser.parse_args()
    
    import asyncio
    asyncio.run(async_main(args.dataset))

if __name__ == "__main__":
    main()