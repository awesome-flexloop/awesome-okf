---
type: concept
title: "进阶：链式提示与工具增强（附录）"
description: "链式提示（Chaining Prompts）、工具使用（Tool Use/Function Calling）、搜索检索（RAG）模式，从提示词到Agent的演进。"
tags: [prompt-engineering, appendix, chaining-prompts, tool-use, function-calling, rag, agents]
sources:
  - id: anthropic-prompt-tutorial
    resource: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering
    title: Anthropic Prompt Engineering Interactive Tutorial (Appendix)
generated: { by: "process:content-structuring", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
---

# 进阶：链式提示与工具增强（附录）

当单轮提示词无法满足复杂需求时，你需要更强大的模式：链式提示分解任务、工具调用扩展能力、检索增强解决知识问题。这些是构建 AI Agent 的基础积木。

---

## Chaining Prompts（链式提示）

### 核心思想

**不要试图用一个巨大的提示词解决所有问题——把复杂任务分解成多个步骤，每一步用专门的提示词处理，前一步的输出作为后一步的输入。**

这就像人类做复杂工作时会分阶段：先理解需求 → 再收集信息 → 然后起草 → 再修改润色 → 最后检查，而不是一次做完所有事。

### 什么时候用链式提示 vs 单提示

| 场景 | 推荐方式 |
|------|---------|
| 简单问答、格式转换、短文本生成 | 单提示 |
| 任务有清晰的多阶段，每个阶段输出可独立验证 | 链式提示 |
| 长文档处理（先提取→再摘要→再翻译） | 链式提示 |
| 需要"审查/修改"前一步输出（如先写代码→再审查→再修复） | 链式提示 |
| 每一步需要不同的角色/指令 | 链式提示 |
| 中间结果需要人工检查或干预 | 链式提示 |
| 单提示效果不稳定、容易"跑偏" | 考虑链式提示 |

### 链式提示的典型模式

#### 模式1：线性管道（Pipeline）

```
输入 → 提示词A → 中间结果1 → 提示词B → 中间结果2 → ... → 最终输出
```

**示例：长文档分析管道**

1. 提示词1：从长文档中提取所有关键事实和论据
2. 提示词2：基于提取的事实，识别逻辑漏洞和矛盾点
3. 提示词3：基于分析结果，撰写最终的评审报告

```python
# 伪代码示例
doc = read_long_document()

# Step 1: 提取
facts = call_claude(
    prompt="从以下文档中提取所有关键事实，按主题分类：" + doc,
    model="claude-3-haiku"
)

# Step 2: 分析
analysis = call_claude(
    prompt=f"""基于以下提取的事实：
<facts>{facts}</facts>
分析其中的逻辑漏洞、矛盾点和证据不足之处。""",
    model="claude-3-haiku"
)

# Step 3: 撰写报告（可以用更强的模型）
report = call_claude(
    prompt=f"""基于事实和分析，撰写一份结构化评审报告：
<facts>{facts}</facts>
<analysis>{analysis}</analysis>
""",
    model="claude-3-sonnet"
)
```

#### 模式2：生成→审查→修复（Generate-Review-Fix）

```
输入 → 生成 → 审查 → 如果有问题 → 修复 → 最终输出
                ↓
            如果没问题 → 输出
```

**示例：代码生成+审查**

1. 提示词1（开发者角色）：生成实现功能的代码
2. 提示词2（审查者角色）：审查代码的bug、安全问题、性能问题
3. 如果审查发现问题，提示词3（修复者角色）：根据审查意见修复代码
4. 可以多轮审查→修复直到满意

#### 模式3：路由（Router）

```
输入 → 路由提示词（判断类型）→ 分发到对应的专门提示词
                         ↓
                    ┌────┼────┐
                    ↓    ↓    ↓
                  类型A 类型B 类型C
                    ↓    ↓    ↓
                  专门处理...
```

**示例：客服意图路由**

```python
user_msg = "我的账号登不上了，还扣了两次会员费"

# Step 1: 路由分类
intent = call_claude(
    prompt=f"""判断用户问题属于以下哪一类，只输出类别编号：
1. 账号登录问题
2. 计费/退款问题
3. 功能使用问题
4. Bug反馈
5. 其他

用户消息：{user_msg}""",
    model="claude-3-haiku"
)

# Step 2: 分发到对应专门提示词
if intent == "1":
    response = handle_login_issue(user_msg)
elif intent == "2":
    response = handle_billing_issue(user_msg)
# ...
```

#### 模式4：并行分解→汇总（Map-Reduce）

```
    大任务
      ↓
  ┌───┼───┐（拆分）
  ↓   ↓   ↓
子任务A 子任务B 子任务C（并行处理）
  ↓   ↓   ↓
  └───┼───┘（汇总）
      ↓
   最终结果
```

适用于处理多个独立项目：如分析10篇文章，每篇单独分析（map），最后汇总所有分析结果（reduce）。

### 链式提示的优势

1. **每步更简单**：每个提示词只负责一件事，更容易写对
2. **可验证**：可以检查中间结果，早发现错误
3. **可调试**：哪一步出问题改哪一步，不用改整个大提示词
4. **可复用**：某一步的提示词可以在其他链条中复用
5. **成本优化**：简单步骤用Haiku省钱，最后复杂步骤用Sonnet/Opus

### 链式提示注意事项

- **错误累积**：前一步的错误会传递到后一步，关键中间结果需要检查
- **延迟增加**：多轮API调用会增加总响应时间
- **Token成本**：需要传前面的结果，可能增加token消耗
- **不要过度拆分**：如果一步能做好，就不要硬拆成三步——增加复杂度没有收益

---

## Tool Use（工具使用 / Function Calling）

### 核心思想

**大语言模型本身不能上网、不能算数学、不能查数据库——但你可以给它"手"和"脚"：让它决定何时调用什么工具，你的代码执行工具后把结果还给它，它再继续回答。**

工具使用（Tool Use，也叫 Function Calling）是构建 Agent 的核心能力。Claude 原生支持工具调用。

### 提示词与工具使用的关系

工具使用不是提示词的替代品——你依然需要提示词，而且**工具的描述本身就是提示词工程的一部分**。模型是否能正确选择工具、正确传参，很大程度上取决于你怎么写工具描述。

### 工具描述最佳实践

```python
tools = [
    {
        "name": "get_stock_price",
        "description": "获取指定股票的当前价格和基本信息。当用户询问某只股票的实时价格、今日涨跌幅时使用此工具。",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "股票代码，如'AAPL'（苹果）、'600519.SS'（贵州茅台）。美股直接用ticker，A股加.SS（沪市）或.SZ（深市）后缀。"
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "search_knowledge_base",
        "description": "搜索公司内部知识库，获取产品文档、政策说明、常见问题答案。当用户询问产品功能、公司政策、操作指南等内部信息时使用。不要用于回答通用知识或外部新闻。",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词，提炼最核心的2-3个关键词，不要用完整问句。"
                },
                "num_results": {
                    "type": "integer",
                    "description": "返回结果数量，默认3条，最多10条",
                    "default": 3
                }
            },
            "required": ["query"]
        }
    }
]
```

### 好的工具描述要点

1. **说清楚"做什么"**：功能描述简洁明确
2. **说清楚"什么时候用"**：触发条件是什么、什么场景该用、什么场景**不该用**
3. **参数描述清楚**：每个参数是什么意思、格式要求、示例值、默认值
4. **给边界条件**：参数取值范围、最大最小值、异常情况处理

### 系统提示词中的工具相关指引

除了工具本身的描述，你还可以在系统提示词中补充工具使用规则：

```text
关于工具使用：
1. 回答问题时，优先判断是否需要调用工具。如果需要，先调用工具获取信息，再根据工具结果回答。
2. 不要凭记忆回答实时性问题（如股价、天气、新闻），必须调用对应的工具。
3. 如果工具返回错误或没有结果，直接告诉用户，不要编造信息。
4. 需要多个工具时可以并行调用，不需要等一个返回再调另一个。
5. 如果用户问的问题不需要工具（如常识、创意写作、基于对话历史的问题），直接回答即可。
```

→ 完整的工具使用教程和代码示例见 [Python SDK 工具使用](/python-sdk/concepts/04-tool-use.md)

---

## Search & Retrieval（搜索与检索 / RAG）

### 核心思想

**模型的训练数据有截止日期，也不可能知道你公司的内部文档、个人笔记、最新信息。检索增强生成（Retrieval-Augmented Generation, RAG）的思路是：先从外部知识库搜索相关信息，把检索到的内容喂给 Claude，让它基于这些真实信息回答。**

这是目前解决幻觉问题最有效的工程手段之一（L2防护层）。

### RAG 的基本流程

```
用户提问
   ↓
[检索] 查询向量数据库/搜索引擎，找到最相关的文档片段
   ↓
[增强] 把检索到的片段注入到提示词中
   ↓
[生成] Claude 基于提供的上下文回答问题
```

### RAG 场景的提示词模式

```xml
<instructions>
你是一个知识库问答助手。严格按照以下规则回答：
1. 只使用<retrieved_documents>中提供的信息回答问题
2. 每个答案后标注来源文档ID
3. 如果检索到的文档中没有答案，明确说"根据现有资料无法回答该问题"，并建议用户换个问法或联系支持
4. 不要使用你自己的先验知识，即使你"知道"答案——只基于提供的文档
5. 如果多个文档的信息有冲突，说明冲突之处，并分别标注来源
</instructions>

<retrieved_documents>
<document id="doc-001" relevance_score="0.92">
[检索到的文档片段1内容]
</document>
<document id="doc-005" relevance_score="0.78">
[检索到的文档片段2内容]
</document>
<document id="doc-012" relevance_score="0.65">
[检索到的文档片段3内容]
</document>
</retrieved_documents>

<user_question>
用户的问题是什么？
</user_question>

<output_format>
<answer>
[你的回答]
</answer>
<sources>
- [doc-001]
- [doc-005]
</sources>
<confidence>高/中/低</confidence>
</output_format>
```

### RAG 提示词关键点

1. **严格隔离**：明确告诉模型只能用提供的文档，不能用"内置知识"
2. **结构化呈现**：每个文档片段带ID，方便引用
3. **来源要求**：强制标注来源，用户可以溯源
4. **兜底机制**：检索不到时明确说不知道，不要编造
5. **冲突处理**：教模型如何处理文档间矛盾的信息

→ 更多 RAG 模式和最佳实践见 [Cookbook RAG 模式](/cookbooks/concepts/03-rag-patterns.md)

---

## 从提示词到 Agent 的演进路径

现在你已经看到了所有积木——单轮提示词、结构化技巧、思维链、防幻觉、链式提示、工具使用、RAG——把这些组合起来，就是 AI Agent：

```
Level 0: 单轮提示（Zero-shot）
    ↓ +角色、清晰直接、格式要求
Level 1: 结构化提示（XML标签、Few-shot、CoT）
    ↓ + 分步骤链式调用
Level 2: 链式工作流（Pipeline、路由、审查修复）
    ↓ + 工具调用能力
Level 3: 工具增强 Agent（能调用搜索、计算、API）
    ↓ + 检索系统
Level 4: RAG Agent（基于私有知识回答）
    ↓ + 规划能力+记忆+反思
Level 5: 自主 Agent（自主规划、执行、反思、迭代完成复杂任务）
```

### Agent 系统的核心组件

一个典型的 AI Agent 系统包含：

| 组件 | 作用 | 对应你学到的技巧 |
|------|------|-----------------|
| **系统提示词（System Prompt）** | 定义Agent的角色、目标、行为准则 | 角色分配、指令结构、约束/防护 |
| **工具集（Tools）** | Agent可以调用的外部能力 | 工具使用、工具描述最佳实践 |
| **记忆（Memory）** | 短期（对话历史）+ 长期（知识库） | RAG检索注入、对话上下文管理 |
| **规划（Planning）** | 把复杂任务分解为步骤 | 链式提示、思维链 |
| **执行（Execution）** | 调用工具、执行动作、获取结果 | 工具调用循环 |
| **反思（Reflection）** | 检查结果是否正确、是否需要修正 | 生成→审查→修复模式 |

### 什么时候需要 Agent，什么时候不需要？

**不需要Agent，单/多轮提示就够：**
- 一次性文本任务（摘要、翻译、写作）
- 格式转换、数据提取
- 简单问答
- 不需要外部工具、不需要多步执行

**需要Agent：**
- 任务需要多步执行、中途可能需要调整
- 需要调用外部工具（搜索、计算、API、数据库）
- 需要在执行过程中"观察→思考→行动"循环
- 任务环境有不确定性，需要根据反馈调整
- 需要自主完成复杂目标（如"帮我订一张明天去上海的最便宜机票"）

> 提示：Claude Code 就是一个成熟的 Agent 实现，可以参考其设计思路。见 [Claude Code Wiki](/claude-code/)。

---

## 课程总结

恭喜你学完了 Anthropic 提示词工程的核心内容！让我们回顾一下 80/20 要点：

### 基础层（必须掌握）
1. **三要素结构**：任务 + 上下文 + 约束
2. **清晰直接**：用肯定句、具体量化、不要模糊
3. **XML 标签**：永远分离数据和指令

### 进阶层（显著提升质量）
4. **角色提示**：专业任务给明确角色和行为规范
5. **格式化输出**：指定格式，用填空模式，必要时预填充开头
6. **思维链**：多步骤推理任务让 Claude 先思考再回答
7. **Few-shot**：风格/格式难描述时，给示例比说更有用

### 高风险场景层
8. **防幻觉**：要求来源引用、不知道就说不知道、置信度标注
9. **复杂提示词模块化**：角色→指令→数据→示例→格式→防护

### 系统层
10. **链式提示**：复杂任务分解为多步
11. **工具使用**：写好工具描述，让 Claude 能调用外部能力
12. **RAG**：事实性场景必须检索增强，不要让模型"凭记忆"

**最重要的技巧其实只有一个：多实践，多迭代。** 提示词工程是经验科学，写得越多、调试越多，感觉越好。

---

## 相关概念

- [高级模式（Ch8-9）](03-advanced-patterns.md) — 回到高级技巧
- [Python SDK 工具使用](/python-sdk/concepts/04-tool-use.md) — 完整的Tool Use代码教程
- [Cookbook RAG 模式](/cookbooks/concepts/03-rag-patterns.md) — RAG实战模式
- [Claude Code 概览](/claude-code/concepts/00-overview.md) — 了解实际的Agent产品
- [Python SDK 概览](/python-sdk/concepts/00-overview.md) — 开始用代码调用Claude
