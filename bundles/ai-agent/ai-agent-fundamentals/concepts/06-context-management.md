---
type: Concept
title: 上下文管理
description: 在有限的上下文窗口内高效管理信息——压缩策略、Token 预算、分层加载与记忆压缩
tags: [ai-agent, context-management, compaction, token-budget, compression, sliding-window]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T01:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T02:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: src-register
    resource: /references/ai-agent-sources.md
  - id: zleap
    resource: /references/ai-agent-sources.md#zleap-agent
  - id: dsh
    resource: /references/ai-agent-sources.md#deepseek-harness
  - id: book2skill
    resource: /references/ai-agent-sources.md#book-to-skill
  - id: veadk
    resource: /references/ai-agent-sources.md#veadk-python
---

# 上下文管理

LLM 的上下文窗口是有限资源——即使是 1M token 的模型，上下文管理仍然是 Agent 框架的核心挑战。上下文管理解决的问题是：**在有限的 token 预算内，让 Agent 看到最相关的信息，同时不丢失关键上下文**。本文分析四种上下文管理策略：滑动窗口、记忆压缩、分层加载和编译时蒸馏。

## 上下文窗口的挑战

### 为什么需要上下文管理

1. **物理限制**：所有模型都有 max_context_tokens 上限（4K–1M+ tokens）
2. **成本控制**：更多 token = 更高的 API 费用
3. **注意力稀释**："中间迷失"（Lost in the Middle）现象——模型对上下文中段信息的注意力较弱
4. **延迟**：更长的上下文 = 更长的推理时间
5. **信噪比**：无关信息会干扰模型推理质量

### 上下文的组成

一个典型 Agent 回合的上下文由以下部分组成：

```
┌────────────────────────────────────────┐
│ System Prompt（100-2000 tokens）       │ ← 固定开销
├────────────────────────────────────────┤
│ Tool Definitions（200-5000 tokens）    │ ← 随工具数量增长
├────────────────────────────────────────┤
│ Retrieved Memory（0-3000 tokens）      │ ← 从长期记忆检索
├────────────────────────────────────────┤
│ Conversation History（可变）           │ ← 随对话轮次增长
│  ├─ 早期消息（可能已被压缩/摘要）       │
│  └─ 最近 N 轮消息（完整保留）           │
├────────────────────────────────────────┤
│ Current Input（100-5000 tokens）       │ ← 当前用户输入
├────────────────────────────────────────┤
│ Tool Results（可变）                   │ ← 工具执行结果
└────────────────────────────────────────┘
```

## 策略一：滑动窗口 + 摘要压缩

最基本也是最普遍的策略——保留最近的 N 轮完整对话，对更早的消息进行摘要压缩。

### veadk-python 的 ShortTermMemory 压缩

```python
class ShortTermMemory:
    def __init__(self, max_tokens: int = 8000):
        self.messages: list[Message] = []
        self.max_tokens = max_tokens
        self._summary: str | None = None  # 早期消息的摘要
    
    def add(self, message: Message):
        self.messages.append(message)
        self._maybe_compact()
    
    def _maybe_compact(self):
        """当 token 数超限时压缩"""
        current_tokens = self._count_tokens()
        if current_tokens <= self.max_tokens:
            return
        
        # 策略：保留 system prompt + 最近 K 轮，摘要更早的消息
        system_msg = self._find_system_message()
        recent_messages = self._get_recent_messages(k=5)  # 保留最近5轮
        old_messages = self._get_old_messages(before=recent_messages[0])
        
        # 使用 LLM 生成旧消息的摘要
        if old_messages:
            new_summary = self._summarize(old_messages, self._summary)
            self._summary = new_summary
        
        # 重建消息列表：system + summary + recent
        self.messages = [system_msg]
        if self._summary:
            self.messages.append(Message(
                role="system",
                content=f"Earlier conversation summary: {self._summary}"
            ))
        self.messages.extend(recent_messages)
    
    def _summarize(self, messages: list[Message], existing_summary: str | None) -> str:
        """使用 LLM 生成/更新摘要"""
        prompt = "Summarize the following conversation concisely:"
        if existing_summary:
            prompt += f"\n\nExisting summary: {existing_summary}"
        prompt += f"\n\nNew messages to incorporate: {format_messages(messages)}"
        return self.llm.complete(prompt)
```

### deepseek-harness 的 compaction 包

deepseek-harness 通过独立的 `compaction` 包实现上下文压缩，作为 Cordis 插件插入 agent-loop：

```typescript
// compaction 包通过 waterfall 事件在循环前检查上下文长度
ctx.waterfall("agent/loop", async (state, next) => {
    const tokenCount = await ctx.llm.countTokens(state.messages);
    if (tokenCount > state.maxTokens * 0.8) {
        // 超过 80% 时触发压缩
        state.messages = await this.compact(state.messages);
    }
    return next(state);
});
```

compaction 的策略比简单的滑动窗口更复杂，可能包括：
- **Semantic compaction**：不是简单截断，而是保留语义关键信息
- **Tool result trimming**：工具返回结果可能很长（如大文件读取），只保留关键部分
- **Thought pruning**：模型的中间思考过程（chain-of-thought）可以安全删除

## 策略二：Workspace 级上下文隔离

Zleap-Agent 的 Workspace 架构天然实现了上下文隔离——每个 Workspace 只看到：

1. System Prompt（全局）
2. Workspace Prompt（当前阶段专属指令）
3. 前一个 Workspace 的 Artifact（不是全部历史，只是前序产出）
4. 当前 Workspace 的可用工具定义
5. 按需检索的记忆

