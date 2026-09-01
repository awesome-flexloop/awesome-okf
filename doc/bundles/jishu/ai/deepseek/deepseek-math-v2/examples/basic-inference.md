---
type: example
scope: deepseek-math-v2
name: basic-inference
description: 使用 DeepSeekMath-V2 API 进行基本数学推理和证明生成
---

# 基本推理示例

本文展示如何使用 DeepSeekMath-V2 API 进行数学推理。

## 快速开始：单题解答

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-deepseek-api-key",
    base_url="https://api.deepseek.com"
)

problem = """
Let a, b, c be positive real numbers such that abc = 1. Prove that:
a^2 + b^2 + c^2 + 2abc >= 2(ab + bc + ca)
"""

response = client.chat.completions.create(
    model="deepseek-math-v2",  # 使用 DeepSeek-Math-V2 模型
    messages=[
        {"role": "system", "content": "You are a world-class mathematician."},
        {"role": "user", "content": f"Prove the following inequality:\n\n{problem}"}
    ],
    temperature=0.7,
    max_tokens=32768
)

# 获取推理过程和最终答案
reasoning = response.choices[0].message.reasoning_content
answer = response.choices[0].message.content
print("=== Reasoning ===")
print(reasoning)
print("\n=== Answer ===")
print(answer)
```

## 使用证明生成模板（推荐）

使用仓库定义的 `proof_generation` 模板，引导模型进行自评：

```python
from openai import OpenAI
import re

client = OpenAI(api_key="your-key", base_url="https://api.deepseek.com")

proof_generation_template = """Your task is to solve a given problem. The problem may ask you to prove a statement, or ask for an answer. If finding an answer is required, you should come up with the answer, and your final solution should also be a rigorous proof of that answer being valid.

Your final solution to the problem should be exceptionally comprehensive and easy-to-follow. You are expected to reason carefully, evaluate your method according to the scoring criteria, and refine your solution by fixing issues until you can make no further progress.

Your final response should be in the following format:

## Solution
[Your detailed solution here]

## Self Evaluation
Here is my evaluation of the solution:
[Your step-by-step analysis]
Based on my evaluation, the final overal score should be:
\\boxed{{...}}

---

## Problem
{question}
"""

problem = "Find all positive integers n such that n^4 + 4 is prime."

response = client.chat.completions.create(
    model="deepseek-math-v2",
    messages=[{"role": "user", "content": proof_generation_template.format(question=problem)}],
    temperature=0.7,
    top_p=0.95,
    max_tokens=32768
)

output = response.choices[0].message.content
print(output)

# 提取自评分
score_match = re.search(r'\\boxed\{([0-9.]+)\}', output)
if score_match:
    score = float(score_match.group(1))
    print(f"\n模型自评分: {score}")
```

## 证明验证示例

使用 `proof_verification` 模板验证一个已有证明：

```python
proof_verification_template = """## Instruction
Your task is to evaluate the quality of a solution to a problem.

Please evaluate the solution and score it according to the following criteria:
- 1: completely correct, all steps proper and clear
- 0.5: generally correct, some details omitted or minor errors
- 0: does not address problem, fatal errors, severe omissions

Here is my evaluation of the solution:
[Your detailed evaluation]
Based on my evaluation, the final overal score should be:
\\boxed{{...}}

---
## Problem
{statement}

## Solution
{proof}
"""

problem = "Prove that sqrt(2) is irrational."
proof = """Assume sqrt(2) = p/q in lowest terms. Then 2q^2 = p^2, so p^2 is even, hence p is even.
Let p = 2k. Then 2q^2 = 4k^2, so q^2 = 2k^2. Thus q^2 is even, so q is even.
But then both p and q are even, contradicting lowest terms. Hence sqrt(2) is irrational."""

response = client.chat.completions.create(
    model="deepseek-math-v2",
    messages=[{"role": "user", "content": proof_verification_template.format(
        statement=problem, proof=proof
    )}],
    temperature=0.0,
    max_tokens=8192
)
print(response.choices[0].message.content)
```

## 批量异步推理

```python
import asyncio, json
from openai import AsyncOpenAI
from tqdm import tqdm

async def solve_problems(problems, api_key, concurrency=16):
    client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    semaphore = asyncio.Semaphore(concurrency)

    async def solve_one(problem):
        async with semaphore:
            response = await client.chat.completions.create(
                model="deepseek-math-v2",
                messages=[{"role": "user", "content": f"Solve: {problem}"}],
                temperature=0.7, max_tokens=16384
            )
            return {
                "problem": problem,
                "reasoning": response.choices[0].message.reasoning_content,
                "answer": response.choices[0].message.content
            }

    tasks = [solve_one(p) for p in problems]
    results = []
    for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks)):
        results.append(await coro)
    return results

# 使用
problems = ["Problem 1...", "Problem 2...", "Problem 3..."]
results = asyncio.run(solve_problems(problems, "your-api-key"))
for r in results:
    print(f"Problem: {r['problem'][:50]}...")
    print(f"Answer: {r['answer'][:200]}...\n")
```
