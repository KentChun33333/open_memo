import{j as e}from"./index-DL95azgn.js";const i={title:"Agent Evaluation Framework Design",date:"2026-01-25",tags:["architecture","agent","analysis"],summary:"An analysis report on agent architecture."};function t(s){const n={code:"code",h1:"h1",h2:"h2",h3:"h3",hr:"hr",li:"li",ol:"ol",p:"p",pre:"pre",strong:"strong",table:"table",tbody:"tbody",td:"td",th:"th",thead:"thead",tr:"tr",...s.components};return e.jsxs(e.Fragment,{children:[e.jsx(n.h1,{children:"Agent Evaluation Framework Design"}),`
`,e.jsx(n.h2,{children:"Objective"}),`
`,e.jsxs(n.p,{children:["Create an ",e.jsx(n.code,{children:"eval/"})," folder to systematically test different agents' performance on command inputs and measure success rates."]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Part 1: Open-Source Benchmark Research"}),`
`,e.jsx(n.h3,{children:"Existing Frameworks Comparison"}),`
`,e.jsxs(n.table,{children:[e.jsx(n.thead,{children:e.jsxs(n.tr,{children:[e.jsx(n.th,{children:"Framework"}),e.jsx(n.th,{children:"Focus"}),e.jsx(n.th,{children:"Key Metrics"}),e.jsx(n.th,{children:"License"})]})}),e.jsxs(n.tbody,{children:[e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"DeepEval"})}),e.jsx(n.td,{children:"LLM evaluation"}),e.jsx(n.td,{children:"Task Completion, Tool Correctness"}),e.jsx(n.td,{children:"Apache 2.0"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"AgentBench"})}),e.jsx(n.td,{children:"Multi-domain agents"}),e.jsx(n.td,{children:"Success rate across 8 environments"}),e.jsx(n.td,{children:"MIT"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"SWE-bench"})}),e.jsx(n.td,{children:"Coding agents"}),e.jsx(n.td,{children:"Resolve Rate (% tests pass)"}),e.jsx(n.td,{children:"MIT"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"τ-bench"})}),e.jsx(n.td,{children:"Tool-agent-user"}),e.jsx(n.td,{children:"Pass@K Reliability"}),e.jsx(n.td,{children:"MIT"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"OSWorld"})}),e.jsx(n.td,{children:"OS automation"}),e.jsx(n.td,{children:"Task completion in real OS"}),e.jsx(n.td,{children:"Apache 2.0"})]})]})]}),`
`,e.jsx(n.h3,{children:"What We Can Learn"}),`
`,e.jsxs(n.table,{children:[e.jsx(n.thead,{children:e.jsxs(n.tr,{children:[e.jsx(n.th,{children:"Source"}),e.jsx(n.th,{children:"Principle"}),e.jsx(n.th,{children:"Apply To Our System"})]})}),e.jsxs(n.tbody,{children:[e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"DeepEval"})}),e.jsx(n.td,{children:"Pytest integration"}),e.jsx(n.td,{children:"Use pytest for test harness"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"AgentBench"})}),e.jsx(n.td,{children:"Containerized environments"}),e.jsx(n.td,{children:"Docker for isolated runs"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"SWE-bench"})}),e.jsx(n.td,{children:"Resolve rate = tests pass"}),e.jsx(n.td,{children:"Define expected outputs per test"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"τ-bench"})}),e.jsx(n.td,{children:"Pass@K (run K times)"}),e.jsx(n.td,{children:"Statistical reliability metric"})]})]})]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Part 2: Proposed Architecture"}),`
`,e.jsx(n.h3,{children:"Directory Structure"}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{children:`mcp_skill_agent/
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
`})}),`
`,e.jsx(n.h3,{children:"Test Case Format (YAML)"}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-yaml",children:`# eval/test_cases/file_operations.yaml
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
`})}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Part 3: Core Metrics"}),`
`,e.jsx(n.h3,{children:"Primary Metrics"}),`
`,e.jsxs(n.table,{children:[e.jsx(n.thead,{children:e.jsxs(n.tr,{children:[e.jsx(n.th,{children:"Metric"}),e.jsx(n.th,{children:"Formula"}),e.jsx(n.th,{children:"Description"})]})}),e.jsxs(n.tbody,{children:[e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Success Rate"})}),e.jsx(n.td,{children:e.jsx(n.code,{children:"passed / total × 100%"})}),e.jsx(n.td,{children:"% of tests fully completed"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Tool Accuracy"})}),e.jsx(n.td,{children:e.jsx(n.code,{children:"correct_calls / total_calls × 100%"})}),e.jsx(n.td,{children:"% of tool calls that succeeded"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Efficiency"})}),e.jsx(n.td,{children:e.jsx(n.code,{children:"optimal_calls / actual_calls × 100%"})}),e.jsx(n.td,{children:"How close to optimal tool count"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Latency"})}),e.jsx(n.td,{children:e.jsx(n.code,{children:"end_time - start_time"})}),e.jsx(n.td,{children:"Time to complete task"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Pass@K"})}),e.jsx(n.td,{children:e.jsx(n.code,{children:"1 - (failures/K)^K"})}),e.jsx(n.td,{children:"Reliability over K runs"})]})]})]}),`
`,e.jsx(n.h3,{children:"Secondary Metrics"}),`
`,e.jsxs(n.table,{children:[e.jsx(n.thead,{children:e.jsxs(n.tr,{children:[e.jsx(n.th,{children:"Metric"}),e.jsx(n.th,{children:"Description"})]})}),e.jsxs(n.tbody,{children:[e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Recovery Rate"})}),e.jsx(n.td,{children:"% of times agent recovered from errors"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Redundancy Score"})}),e.jsx(n.td,{children:"# of repeated tool calls for same purpose"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"CWD Stability"})}),e.jsx(n.td,{children:"# of times wrong working directory used"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Crash Rate"})}),e.jsx(n.td,{children:"% of runs that caused MCP server crash"})]})]})]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Part 4: Implementation Plan"}),`
`,e.jsx(n.h3,{children:"Phase 1: Core Infrastructure (MVP)"}),`
`,e.jsxs(n.ol,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:e.jsx(n.code,{children:"eval/runner.py"})})," - Load test cases, run agent, collect results"]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:e.jsx(n.code,{children:"eval/metrics.py"})})," - Calculate success rate, latency"]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:e.jsx(n.code,{children:"eval/agents/base.py"})})," - Abstract agent interface"]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:e.jsx(n.code,{children:"eval/test_cases/file_operations.yaml"})})," - 5 basic test cases"]}),`
`]}),`
`,e.jsx(n.h3,{children:"Phase 2: Agent Integration"}),`
`,e.jsxs(n.ol,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:e.jsx(n.code,{children:"eval/agents/mcp_agent.py"})})," - Wrap our MCP skill agent"]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:e.jsx(n.code,{children:"eval/agents/baseline.py"})})," - Simple hardcoded baseline"]}),`
`,e.jsx(n.li,{children:"Add timeout handling and crash recovery"}),`
`]}),`
`,e.jsx(n.h3,{children:"Phase 3: Reporting"}),`
`,e.jsxs(n.ol,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"JSON results"})," - Machine-readable output"]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Markdown reports"})," - Human-readable summaries"]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Comparison tables"})," - Multi-agent comparison"]}),`
`]}),`
`,e.jsx(n.h3,{children:"Phase 4: Advanced"}),`
`,e.jsxs(n.ol,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Docker isolation"})," - Run tests in containers"]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Pass@K evaluation"})," - Run same test K times"]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"CI integration"})," - Run on every PR"]}),`
`]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Part 5: API Design"}),`
`,e.jsx(n.h3,{children:"Runner Interface"}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`# eval/runner.py
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
`})}),`
`,e.jsx(n.h3,{children:"Agent Interface"}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`# eval/agents/base.py
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
`})}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Part 6: CLI Usage"}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-bash",children:`# Run all tests
python -m eval.runner --agent mcp --suite file_operations

# Run specific test
python -m eval.runner --agent mcp --test file_001

# Run with K repetitions for reliability
python -m eval.runner --agent mcp --suite all --pass-k 5

# Compare agents
python -m eval.runner --agents mcp,baseline --suite all --compare

# Generate report
python -m eval.runner --agent mcp --suite all --report markdown
`})}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Decision Points for User"}),`
`,e.jsxs(n.ol,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Test isolation"}),": Use Docker containers or temp directories?"]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Agent comparison"}),": Which other agents to benchmark against?"]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"CI integration"}),": Add to GitHub Actions workflow?"]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Metrics priority"}),": Which metrics are most important for v1?"]}),`
`]})]})}function l(s={}){const{wrapper:n}=s.components||{};return n?e.jsx(n,{...s,children:e.jsx(t,{...s})}):t(s)}export{l as default,i as frontmatter};
