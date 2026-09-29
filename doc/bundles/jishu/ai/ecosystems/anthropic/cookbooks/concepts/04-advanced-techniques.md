---
type: concept
title: "高级技巧"
description: "Claude 高级应用技巧：Sub-agents 子 Agent 协作模式、Extended Thinking 扩展思考、Prompt Caching 提示缓存、JSON 模式、自动化评估 Evals、成本优化策略、Fine-tuning 微调等 Cookbook 中的进阶实践。"
tags: [advanced, sub-agents, extended-thinking, prompt-caching, json-mode, evals, cost-optimization, fine-tuning]
generated: { by: "process:content-structuring", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
---

# 高级技巧

当你掌握了基础的消息、工具调用、RAG、多模态之后，Cookbooks 中的高级技巧能帮你把系统从"能用"提升到"好用、经济、可靠"。本文档讲解 Cookbook 中展示的进阶能力：子 Agent 协作、扩展思考、提示缓存、JSON 模式、自动化评估、成本优化、微调等。

这些技巧不是互斥的——生产级系统通常会组合使用多种技巧。

## Sub-agents（子 Agent）模式

Sub-agents 是 Cookbook 中展示的最强大的架构模式之一：用多个小的、专门化的 Agent 协作完成复杂任务，而不是一个大而全的 Agent。

### 核心思想

```
❌ 单体 Agent 模式（一个大 Agent 做所有事）：
   用户 → 全能 Agent → 结果
   问题：系统提示太长、工具太多难以选择、成本高（大模型做简单任务）

✅ Sub-agents 模式（主 Agent 路由 + 子 Agent 执行）：
                 ┌─→ 研究子 Agent (Haiku，便宜快)
                 │
   用户 → 主 Agent ─→ 写作子 Agent (Sonnet，平衡)
                 │
                 └─→ 深度推理子 Agent (Opus，复杂思考)
```

### 典型分工：Haiku 做路由，Opus 做推理

Cookbook 中的经典模式：

| 模型 | 角色 | 做什么 | 原因 |
|------|------|--------|------|
| **Haiku** | 路由器/分类器 | 判断用户意图、分类任务、简单查询、提取参数 | 速度快、成本低（约为 Sonnet 的 1/10） |
| **Sonnet** | 主力执行 | 大多数常规任务、工具调用、RAG 问答 | 性价比最高 |
| **Opus** | 深度推理 | 复杂分析、多步推理、代码生成、困难决策 | 能力最强，只在需要时调用 |

### Sub-agent 实现骨架

```python
from anthropic import Anthropic
from enum import Enum

client = Anthropic()

class TaskType(Enum):
    SIMPLE = "simple"      # 简单问答 → Haiku 直接回答
    RESEARCH = "research"  # 信息检索 → Sonnet + 搜索工具
    WRITING = "writing"    # 写作创作 → Sonnet
    COMPLEX = "complex"    # 复杂推理 → Opus

def route_task(user_message: str) -> TaskType:
    """用 Haiku 判断任务类型（路由）"""
    router_prompt = f"""判断以下用户请求属于哪种类型，只返回类型名称：

- simple: 简单问候、常识问题、不需要工具的直接回答
- research: 需要查找信息、搜索文档、查询数据
- writing: 写文章、写邮件、写代码、创作内容
- complex: 复杂推理、数学证明、多步分析、困难的决策

用户请求：{user_message}

类型："""

    response = client.messages.create(
        model="claude-3-haiku-20240307",  # 便宜快速的模型做路由
        max_tokens=50,
        messages=[{"role": "user", "content": router_prompt}]
    )
    result = response.content[0].text.strip().lower()
    try:
        return TaskType(result)
    except ValueError:
        return TaskType.COMPLEX  # 默认用复杂模式

def handle_simple(message: str) -> str:
    """简单任务 - Haiku 直接回答"""
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=500,
        messages=[{"role": "user", "content": message}]
    )
    return response.content[0].text

def handle_research(message: str) -> str:
    """研究任务 - Sonnet + 工具"""
    # 这里是完整的工具调用循环（参见工具调用模式）
    return run_agent_with_tools(
        model="claude-3-5-sonnet-latest",
        tools=[search_web, query_database],
        message=message
    )

def handle_complex(message: str) -> str:
    """复杂任务 - Opus + 扩展思考"""
    return run_agent_with_tools(
        model="claude-3-opus-20240229",
        tools=[...],  # 全套工具
        message=message,
        thinking=True  # 开启扩展思考（见后文）
    )

# 主函数
def chat(user_message: str) -> str:
    task_type = route_task(user_message)
    
    handlers = {
        TaskType.SIMPLE: handle_simple,
        TaskType.RESEARCH: handle_research,
        TaskType.WRITING: handle_research,  # 写作也用 Sonnet
        TaskType.COMPLEX: handle_complex,
    }
    
    return handlers[task_type](user_message)
```

### Sub-agent 模式的收益

Cookbook 中的经验数据：
- **成本降低 60-80%**：大部分简单任务用 Haiku 处理
- **响应速度提升**：Haiku 比 Opus 快数倍
- **准确率提升**：每个子 Agent 的系统提示更短更专注，减少"分心"
- **可维护性提升**：每个子 Agent 独立修改，不互相影响

### Agent SDK 中的企业级 Agent

Cookbooks 的 Claude Agent SDK 部分提供了更完善的子 Agent 实现（幕僚长、SRE、研究等专用 Agent），这是比手动编排更高级的模式，适合复杂企业场景。

## Extended Thinking（扩展思考）

Extended Thinking 让 Claude 在回答之前进行更长时间的"内部思考"——显示思维链、增加推理预算，显著提升复杂任务的准确率。

### 什么是 Extended Thinking？

```
普通模式：
  用户问题 → Claude 快速思考（几百 token）→ 回答
  适合：简单问答、常规任务

扩展思考模式：
  用户问题 → Claude 深度思考（数千甚至上万 token）→ 思考过程可见 → 最终回答
  适合：数学题、复杂推理、代码调试、多步分析、困难决策
```

### 开启方式

```python
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",  # 支持 thinking 的模型
    max_tokens=4096,
    thinking={
        "type": "enabled",
        "budget_tokens": 2000  # 思考预算（1024-32000 之间）
    },
    messages=[{"role": "user", "content": "一个复杂的数学/推理问题"}]
)

# 响应中会包含 thinking 内容块
for block in response.content:
    if block.type == "thinking":
        print(f"[思考过程] {block.thinking}")
    elif block.type == "text":
        print(f"[最终回答] {block.text}")
```

### 什么时候用 Extended Thinking？

Cookbook 建议在以下场景开启：

| 场景 | 是否开启 | 思考预算建议 |
|------|---------|-------------|
| 简单聊天/问答 | ❌ 不需要 | - |
| 常规写作/摘要 | ❌ 不需要 | - |
| 数学题、逻辑题 | ✅ 建议 | 2000-4000 |
| 代码调试/复杂重构 | ✅ 建议 | 3000-6000 |
| 多步推理、因果分析 | ✅ 建议 | 4000-8000 |
| 极其困难的问题 | ✅ 建议 | 8000+ |

### 使用技巧

1. **思考预算不是越大越好**：超过一定阈值后收益递减，先从 2000 开始试
2. **思考过程也要算钱**：thinking tokens 按 input token 费率计费，注意成本
3. **可以和工具调用结合**：思考→决定调用工具→看结果→继续思考→回答
4. **流式输出时也能看到思考过程**：思考内容块会随着生成逐步返回

## Prompt Caching（提示缓存）

Prompt Caching 是 Anthropic 推出的成本优化功能——缓存不常变化的提示前缀，重复请求时直接使用缓存，最多降低 90% 成本，同时加快响应速度。

### 缓存什么？

| 缓存内容 | 示例 | 缓存收益 |
|---------|------|---------|
| 系统提示 | 角色设定、规则说明、风格指南 | 极高 |
| 工具定义 | JSON Schema 格式的 tools 列表 | 极高 |
| 长文档上下文 | RAG 中的知识库内容、PDF 内容 | 高 |
| 多轮对话历史 | 前几轮的消息（通常不变） | 中 |
| 用户当前问题 | 不缓存（每次不同） | - |

### 开启方式

Cache Control 是通过在消息内容块上标记 `cache_control` 来实现的：

```python
system_prompt = [
    {
        "type": "text",
        "text": "你是一个客服助手，需要遵守以下 100 条规则...（很长的系统提示）",
        "cache_control": {"type": "ephemeral"}  # 标记这个块需要缓存
    }
]

tools = [
    {
        "name": "get_order_status",
        "description": "...",
        "input_schema": {...},
        # 整个 tools 列表会自动被缓存（如果系统提示标记了）
    }
]

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    system=system_prompt,
    tools=tools,
    messages=[
        # 消息历史也可以标记缓存点
        {"role": "user", "content": [
            {"type": "text", "text": "很长的文档内容...", "cache_control": {"type": "ephemeral"}},
        ]},
        {"role": "assistant", "content": "..."},
        {"role": "user", "content": "用户当前的问题（不缓存）"}
    ]
)
```

### 缓存工作原理

```
第一次请求：
  ┌─────────────────────────────────────────┐
  │ 系统提示（标记缓存）→ 计算缓存键 → 存储 │
  │ 工具定义（标记缓存）→ 计算缓存键 → 存储 │
  │ 文档内容（标记缓存）→ 计算缓存键 → 存储 │
  │ 用户问题 → 正常处理                      │
  └─────────────────────────────────────────┘
  → 按正常价格收费

第二次请求（相同前缀）：
  ┌─────────────────────────────────────────┐
  │ 系统提示 → 命中缓存 → 缓存读取价格（10%）│
  │ 工具定义 → 命中缓存 → 缓存读取价格       │
  │ 文档内容 → 命中缓存 → 缓存读取价格       │
  │ 用户新问题 → 正常处理                    │
  └─────────────────────────────────────────┘
  → 成本降低 90%，响应更快

缓存有效期：5 分钟不活跃后过期
```

### 最佳实践（来自 Cookbook）

1. **把最长、最不变的内容放最前面**：缓存按前缀匹配，从消息开头开始
2. **在"断点"处标记缓存**：在变化内容之前的最后一个不变块上标记
3. **RAG 系统提示必缓存**：系统提示和工具定义通常 100% 不变，缓存收益最大
4. **长文档优先缓存**：如果你加载了一本手册或多个 PDF，缓存它们
5. **不要缓存用户当前问题**：那总是变的，缓存了也不会命中
6. **观察 cache_creation 和 cache_read 指标**：在 response.usage 里能看到缓存命中情况

## JSON 模式（结构化输出）

JSON 模式强制 Claude 只返回有效的 JSON，不会有多余的解释文字——这在提取结构化数据、分类、函数调用参数生成等场景中极其有用。

### 开启方式

```python
response = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    messages=[{"role": "user", "content": "从以下文本提取用户信息：张三，30岁，北京人"}],
    response_format={"type": "json_object"}  # 开启 JSON 模式
)

# 响应保证是有效 JSON，可以直接解析
import json
result = json.loads(response.content[0].text)
print(result["name"], result["age"], result["city"])
```

### 配合 JSON Schema 使用（更精确）

```python
# 定义期望的结构
user_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "用户姓名"},
        "age": {"type": "integer", "description": "用户年龄"},
        "city": {"type": "string", "description": "所在城市"},
        "interests": {
            "type": "array",
            "items": {"type": "string"},
            "description": "兴趣爱好列表"
        }
    },
    "required": ["name", "age", "city"]
}

response = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    system="你是一个信息提取专家，严格按 schema 输出 JSON。",
    messages=[{
        "role": "user",
        "content": f"从以下文本提取信息，符合这个 JSON Schema：\n{json.dumps(user_schema, ensure_ascii=False)}\n\n文本：{user_text}"
    }],
    response_format={"type": "json_object"}
)
```

### JSON 模式最佳实践

1. **在系统提示中明确说明"只输出 JSON"**：双保险，即使不开 response_format 也能提高概率
2. **给出 JSON Schema**：Claude 根据 schema 生成，准确率大幅提升
3. **提供示例**：给一个输入输出的例子（few-shot），效果更好
4. **结合 Vision 使用**：从图片中提取结构化信息（发票、表单等）时，JSON 模式是神器
5. **不要在 JSON 模式下让 Claude 解释**：它不会（也不应该）输出解释文字

## 自动化评估（Evals）框架

Evals（自动化评估）是确保 LLM 系统质量的关键——你不可能每次改完提示词都人工测试所有 case。Cookbook 展示了用 Claude 评估 Claude 的"LLM-as-Judge"模式。

### Evals 核心流程

```
┌─────────────────────────────────────────────────────────┐
│  1. 准备测试集（黄金标准）                              │
│     输入 + 期望输出（人工标注）                         │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│  2. 运行你的系统                                        │
│     对每个测试输入，收集系统的实际输出                  │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│  3. LLM-as-Judge 评估                                   │
│     用 Claude（通常是 Opus）对比期望输出 vs 实际输出    │
│     打分（1-5）或判定（对/错/部分对），给出理由         │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│  4. 生成评估报告                                        │
│     通过率、平均分、失败案例、改进建议                  │
└─────────────────────────────────────────────────────────┘
```

### Cookbook 风格的 Eval 实现

```python
import json
from dataclasses import dataclass

@dataclass
class EvalCase:
    input: str
    expected: str
    category: str = "general"

def evaluate_case(case: EvalCase, actual_output: str) -> dict:
    """用 Claude 评估单个 case"""
    judge_prompt = f"""你是一个严格的质量评估员。对比"期望回答"和"系统实际回答"，评估回答质量。

输入问题：{case.input}
期望回答：{case.expected}
系统实际回答：{actual_output}

请评估：
1. 正确性（1-5）：事实是否正确？是否回答了问题？
2. 完整性（1-5）：是否遗漏了要点？
3. 简洁性（1-5）：是否有多余废话？
4. 总体评分（1-5）

以 JSON 格式返回：
{{
  "correctness": 分数,
  "completeness": 分数,
  "conciseness": 分数,
  "overall": 分数,
  "passed": true/false（overall >= 4 算通过）,
  "issues": "具体问题描述",
  "suggestions": "改进建议"
}}"""

    response = client.messages.create(
        model="claude-3-opus-20240229",  # 用最强模型做评判
        max_tokens=500,
        messages=[{"role": "user", "content": judge_prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.content[0].text)

def run_evals(test_cases: list[EvalCase], your_system_fn) -> dict:
    """运行整个评估集"""
    results = []
    for case in test_cases:
        actual = your_system_fn(case.input)
        eval_result = evaluate_case(case, actual)
        eval_result["input"] = case.input
        eval_result["expected"] = case.expected
        eval_result["actual"] = actual
        results.append(eval_result)
    
    # 汇总统计
    passed = sum(1 for r in results if r["passed"])
    avg_score = sum(r["overall"] for r in results) / len(results)
    
    return {
        "total": len(results),
        "passed": passed,
        "pass_rate": passed / len(results),
        "avg_score": avg_score,
        "failures": [r for r in results if not r["passed"]],
        "details": results
    }
```

### Eval 最佳实践

1. **测试集要多样化**：覆盖简单、中等、困难的 case，覆盖边缘情况
2. **测试集要有人工标注的黄金答案**：至少 50-100 个 case 才有统计意义
3. **每次改提示词/模型/参数都跑一遍 Evals**：防止改坏了
4. **保留失败案例**：每一个失败 case 都要加入测试集，防止回归
5. **不要用同一个模型做生成和评估**：生成用 Sonnet，评估用 Opus，更客观
6. **评估提示词也要迭代**：Judge 本身也可能判错，人工抽检评估结果

## 成本优化策略

Cookbook 中综合的成本优化技巧，按投入产出比排序：

| 优化手段 | 成本降低 | 实现难度 | 性能影响 |
|---------|---------|---------|---------|
| **Prompt Caching** | 最多 90% | ⭐ 极低 | ✅ 可能更快 |
| **模型路由（Sub-agents）** | 60-80% | ⭐⭐ 低 | ✅ 简单任务更快 |
| **缩短 max_tokens** | 10-30% | ⭐ 极低 | ⚠️ 不要设太小 |
| **优化系统提示长度** | 10-50% | ⭐⭐ 低 | ✅ 更专注 |
| **Haiku 做预处理/路由** | 20-60% | ⭐⭐ 中 | ⚠️ 需要测试 |
| **Streaming 提升感知速度** | 0%（但感觉更快）| ⭐ 极低 | ✅ 用户体验更好 |
| **批量请求** | 咨询官方 | ⭐⭐⭐ 中 | ✅ 离线场景 |

### 成本监控代码

```python
# 每次 API 调用后检查 usage
response = client.messages.create(...)
print(f"Input tokens: {response.usage.input_tokens}")
print(f"Output tokens: {response.usage.output_tokens}")
# 如果开启了 caching
print(f"Cache creation: {response.usage.cache_creation_input_tokens}")
print(f"Cache read: {response.usage.cache_read_input_tokens}")
```

记住：**最便宜的 token 是你没发出去的 token**——优化提示词长度、只发送必要的上下文、善用缓存，比换模型效果更显著。

## Fine-tuning（微调）

Cookbook 中展示了在 AWS Bedrock 上微调 Claude 的流程。注意：**大多数场景你不需要微调！** RAG 和提示工程通常就能解决问题。

### 什么时候考虑微调？

| 场景 | 是否建议微调 | 为什么 |
|------|-------------|--------|
| 注入新知识 | ❌ 不建议 | 用 RAG，更新更方便 |
| 改变模型风格/语气 | ✅ 可以考虑 | 大量一致风格的数据时 |
| 特定输出格式 | ⚠️ 先试提示工程 | JSON 模式 + few-shot 通常就够了 |
| 减少 token 使用 | ✅ 可能 | 微调后系统提示可以更短 |
| 特定领域任务（如医疗/法律分类）| ✅ 有领域数据时 | 足够数据下效果提升明显 |
| 你只有不到 100 个训练样本 | ❌ 绝对不要 | 数据太少，不如 few-shot |

> 💡 **Cookbook 经验法则**：先把提示工程和 RAG 做到极致，仍然不满足需求时再考虑微调。

## 内容审核（Content Moderation）

Cookbook 提供了内容审核的模式：输入和输出都需要审核，确保符合安全政策。

### 输入/输出审核双重模式

```
用户输入 → 输入审核（安全吗？）
              ↓ 不安全：直接拒绝
              ↓ 安全
         正常处理（RAG/工具调用/生成）
              ↓
         输出审核（生成的内容安全吗？）
              ↓ 不安全：过滤或重生成
              ↓ 安全
         返回给用户
```

审核本身也可以用 Claude 做（用 Haiku，快速便宜），判断输入/输出是否包含违规内容。

## 相关概念

- [Cookbook 导览](00-overview.md) — 回到 Cookbooks 总览
- [工具调用模式](01-tool-use-patterns.md) — Sub-agents 的工具编排基础
- [RAG 与知识检索模式](03-rag-patterns.md) — Prompt Caching 对 RAG 系统收益最大
- [Python SDK - Beta Agents](../../python-sdk/concepts/08-beta-agents.md) — SDK 层面的 Agents 体系
- [Python SDK - Streaming](../../python-sdk/concepts/03-streaming.md) — Extended Thinking 和流式输出结合使用
- [食谱完整索引](../references/recipe-index.md) — 查找具体高级技巧的食谱
