# Prompt Engineering

Techniques for effectively communicating with LLMs.

## Core Principles

### Clarity and Specificity
- Be explicit about what you want
- Include context and constraints
- Specify format explicitly

### Chain of Thought
- Break complex problems into steps
- Show reasoning process
- Let the model think step-by-step

### Few-shot Learning
- Provide examples in the prompt
- Demonstrate desired output format
- Include edge cases

## Advanced Techniques

### Self-Consistency
- Ask for multiple reasoning paths
- Aggregate consistent answers
- Vote on most coherent output

### Tree of Thoughts
- Explore multiple reasoning branches
- Backtrack on dead ends
- Navigate a search space of ideas

### Program-Aided Language Models
- Use code execution to verify reasoning
- Break complex tasks into subtasks
- Reuse existing code libraries

## Prompt Patterns

### ReAct (Reasoning + Acting)
1. Think: Analyze the task
2. Act: Use a tool or function
3. Observe: Review the output
4. Repeat until complete

### Self-Ask
1. Ask the model to generate questions
2. Answer each question
3. Synthesize final answer

### Role Prompting
1. Assign a persona or expertise
2. Frame the problem in that context
3. Guide the model's approach

## Common Pitfalls

- Vague instructions leading to generic outputs
- Over-constraining with too many rules
- Ignoring the model's capabilities and limitations
- Not testing with diverse inputs