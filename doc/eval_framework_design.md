# Agent Evaluation Framework Design

## Objective

Create an `eval/` folder to systematically test different agents' performance on command inputs and measure success rates.

---

## Part 1: Open-Source Benchmark Research

### Existing Frameworks Comparison

| Framework | Focus | Key Metrics | License |
|-----------|-------|-------------|---------|
| **DeepEval** | LLM evaluation | Task Completion, Tool Correctness | Apache 2.0 |
| **AgentBench** | Multi-domain agents | Success rate across 8 environments | MIT |
| **SWE-bench** | Coding agents | Resolve Rate (% tests pass) | MIT |
| **τ-bench** | Tool-agent-user | Pass@K Reliability | MIT |
| **OSWorld** | OS automation | Task completion in real OS | Apache 2.0 |

### What We Can Learn

| Source | Principle | Apply To Our System |
|--------|-----------|---------------------|
| **DeepEval** | Pytest integration | Use pytest for test harness |
| **AgentBench** | Containerized environments | Docker for isolated runs |
| **SWE-bench** | Resolve rate = tests pass | Define expected outputs per test |
| **τ-bench** | Pass@K (run K times) | Statistical reliability metric |

---

## Part 2: Proposed Architecture

### Directory Structure

```
mcp_skill_agent/
├── eval/
│   ├── __init__.py
│   ├── runner.py              # Main evaluation runner
│   ├── metrics.py             # Success rate, tool accuracy, latency
│   ├── test_cases/
│   │   ├── __init__.py
│   │   ├── file_operations.yaml    # Test: create, read, edit files
│   │   ├── web_artifact.yaml       # Test: init-artifact, bundle
│   │   ├── shell_commands.yaml     # Test: execute_command accuracy
│   │   └── skill_execution.yaml    # Test: skill invocation
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py            # Abstract agent interface
│   │   ├── mcp_agent.py       # Our MCP skill agent
│   │   └── baseline.py        # Simple baseline for comparison
│   ├── results/
│   │   └── .gitkeep           # Store evaluation results (JSON)
│   └── reports/
│       └── .gitkeep           # Generated HTML/MD reports
```

### Test Case Format (YAML)

```yaml
# eval/test_cases/file_operations.yaml
name: "File Operations Suite"
description: "Test basic file read/write/edit capabilities"

test_cases:
  - id: "file_001"
    name: "Create and read file"
    command: "Create a file called test.txt with content 'Hello World', then read it back"
    expected_artifacts:
      - path: "test.txt"
        contains: "Hello World"
    max_tool_calls: 5
    timeout_seconds: 60

  - id: "file_002"
    name: "Edit existing file"
    setup:
      - create_file: { path: "edit_me.txt", content: "Original content" }
    command: "Change 'Original' to 'Modified' in edit_me.txt"
    expected_artifacts:
      - path: "edit_me.txt"
        contains: "Modified content"
        not_contains: "Original"
    max_tool_calls: 3
    timeout_seconds: 30

  - id: "web_001"
    name: "Initialize web artifact"
    command: "Create a new React web artifact called 'demo-app' using the web-artifacts-builder skill"
    expected_artifacts:
      - path: "demo-app/package.json"
        exists: true
      - path: "demo-app/src/App.tsx"
        exists: true
    max_tool_calls: 10
    timeout_seconds: 180
```

---

## Part 3: Core Metrics

### Primary Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| **Success Rate** | `passed / total × 100%` | % of tests fully completed |
| **Tool Accuracy** | `correct_calls / total_calls × 100%` | % of tool calls that succeeded |
| **Efficiency** | `optimal_calls / actual_calls × 100%` | How close to optimal tool count |
| **Latency** | `end_time - start_time` | Time to complete task |
| **Pass@K** | `1 - (failures/K)^K` | Reliability over K runs |

### Secondary Metrics

| Metric | Description |
|--------|-------------|
| **Recovery Rate** | % of times agent recovered from errors |
| **Redundancy Score** | # of repeated tool calls for same purpose |
| **CWD Stability** | # of times wrong working directory used |
| **Crash Rate** | % of runs that caused MCP server crash |

---

## Part 4: Implementation Plan

### Phase 1: Core Infrastructure (MVP)

1. **`eval/runner.py`** - Load test cases, run agent, collect results
2. **`eval/metrics.py`** - Calculate success rate, latency
3. **`eval/agents/base.py`** - Abstract agent interface
4. **`eval/test_cases/file_operations.yaml`** - 5 basic test cases

### Phase 2: Agent Integration

1. **`eval/agents/mcp_agent.py`** - Wrap our MCP skill agent
2. **`eval/agents/baseline.py`** - Simple hardcoded baseline
3. Add timeout handling and crash recovery

### Phase 3: Reporting

1. **JSON results** - Machine-readable output
2. **Markdown reports** - Human-readable summaries
3. **Comparison tables** - Multi-agent comparison

### Phase 4: Advanced

1. **Docker isolation** - Run tests in containers
2. **Pass@K evaluation** - Run same test K times
3. **CI integration** - Run on every PR

---

## Part 5: API Design

### Runner Interface

```python
# eval/runner.py
from dataclasses import dataclass
from typing import List, Dict
import yaml

@dataclass
class TestResult:
    test_id: str
    passed: bool
    tool_calls: int
    latency_seconds: float
    error_message: str | None
    artifacts_verified: Dict[str, bool]

class EvalRunner:
    def __init__(self, agent: "BaseAgent", test_suite: str):
        self.agent = agent
        self.test_cases = self._load_test_cases(test_suite)
    
    def run_all(self) -> List[TestResult]:
        """Run all test cases and return results."""
        results = []
        for test in self.test_cases:
            result = self._run_single(test)
            results.append(result)
        return results
    
    def _run_single(self, test: dict) -> TestResult:
        """Run a single test case."""
        # Setup (if any)
        self._setup_test(test.get("setup", []))
        
        # Execute
        start = time.time()
        tool_calls, error = self.agent.execute(test["command"])
        latency = time.time() - start
        
        # Verify
        artifacts_ok = self._verify_artifacts(test.get("expected_artifacts", []))
        
        return TestResult(
            test_id=test["id"],
            passed=all(artifacts_ok.values()) and error is None,
            tool_calls=tool_calls,
            latency_seconds=latency,
            error_message=error,
            artifacts_verified=artifacts_ok
        )
```

### Agent Interface

```python
# eval/agents/base.py
from abc import ABC, abstractmethod
from typing import Tuple

class BaseAgent(ABC):
    @abstractmethod
    def execute(self, command: str) -> Tuple[int, str | None]:
        """
        Execute a command and return (tool_call_count, error_or_none).
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset agent state between tests."""
        pass
```

---

## Part 6: CLI Usage

```bash
# Run all tests
python -m eval.runner --agent mcp --suite file_operations

# Run specific test
python -m eval.runner --agent mcp --test file_001

# Run with K repetitions for reliability
python -m eval.runner --agent mcp --suite all --pass-k 5

# Compare agents
python -m eval.runner --agents mcp,baseline --suite all --compare

# Generate report
python -m eval.runner --agent mcp --suite all --report markdown
```

---

## Decision Points for User

1. **Test isolation**: Use Docker containers or temp directories?
2. **Agent comparison**: Which other agents to benchmark against?
3. **CI integration**: Add to GitHub Actions workflow?
4. **Metrics priority**: Which metrics are most important for v1?
