---
type: bundle
okf_version: "0.2"
scope: deepseek-math-v2
name: deepseek-math-v2
version: "2.0.0"
source: https://github.com/deepseek-ai/DeepSeek-Math-V2
description: DeepSeekMath-V2——面向自验证数学推理的大语言模型，IMO 金牌级定理证明能力
---

# DeepSeekMath-V2

**DeepSeekMath-V2**（论文：*DeepSeekMath-V2: Towards Self-Verifiable Mathematical Reasoning*）是 DeepSeek 推出的数学推理大模型，核心创新是实现**自验证数学推理**——模型不仅生成证明，还能验证自身推理的正确性，通过多轮生成-验证-精炼闭环不断提升证明质量。基于 DeepSeek-V3.2-Exp-Base 训练。

- **论文**：arXiv:2025（作者：Zhihong Shao 等）
- **HuggingFace 模型**：`deepseek-ai/DeepSeek-Math-V2`
- **基础模型**：DeepSeek-V3.2-Exp-Base
- **许可证**：Apache 2.0

## 核心成绩

| 基准 | 成绩 |
|---|---|
| IMO 2025 | 🥇 金牌级别 |
| CMO 2024 | 🥇 金牌级别 |
| Putnam 2024 | **118/120**（接近满分，扩展 test-time compute） |
| IMO-ProofBench | 强力表现 |

## 核心特性

- **自验证闭环**：三层验证架构（生成→验证→元验证）+ 迭代精炼，实现严谨的数学证明
- **忠实自评**：模型被激励如实报告自身错误，禁止"伪正确"
- **test-time compute 扩展**：通过增加采样数、验证次数、精炼轮次提升准确率
- **生成-验证共进化**：扩展验证计算自动标注难例，维持验证器对强生成器的评估能力
- **三级评分体系**：1（完全正确）/ 0.5（大体正确）/ 0（致命错误）

## 快速开始

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-deepseek-api-key",
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-math-v2",
    messages=[{"role": "user", "content": "Prove that sqrt(2) is irrational."}],
    temperature=0.7,
    max_tokens=32768
)

print(response.choices[0].message.reasoning_content)  # 推理链
print(response.choices[0].message.content)             # 最终证明
```

## 文档导航

### 核心概念

- 总览 — 模型定位、自验证动机、训练方法论、评测成绩
- 自验证机制详解 — 三层验证架构、评分体系、迭代精炼流程

### API 参考

- API 使用参考 — API 配置、调用方式、四种 prompt 模板
- 自验证推理管线 — 多轮管线参数与配置

### 使用示例

- 基本推理 — 单题解答、证明生成/验证、批量推理
- 自验证管线 — 运行完整管线、参数调节、断点续跑

## 目录结构

```
deepseek-math-v2/
├── concepts/              # 核心概念（2 篇）
├── references/            # API/配置参考（2 篇）
├── examples/              # 使用示例（2 篇）
└── index.md               # 本文件
```

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
```