```
┌─ Workspace 1: 规划 ──────────────┐
│ System Prompt                    │
│ Workspace Prompt: "制定计划..."    │
│ Tools: web_search, read_file     │
│ Memory: 用户偏好 + 相关经验        │
│ Input: 用户原始请求               │
└──────────────────────────────────┘
          │ Artifact: 执行计划
          ▼
┌─ Workspace 2: 执行 ──────────────┐
│ System Prompt                    │
│ Workspace Prompt: "按计划执行..."  │
│ Tools: terminal, write_file, git │
│ Memory: 编码规范 + 项目背景        │
│ Input: [执行计划]                 │ ← 只看到计划，不看到规划过程
└──────────────────────────────────┘
```

**优势**：
- 每个 Workspace 的上下文天然短小（只包含当前阶段需要的信息）
- 早期阶段的无关推理不会污染后续阶段
- 工具定义只包含当前阶段需要的工具，节省 tool definition tokens

## 策略三：编译时知识蒸馏

book-to-skill 项目提出了一种根本不同的策略——**编译时知识蒸馏**（Compile-time Knowledge Distillation），将 RAG 的查询时检索前移为编译时的结构化提取。

### 核心洞察：发现循环税

book-to-skill 提出了"发现循环税"（Discovery Loop Tax）的概念：每次 Agent 使用 RAG 检索时，都需要经历"猜测关键词→检索→阅读→判断是否相关→重新检索"的循环，每次循环消耗大量 token 和时间。通过编译时预处理，可以避免这个税。

### 四层产出结构

```
编译时（一次性支付）：
  原始书籍/文档
    → 格式解析（7种parser）
    → LLM 深度分析（章节结构、框架、反模式）
    → 分层产出：
        ├── SKILL.md          (~4K tokens, 核心心智模型+索引)
        ├── chapters/         (每章一个文件, 800-3000 tokens)
        ├── glossary.md       (~1.5K tokens, 术语表)
        ├── patterns.md       (~2K tokens, 模式总结)
        └── cheatsheet.md     (~1.2K tokens, 决策速查)

运行时（每次使用）：
  Agent 加载 SKILL.md 常驻 → 需要具体细节时按需加载单个 chapter 文件
```

### 与传统 RAG 的对比

| 维度 | 传统 RAG | book-to-skill 编译时蒸馏 |
|------|---------|------------------------|
| 检索时机 | 查询时（每次都检索） | 编译时（一次性） |
| 检索内容 | 文本片段（chunks） | 命名框架、决策规则、章节 |
| Token 开销 | 每次查询 2K-8K 检索结果 | 常驻 4K + 按需 1K/章节 |
| 质量保证 | 依赖向量相似度 | LLM 深度分析，结构化产出 |
| 可更新性 | 索引自动更新 | Fold-in 模式增量合并 |
| 节省 | — | 声称 24×–51× token |

### REPL 式大文件访问

对于 >50K token 的大文件，book-to-skill 建议使用 grep/sed 等程序化工具探查，而非全量读入上下文：

```python
# 概念：程序化探查而非全量加载
# 不要：将整本书读入上下文
# 要：使用工具按需搜索
result = subprocess.run(["grep", "-n", "chapter.*regex", "book.md"], capture_output=True)
# 然后只读匹配的行或段落
```

## 策略四：Zleap 的记忆压缩

Zleap-Agent 在 `packages/agent/` 中实现了专门的记忆压缩（compression）模块：

- **对话压缩**：当对话历史超过阈值时，将早期轮次压缩为结构化摘要
- **选择性保留**：不是所有信息都同等重要——用户明确要求"记住"的信息、关键决策、错误及其解决方案被优先保留
- **分区压缩**：人/事/经验三个记忆分区有不同的压缩策略——用户偏好（人）几乎不压缩，事件状态（事）在完成后压缩，经验（经验）经过提炼后保留

## 上下文预算分配

无论使用哪种策略，都需要对有限的 token 预算进行分配：

```
Token 预算分配（假设 8K 窗口）：

System Prompt:          ~1000 tokens  (12.5%)
Tool Definitions:       ~1500 tokens  (18.75%)  ← Workspace 模式可大幅减少
Retrieved Memory:       ~1000 tokens  (12.5%)
Conversation History:   ~3000 tokens  (37.5%)  ← 压缩/滑动窗口管理
Current Input:          ~1000 tokens  (12.5%)
Tool Results Buffer:     ~500 tokens  (6.25%)  ← 工具结果预留
```

Zleap-Agent 的 Skill 系统甚至在 Skill 级别定义了 `tokenBudget`，让每个 Skill 声明自己需要多少 token。

## 上下文管理策略选择

| 场景 | 推荐策略 | 代表实现 |
|------|---------|---------|
| 简单对话 Agent | 滑动窗口+摘要 | veadk ShortTermMemory |
| 长对话/复杂任务 | Workspace 隔离 | Zleap-Agent |
| 频繁使用大型文档/书籍 | 编译时蒸馏 | book-to-skill |
| 生产级平台（需插件化） | compaction 插件包 | deepseek-harness |
| 多轮工具调用循环 | 语义压缩+工具结果裁剪 | dsh guard+compaction |

## 相关概念

- [记忆架构](03-memory-architecture.md) — 长期记忆是上下文管理的重要来源
- [模型 Provider 抽象](05-provider-abstraction.md) — Token 计数依赖 provider 的 tokenizer
- [技能与 Persona 系统](07-skill-persona.md) — book-to-skill 的编译时蒸馏方法
- [Agent 核心循环](01-agent-loop.md) — 上下文管理在每个循环回合中的位置
